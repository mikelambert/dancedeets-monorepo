import datetime
import xml.sax.saxutils

import base_servlet
from events import eventdata
from events import users
from logic import search

from google.appengine.ext.webapp import RequestHandler

class AtomHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()

        user_location = None
        distance = None
        distance_units = None
        distance_in_km = None
        if self.request.get('city_name'):
            city_name = self.request.get('city_name')
            location = city_name
            distance = 50
            distance_units = 'miles'
        else:
            location = self.request['location']
            distance = int(self.request.get('distance', '50'))
            distance_units = self.request.get('distance_units', 'miles')

        if distance_units == 'miles':
            distance_in_km = locations.miles_in_km(distance)
        else:
            distance_in_km = distance
        bounds = locations.get_location_bounds(location, distance_in_km)

        time_period = self.request.get('time_period', eventdata.TIME_FUTURE)

        query = search.SearchQuery(time_period=time_period, bounds=bounds, distance_in_km=distance_in_km)
        search_results = query.get_search_results(self.fb_uid, self.fb_graph)

        title = 'dance events within %(distance) %(distance_units)s of %(user_location)s.' % dict(
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
        <link href="http://www.facebook.com/events/%(id)s/" />
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

