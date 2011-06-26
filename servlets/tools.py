import csv
import logging
import StringIO
import time
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext import deferred

from util.mapper import Mapper
from events import cities
from events import eventdata
from events import users
import fb_api
from logic import event_classifier
from logic import event_smart_classifier
from logic import potential_events
from logic import thing_db

class UnprocessFutureEvents(Mapper):
    KIND = fb_api.FacebookCachedObject

    def map(self, entity):
        if entity.key().name().endswith('OBJ_EVENT'):
            if entity.json_data:
                event = entity.decode_data()
                if not event['deleted']:
                    info = event['info']
                    if info.get('start_time') > '2011-04-05' and info['updated_time'] > '2011-04-05':
                        if event_classifier.is_dance_event(event):
                            pe = potential_events.PotentialEvent.get_or_insert(str(event['info']['id']))
                            pe.looked_at = False
                            pe.put()
                            logging.info("PE %s", event['info']['id'])
        return ([], [])

class UnprocessFutureEventsHandler(webapp.RequestHandler):
    def get(self):
        m = UnprocessFutureEvents()
        m.run()
        return

from servlets import tasks
class OneOffHandler(tasks.BaseTaskFacebookRequestHandler):#webapp.RequestHandler):
    def get(self):
        f = urllib2.urlopen('https://graph.facebook.com/%s' % 105818469508896)
        data = f.read()
        for i in range(0, len(data), 100):
            logging.info(data[100*i:100*i+100])
        return
        source_id = 142477195771244
        self.batch_lookup.lookup_thing_feed(source_id)
        self.batch_lookup.finish_loading()
        data = self.batch_lookup.data_for_thing_feed(source_id)
        thing_db.create_source_for_id(source_id, data, style_type=None)

        #event_id = self.request.get('event_id')
        #batch_lookup = fb_api.CommonBatchLookup(None, None)
        #batch_lookup.lookup_event(event_id)
        #batch_lookup.finish_loading()
        #fb_event = batch_lookup.data_for_event(event_id)
        #event_smart_classifier.predict_types_for_event(fb_event)

class OwnedEventsHandler(webapp.RequestHandler):
    def get(self):
        db_events_query = eventdata.DBEvent.gql('WHERE owner_fb_uid = :1', self.request.get('owner_id'))
        db_events = db_events_query.fetch(1000)

        batch_lookup = fb_api.CommonBatchLookup(None, None)

        print 'Content-type: text/plain\n\n'
        fb_events = fb_api.FacebookCachedObject.get_by_key_name(batch_lookup._string_key(batch_lookup._event_key(x.fb_event_id)) for x in db_events)
        for db_event, fb_event in zip(db_events, fb_events):
            real_fb_event = fb_event.decode_data()
            print db_event.tags, real_fb_event['info']['name']

class TrainingCsvHandler(webapp.RequestHandler):
    def get(self):
        key_query = potential_events.PotentialEvent.all(keys_only=True)
        batch_event_keys = key_query.fetch(1000)
        self.handle_potential_events(batch_event_keys)
        while len(batch_event_keys) == 1000:
            last_key = batch_event_keys[-1]
            batch_event_keys = key_query.filter('__key__ >', last_key).fetch(1000)
            self.handle_potential_events(batch_event_keys)

    def handle_potential_events(self, batch_potential_events):

        csv_file = StringIO.StringIO()
        csv_writer = csv.writer(csv_file)
        batch_event_ids = [event.name() for event in batch_potential_events]
        db_events = eventdata.DBEvent.get_by_key_name(batch_event_ids)

        batch_lookup = fb_api.CommonBatchLookup(None, None)
        fb_events = fb_api.FacebookCachedObject.get_by_key_name(batch_lookup._string_key(batch_lookup._event_key(x)) for x in batch_event_ids)
        for event_id, db_event, fb_event in zip(batch_event_ids, db_events, fb_events):
            try:
                if not fb_event or not fb_event.json_data:
                    continue
                real_fb_event = fb_event.decode_data()
                if real_fb_event['deleted']:
                    continue
                if db_event:
                    tags = ' '.join(db_event.tags)
                else:
                    tags = ''
                features = event_smart_classifier.get_training_features(real_fb_event)
                csv_writer.writerow([tags] + list(features))
            except Exception, e:
                logging.error("Problem with event id %s: %r", event_id, e)
        self.response.out.write(csv_file.getvalue())
    

class ImportCitiesHandler(webapp.RequestHandler):
    def get(self):
        cities.import_cities()
        self.response.out.write("Imported Cities!")


class DBEventMapper(Mapper):
    KIND = eventdata.DBEvent

    def map(self, entity):
        if entity.key().name():
            return ([], [])

        new_entity = eventdata.DBEvent(
            key_name = str(entity.__dict__['_entity']['fb_event_id']),
            tags = entity.tags,
            creating_fb_uid = entity.creating_fb_uid,
        )

        return ([new_entity], [entity])

class MigrateDBEventsHandler(webapp.RequestHandler):
    def get(self):
        m = DBEventMapper()
        #m.run()

class ClearMemcacheHandler(webapp.RequestHandler):
    def get(self):
        smemcache.flush_all()
        self.response.out.write("Flushed memcache!")


