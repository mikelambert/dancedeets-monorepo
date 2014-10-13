import datetime
import json
import logging
import xml.sax.saxutils

import base_servlet
import fb_api
from events import eventdata
from logic import event_locations
from logic import search
from logic import search_base
from util import text
from util import urls

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

def write_json_data(callback, response, json_data):
    if callback:
        response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
    else:
        response.headers['Content-Type'] = 'application/json; charset=utf-8'

    if callback:
        response.out.write('%s(' % callback)
    response.out.write(json.dumps(json_data))
    if callback:
        response.out.write(')')


class FeedHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False
    

    def get(self):
        self.finish_preload()

        # Search API explicitly uses user=None
        fe_search_query = search_base.FrontendSearchQuery.create_from_request_and_user(self.request, None)

        if not fe_search_query.location:
            self.add_error('Need location parameter')
        format = self.request.get('format', 'json')
        if format not in ('json', 'atom'):
            self.add_error('Unknown format')
        self.errors_are_fatal()

        search_query = search.SearchQuery.create_from_query(fe_search_query)
        search_results = search_query.get_search_results(self.fbl)
        #TODO(lambert): move to common library.
        now = datetime.datetime.now() - datetime.timedelta(hours=12)
        search_results = [x for x in search_results if x.start_time > now]
        
        title = 'events near %(location)s.' % dict(
            distance=fe_search_query.distance,
            distance_units=fe_search_query.distance_units,
            location=fe_search_query.location,
        )
        if fe_search_query.keywords:
            title = '"%s" %s' % (fe_search_query.keywords, title)

        if format == 'atom':
            return self.handle_atom_feed(title, search_results)
        elif format == 'json':
            return self.handle_json_feed(title, search_results)
        else:
            logging.fatal("Unkonwn format, should have been caught up above")

    @staticmethod
    def SearchResultToJson(x):
        if x.fb_event['info'].get('location'):
            location = '%s, %s' % (x.fb_event['info']['location'], x.actual_city_name)
        else:
            location = x.actual_city_name
        return {
            'id': x.fb_event['info']['id'],
            'title': x.fb_event['info']['name'],
            'description': x.fb_event['info'].get('description'),
            'location': x.actual_city_name,
            'city': location,
            'image_url': x.get_image(),
            'cover_url': eventdata.get_largest_cover(x.fb_event),
            'start_time': x.start_time.strftime(DATETIME_FORMAT),
            'end_time': x.end_time and x.end_time.strftime(DATETIME_FORMAT) or None,
            'keywords': x.event_keywords,
        }

    def handle_json_feed(self, title, search_results):
        json_results = [self.SearchResultToJson(x) for x in search_results]
        write_json_data(self.request.get('callback'), self.response, json_results)

    def handle_atom_feed(self, title, search_results):
        self.response.headers['Content-Type'] = 'application/atom+xml'

        last_modified = datetime.datetime.now().strftime(DATETIME_FORMAT)

        url = 'http://www.dancedeets.com/events/feed?%s' % '&'.join('%s=%s' % (k, v) for (k, v) in self.request.params.iteritems())

        self.response.out.write("""\
<?xml version="1.0" encoding="utf-8"?>

<feed xmlns="http://www.w3.org/2005/Atom">
 
    <title>%(title)s</title>
    <link href="%(url)s" rel="self" />
    <id>http://www.dancedeets.com</id>
    <updated>%(last_modified)s</updated>
    <author>
        <name>Dance Deets</name>
        <email>dancedeets@dancedeets.com</email>
    </author>
""" % dict(
            title=xml.sax.saxutils.escape(title),
            url=xml.sax.saxutils.escape(url),
            last_modified=last_modified,
        ))

        #TODO(lambert): setup proper date-modified times

        for result in search_results:
            location = event_locations.get_address_for_fb_event(result.fb_event) or 'Unknown'

            lines = []
            lines.append('<img src="%s" />' % urls.fb_event_image_url(result.fb_event['info']['id']))
            lines.append('Start Time: %s' % text.date_format(u'%Y-%m-%d %H:%M', result.start_time))
            if result.end_time:
                lines.append('End Time: %s' % text.date_format(u'%Y-%m-%d %H:%M', result.end_time))
            if location:
                lines.append('Location: %s' % xml.sax.saxutils.escape(location))
            lines.append('')
            lines.append(xml.sax.saxutils.escape(result.fb_event['info'].get('description', '')))
            description = '\n'.join(lines)

            description = description.replace('\n', '<br/>\n')
            self.response.out.write("""\
    <entry>
        <title>%(title)s</title>
        <link href="http://www.facebook.com/events/%(id)s/" />
        <id>http://www.dancedeets.com/event/%(id)s</id>
        <published>%(published)s</published>
        <summary type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml">%(description)s</div></summary>
    </entry>
""" % dict(
                title=xml.sax.saxutils.escape(result.fb_event['info']['name'].encode('ascii', 'xmlcharrefreplace')),
                id=result.fb_event['info']['id'],
                published=result.start_time.strftime(DATETIME_FORMAT),
                description=(description.encode('ascii', 'xmlcharrefreplace')),
            ))

        self.response.out.write("""\
</feed>
""")

