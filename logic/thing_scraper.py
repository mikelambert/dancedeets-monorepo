import cgi
import logging
import urlparse

from logic import potential_events

def scrape_events_from_users(batch_lookup, thing_ids):
    batch_lookup = batch_lookup.copy(allow_cache=False)
    for thing_id in thing_ids:
        batch_lookup.lookup_thing_feed(thing_id)
    batch_lookup.finish_loading()

    for thing_id in thing_ids:
        thing_feed = batch_lookup.data_for_thing_feed(thing_id)
        process_thing_feed(thing_feed)

def process_thing_feed(thing_feed):
    thing_id = thing_feed['info']['id']
    if 'data' not in thing_feed['feed']:
        logging.error("No 'data' found in: %s", thing_feed['feed'])
        return
    for post in thing_feed['feed']['data']:
        if 'link' in post:
            p = urlparse.urlparse(post['link'])
            if p.path.endswith('event.php'):
                qs = cgi.parse_qs(p.query)
                eid = qs['eid'][0]
                potential_events.save_potential_fb_event_ids_if_new([eid], source=potential_events.source_from_posts(thing_id))



