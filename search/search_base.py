import datetime

class FrontendSearchQuery(object):
    def __init__(self):
        self.location = None
        self.distance = 50
        self.distance_units = 'miles'
        self.min_attendees = 0
        self.past = 0
        self.keywords = ''
        self.deb = None

        # Only used for calendaring queries:
        self.start_time = None
        self.end_time = None

        self.validated = False

    def url_params(self):
        return {
            'location': self.location,
            'distance': self.distance,
            'distance_units': self.distance_units,
            'min_attendees': self.min_attendees,
            'past': self.past,
            'keywords': self.keywords,
            'deb': self.deb,
        }

    @classmethod
    def create_from_request_and_user(cls, request, user, city_name=None):
        self = cls()
        self.deb = request.get('deb')
        self.keywords = request.get('keywords')

        # in case we get it passed in via the URL handler
        city_name = city_name or request.get('city_name')

        if city_name:
            self.location = city_name
            self.distance = 50
            self.distance_units = 'miles'
        else:
            self.location = request.get('location', user and user.location)
            self.distance = int(request.get('distance', user and user.distance or 50))
            self.distance_units = request.get('distance_units', user and user.distance_units or 'miles')

        self.past = request.get('past', '0') not in ['0', '', 'False', 'false']
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
            if '[/url]' in value:
                errors.append('wiki markup in %s' % field)
            if '</a>' in value:
                errors.append('html in %s' % field)
        if not self.location.strip():
            errors.append('must specify a location')
        self.validated = not bool(errors)
        return errors
