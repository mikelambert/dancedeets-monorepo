import json
import logging

from mapreduce import mapreduce_pipeline
from dancedeets.util import fb_mapreduce

from dancedeets import app
from dancedeets import base_servlet
from dancedeets.util import mr
from . import event_pipeline
from . import potential_events
from . import thing_scraper


def scrape_sources_for_events(sources):
    fbl = fb_mapreduce.get_fblookup()
    fbl.allow_cache = False
    # Eliminate all caches (both fetching, and saving!)
    # This should save on a bunch of unnecessary put() calls while scraping
    # (Current estimates are 30qps * 60 sec/min * 50min * $0.18/10K Queries * 30 days = $48/month)
    fbl.make_passthrough()
    discovered_list = thing_scraper.discover_events_from_sources(fbl, sources)
    for x in discovered_list:
        state = (x.event_id, x.source_id, x.source_field, x.extra_source_id)
        mr.increment('found-event-to-check')
        # Don't "shard" events....just group them by id.
        # And let the functionality of them sharing sources happen naturally
        yield (x.event_id, json.dumps(state))


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
    # Some of these are newly-discovered events, some of these are already-cached and classified.
    # TODO: Filter out the already-classified ones, so we don't waste time re-classifying on cached on data.
    event_pipeline.process_discovered_events(fbl, discovered_list)


@app.route('/tasks/scrape_sources_and_process_events')
class LoadPotentialEventsFromWallPostsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        min_potential_events = int(self.request.get('min_potential_events', '0'))
        queue = self.request.get('queue', 'slow-queue')
        mapreduce_scrape_sources_and_process_events(self.fbl, min_potential_events=min_potential_events, queue=queue)


def mapreduce_scrape_sources_and_process_events(fbl, min_potential_events, queue):
    mapper_params = {
        'entity_kind': 'dancedeets.event_scraper.thing_db.Source',
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
        'dancedeets.event_scraper.thing_scraper2.scrape_sources_for_events',
        'dancedeets.event_scraper.thing_scraper2.process_events',
        'mapreduce.input_readers.DatastoreInputReader',
        'mapreduce.output_writers.GoogleCloudStorageOutputWriter',
        mapper_params=mapper_params,
        reducer_params=reducer_params,
        shards=16,
    )

    pipeline.start(queue_name=queue)
