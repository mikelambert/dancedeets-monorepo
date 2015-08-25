from google.appengine.api import search

from event_scraper import thing_db
from . import index

class SourceIndex(index.BaseIndex):
    obj_type = thing_db.Source
    index_name = 'AllSources'

    @classmethod
    def _get_id(cls, obj):
        return obj.graph_id

    @classmethod
    def _create_doc_event(cls, source):
        # TODO: We need to populate the fb data into the db
        fb_source = source.fb_source
        if fb_source['empty']:
            return None
        # TODO(lambert): find a way to index no-location sources.
        # As of now, the lat/long number fields cannot be None.
        # In what radius/location should no-location sources show up
        # and how do we want to return them
        # Perhaps a separate index that is combined at search-time?
        if fb_source['info'].get('location', None) is None:
            return None
        doc_event = search.Document(
            doc_id=source.graph_id,
            fields=[
                search.TextField(name='name', value=source.name),
                search.TextField(name='description', value=fb_source['info'].get('general_info', '')),
                search.NumberField(name='like_count', value=fb_source['info']['likes']),
                search.NumberField(name='latitude', value=fb_source['info']['location']['latitude']),
                search.NumberField(name='longitude', value=fb_source['info']['location']['longitude']),
                #search.TextField(name='categories', value=' '.join(source.auto_categories)),
                search.TextField(name='country', value=fb_source['info']['location']['country']),
            ],
            #language=XX, # We have no good language detection
            rank=fb_source['info']['likes'],
            )
        return doc_event
