class FrontendSearchQuery(object):
    def __init__(self):
        self.location = None
        self.distance = 50
        self.distance_units = 'miles'
        self.min_attendees = 0
        self.past = 0
        self.keywords = ''

    def url_params(self):
        return {
            'location': self.location,
            'distance': self.distance,
            'distance_units': self.distance_units,
            'min_attendees': self.min_attendees,
            'past': self.past,
            'keywords': self.keywords,
        }
