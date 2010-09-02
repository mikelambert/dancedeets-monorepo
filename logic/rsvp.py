import smemcache

class RSVPManager(object):

    def __init__(self, batch_lookup):
        self.batch_lookup = batch_lookup
        rsvps_list = self.batch_lookup.data_for_user(self.batch_lookup.fb_uid)['rsvp_for_events']
        self.rsvps = dict((int(x['eid']), x['rsvp_status']) for x in rsvps_list)

    def get_rsvp_for_event(self, event_id):
        rsvp = self.rsvps.get(int(event_id))
        if rsvp == 'unsure':
            rsvp = 'maybe'
        return rsvp

    def set_rsvp_for_event(self, fb_graph, event_id, rsvp_status):
        if rsvp_status == 'maybe':
            rsvp_status = 'unsure'

        self.batch_lookup.invalidate_event(event_id)
        self.batch_lookup.invalidate_user(self.batch_lookup.fb_uid)

        result = fb_graph.api_request('method/events.rsvp', args=dict(eid=event_id, rsvp_status=rsvp_status))
        return result

def decorate_with_rsvps(batch_lookup, search_results):
    rsvps = RSVPManager(batch_lookup)
    for result in search_results:
        result.rsvp_status = rsvps.get_rsvp_for_event(result.db_event.fb_event_id)