class SearchHandler(base_servlet.BaseRequestHandler):
    pass

FB_EVENT_COPY_KEYS = ['id', 'name', 'description', 'start_time', 'end_time']
VENUE_ADDRESS_COPY_KEYS = ['street', 'city', 'state', 'zip', 'country']
VENUE_GEOCODE_COPY_KEYS = ['longitude', 'latitude']

#EXTRA_KEYS = ['admins']
#MEMBER_KEYS = [fql_info][all_members_count]

def canonicalize_event_data(fb_event, db_event):
    event_api = {}
    for key in FB_EVENT_COPY_KEYS:
        event_api[key] = fb_event['info'][key]

    # cover images
    if fb_event['cover_info']:
        cover_id = fb_event['info']['cover']['cover_id']
        cover_images = sorted(fb_event['cover_info'][cover_id]['images'], key=lambda x: -x['height'])
        event_api['cover'] = {
            'cover_id': cover_id,
            'images': cover_images,
        }
    else:
        event_api['cover'] = None

    # location data
    location = fb_event['info']['location']
    venue = fb_event['info']['venue']
    address = {}
    for key in VENUE_ADDRESS_COPY_KEYS:
        address[key] = venue[key]
    geocode = {}
    for key in VENUE_GEOCODE_COPY_KEYS:
        geocode[key] = venue[key]
    event_api['venue'] = {
        'id': venue['id'],
        'name': location,
        'address': address,
        'geocode': geocode,
    }
    # people data
    event_api['admins'] = fb_event['info']['admins']['data']
    event_api['metadata'] = {
        'added_time': db_event.creation_time.strftime(DATETIME_FORMAT),
        'added_method': db_event.creating_method,
        'added_person': db_event.creating_fb_uid,
        'dance_keywords': db_event.event_keywords,
    }
    return event_api

class EventHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()

        path_bits = self.request.path.split('/')
        if not self.request.path.startswith('/api/events/'):
            self.add_error('Path is malformed: %s' % self.request.path)
        elif len(path_bits) != 4 and len(path_bits) != 5:
            self.add_error('Path is malformed: %s' % self.request.path)
            self.response.out.write('Need an event_id.')
        else:
            try:
                event_id = str(int(path_bits[3]))
            except TypeError:
                self.add_error('Event id expected: %s' % path_bits[3])

            fb_event = self.fbl.get(fb_api.LookupEvent, event_id)
            if fb_event['empty']:
                self.add_error('This event was %s.' % fb_event['empty'])

        self.errors_are_fatal()

        db_event = eventdata.DBEvent.get_by_key_name(event_id)

        json_data = canonicalize_event_data(fb_event, db_event)

        write_json_data(self.request.get('callback'), self.response, json_data)


