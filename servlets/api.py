import datetime
import json
import logging
import xml.sax.saxutils

import base_servlet
from logic import event_locations
from logic import search
from logic import search_base
from util import text
from util import urls

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

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
        
        title = 'dance events within %(distance)s %(distance_units)s of %(location)s.' % dict(
            distance=fe_search_query.distance,
            distance_units=fe_search_query.distance_units,
            location=fe_search_query.location,
        )

        if format == 'atom':
            return self.HandleAtomFeed(title, search_results)
        elif format == 'json':
            return self.HandleJsonFeed(search_results)
        else:
            logging.fatal("Unkonwn format, should have been caught up above")

    @staticmethod
    def SearchResultToJson(x):
        if x.location:
            location = '%s, %s' % (x.location, x.actual_city_name)
        else:
            location = x.actual_city_name
        return {
            'id': x.fb_event['info']['id'],
            'title': x.fb_event['info']['name'],
            'description': x.fb_event['info'].get('description'),
            'location': x.actual_city_name,
            'city': location,
            'image_url': x.get_image(),
            'cover_url': x.fb_event['info'].get('cover'),
            'start_time': x.start_time.strftime(DATETIME_FORMAT),
            'end_time': x.end_time and x.end_time.strftime(DATETIME_FORMAT) or None,
            'keywords': x.event_keywords,
        }

    def HandleJsonFeed(self, search_results):
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

    def HandleAtomFeed(self, title, search_results):
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

