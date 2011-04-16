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
from logic import potential_events

class UnprocessFutureEvents(Mapper):
    KIND = fb_api.FacebookCachedObject

    def map(self, entity):
        if entity.key().name().endswith('OBJ_EVENT'):
            if entity.json_data:
                event = entity.decode_data()
                if not event['deleted']:
                    info = event['info']
                    if info['start_time'] > '2011-04-05' and info['updated_time'] > '2011-04-05':
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

class OneOffHandler(webapp.RequestHandler):
    def get(self):
        return

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
                if 'owner' in real_fb_event['info']:
                    owner_name = real_fb_event['info']['owner']['id']
                else:
                    owner_name = ''
                location = eventdata.get_original_address_for_event(real_fb_event).encode('utf8')
                name_and_description = '%s %s' % (real_fb_event['info']['name'], real_fb_event['info'].get('description', ''))
                name_and_description = name_and_description.replace('\n', ' ').encode('utf8')
                
                csv_writer.writerow([tags, owner_name, location, name_and_description])
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


