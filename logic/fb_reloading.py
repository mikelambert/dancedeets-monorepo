from logic import pubsub
from util import dates
from util import fb_mapreduce
from util import timings


@timings.timed
def yield_post_jp_event(fbl, db_events):
    from mapreduce import context
    ctx = context.get()
    params = ctx.mapreduce_spec.mapper.params
    token_nickname = params.get('token_nickname')
    db_events = [x for x in db_events if x.actual_city_name and x.actual_city_name.endswith('Japan')]
    for db_event in db_events:
        pubsub.eventually_publish_event(fbl, db_event.fb_event_id, token_nickname)
map_post_jp_event = fb_mapreduce.mr_wrap(yield_post_jp_event)

def mr_post_jp_events(fbl, token_nickname):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Post Future Japan Events',
        handler_spec='logic.fb_reloading.map_post_jp_event',
        entity_kind='events.eventdata.DBEvent',
        filters=[('search_time_period', '=', dates.TIME_FUTURE)],
        handle_batch_size=20,
        extra_mapper_params={'token_nickname': token_nickname},
    )

