# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import base_auto_classifier
from dancedeets.nlp import grammar
from dancedeets.nlp import style_base

Any = grammar.Any
Name = grammar.Name
connected = grammar.connected
commutative_connected = grammar.commutative_connected

DANCE = Any(
    u'cheerlead\w+',
    u'lideres de torcida',  # portuguese
    u'líder de torcida',  # portuguese
    u'navijanje',  # croatian
    u'navijačic\w+',  # croatian
    u'pembimbing sorak',  # malay
    u'pom pom girls',  # french
    u'pompom lányok',  # hungarian
    u'pompomlány',  # hungarian
    u'ponpon kız',  # turkish
    u'porristas',  # spanish
    u'roztleskáv\w+',  # czech
    u'μαζορέτ\w+',  # greek
    u'болельщи\w+',  # russian
    u'мажоретка',  # macedonian
    u'навивање',  # macedonian
    u'черлидинг\w+',  # russian
    u'מעודדות',  # hebrew
    u'מעודדת',  # hebrew
    u'עידוד',  # hebrew
    u'التشجيع',  # arabic
    u'المشجع',  # arabic
    u'المصفقين',  # arabic
    u'เชียร์ลีดเดอร์',  # thai
    u'チア\W?ダン',
    u'チア\W?ダンス',
    u'チアリーダー',  # japanese
    u'チアリーディング',  # japanese
    u'啦啦队',  # chinese simplified
    u'啦啦隊',  # chinese traditional
    u'拉拉队长',  # chinese simplified
    u'拉拉隊長',  # chinese traditional
    #
    u'cheer',
    u'チア',
    u'치어',
    u'Черлидинг',  # russian cheerleading
)

AMBIGUOUS_DANCE = Any()


class Classifier(base_auto_classifier.DanceStyleEventClassifier):
    GOOD_DANCE = DANCE
    GOOD_BAD_PAIRINGS = [
        (Any('cheer'), Any('cheer\w* up')),
    ]

    #AMBIGUOUS_DANCE = AMBIGUOUS_DANCE

    def _quick_is_dance_event(self):
        return True


class Style(style_base.Style):
    @classmethod
    def get_name(cls):
        return 'CHEER'

    @classmethod
    def get_rare_search_keywords(cls):
        return [
            u'болельщи',
            u'チアダン',
            u'치어댄스',
        ]

    @classmethod
    def get_popular_search_keywords(cls):
        return [
            'cheerleading',
            'cheerleader',
            'cheer dance',
            'cheer',
        ]

    @classmethod
    def get_search_keyword_event_types(cls):
        return []

    @classmethod
    def _get_classifier(cls):
        return Classifier

    @classmethod
    def get_basic_regex(cls):
        return Any(DANCE, AMBIGUOUS_DANCE)
