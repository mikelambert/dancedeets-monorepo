import io
import logging
import objgraph
import sys

from dancedeets import app
from dancedeets import base_servlet
from dancedeets import fb_api
from dancedeets.events import eventdata
from dancedeets.nlp.styles import street
from dancedeets.users import new_user_email
from dancedeets.util import fb_events
from dancedeets.util import mr
from dancedeets.util import fb_mapreduce
from dancedeets.util import sqlite_db
from dancedeets.util import memcache
from dancedeets.util.flask_adapter import BaseHandler

# Note: MapReduce is no longer available in App Engine Flexible.
# The mapreduce handlers below are kept for reference but will not work.
# Use Cloud Dataflow for batch processing tasks.


@app.route("/my_liveness_check")
class HealthzLiveHandler(BaseHandler):
    def get(self):
        self.response.out.write("OK")


def preload():
    # Download the necessary files, to avoid serving delays
    sqlite_db.get_connection("pr_person_city")
    sqlite_db.get_connection("pr_city_category")
    sqlite_db.get_connection("cities")
    # Load and compile regexes!


@app.route("/my_readiness_check")
class HealthzReadyHandler(BaseHandler):
    def get(self):
        preload()
        self.response.out.write("OK")


@app.route("/tools/memory_top_users")
class MemoryUsers(BaseHandler):
    def get(self):
        results = objgraph.most_common_types(limit=100, shortnames=False)
        self.response.headers["Content-Type"] = "text/plain"
        for i, result in enumerate(results):
            data = "Top memory: %s" % (result,)
            logging.info(data)
            self.response.out.write(data + "\n")


def resave_object(obj):
    """Note: MapReduce not available in Flexible Environment. Use Cloud Dataflow."""
    STREET = street.Style.get_name()
    if obj.verticals == [STREET, STREET]:
        obj.verticals = [STREET]
    obj.put()


@app.route("/tools/fixup")
class FixupObjects(BaseHandler):
    def get(self):
        # MapReduce not available in Flexible Environment
        # Use Cloud Dataflow for batch processing
        self.response.out.write(
            "MapReduce not available. Use Cloud Dataflow for batch processing."
        )


@app.route("/tools/email/add_event")
class DisplayAddEventEmailHandler(base_servlet.EventIdOperationHandler):
    def event_id_operation(self, fbl, event_ids):
        from dancedeets.events import event_emails_sending

        try:
            messages = event_emails_sending.send_event_add_emails(
                event_ids[0], should_send=False
            )
        except Exception as e:
            self.response.out.write("Error generating mail html: %s" % e)
        else:
            for message in messages:
                logging.info("Email generated: %s", message)
                self.response.out.write(message["html"])


@app.route("/tools/email/new_user")
class DisplayNewUserEmailHandler(base_servlet.UserOperationHandler):
    def user_operation(self, fbl, users):
        fbl.get(fb_api.LookupUser, users[0].fb_uid)
        try:
            message = new_user_email.email_for_user(users[0], fbl, should_send=False)
        except Exception as e:
            self.response.out.write("Error generating mail html: %s" % e)
        else:
            self.response.out.write(message["html"])


@app.route("/tools/memory_dump_objgraph")
class MemoryDumper(BaseHandler):
    def get(self):
        count = int(self.request.get("count", "20"))
        max_depth = int(self.request.get("max_depth", "10"))
        type_name = self.request.get("type")
        all_objects = list(objgraph.by_type(type_name))
        # ignore the references from our all_objects container
        ignore = [
            id(all_objects),
            id(sys._getframe(1)),
            id(sys._getframe(1).f_locals),
        ]
        sio = io.StringIO()
        objgraph.show_backrefs(
            all_objects[:count],
            max_depth=max_depth,
            shortnames=False,
            extra_ignore=ignore,
            output=sio,
        )
        self.response.headers["Content-Type"] = "text/plain"
        self.response.out.write(sio.getvalue())


@app.route("/tools/unprocess_future_events")
class UnprocessFutureEventsHandler(BaseHandler):
    def get(self):
        # TODO(lambert): reimplement if needed:
        # if entity.key().name().endswith('OBJ_EVENT'):
        #    if entity.json_data:
        #        event = entity.decode_data()
        #        if not event['empty']:
        #            info = event['info']
        #            if info.get('start_time') > '2011-04-05' and info['updated_time'] > '2011-04-05':
        #                pe = potential_events.PotentialEvent.get_or_insert(event['info']['id'])
        #                pe.looked_at = None
        #                pe.put()
        #                logging.info("PE %s", event['info']['id'])
        return


