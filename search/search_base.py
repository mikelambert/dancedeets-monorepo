import datetime
import jinja2
import re
import wtforms

from google.appengine.api import search

import event_types
from loc import math
import styles
from util import dates

TIME_PAST = 'PAST'
TIME_ONGOING = 'ONGOING'
TIME_UPCOMING = 'UPCOMING'
TIME_ALL_FUTURE = 'ALL_FUTURE'

FUTURE_INDEX_TIMES = [TIME_ONGOING, TIME_UPCOMING, TIME_ALL_FUTURE]

TIME_LIST = [TIME_PAST, TIME_ONGOING, TIME_UPCOMING, TIME_ALL_FUTURE]

CATEGORY_LOOKUP = dict([(x.index_name, x.public_name) for x in styles.STYLES + event_types.EVENT_TYPES])

def humanize_categories(categories):
    return [CATEGORY_LOOKUP[x] for x in categories]


def no_wiki_or_html(form, field):
    if '[/url]' in field.data:
        raise wtforms.ValidationError('Cannot search with wiki markup')
    if '</a>' in field.data:
        raise wtforms.ValidationError('Cannot search with html markup')

def valid_query(form, field):
    try:
        search.search._CheckQuery(field.data)
    except search.QueryError as e:
        raise wtforms.ValidationError(str(e))


class SearchException(Exception):
    pass

class SearchForm(wtforms.Form):
    location = wtforms.StringField(default='', validators=[no_wiki_or_html])
    keywords = wtforms.StringField(default='', validators=[no_wiki_or_html, valid_query])
    distance = wtforms.IntegerField(default=50)
    distance_units  = wtforms.SelectField(choices=[('miles', 'Miles'), ('km', 'KM')], default='km')
    min_attendees = wtforms.IntegerField(default=0)
    time_period = wtforms.SelectField(choices=[(x, x) for x in TIME_LIST], default=TIME_ALL_FUTURE)
    deb = wtforms.StringField(default='')

    # For calendaring datetime-range queries:
    start = wtforms.DateField()
    end = wtforms.DateField()

    def distance_in_km(self):
        if self.distance_units.data == 'miles':
            distance_in_km = math.miles_in_km(self.distance.data)
        else:
            distance_in_km = self.distance.data
        return distance_in_km

    def url_params(self):
        d = {}
        if self.deb.data:
            d['deb'] = self.deb.data
        if self.keywords.data:
            d['keywords'] = self.keywords.data.encode('utf-8')
        if self.min_attendees.data:
            d['min_attendees'] = self.min_attendees.data
        d['location'] = self.location.data.encode('utf-8') or ''
        d['distance'] = self.distance.data
        d['distance_units'] = self.distance_units.data
        return d

class HtmlSearchForm(SearchForm):
    def __init__(self, formdata, data=None):
        if formdata.get('past', '0') not in ['0', '', 'False', 'false']:
            time_period = TIME_PAST
        else:
            time_period = TIME_ALL_FUTURE
        if not data:
            data = {}
        data['time_period'] = time_period
        super(HtmlSearchForm, self).__init__(formdata, data=data)


class SearchResult(object):
    def __init__(self, fb_event_id, display_event_dict, db_event=None):
        self.fb_event_id = fb_event_id
        self.data = display_event_dict
        # Only used by /search API calls that want to return all data
        self.db_event = db_event # May be None

        self.rsvp_status = "unknown"
        # These are initialized in logic/friends.py
        self.attending_friend_count = 0
        self.attending_friends = []

    name = property(lambda x: x.data['name'])
    actual_city_name = property(lambda x: x.data['location'])
    latitude = property(lambda x: x.data['lat'])
    longitude = property(lambda x: x.data['lng'])
    event_keywords = property(lambda x: x.data['keywords'])
    attendee_count = property(lambda x: x.data['attendee_count'])

    start_time_raw = property(lambda x: x.data['start_time'])
    end_time_raw = property(lambda x: x.data['end_time'])

    start_time = property(lambda x: dates.parse_fb_timestamp(x.start_time_raw))
    end_time = property(lambda x: dates.parse_fb_timestamp(x.end_time_raw))
    fake_end_time = property(lambda x: dates.faked_end_time(x.start_time, x.end_time))

    categories = property(lambda x: humanize_categories(x.data.get('categories', [])))
    def extended_categories(self):
        """Rewrites hiphop as streetjazz and jazzfunk sometimes when appropriate."""
        categories = list(self.categories)
        # It'd be nice to solve this in a better way, either do it at the global level
        # Or find a way to separate them that doesn't alienate the audiences.
        if 'Hip-Hop' in categories:
            categories.remove('Hip-Hop')
            categories.append('Hip-Hop & Street-Jazz')
        return categories

    image = property(lambda x: x.data['image'])
    sponsor = property(lambda x: x.data.get('sponsor'))

    # Only for use by StudioClass-indexed results
    source_page = property(lambda x: x.data['source_page'])

    def multi_day_event(self):
        return not self.end_time or (self.end_time - self.start_time) > datetime.timedelta(hours=24)

    def get_attendance(self):
        if self.rsvp_status == 'unsure':
            return 'maybe'
        return self.rsvp_status

    def location_schema_html(self):
        html = [
            '<span itemscope itemprop="location" itemtype="http://schema.org/Place">',
            '  <meta itemprop="name" content="%s" />' % self.actual_city_name,
            '  <meta itemprop="address" content="%s" />' % self.actual_city_name,
        ]
        if self.latitude:
            html += [
                '  <span itemprop="geo" itemscope itemtype="http://schema.org/GeoCoordinates">',
                '    <meta itemprop="latitude" content="%s" />' % self.latitude,
                '    <meta itemprop="longitude" content="%s" />' % self.longitude,
                '  </span>',
            ]
        html += [
            '</span>',
        ]
        return jinja2.Markup('\n'.join(html))
