import datetime
import xml.sax.saxutils

import base_servlet
from events import users
from events import tags
from logic import search

from google.appengine.ext.webapp import RequestHandler

class AtomHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()

        city_name = None
        user_location = None
        distance = None
        distance_units = None
        distance_in_km = None
        latlng_user_location = None
        if self.request.get('city_name'):
            city_name = self.request.get('city_name')
        else:
            user_location = self.request['location']
            distance = int(self.request.get('distance', '100'))
            distance_units = self.request.get('distance_units', 'miles')
            if distance_units == 'miles':
                distance_in_km = locations.miles_in_km(distance)
            else:
                distance_in_km = distance
            latlng_location = locations.get_geocoded_location(location)['latlng']

        dance_type = self.request.get('dance_type', users.DANCE_TYPES_LIST[0]['internal'])
        time_period = self.request.get('time_period', tags.TIME_FUTURE)

        event_types = []
        if choreo in [x['internal'] for x in users.CHOREO_LIST[1:]]:
            event_types.append('choreo')
        if freestyle in [x['internal'] for x in users.FREESTYLE_LIST[1:]]:
            event_types.append('freestyle')
        event_types_str = ' and '.join(event_types)


        query = search.SearchQuery(city_name=city_name, time_period=time_period, location=latlng_location, distance_in_km=distance_in_km, dance_type=dance_type)
        search_results = query.get_search_results(self.fb_uid, self.fb_graph)

        if city_name:
            title = "%(event_types)s dance events in %(city_name)s." % dict(
                event_types=event_types_str,
                city_name=city_name,
            )
        else:
            title = '%(event_types)s dance events within %(distance) %(distance_units)s of %(user_location)s.' % dict(
                event_types=event_types_str,
                distance=distance,
                distance_units=distance_units,
                user_location=user_location,
            )
        atom_date_format = "%Y-%m-%dT%H:%M:%SZ"
        last_modified = datetime.datetime.now().strftime(atom_date_format)

        url = '/events/feed?%s' % '&'.join('%s=%s' % (k, v) for (k, v) in self.request.params.iteritems())

        self.response.out.write("""\
<?xml version="1.0" encoding="utf-8"?>

<feed xmlns="http://www.w3.org/2005/Atom">
 
    <title>%(title)s</title>
    <link href="%(url)s" rel="self" />
    <link href="http://www.dancedeets.com/" />
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
            self.response.out.write("""\
    <entry>
        <title>%(title)s</title>
        <link href="http://www.facebook.com/event.php?eid=%(id)s" />
        <id>http://www.dancedeets.com/event/%(id)s</id>
        <updated>%(last_modified)s</updated>
        <summary>%(description)s</summary>
    </entry>
""" % dict(
                title=xml.sax.saxutils.escape(result.fb_event['info']['name'].encode('ascii', 'xmlcharrefreplace')),
                id=result.fb_event['info']['id'],
                last_modified=result.start_time.strftime(atom_date_format),
                description=xml.sax.saxutils.escape(result.fb_event['info']['description'].encode('ascii', 'xmlcharrefreplace')),
            ))

        self.response.out.write("""\
</feed>
""")

