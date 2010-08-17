import smemcache

class RSVPManager(object):

    def __init__(self, batch_lookup):
        self.batch_lookup = batch_lookup
        #TODO(lambert): write code to purge these from cache, or load in background, or whatever. they aren't getting updated...
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

