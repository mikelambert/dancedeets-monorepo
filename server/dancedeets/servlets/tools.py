import logging
import objgraph
import StringIO
import sys
import webapp2

from google.appengine.api import memcache

from mapreduce import control
from mapreduce import operation as op

import app
import base_servlet
from events import eventdata
import fb_api
from util import fb_events
from util import mr
from util import fb_mapreduce


# This code is used by Lets Encrypt Acme to prove ownership of dancedeets.com
# We were trying to enable SSL, and while we didn't ultimately succeed,
# it's probably worth keeping this around for whenever we want to try again.
@app.route('/.well-known/acme-challenge/J2lIvB957EnuN8U4ynpr7RX_2GbgJ9v66R7k9HEXD-o')
class SSL(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('J2lIvB957EnuN8U4ynpr7RX_2GbgJ9v66R7k9HEXD-o.XQbaOct9vX37AOs7-ADz5xfdu5eOwjUmk3FbCoPpNw8')


@app.route('/tools/memory_top_users')
class MemoryUsers(webapp2.RequestHandler):
    def get(self):
        results = objgraph.most_common_types(limit=100, shortnames=False)
        self.response.headers["Content-Type"] = "text/plain"
        for i, result in enumerate(results):
            data = "Top memory: %s" % (result,)
            logging.info(data)
            self.response.out.write(data + '\n')


@app.route('/tools/memory_dump_objgraph')
class MemoryDumper(webapp2.RequestHandler):
    def get(self):
        count = int(self.request.get('count', '20'))
        max_depth = int(self.request.get('max_depth', '10'))
        type_name = self.request.get('type')
        all_objects = list(objgraph.by_type(type_name))
        # ignore the references from our all_objects container
        ignore = [
            id(all_objects),
            id(sys._getframe(1)),
            id(sys._getframe(1).f_locals),
        ]
        sio = StringIO.StringIO()
        objgraph.show_backrefs(all_objects[:count], max_depth=max_depth, shortnames=False, extra_ignore=ignore, output=sio)
        self.response.headers["Content-Type"] = "text/plain"
        self.response.out.write(sio.getvalue())


@app.route('/tools/unprocess_future_events')
class UnprocessFutureEventsHandler(webapp2.RequestHandler):
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
    user_id, obj_id, obj_type = fbo.key().name().split('.')
    bl = fb_api.BatchLookup
    bl_types = (bl.OBJECT_EVENT, bl.OBJECT_EVENT_ATTENDING, bl.OBJECT_EVENT_MEMBERS, bl.OBJECT_THING_FEED, bl.OBJECT_VENUE)
    if obj_type in bl_types and user_id != '701004':
        yield op.db.Delete(fbo)


def count_private_events(fbl, e_list):
    for e in e_list:
        try:
            fbe = e.fb_event
            if 'info' not in fbe:
                logging.error("skipping row2 for event id %s", e.fb_event_id)
                continue
            attendees = fb_events.get_all_members_count(fbe)
            if not fb_events.is_public(fbe) and fb_events.is_public_ish(fbe):
                mr.increment('nonpublic-and-large')
            privacy = fbe['info'].get('privacy', 'UNKNOWN')
            mr.increment('privacy-%s' % privacy)

            start_date = e.start_time.strftime('%Y-%m-%d') if e.start_time else ''
            yield '%s\n' % '\t'.join(str(x) for x in [e.fb_event_id, start_date, privacy, attendees])
        except fb_api.NoFetchedDataException:
            logging.error("skipping row for event id %s", e.fb_event_id)


map_dump_private_events = fb_mapreduce.mr_wrap(count_private_events)


def mr_private_events(fbl):
    fb_mapreduce.start_map(
        fbl,
        'Dump Private Events',
        'servlets.tools.map_dump_private_events',
        'events.eventdata.DBEvent',
        handle_batch_size=80,
        queue=None,
        output_writer_spec='mapreduce.output_writers.GoogleCloudStorageOutputWriter',
        output_writer={
            'mime_type': 'text/plain',
            'bucket_name': 'dancedeets-hrd.appspot.com',
        },
    )


@app.route('/tools/oneoff')
class OneOffHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        mr_private_events(self.fbl)


@app.route('/tools/owned_events')
class OwnedEventsHandler(webapp2.RequestHandler):
    def get(self):
        db_events_query = eventdata.DBEvent.query(eventdata.DBEvent.owner_fb_uid == self.request.get('owner_id'))
        db_events = db_events_query.fetch(1000)

        print 'Content-type: text/plain\n\n'
        keys = [fb_api.generate_key(fb_api.LookupEvent, x.fb_event_id) for x in db_events]
        fb_events = fb_api.DBCache(None).fetch_keys(keys)
        for db_event, fb_event in zip(db_events, fb_events):
            real_fb_event = fb_event.decode_data()
            print db_event.tags, real_fb_event['info']['name']


@app.route('/tools/clear_memcache')
class ClearMemcacheHandler(webapp2.RequestHandler):
    def get(self):
        memcache.flush_all()
        self.response.out.write("Flushed memcache!")


def resave_table(obj):
    yield op.db.Put(obj)


@app.route('/tools/resave_table')
class ResaveHandler(webapp2.RequestHandler):
    def get(self):
        table = self.request.get('table')  # users.users.User or events.eventdata.DBEvent or ...
        control.start_map(
            name='Resave %s' % table,
            reader_spec='mapreduce.input_readers.DatastoreInputReader',
            handler_spec='servlets.tools.resave_table',
            mapper_parameters={
                'entity_kind': table,
            },
        )


def delete_table(obj):
    if obj.created_date is None:
        logging.info('Deleting %s', obj)
        yield op.db.Delete(obj)


@app.route('/tools/delete_table')
class DeleteTableHandler(webapp2.RequestHandler):
    def get(self):
        table = 'rankings.cities.City'
        control.start_map(
            name='Delete %s' % table,
            reader_spec='mapreduce.input_readers.DatastoreInputReader',
            handler_spec='servlets.tools.delete_table',
            mapper_parameters={
                'entity_kind': table,
            },
        )
