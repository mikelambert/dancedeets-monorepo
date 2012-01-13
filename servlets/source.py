import datetime
from django.utils import simplejson
import logging
import pprint
import urllib2

import base_servlet
from events import eventdata
from logic import potential_events
from logic import thing_db
from logic import thing_scraper

def get_id_from_url(url):
        if '#' in url:
                url = url.split('#')[1]
        match = re.search('id=(\d+)', url)
        if not match:
                return None
        return match.group(1)

class AdminEditHandler(base_servlet.BaseRequestHandler):
    def get(self):
        source_id = None
        if self.request.get('source_url'):
            #TODO(lambert): probably broken
            source_id = get_id_from_url(self.request.get('source_url'))
        elif self.request.get('source_id'):
            source_id = self.request.get('source_id')
        self.batch_lookup.lookup_thing_feed(source_id)
        self.finish_preload()

        fb_source = self.batch_lookup.data_for_thing_feed(source_id)

        real_source_id = fb_source['info']['id']
        s = thing_db.create_source_for_id(real_source_id, fb_source)

        source_potential_events = potential_events.PotentialEvent.gql('WHERE source_ids = :graph_id', graph_id=s.graph_id).fetch(1000)
        found_db_events = [x for x in eventdata.DBEvent.get_by_key_name([str(x.fb_event_id) for x in source_potential_events]) if x]


        if s.creating_fb_uid:
            f = urllib2.urlopen('https://graph.facebook.com/%s?access_token=%s' % (s.creating_fb_uid, self.fb_graph.access_token))
            json = simplejson.loads(f.read())
            creating_user = json['name']
        else:
            creating_user = None

        self.display['creating_user'] = creating_user
        self.display['potential_events'] = source_potential_events
        self.display['db_events'] = found_db_events
        self.display['no_good_event_ids'] = set(x.fb_event_id for x in source_potential_events).difference(x.fb_event_id for x in found_db_events)

        self.display['source'] = s
        self.display['fb_source'] = fb_source
        self.display['fb_source_data'] = pprint.pformat(fb_source['feed']['data'])
        self.display['link_for_fb_source'] = thing_db.link_for_fb_source

        self.display['track_google_analytics'] = False
        self.render_template('admin_source')

    def post(self):
                source_id = self.request.get('source_id')
                self.batch_lookup.lookup_thing_feed(source_id, allow_cache=False)
                self.finish_preload()

        s = thing_db.create_source_for_id(source_id, self.batch_lookup.data_for_thing_feed(source_id))

                if self.request.get('delete'):
                        s.delete()
                        self.user.add_message("Source deleted!")
                        self.redirect('/sources/admin_edit?source_id=%s' % source_id)
                        return

                s.creating_fb_uid = self.user.fb_uid
                s.creation_time = datetime.datetime.now()
        s.put()

        self.user.add_message("Source added!")
        #TODO(lambert): make this a backgrounded action?
        thing_scraper.scrape_events_from_sources(self.batch_lookup.copy(), [s])
        self.redirect('/sources/admin_edit?source_id=%s' % source_id)

