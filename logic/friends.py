import logging
import smemcache

import fb_api

def decorate_with_friends(batch_lookup, search_results):
    if batch_lookup.fb_uid:
        friends_list = batch_lookup.data_for_user(batch_lookup.fb_uid)['friends']['data']
        friend_map = dict((x['id'], x['name']) for x in friends_list)
        friend_ids = set(friend_map.keys())

        attendee_batch_lookup = fb_api.CommonBatchLookup(batch_lookup.fb_uid, batch_lookup.fb_graph)
        for result in search_results:
            attendee_batch_lookup.lookup_event_attending(result.db_event.fb_event_id)
        attendee_batch_lookup.finish_loading()

        for result in search_results:
            event_attendees = attendee_batch_lookup.data_for_event_attending(result.db_event.fb_event_id)['attending']['data']
            event_attendee_ids = [x['id'] for x in event_attendees]
            event_friend_attendees = friend_ids.intersection(event_attendee_ids)
            result.attending_friends = [friend_map[x] for x in event_friend_attendees]
    else:
        for result in search_results:
            result.attending_friends = []
    for result in search_results:
        result.attending_friend_count = len(result.attending_friends)
        
