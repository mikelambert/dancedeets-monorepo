# -*-*- encoding: utf-8 -*-*-
#

import datetime
import jinja2
import markupsafe
import re
import wtforms

from dancedeets.util import search_compat as search

from dancedeets import event_types
from dancedeets.loc import gmaps_api
from dancedeets.loc import math
from dancedeets.nlp import categories
from dancedeets.util import dates
from dancedeets.util import urls

TIME_PAST = 'PAST'
TIME_ONGOING = 'ONGOING'
TIME_UPCOMING = 'UPCOMING'
TIME_ALL_FUTURE = 'ALL_FUTURE'

FUTURE_INDEX_TIMES = [TIME_ONGOING, TIME_UPCOMING, TIME_ALL_FUTURE]

TIME_LIST = [TIME_PAST, TIME_ONGOING, TIME_UPCOMING, TIME_ALL_FUTURE]


def _no_wiki_or_html(form, field):
    if '[/url]' in field.data:
        raise wtforms.ValidationError('Cannot search with wiki markup')
    if '</a>' in field.data:
        raise wtforms.ValidationError('Cannot search with html markup')


def _valid_query(form, field):
    keywords = _get_parsed_keywords(field.data)
    try:
        search._CheckQuery(keywords)
    except search.QueryError as e:
        raise wtforms.ValidationError(str(e))


def _geocodable_location(form, field):
    if field.data:
        geocode = gmaps_api.lookup_address(field.data)
        if not geocode:
            raise wtforms.ValidationError("Did not understand location: %s" % field.data)


def _get_parsed_keywords(keywords):
    cleaned_keywords = re.sub(r'[<=>:(),|&/\\~?!.•\-]', ' ', keywords.decode('utf-8') if isinstance(keywords, bytes) else keywords).replace(' - ', ' ')
    unquoted_quoted_keywords = cleaned_keywords.split('"')
    for i in range(0, len(unquoted_quoted_keywords), 2):
        unquoted_quoted_keywords[i] = categories.format_as_search_query(unquoted_quoted_keywords[i])
    reconstructed_keywords = '"'.join(unquoted_quoted_keywords).strip()
    return reconstructed_keywords


class SearchException(Exception):
    pass


class SearchForm(wtforms.Form):
    location = wtforms.StringField(default='', validators=[_no_wiki_or_html, _geocodable_location])
    keywords = wtforms.StringField(default='', validators=[_no_wiki_or_html, _valid_query])
    distance = wtforms.IntegerField(default=50)
    distance_units = wtforms.SelectField(choices=[('miles', 'Miles'), ('km', 'KM')], default='km')
    locale = wtforms.StringField(default='')
    min_attendees = wtforms.IntegerField(default=0)
    min_worth = wtforms.IntegerField(default=0)
    deb = wtforms.StringField(default='')

    # Only used by API
    skip_people = wtforms.IntegerField(default=0)

    # For calendaring datetime-range queries:
    start = wtforms.DateField(default=None)
    end = wtforms.DateField(default=None)

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
            d['keywords'] = self.keywords.data
        if self.min_attendees.data:
            d['min_attendees'] = self.min_attendees.data
        if self.location.data:
            d['location'] = self.location.data
        if self.min_worth.data:
            d['min_worth'] = self.min_worth.data
        if self.distance.data:
            d['distance'] = self.distance.data
        if self.distance_units.data:
            d['distance_units'] = self.distance_units.data
        if self.locale.data:
            d['locale'] = self.locale.data
        if self.start.data:
            d['start'] = self.start.data.strftime("%Y-%m-%d")
        if self.end.data:
            d['end'] = self.end.data.strftime("%Y-%m-%d")
        return d

    def validate(self):
        rv = super(SearchForm, self).validate()
        if not rv:
            return False
        success = True
        if self.start.data and self.end.data:
            if not self.start.data <= self.end.data:
                self.start.errors.append('start must be less than end')
                self.end.errors.append('start must be less than end')
                success = False
        return success

    def build_query(self, start_end_query=False):
        bounds = None
        country_code = None
        if self.location.data:
            geocode = gmaps_api.lookup_address(self.location.data, language=self.locale.data)
            if geocode.is_country_geocode():
                country_code = geocode.country()
            else:
                bounds = math.expand_bounds(geocode.latlng_bounds(), self.distance_in_km())
        keywords = _get_parsed_keywords(self.keywords.data)
        common_fields = dict(
            bounds=bounds,
            min_attendees=self.min_attendees.data,
            min_worth=self.min_worth.data,
            keywords=keywords,
            country_code=country_code
        )
        query = SearchQuery(start_date=self.start.data, end_date=self.end.data, **common_fields)
        return query


