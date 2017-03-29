import json
import logging

from mapreduce import mapreduce_pipeline
from util import fb_mapreduce

import app
import base_servlet
from util import mr
from . import event_pipeline
from . import potential_events
from . import thing_scraper


# Given that we get around 50K events in our MR (see below),
# let's do 1000 shards, for roughly 50-events-per.
# Should allow for much better CPU/network/etc usage and run faster
NUM_SHARDS = 1000
def _shard_for(event_id):
    return hash(event_id) % NUM_SHARDS

def scrape_sources_for_events(sources):
    fbl = fb_mapreduce.get_fblookup()
    fbl.allow_cache = False
    discovered_list = thing_scraper.discover_events_from_sources(fbl, sources)
    for x in discovered_list:
        state = (x.event_id, x.source_id, x.source_field, x.extra_source_id)
        mr.increment('found-event-to-check')
        yield (_shard_for(x.event_id), json.dumps(state))


def process_events(event_id, via_sources):
    fbl = fb_mapreduce.get_fblookup()
    fbl.allow_cache = True
    discovered_list = []
    logging.info('Running process_events with %s event-sources', len(via_sources))
    for data in via_sources:
        event_id, source_id, source_field, extra_source_id = json.loads(data)
        discovered = potential_events.DiscoveredEvent(event_id, None, source_field, extra_source_id)
        discovered.source = None  # TODO: This will come back to bite us I'm sure :(
        discovered.source_id = source_id
        discovered_list.append(discovered)
    event_pipeline.process_discovered_events(fbl, discovered_list)


@app.route('/tasks/scrape_sources_and_process_events')
class LoadPotentialEventsFromWallPostsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        min_potential_events = int(self.request.get('min_potential_events', '0'))
        queue = self.request.get('queue', 'slow-queue')
        mapreduce_scrape_sources_and_process_events(self.fbl, min_potential_events=min_potential_events, queue=queue)


def mapreduce_scrape_sources_and_process_events(fbl, min_potential_events, queue):
    mapper_params = {
        'entity_kind': 'event_scraper.thing_db.Source',
        'min_potential_events': min_potential_events,
        'handle_batch_size': 20,
    }
    reducer_params = {
        'output_writer': {
            'bucket_name': 'dancedeets-hrd.appspot.com',
            'content_type': 'text/plain',
        }
    }
    fb_params = fb_mapreduce.get_fblookup_params(fbl, randomize_tokens=True)
    mapper_params.update(fb_params)
    reducer_params.update(fb_params)

    # output = yield ...
    pipeline = mapreduce_pipeline.MapreducePipeline(
        'Scrape sources, then load and classify the events',
        'event_scraper.thing_scraper2.scrape_sources_for_events',
        'event_scraper.thing_scraper2.process_events',
        'mapreduce.input_readers.DatastoreInputReader',
        'mapreduce.output_writers.GoogleCloudStorageOutputWriter',
        mapper_params=mapper_params,
        reducer_params=reducer_params,
        shards=16,
    )

    pipeline.start(queue_name='slow-queue')
