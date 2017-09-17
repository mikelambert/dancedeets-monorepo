from mapreduce import control

import app
import base_servlet
from events import eventdata
from event_scraper import potential_events


def update_user_qualities(user):
    #STR_ID_MIGRATE
    source_potential_events = potential_events.PotentialEvent.gql('WHERE source_ids = :graph_id', graph_id=long(user.fb_uid)).fetch(1000)
    added_events = eventdata.DBEvent.get_by_ids([x.fb_event_id for x in source_potential_events])

    user.num_auto_added_events = len([
        x for x in added_events if x and x.creating_method in [eventdata.CM_AUTO, eventdata.CM_AUTO_ATTENDEE]
    ])
    user.num_auto_added_own_events = len([
        x for x in added_events
        if x and x.creating_method in [eventdata.CM_AUTO, eventdata.CM_AUTO_ATTENDEE] and x.owner_fb_uid == user.fb_uid
    ])
    #STR_ID_MIGRATE
    user.num_hand_added_events = len([
        x for x in added_events if x and x.creating_method == eventdata.CM_USER and str(x.creating_fb_uid) == user.fb_uid
    ])
    #STR_ID_MIGRATE
    user.num_hand_added_own_events = len([
        x for x in added_events
        if x and x.creating_method == eventdata.CM_USER and str(x.creating_fb_uid) == user.fb_uid and x.owner_fb_uid == user.fb_uid
    ])


def map_compute_user_stats(user):
    update_user_qualities(user)
    user.put()


@app.route('/tasks/recompute_user_stats')
class RecomputeUserStatsHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        control.start_map(
            name='Compute User-Event Stats',
            reader_spec='mapreduce.input_readers.DatastoreInputReader',
            handler_spec='users.user_event_tasks.map_compute_user_stats',
            mapper_parameters={'entity_kind': 'users.users.User'},
            queue_name='fast-queue',
            shard_count=5,
        )

    post = get