def _get_geocode_from_form(form):
    place = gmaps_api.fetch_place_as_json(query=form.location.data, language=form.locale.data)
    if place['status'] == 'OK' and place['results']:
        geocode = gmaps_api.GMapsGeocode(place['results'][0])
        return geocode
    else:
        raise Exception('Error geocoding search address')


def get_geocode_with_distance(form):
    geocode = _get_geocode_from_form(form)
    distance = form.distance_in_km()
    return geocode, distance


def get_center_and_bounds(geocode, distance):
    southwest, northeast = math.expand_bounds(geocode.latlng_bounds(), distance)
    return geocode.latlng(), southwest, northeast


class SearchQuery(object):
    def __init__(
        self,
        time_period=None,
        start_date=None,
        end_date=None,
        bounds=None,
        min_attendees=None,
        min_worth=None,
        keywords=None,
        country_code=None
    ):
        self.time_period = time_period
        self.min_attendees = min_attendees
        self.min_worth = min_worth
        self.start_date = start_date
        self.end_date = end_date
        self.bounds = bounds
        self.keywords = keywords
        self.country_code = country_code

    def __repr__(self):
        return 'SearchQuery(**%r)' % self.__dict__


class SearchResult(object):
    def __init__(self, event_id, display_event_dict, db_event=None):
        self.event_id = event_id
        self.data = display_event_dict
        # Only used by /search API calls that want to return all data
        self.db_event = db_event  # May be None

        self.rsvp_status = "unknown"
        # These are initialized in logic/friends.py
        self.attending_friend_count = 0
        self.attending_friends = []

    name = property(lambda x: x.data['name'])

    @property
    def actual_city_name(self):
        # If it's a "Class" result, then use that stored data
        if 'location' in self.data:
            return self.data['location']
        # otherwise it's an "Event" rseult, so reconstruct the city from our good data
        else:
            # Semi backwards-compatible support for people who aren't upgrading to use the data directly
            address = self.data.get('venue', {}).get('address')
            if address:
                city_parts = [address[x] for x in ['city', 'state', 'country'] if address.get(x)]
                return ', '.join(city_parts)
            else:
                return None

    latitude = property(lambda x: x.data['lat'])
    longitude = property(lambda x: x.data['lng'])
    event_keywords = property(lambda x: x.data['keywords'])
    attendee_count = property(lambda x: x.data['attendee_count'])

    start_time_raw = property(lambda x: x.data['start_time'])
    end_time_raw = property(lambda x: x.data['end_time'])

    start_time = property(lambda x: dates.parse_fb_timestamp(x.start_time_raw))
    end_time = property(lambda x: dates.parse_fb_timestamp(x.end_time_raw))
    fake_end_time = property(lambda x: dates.faked_end_time(x.start_time, x.end_time))

    categories = property(lambda x: event_types.humanize_categories(x.data.get('categories', [])))

    def extended_categories(self):
        """Rewrites hiphop as streetjazz and jazzfunk sometimes when appropriate."""
        categories = list(self.categories)
        # It'd be nice to solve this in a better way, either do it at the global level
        # Or find a way to separate them that doesn't alienate the audiences.
        if 'Hip-Hop' in categories:
            categories.remove('Hip-Hop')
            categories.append('Hip-Hop & Street-Jazz')
        return categories

    image = property(lambda x: urls.event_image_url(x.event_id, width=360, height=360))
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
        return markupsafe.Markup('\n'.join(html))
