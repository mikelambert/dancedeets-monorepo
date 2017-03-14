
import logging

from events import eventdata
import fb_api
from logic import popular_people
from . import auto_add

def debug_attendee_addition_for_event(fbl, fb_event):
    """Used to debug the attendees for an event:
    - Where they came from
    - Are they legit
    - Did we pollute this city with bad events (and bad attendees / scene)

    So given this event and its dancer-attendees,
    let's find all the events that contributed to these dancer-attendees.

    Let's list out the events for each attendee, and the top-events for this set-of-attendees.
    """

    num_events = 1000

    # A certain set of dancer-attendees triggered this event to be added.
    # Let's get all the events from all the cities that contributed to the dancer-attendee list used for this event
    latlong = auto_add.get_latlong_for_fb_event(fb_event)
    city_names = popular_people.get_city_names_near(latlong)
    event_keys = eventdata.DBEvent.query(eventdata.DBEvent.city_name.IN(city_names)).fetch(num_events, keys_only=True)
    event_ids = [x.string_id() for x in event_keys]
    logging.info('%r', event_ids)


    # Look up a toooooooooooon of crap here, for all O(num_events) events.
    # TODO: Will this blow memory, and need to be segmented into loops?
    fbl.request_multi(fb_api.LookupEventAttendingMaybe, event_ids)
    fbl.batch_fetch()


    # Build lookup for finding all events for a given attendee
    attendee_id_to_event_ids = {}
    for event_id in event_ids:
        fb_event_attending_maybe = fbl.fetched_data(fb_api.LookupEventAttendingMaybe, event_id)
        if fb_event_attending_maybe['empty']:
            logging.info('Event %s has no attendees, skipping attendee-based classification.', event_id)
            return []

        people = fb_event_attending_maybe['attending']['data']
        event_attendee_ids = [attendee['id'] for attendee in people]
        for attendee_id in set(event_attendee_ids).intersection(attendee_id_to_event_ids):
            attendee_id_to_event_ids[attendee_id].append(event_id)
        for attendee_id in set(event_attendee_ids).difference(attendee_id_to_event_ids):
            attendee_id_to_event_ids[attendee_id] = [event_id]


    # Now get a list of dancer-attendees for this event...that we want to debug
    good_event_attendee_ids = auto_add.is_good_event_by_attendees(fbl, fb_event)


    # Compute which events are most popular/common among our attendees, in triggering the list of dancer-attendees
    event_popularity = {}
    for dancer_id in good_event_attendee_ids:
        if dancer_id in attendee_id_to_event_ids:
            event_ids = attendee_id_to_event_ids[dancer_id]
        else:
            event_ids = []
            logging.error('Could not find events for dancer-attendee %s, perhaps this is running on dev?', dancer_id)
        for event_id in event_ids:
            if event_id in event_popularity:
                event_popularity[event_id] += 1
            else:
                event_popularity[event_id] = 1

    # Now find the top ten events based on this ranking, and load them
    top_n = 10
    sorted_popular_event_ids = sorted(event_popularity, key=lambda x: -event_popularity[x])[:top_n]
    events = eventdata.DBEvent.get_by_ids(sorted_popular_event_ids)


    # Generate our results to send to the caller for display/printing

    # Output the events for each dancer-attendee.
    dancer_to_events = {}
    for dancer_id in good_event_attendee_ids:
        dancer_to_events[dancer_id] = attendee_id_to_event_ids.get(dancer_id)

    # And the overall most popular events leading to these dancer-attendees
    event_popularity_list = []
    for event in events:
        event_popularity_list.append((event, event_popularity[event.id]))

    return dancer_to_events, event_popularity_list
