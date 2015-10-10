import time
from google.appengine.api import search

from classes import class_models
from search import index

# StudioClass Models:
# scrapy.Item (optional)
# ndb.Model
# search.Document
# (eventually, json representation?)

class EventsIndex(index.BaseIndex):
    obj_type = class_models.StudioClass

    @classmethod
    def _create_doc_event(cls, studio_class):
        title = '%s: %s' % (studio_class.style, studio_class.teacher)
        description = studio_class.teacher_link
        # include twitter link to studio?
        doc_event = search.Document(
            doc_id=studio_class.id,
            fields=[
                search.TextField(name='name', value=title),
                search.TextField(name='studio', value=studio_class.studio_name),
                search.TextField(name='description', value=description),
                search.DateField(name='start_time', value=studio_class.start_time),
                search.DateField(name='end_time', value=studio_class.end_time),
                search.NumberField(name='latitude', value=studio_class.latitude),
                search.NumberField(name='longitude', value=studio_class.longitude),
                search.TextField(name='categories', value=' '.join(studio_class.auto_categories)),
                search.TextField(name='country', value=studio_class.country),
            ],
            #language=XX, # We have no good language detection
            rank=int(time.mktime(studio_class.start_time.timetuple())),
            )
        return doc_event
