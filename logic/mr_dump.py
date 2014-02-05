import csv
import json
import logging
import StringIO

import fb_api
from util import fb_mapreduce

def dump_fb_json(batch_lookup, pe_list):
    pe_list = [x for x in pe_list if x.match_score > 0]
    if not pe_list:
        return

    for pe in pe_list:
        batch_lookup.lookup_event(pe.fb_event_id)
    batch_lookup.finish_loading()

    csv_file = StringIO.StringIO()
    csv_writer = csv.writer(csv_file)

    for pe in pe_list:
        try:
            result = json.dumps(batch_lookup.data_for_event(pe.fb_event_id))
            csv_writer.writerow([batch_lookup._string_key(batch_lookup._event_key(pe.fb_event_id)), result])
        except fb_api.NoFetchedDataException:
            logging.error("skipping row for event id %s", pe.fb_event_id)
    yield csv_file.getvalue()

map_dump_fb_json = fb_mapreduce.mr_wrap(dump_fb_json)

def mr_dump_events(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup.copy(allow_cache=False),
        'Dump Potential FB Event Data',
        'logic.mr_dump.map_dump_fb_json',
        'logic.potential_events.PotentialEvent',
        handle_batch_size=80,
        queue=None,
        filters=[('looked_at', '=', None)],
        output_writer_spec='mapreduce.output_writers.BlobstoreOutputWriter',
        extra_mapper_params={'mime_type': 'text/plain'},
    )


