#!/usr/bin/python


from sklearn import metrics
from sklearn.feature_extraction import text
from sklearn import cross_validation
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier

import numpy as np

from classifiers import processing

from nlp import rules
from nlp import keywords
from nlp import grammar
def get_magic_rules(module):
    rules = {}
    for var in dir(module):
        var_value = getattr(module, var)
        if isinstance(var_value, grammar.Name):
            name = '%s.%s' % (module.__name__, var)
            if re.search(r'\.(?:CONNECTOR|ROMANCE)$', var):
                rules[name] = var_value
    return rules
# These are the regexes that will be our feature detectors
named_rules = {}
named_rules.update(get_magic_rules(rules))
named_rules.update(get_magic_rules(keywords))
named_rules['nlp.rules.MANUAL_DANCE[grammar.STRONG]'] = rules.MANUAL_DANCE[grammar.STRONG]
named_rules['nlp.rules.MANUAL_DANCE[grammar.STRONG_WEAK]'] = rules.MANUAL_DANCE[grammar.STRONG_WEAK]
named_rules['nlp.rules.MANUAL_DANCER[grammar.STRONG]'] = rules.MANUAL_DANCER[grammar.STRONG]
named_rules['nlp.rules.MANUAL_DANCER[grammar.STRONG_WEAK]'] = rules.MANUAL_DANCER[grammar.STRONG_WEAK]
named_rules_list = sorted(named_rules.items())
all_ids = processing.load_all_ids()
training_data = processing.load_classified_ids(all_ids)
loaded_data = processing.all_fb_data(all_ids)

print 'loaded ids'

class Bunch(object):
    pass

train = Bunch()

def process(fb_event):
    return '%s\n\n%s' % (fb_event['info'].get('name'), fb_event['info'].get('description'))
import itertools
process_all = True
if process_all:
    loaded_data = list(loaded_data)
else:
    loaded_data = list(itertools.islice(loaded_data, 0, 1000))
train.data = [process(x[1]) for x in loaded_data]

print 'loaded data'

def good_id(event_id):
    return event_id in training_data.good_ids
train.target = [good_id(x[0]) for x in loaded_data]

total_count = len(all_ids)
good_count = len([x for x in train.target if x])
bad_count = total_count - good_count
assert bad_count + good_count == total_count
sample_weights = [0.5 * total_count / (x and good_count or bad_count) for x in train.target]

import array
import re
from sklearn import base
from nlp import event_classifier
from sklearn.externals.joblib import Parallel, delayed

def process_doc(fb_event):
    values = array.array(str("f"))
    classified_event = event_classifier.ClassifiedEvent(fb_event)
    classified_event.classify()
    processed_title = event_classifier.StringProcessor(fb_event['info'].get('name', ''))
    processed_text = event_classifier.StringProcessor(fb_event['info'].get('text', ''))
    dummy, title_word_count = re.subn(r'\w+', '', processed_title.text)
    dummy, text_word_count = re.subn(r'\w+', '', processed_text.text)
    # TODO: Ideally we want this to be the rules_list of the GrammarFeatureVector
    for i, (name, rule) in enumerate(named_rules_list):
        if title_word_count:
            dummy, title_token_count = processed_title.replace_with(rule, '')
            # processed_title.count_tokens(rule)
            title_matches = 1.0 * title_token_count# / title_word_count
        else:
            title_matches = 0
        if text_word_count:
            dummy, text_token_count = processed_text.replace_with(rule, '')
            # processed_text.count_tokens(rule)
            text_matches = 1.0 * text_token_count# / text_word_count
        else:
            text_matches = 0
        values.append(title_matches)
        values.append(text_matches)
    return values

class GrammarFeatureVector(base.BaseEstimator):
    def __init__(self, rules_dict, binary=False):
        #self.rules_dict = rules_dict
        #self.rules_list = sorted(rules_dict.iteritems())
        self.rules_list = named_rules_list
        self.binary = binary
        self.dtype = np.float64

    def _compute_features(self, raw_documents):

        values = array.array(str("f"))
        print "Preloading regexes"
        dummy_processor = event_classifier.StringProcessor('')
        for name, rule in named_rules_list:
            dummy_processor.count_tokens(rule)

        print "Computing Features"
        result = Parallel(n_jobs=7, verbose=5)(delayed(process_doc)(fb_event) for event_id, fb_event in raw_documents)
        for row_values in result:
            values.extend(row_values)

        X = np.array(values)
        X.shape = (len(raw_documents), len(self.rules_list)*2)

        return X

    def fit(self, raw_documents, y=None):
        return self

    def fit_transform(self, raw_documents, y=None):
        return self.fit(raw_documents, y=y).transform(raw_documents)

    def transform(self, raw_documents):
        # use the same matrix-building strategy as fit_transform
        X = self._compute_features(raw_documents)
        if self.binary:
            X.data.fill(1)
        return X

    def get_feature_names(self):
        return _flatten([('%s in title' % name, '%s in text' % name) for (name, rule) in self.rules_list])


def _flatten(listOfLists):
    "Flatten one level of nesting"
    return list(itertools.chain.from_iterable(listOfLists))

grammar_processor = GrammarFeatureVector(named_rules)
for i, name in enumerate(grammar_processor.get_feature_names()):
    print i, name
grammar_processed_data = grammar_processor.fit_transform(loaded_data, train.target)
processed_test_data = grammar_processed_data

if process_all:
    from sklearn.externals import joblib
    joblib.dump(grammar_processed_data, 'grammar-processed.pkl') 

if False:
    text_processor = text.TfidfVectorizer(stop_words='english')
    processed_train_data = text_processor.fit_transform(train.data, train.target)
    # Cheating, but what we did with eval_auto_classifier.py
    processed_test_data = processed_train_data
    # Correct
    #processed_test_data = text_processor.fit_transform(train.test)

test = train

def eval_model(name, model, data):
    print '=' * 20
    print name, 'training'
    model.fit(data, train.target, sample_weight=sample_weights)
    print name, 'trained'

    predictions = model.predict(processed_test_data)
    print name, 'accuracy', np.mean(predictions == test.target)

    print (metrics.classification_report(test.target, predictions))
    print metrics.confusion_matrix(test.target, predictions)

    print name, 'cross validation', cross_validation.cross_val_score(model, grammar_processed_data, train.target, scoring='f1')
    return model, predictions

from sklearn import tree
tree_model, tree_predictions = eval_model('tree', tree.DecisionTreeClassifier(max_depth=10), grammar_processed_data)

feature_names = np.asarray(grammar_processor.get_feature_names())

with open("dtree.dot", 'w') as f:
     f = tree.export_graphviz(tree_model, out_file=f, feature_names=feature_names)

bayes_model, bayes_predictions = eval_model('bayes', MultinomialNB(), grammar_processed_data)
svm_model, svm_predictions = eval_model('svm', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=5), grammar_processed_data)

def show_top10(classifier, categories):
    for i, category in enumerate(categories):
        top10 = np.argsort(classifier.coef_[i])[-10:]
        print category
        for j in reversed(top10):
            print '%s: %s' % (classifier.coef_[i][j], feature_names[j])
        print '...'
        bot10 = np.argsort(classifier.coef_[i])[:10]
        for j in bot10:
            print '%s: %s' % (classifier.coef_[i][j], feature_names[j])

show_top10(bayes_model, ['result'])
