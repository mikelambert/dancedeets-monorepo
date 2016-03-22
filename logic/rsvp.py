import fb_api
from logic import backgrounder

CHOOSE_RSVPS = ['attending', 'maybe', 'declined']


class RSVPManager(object):
    def __init__(self, fbl):
        self.fbl = fbl
        fb_user = self.fbl.fetched_data(fb_api.LookupUser, self.fbl.fb_uid)
        if 'rsvp_for_future_events' in fb_user:
            rsvps_list = fb_user['rsvp_for_future_events']['data']
            self.rsvps = dict((x['id'], x['rsvp_status']) for x in rsvps_list)
        else:
            self.rsvps = {}

    def get_rsvp_for_event(self, event_id):
        rsvp = self.rsvps.get(event_id, 'none')
        if rsvp == 'unsure':
            rsvp = 'maybe'
        return rsvp

    def set_rsvp_for_event(self, access_token, event_id, rsvp_status):
        fb = fb_api.FBAPI(access_token)
        result = fb.post('v2.2/%s/%s' % (event_id, rsvp_status), args={}, post_args={})
        backgrounder.load_users([self.fbl.fb_uid], allow_cache=False)
        backgrounder.load_event_attending([event_id], allow_cache=False)
        return result


def decorate_with_rsvps(fbl, search_results):
    if fbl.fb_uid:
        rsvps = RSVPManager(fbl)
        for result in search_results:
            # TODO: WEB_EVENTS: filter out non-FB events for lookup
            result.rsvp_status = rsvps.get_rsvp_for_event(result.event_id)
    else:
        for result in search_results:
            result.rsvp_status = None
