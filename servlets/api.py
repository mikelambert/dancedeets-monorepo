import datetime
import json
import logging
import xml.sax.saxutils

import base_servlet
from events import eventdata
import locations
from logic import event_locations
from logic import search
from util import text
from util import urls

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

class FeedHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()

        location = self.request.get('location')
        distance = int(self.request.get('distance', '50'))
        distance_units = self.request.get('distance_units', 'miles')

        if not location:
            self.add_error('Need location parameter')
        format = self.request.get('format', 'json')
        if format not in ('json', 'atom'):
            self.add_error('Unknown format')
        self.errors_are_fatal()

        if distance_units == 'miles':
            distance_in_km = locations.miles_in_km(distance)
        else:
            distance_in_km = distance
        bounds = locations.get_location_bounds(location, distance_in_km)

        time_period = self.request.get('time_period', eventdata.TIME_FUTURE)

        query = search.SearchQuery(time_period=time_period, bounds=bounds)
        search_results = query.get_search_results(self.fbl)
        #TODO(lambert): move to common library.
        now = datetime.datetime.now() - datetime.timedelta(hours=12)
        search_results = [x for x in search_results if x.start_time > now]
        
        if format == 'atom':
            return self.HandleAtomFeed(distance, distance_units, location, search_results)
        elif format == 'json':
            return self.HandleJsonFeed(distance, distance_units, location, search_results)
        else:
            logging.fatal("Unkonwn format, should have been caught up above")

    @staticmethod
    def SearchResultToJson(x):
        return {
            'id': x.fb_event['info']['id'],
            'title': x.fb_event['info']['name'],
            'description': x.fb_event['info'].get('description'),
            'city': x.actual_city_name,
            'image_url': x.get_image(),
            'cover_url': x.fb_event['info'].get('cover'),
            'start_time': x.start_time.strftime(DATETIME_FORMAT),
            'end_time': x.end_time and x.end_time.strftime(DATETIME_FORMAT) or None,
            'keywords': x.event_keywords,
        }

    def HandleJsonFeed(self, distance, distance_units, location, search_results):
        callback = self.request.get('callback')
        if callback:
            self.response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
        else:
            self.response.headers['Content-Type'] = 'application/json; charset=utf-8'

        json_results = [self.SearchResultToJson(x) for x in search_results]
        if callback:
            self.response.out.write('%s(' % callback)
        self.response.out.write(json.dumps(json_results))
        if callback:
            self.response.out.write(')')

    def HandleAtomFeed(self, distance, distance_units, location, search_results):
        self.response.headers['Content-Type'] = 'application/atom+xml'

        title = 'dance events within %(distance)s %(distance_units)s of %(location)s.' % dict(
            distance=distance,
            distance_units=distance_units,
            location=location,
        )
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

