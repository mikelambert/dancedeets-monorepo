import logging

from mapreduce import context

import fb_api

from events import eventdata
from logic import add_entities
from logic import event_auto_classifier
from logic import event_classifier
from logic import event_locations
from logic import potential_events
from util import fb_mapreduce

def classify_events(fbl, pe_list):
    fbl = fb_api.massage_fbl(fbl)
    fbl.request_multi(fb_api.LookupEvent, [x.fb_event_id for x in pe_list])
    #fbl.request_multi(fb_api.LookupEventAttending, [x.fb_event_id for x in pe_list])
    
    fbl.batch_fetch()

    results = []
    for pe in pe_list:
        try:
            fb_event = fbl.fetched_data(fb_api.LookupEvent, pe.fb_event_id)
        except fb_api.NoFetchedDataException:
            continue
        if fb_event['empty']:
            continue
        classified_event = event_classifier.ClassifiedEvent(fb_event)
        classified_event.classify()
        auto_add_result = event_auto_classifier.is_auto_add_event(classified_event)
        if auto_add_result[0]:
            location_info = event_locations.LocationInfo(fb_event)
            result = '+%s\n' % '\t'.join(unicode(x) for x in (pe.fb_event_id, location_info.exact_from_event, location_info.final_city, location_info.final_city != None, location_info.fb_address, fb_event['info'].get('name', '')))
            try:
                add_entities.add_update_event(pe.fb_event_id, 0, fbl, creating_method=eventdata.CM_AUTO)
                pe2 = potential_events.PotentialEvent.get_by_key_name(str(pe.fb_event_id))
                pe2.looked_at = True
                pe2.auto_looked_at = True
                pe2.put()
                # TODO(lambert): handle un-add-able events differently
                results.append(result)
                ctx = context.get()
                ctx.counters.increment('auto-added-dance-events')
            except fb_api.NoFetchedDataException as e:
                logging.error("Error adding event %s, no fetched data: %s", pe.fb_event_id, e)
            except add_entities.AddEventException as e:
                logging.warning("Error adding event %s, no fetched data: %s", pe.fb_event_id, e)
        auto_notadd_result = event_auto_classifier.is_auto_notadd_event(classified_event, auto_add_result=auto_add_result)
        if auto_notadd_result[0]:
            pe2 = potential_events.PotentialEvent.get_by_key_name(str(pe.fb_event_id))
            pe2.looked_at = True
            pe2.auto_looked_at = True
            pe2.put()
            result = '-%s\n' % '\t'.join(unicode(x) for x in (pe.fb_event_id, fb_event['info'].get('name', '')))
            results.append(result)
            ctx = context.get()
            ctx.counters.increment('auto-notadded-dance-events')
    yield ''.join(results).encode('utf-8')

map_classify_events = fb_mapreduce.mr_wrap(classify_events)

def mr_classify_potential_events(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup.copy(allow_cache=True),
        'Auto-Add Events',
        'logic.auto_add.map_classify_events',
        'logic.potential_events.PotentialEvent',
        filters=[('looked_at', '=', None), ('should_look_at', '=', True)],
        handle_batch_size=20,
        queue='fast-queue',
        output_writer_spec='mapreduce.output_writers.BlobstoreOutputWriter',
        extra_mapper_params={'mime_type': 'text/plain'},
    )

