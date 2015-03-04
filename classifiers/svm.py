#!/usr/bin/python


from sklearn import metrics
from sklearn.feature_extraction import text
from sklearn import cross_validation
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier

import numpy as np

from classifiers import processing

all_ids = processing.load_all_ids()
training_data = processing.load_classified_ids(all_ids)
loaded_data = processing.all_fb_data(all_ids)

print 'loaded ids'

class Bunch(object):
    pass

train = Bunch()

def process(fb_event):
    return '%s\n\n%s' % (fb_event['info'].get('name'), fb_event['info'].get('description'))
loaded_data = list(loaded_data)
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


text_processor = text.TfidfVectorizer()
processed_train_data = text_processor.fit_transform(train.data, train.target)
# Cheating, but what we did with eval_auto_classifier.py
test = train
processed_test_data = processed_train_data
# Correct
#processed_test_data = text_processor.fit_transform(train.test)


def eval_model(name, model):
    print '=' * 20
    print name, 'training'
    model.fit(processed_train_data, train.target, sample_weight=sample_weights)
    print name, 'trained'

    predictions = model.predict(processed_test_data)
    print name, 'accuracy', np.mean(predictions == test.target)

    print (metrics.classification_report(test.target, predictions))
    print metrics.confusion_matrix(test.target, predictions)

    print name, 'cross validation', cross_validation.cross_val_score(model, processed_train_data, train.target, scoring='f1')
    return model, predictions

bayes_model, bayes_predictions = eval_model('bayes', MultinomialNB())
svm_model, svm_predictions = eval_model('svm', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=5))

def show_top10(classifier, vectorizer, categories):
    feature_names = np.asarray(vectorizer.get_feature_names())
    for i, category in enumerate(categories):
        top10 = np.argsort(classifier.coef_[i])[-50:]
        print("%s: %s" % (category, " ".join(feature_names[top10])))

show_top10(bayes_model, text_processor, [False, True])
