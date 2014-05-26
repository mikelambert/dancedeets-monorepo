import fb_api

# We only do this many at once, so that we don't load them all into memory simultaneously.
# This helps us avoid blowing our soft memory limit and killing our serving process just because the user looked up every-event-in-the-world.
# With 100, we seem to stay under the limit and have no real discernable difference in latency (below noise). Probably because our time is dominated by deserialization, not round-trip latency.
RESULTS_AT_ONCE = 100

def decorate_with_friends(fbl, search_results):

    if len(search_results) > RESULTS_AT_ONCE:
        decorate_with_friends(fbl, search_results[RESULTS_AT_ONCE:])
        search_results = search_results[:RESULTS_AT_ONCE]

    if fbl.fb_uid: # if logged in
        friends_list = fbl.fetched_data(fb_api.LookupUser, fbl.fb_uid)['friends']['data']
        friend_map = dict((x['id'], x['name']) for x in friends_list if 'name' in x)
        friend_ids = set(friend_map.keys())

        fbl.request_multi(fb_api.LookupEventAttending, [x.fb_event_id for x in search_results])
        fbl.batch_fetch()

        for result in search_results:
            event_attendees = fbl.fetched_data(fb_api.LookupEventAttending, result.fb_event_id)['attending']['data']
            event_attendee_ids = [x['id'] for x in event_attendees]
            event_friend_attendees = friend_ids.intersection(event_attendee_ids)
            result.attending_friends = sorted(friend_map[x] for x in event_friend_attendees)
    else:
        for result in search_results:
            result.attending_friends = []
    for result in search_results:
        result.attending_friend_count = len(result.attending_friends)
        
