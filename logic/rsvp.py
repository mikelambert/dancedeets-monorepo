import fb_api
from logic import backgrounder

class RSVPManager(object):

    def __init__(self, batch_lookup):
        self.batch_lookup = batch_lookup
        fb_user = self.batch_lookup.data_for_user(self.batch_lookup.fb_uid)
        if 'rsvp_for_future_events' in fb_user:
            rsvps_list = fb_user['rsvp_for_future_events']['data']
            self.rsvps = dict((int(x['id']), x['rsvp_status']) for x in rsvps_list)
        else:
            self.rsvps = {}

    def get_rsvp_for_event(self, event_id):
        rsvp = self.rsvps.get(int(event_id), 'none')
        if rsvp == 'unsure':
            rsvp = 'maybe'
        return rsvp

    def set_rsvp_for_event(self, access_token, event_id, rsvp_status):
        fb = fb_api.FBAPI(access_token)
        result = fb.post('%s/%s' % (event_id, rsvp_status), args={}, post_args={})
        backgrounder.load_users([self.batch_lookup.fb_uid], allow_cache=False)
        backgrounder.load_event_attending([event_id], allow_cache=False)
        return result

def decorate_with_rsvps(batch_lookup, search_results):
    if batch_lookup.fb_uid:
        rsvps = RSVPManager(batch_lookup)
        for result in search_results:
            result.rsvp_status = rsvps.get_rsvp_for_event(result.fb_event_id)
    else:
        for result in search_results:
            result.rsvp_status = None
