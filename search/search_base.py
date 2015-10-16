import wtforms

from loc import math

TIME_PAST = 'PAST'
TIME_ONGOING = 'ONGOING'
TIME_UPCOMING = 'UPCOMING'
TIME_ALL_FUTURE = 'ALL_FUTURE'

FUTURE_INDEX_TIMES = [TIME_ONGOING, TIME_UPCOMING, TIME_ALL_FUTURE]

TIME_LIST = [TIME_PAST, TIME_ONGOING, TIME_UPCOMING, TIME_ALL_FUTURE]

def no_wiki_or_html(form, field):
    if '[/url]' in field.data:
        raise wtforms.ValidationError('Cannot search with wiki markup')
    if '</a>' in field.data:
        raise wtforms.ValidationError('Cannot search with html markup')

class SearchForm(wtforms.Form):
    location = wtforms.StringField(default='', validators=[no_wiki_or_html])
    keywords = wtforms.StringField(default='', validators=[no_wiki_or_html])
    distance = wtforms.IntegerField(default=50)
    distance_units  = wtforms.SelectField(choices=[('miles', 'Miles'), ('km', 'KM')], default='km')
    min_attendees = wtforms.IntegerField(default=0)
    time_period = wtforms.SelectField(choices=[(x, x) for x in TIME_LIST], default=TIME_ALL_FUTURE)
    deb = wtforms.BooleanField(default=False)

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
            d['keywords'] = self.keywords.data
        if self.min_attendees.data:
            d['min_attendees'] = self.min_attendees.data
        d['time_period'] = self.time_period.data
        d['location'] = self.location.data or ''
        d['distance'] = self.distance.data
        d['distance_units'] = self.distance_units.data
        return d

class HtmlSearchForm(SearchForm):
    def __init__(self, formdata, data=None):
        if formdata.get('past', '0') not in ['0', '', 'False', 'false']:
            time_period = TIME_PAST
        else:
            time_period = TIME_ALL_FUTURE
        data['time_period'] = time_period
        super(HtmlSearchForm, self).__init__(formdata, data=data)
