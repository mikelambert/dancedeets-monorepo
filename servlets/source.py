import datetime
from django.utils import simplejson
import urllib2

import base_servlet
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
        self.batch_lookup.lookup_thing_feed(source_id, allow_cache=False)
        self.finish_preload()

        fb_source = self.batch_lookup.data_for_thing_feed(source_id)

        real_source_id = fb_source['info']['id']
        s = thing_db.create_source_for_id(real_source_id, fb_source)
        if s.creating_fb_uid:
            f = urllib2.urlopen('https://graph.facebook.com/%s?access_token=%s' % (s.creating_fb_uid, self.fb_graph.access_token))
            json = simplejson.loads(f.read())
            creating_user = json['name']
        else:
            creating_user = None

        self.display['creating_user'] = creating_user

        self.display['source'] = s
        self.display['fb_source'] = fb_source
        self.display['link_for_fb_source'] = thing_db.link_for_fb_source

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

