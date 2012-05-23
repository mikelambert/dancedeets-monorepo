import logging

import fb_api

from events import eventdata
from logic import add_entities
from logic import event_auto_classifier
from logic import event_classifier
from logic import event_locations
from logic import potential_events
from util import fb_mapreduce
from util import mr_helper

class UnprocessedPotentialEventsReader(mr_helper.FilteredInputReader):
    def filter_query(self, query):
        query.filter('looked_at =', None)

def classify_events(batch_lookup, pe_list):
    for pe in pe_list:
        batch_lookup.lookup_event(pe.fb_event_id)
        #batch_lookup.lookup_event_attending(pe.fb_event_id)
    batch_lookup.finish_loading()

    results = []
    for pe in pe_list:
        try:
            fb_event = batch_lookup.data_for_event(pe.fb_event_id)
        except fb_api.NoFetchedDataException:
            continue
        if fb_event['deleted']:
            continue
        classified_event = event_classifier.ClassifiedEvent(fb_event)
        classified_event.classify()
        if event_auto_classifier.is_battle(classified_event):
            location_info = event_locations.LocationInfo(batch_lookup, fb_event)
            result = '%s\n' % '\t'.join(unicode(x) for x in (pe.fb_event_id, location_info.exact_from_event, location_info.final_city, location_info.final_city != None, location_info.fb_address, fb_event['info'].get('name', '')))
            results.append(result)
            try:
                add_entities.add_update_event(pe.fb_event_id, 0, batch_lookup, creating_method=eventdata.CM_AUTO)
            except fb_api.NoFetchedDataException, e:
                logging.error("Error adding event %s, no fetched data: %s", pe.fb_event_id, e)
    yield ''.join(results).encode('utf-8')


map_classify_events = fb_mapreduce.mr_wrap(classify_events)

def mr_classify_potential_events(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup.copy(allow_cache=True),
        'Auto-Add Events',
        'logic.auto_add.map_classify_events',
        'logic.potential_events.PotentialEvent',
        handle_batch_size=20,
        queue='slow-queue',
        reader_spec='logic.auto_add.UnprocessedPotentialEventsReader',
        output_writer_spec='mapreduce.output_writers.BlobstoreOutputWriter',
        extra_mapper_params={'mime_type': 'text/plain'},
    )

