import smemcache

from logic import backgrounder

class RSVPManager(object):

    def __init__(self, batch_lookup):
        self.batch_lookup = batch_lookup
        rsvps_data = self.batch_lookup.data_for_user(self.batch_lookup.fb_uid)['rsvp_for_future_events']
        rsvps_list = rsvps_data['data']
        self.rsvps = dict((int(x['id']), x['rsvp_status']) for x in rsvps_list)

    def get_rsvp_for_event(self, event_id):
        rsvp = self.rsvps.get(int(event_id), 'none')
        if rsvp == 'unsure':
            rsvp = 'maybe'
        return rsvp

    def set_rsvp_for_event(self, fb_graph, event_id, rsvp_status):
        if rsvp_status == 'maybe':
            rsvp_status = 'unsure'

        result = fb_graph.api_request('method/events.rsvp', args=dict(eid=event_id, rsvp_status=rsvp_status))
        backgrounder.load_events_full([event_id], allow_cache=False)
        backgrounder.load_users([self.batch_lookup.fb_uid], allow_cache=False)
        return result

def decorate_with_rsvps(batch_lookup, search_results):
    if batch_lookup.fb_uid:
        rsvps = RSVPManager(batch_lookup)
        for result in search_results:
            result.rsvp_status = rsvps.get_rsvp_for_event(result.db_event.fb_event_id)
    else:
        for result in search_results:
            result.rsvp_status = None
