import pprint
import re

import app
import base_servlet
from events import eventdata
import fb_api
from . import potential_events
from . import thing_db
from . import thing_scraper

def get_id_from_url(url):
    if '#' in url:
        url = url.split('#')[1]
    match = re.search('id=(\d+)', url)
    if not match:
        return None
    return match.group(1)

@app.route('/sources/admin_edit')
class AdminEditHandler(base_servlet.BaseRequestHandler):
    def get(self):
        source_id = None
        if self.request.get('source_url'):
            #TODO(lambert): probably broken
            source_id = get_id_from_url(self.request.get('source_url'))
        elif self.request.get('source_id'):
            source_id = self.request.get('source_id')
        s = thing_db.create_source_from_id(self.fbl, source_id)

        #STR_ID_MIGRATE
        source_potential_events = potential_events.PotentialEvent.gql('WHERE source_ids = :graph_id', graph_id=long(s.graph_id)).fetch(1000)
        found_db_event_ids = [x.string_id() for x in eventdata.DBEvent.get_by_ids([x.fb_event_id for x in source_potential_events], keys_only=True) if x]

        if s.creating_fb_uid:
            #STR_ID_MIGRATE
            creating_user = self.fbl.get(fb_api.LookupUser, str(s.creating_fb_uid))
        else:
            creating_user = None

        self.display['creating_user'] = creating_user
        self.display['potential_events'] = sorted(source_potential_events, key=lambda x:x.fb_event_id)
        self.display['db_event_ids'] = sorted(found_db_event_ids)
        self.display['no_good_event_ids'] = sorted(list(set(x.fb_event_id for x in source_potential_events).difference(found_db_event_ids)))

        self.display['source'] = s
        self.display['fb_source'] = {'info': s.fb_info}
        self.jinja_env.globals['link_for_fb_source'] = thing_db.link_for_fb_source

        self.display['track_analytics'] = False
        self.render_template('admin_source')

    def post(self):
        source_id = self.request.get('source_id')
        s = thing_db.create_source_from_id(self.fbl, source_id)

        if self.request.get('delete'):
            s.delete()
            self.user.add_message("Source deleted!")
            self.redirect('/sources/admin_edit?source_id=%s' % source_id)
            return

        #STR_ID_MIGRATE
        s.creating_fb_uid = long(self.user.fb_uid)
        s.street_dance_related = True
        s.put()

        self.user.add_message("Source added!")
        #TODO(lambert): make this a backgrounded action?
        thing_scraper.scrape_events_from_sources(self.fbl, [s])
        self.redirect('/sources/admin_edit?source_id=%s' % source_id)

@app.route('/sources/scrape')
class ScrapeSourceHandler(base_servlet.SourceIdOperationHandler):
    source_id_operation = staticmethod(thing_scraper.scrape_events_from_source_ids_with_fallback)
