import datetime

TIME_PAST = 'PAST'
TIME_ONGOING = 'ONGOING'
TIME_UPCOMING = 'UPCOMING'
TIME_ALL_FUTURE = 'ALL_FUTURE'

FUTURE_INDEX_TIMES = [TIME_ONGOING, TIME_UPCOMING, TIME_ALL_FUTURE]
class FrontendSearchQuery(object):
    def __init__(self):
        self.location = None
        self.distance = 50
        self.distance_units = 'miles'
        self.min_attendees = 0
        self.time_period = None
        self.keywords = ''
        self.deb = None

        # Only used for calendaring queries:
        self.start_time = None
        self.end_time = None

        self.validated = False

    def url_params(self):
        d = {}
        if self.deb:
            d['deb'] = self.deb
        if self.keywords:
            d['keywords'] = self.keywords
        if self.min_attendees:
            d['min_attendees'] = self.min_attendees
        d['time_period'] = self.time_period
        d['location'] = self.location or ''
        d['distance'] = self.distance
        d['distance_units'] = self.distance_units
        return d

    @classmethod
    def create_from_request_and_user(cls, request, user, major_version=None, minor_version=None):
        self = cls()
        self.deb = request.get('deb')
        self.keywords = request.get('keywords')

        self.location = request.get('location', user and user.location)
        self.distance = int(request.get('distance', user and user.distance or 50))
        self.distance_units = request.get('distance_units', user and user.distance_units or 'miles')

        if major_version is None and minor_version is None:
            if request.get('past', '0') not in ['0', '', 'False', 'false']:
                self.time_period = TIME_PAST
            else:
                self.time_period = TIME_ALL_FUTURE
        else:
            # If it's 1.0 clients, or web clients, then grab all data
            if major_version == '1' and minor_version == '0':
                self.time_period = TIME_UPCOMING
            else:
                self.time_period = request.get('time_period')

        self.min_attendees = int(request.get('min_attendees', user and user.min_attendees or 0))

        if request.get('start'):
            self.start_time = datetime.datetime.strptime(request.get('start'), '%Y-%m-%d')
        else:
            self.start_time = datetime.datetime.now()
        if request.get('end'):
            self.end_time = datetime.datetime.strptime(request.get('end'), '%Y-%m-%d')
        else:
            self.end_time = datetime.datetime.now() + datetime.timedelta(days=365)
        return self

    def validation_errors(self):
        errors = []
        for field in ['keywords', 'location']:
            value = getattr(self, field)
            if not value:
                continue
            if '[/url]' in value:
                errors.append('wiki markup in %s' % field)
            if '</a>' in value:
                errors.append('html in %s' % field)
        self.validated = not bool(errors)
        return errors
