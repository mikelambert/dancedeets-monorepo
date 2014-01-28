import logging

import fb_api

from logic import gprediction
from logic import potential_events
from util import fb_mapreduce

def classify_events(batch_lookup, pe_list):
    pe_list = [x for x in pe_list if x.match_score > 0]
    if not pe_list:
        return
    predict_service = None
    for pe in pe_list:
        if not getattr(pe, 'dance_bias_score'):
            batch_lookup.lookup_event(pe.fb_event_id)
            batch_lookup.lookup_event_attending(pe.fb_event_id)
    batch_lookup.finish_loading()

    results = []
    for pe in pe_list:
        if not getattr(pe, 'dance_bias_score'):
            try:
                fb_event = batch_lookup.data_for_event(pe.fb_event_id)
                fb_event_attending = batch_lookup.data_for_event_attending(pe.fb_event_id)
            except fb_api.NoFetchedDataException:
                continue
            if fb_event['empty']:
                continue
            predict_service = predict_service or gprediction.get_predict_service()
            pe = potential_events.update_scores_for_potential_event(pe, fb_event, fb_event_attending, predict_service)
        logging.info("%s has ms=%s, d=%s, nd=%s", pe.fb_event_id, pe.match_score, pe.dance_bias_score, pe.non_dance_bias_score)
        if pe.dance_bias_score > 0.5 and pe.non_dance_bias_score > 0.5:
            result = '%s:%s:%s:%s\n' % (pe.fb_event_id, pe.match_score, pe.dance_bias_score, pe.non_dance_bias_score)
            results.append(result)
    yield ''.join(results).encode('utf-8')


map_classify_events = fb_mapreduce.mr_wrap(classify_events)

def mr_classify_potential_events(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup.copy(allow_cache=False),
        'Auto-Classify Events',
        'logic.mr_prediction.map_classify_events',
        'logic.potential_events.PotentialEvent',
        filters=[('looked_at', '=', None)],
        handle_batch_size=20,
        queue='slow-queue',
        output_writer_spec='mapreduce.output_writers.BlobstoreOutputWriter',
        extra_mapper_params={'mime_type': 'text/plain'},
    )

