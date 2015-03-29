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
        d = {}
        if self.deb:
            d['deb'] = self.deb
        if self.keywords:
            d['keywords'] = self.keywords
        if self.past:
            d['past'] = self.past
        if self.min_attendees:
            d['min_attendees'] = self.min_attendees
        d['location'] = self.location or ''
        d['distance'] = self.distance
        d['distance_units'] = self.distance_units
        return d

    @classmethod
    def create_from_request_and_user(cls, request, user):
        self = cls()
        self.deb = request.get('deb')
        self.keywords = request.get('keywords')

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
            if not value:
                continue
            if '[/url]' in value:
                errors.append('wiki markup in %s' % field)
            if '</a>' in value:
                errors.append('html in %s' % field)
        self.validated = not bool(errors)
        return errors
