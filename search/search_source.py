import iso3166

from google.appengine.api import search

import app
import base_servlet
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
        fb_info = source.fb_info
        if not fb_info:
            return None
        # TODO(lambert): find a way to index no-location sources.
        # As of now, the lat/long number fields cannot be None.
        # In what radius/location should no-location sources show up
        # and how do we want to return them
        # Perhaps a separate index that is combined at search-time?
        if fb_info.get('location', None) is None:
            return None
        if not source.latitude:
            return None

        country = fb_info['location'].get('country', '').upper()
        if country in iso3166.countries_by_name:
            country_code = iso3166.countries_by_name[country].alpha2
        else:
            country_code = None

        doc_event = search.Document(
            doc_id=source.graph_id,
            fields=[
                search.TextField(name='name', value=source.name),
                search.TextField(name='description', value=fb_info.get('general_info', '')),
                search.NumberField(name='like_count', value=fb_info['likes']),
                search.TextField(name='category', value=fb_info['category']),
                search.TextField(name='category_list', value=', '.join(str(x['name']) for x in fb_info.get('category_list', []))),
                search.NumberField(name='latitude', value=source.latitude),
                search.NumberField(name='longitude', value=source.longitude),
                #search.TextField(name='categories', value=' '.join(source.auto_categories)),
                search.TextField(name='country', value=country_code),
                search.NumberField(name='num_real_events', value=source.num_real_events or 0),
            ],
            #language=XX, # We have no good language detection
            rank=source.num_real_events or 0,
            )
        return doc_event

@app.route('/tasks/refresh_source_index')
class RefreshSourceSearchIndex(base_servlet.BaseTaskRequestHandler):
    def get(self):
        SourceIndex.rebuild_from_query()