def map_delete_cached_with_wrong_user_id(fbo):
    """Note: MapReduce not available in Flexible Environment."""
    user_id, obj_id, obj_type = fbo.key.string_id().split(".")
    bl = fb_api.BatchLookup
    bl_types = (
        bl.OBJECT_EVENT,
        bl.OBJECT_EVENT_ATTENDING,
        bl.OBJECT_EVENT_MEMBERS,
        bl.OBJECT_THING_FEED,
        bl.OBJECT_VENUE,
    )
    if obj_type in bl_types and user_id != "701004":
        fbo.key.delete()


def count_private_events(fbl, e_list):
    for e in e_list:
        try:
            fbe = e.fb_event
            if "info" not in fbe:
                logging.error("skipping row2 for event id %s", e.fb_event_id)
                continue
            attendees = fb_events.get_all_members_count(fbe)
            if not fb_events.is_public(fbe) and fb_events.is_public_ish(fbe):
                mr.increment("nonpublic-and-large")
            privacy = fbe["info"].get("privacy", "UNKNOWN")
            mr.increment("privacy-%s" % privacy)

            start_date = e.start_time.strftime("%Y-%m-%d") if e.start_time else ""
            yield "%s\n" % "\t".join(
                str(x) for x in [e.fb_event_id, start_date, privacy, attendees]
            )
        except fb_api.NoFetchedDataException:
            logging.error("skipping row for event id %s", e.fb_event_id)


map_dump_private_events = fb_mapreduce.mr_wrap(count_private_events)


def mr_private_events(fbl):
    fb_mapreduce.start_map(
        fbl,
        "Dump Private Events",
        "dancedeets.servlets.tools.map_dump_private_events",
        "dancedeets.events.eventdata.DBEvent",
        handle_batch_size=80,
        queue=None,
        output_writer_spec="mapreduce.output_writers.GoogleCloudStorageOutputWriter",
        output_writer={
            "mime_type": "text/plain",
            "bucket_name": "dancedeets-hrd.appspot.com",
        },
    )


@app.route("/tools/oneoff")
class OneOffHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        mr_private_events(self.fbl)


@app.route("/tools/owned_events")
class OwnedEventsHandler(BaseHandler):
    def get(self):
        db_events_query = eventdata.DBEvent.query(
            eventdata.DBEvent.owner_fb_uid == self.request.get("owner_id")
        )
        db_events = db_events_query.fetch(1000)

        self.response.headers["Content-Type"] = "text/plain"
        keys = [
            fb_api.generate_key(fb_api.LookupEvent, x.fb_event_id) for x in db_events
        ]
        fb_events_data = fb_api.DBCache(None).fetch_keys(keys)
        for db_event, fb_event in zip(db_events, fb_events_data):
            real_fb_event = fb_event.decode_data()
            self.response.out.write(
                "%s %s\n" % (db_event.tags, real_fb_event["info"]["name"])
            )


@app.route("/tools/clear_memcache")
class ClearMemcacheHandler(BaseHandler):
    def get(self):
        memcache.flush_all()
        self.response.out.write("Flushed memcache!")


def resave_table(obj):
    """Note: MapReduce not available in Flexible Environment."""
    obj.put()


@app.route("/tools/resave_table")
class ResaveHandler(BaseHandler):
    def get(self):
        # MapReduce not available in Flexible Environment
        # Use Cloud Dataflow for batch processing
        self.response.out.write(
            "MapReduce not available. Use Cloud Dataflow for batch processing."
        )


def delete_table(obj):
    """Note: MapReduce not available in Flexible Environment."""
    if obj.created_date is None:
        logging.info("Deleting %s", obj)
        obj.key.delete()


@app.route("/tools/delete_table")
class DeleteTableHandler(BaseHandler):
    def get(self):
        # MapReduce not available in Flexible Environment
        # Use Cloud Dataflow for batch processing
        self.response.out.write(
            "MapReduce not available. Use Cloud Dataflow for batch processing."
        )
