import csv
import json
import logging
import StringIO

import fb_api
from util import fb_mapreduce


def dump_fb_json(fbl, pe_list):
    pe_list = [x for x in pe_list if x.match_score > 0]
    if not pe_list:
        return

    fbl.request_multi(fb_api.LookupEvent, [x.fb_event_id for x in pe_list])
    fbl.batch_fetch()

    csv_file = StringIO.StringIO()
    csv_writer = csv.writer(csv_file)

    for pe in pe_list:
        try:
            result = json.dumps(fbl.fetched_data(fb_api.LookupEvent, pe.fb_event_id))
            cache_key = fbl.key_to_cache_key(fb_api.generate_key(fb_api.LookupEvent, pe.fb_event_id))
            csv_writer.writerow([cache_key, result])
        except fb_api.NoFetchedDataException:
            logging.error("skipping row for event id %s", pe.fb_event_id)
    yield csv_file.getvalue()


map_dump_fb_json = fb_mapreduce.mr_wrap(dump_fb_json)


def mr_dump_events(fbl):
    fb_mapreduce.start_map(
        fbl,
        'Dump Potential FB Event Data',
        'logic.mr_dump.map_dump_fb_json',
        'event_scraper.potential_events.PotentialEvent',
        handle_batch_size=80,
        queue=None,
        filters=[('looked_at', '=', None)],
        output_writer_spec='mapreduce.output_writers.GoogleCloudStorageOutputWriter',
        output_writer={
            'mime_type': 'text/plain',
            'bucket_name': 'dancedeets-hrd.appspot.com',
        },
    )
