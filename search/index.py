import logging

from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.ext import ndb
from google.appengine.api import search

MAX_OBJECTS = 100000

class BaseIndex(object):
    obj_type = None
    index_name = None

    @classmethod
    def _create_doc_event(cls, obj):
        raise NotImplementedError()

    @classmethod
    def _is_ndb(cls):
        return issubclass(cls.obj_type, ndb.Model)

    @classmethod
    def real_index(cls):
        return search.Index(name=cls.index_name)

    @classmethod
    def search(cls, query):
        return cls.real_index().search(query)

    @classmethod
    def _get_query_params_for_indexing(cls):
        return []

    @classmethod
    def _get_id(cls, obj):
        if cls._is_ndb():
            if not isinstance(obj, ndb.Key):
                # Turn objects into keys
                key = obj.key
            else:
                key = obj
            obj_id = key.string_id()
        else:
            if not isinstance(key, db.Key):
                # Turn objects into keys
                key = obj.key()
            else:
                key = obj
            obj_id = key().name()
        return obj_id

    @classmethod
    def update_index(cls, objects_to_update):
        index_objs = []
        deindex_ids = []
        for obj in objects_to_update:
            obj_id = cls._get_id(obj)

            logging.info("Adding to search index: %s", obj_id)
            doc_event = cls._create_doc_event(obj)
            if not doc_event:
                deindex_ids.append(obj_id)
            else:
                if doc_event.doc_id != cls._get_id(obj):
                    logging.error("Error, created DocEvent with id %r instead of %r" % (doc_event.doc_id, cls._get_id(obj)))
                index_objs.append(doc_event)
        cls.put_objects(index_objs)
        cls.delete_ids(deindex_ids)

    @classmethod
    def put_objects(cls, objects):
        doc_index = cls.real_index()
        for i in range(0, len(objects), search.MAXIMUM_DOCUMENTS_PER_PUT_REQUEST):
            doc_index.put(objects[i:i + search.MAXIMUM_DOCUMENTS_PER_PUT_REQUEST])

    @classmethod
    def delete_ids(cls, object_ids):
        logging.info("Deleting from search index: %s", object_ids)
        doc_index = cls.real_index()
        for i in range(0, len(object_ids), search.MAXIMUM_DOCUMENTS_PER_PUT_REQUEST):
            doc_index.delete(object_ids[i:i + search.MAXIMUM_DOCUMENTS_PER_PUT_REQUEST])

    @classmethod
    def rebuild_from_query(cls, force=False):
        logging.info("Loading Index")
        if cls._is_ndb():
            db_query = cls.obj_type.query(*cls._get_query_params_for_indexing())
        else:
            db_query = cls.obj_type.all()
        object_keys = db_query.fetch(MAX_OBJECTS, keys_only=True)
        object_ids = set(cls._get_id(x) for x in object_keys)

        logging.info("Loaded %s objects for indexing", len(object_ids))
        if len(object_ids) >= MAX_OBJECTS:
            logging.critical('Found %s objects. Increase the MAX_OBJECTS limit to search more events.', MAX_OBJECTS)

        doc_index = cls.real_index()

        docs_per_group = search.MAXIMUM_DOCUMENTS_PER_PUT_REQUEST

        logging.info("Deleting Expired docs")
        start_id = '0'
        doc_ids_to_delete = set()
        while True:
            doc_ids = [x.doc_id for x in doc_index.get_range(ids_only=True, start_id=start_id, include_start_object=False)]
            if not doc_ids:
                break
            new_ids_to_delete = set(doc_ids).difference(object_ids)
            doc_ids_to_delete.update(new_ids_to_delete)
            logging.info("Looking at %s doc_id candidates for deletion, will delete %s entries.", len(doc_ids), len(new_ids_to_delete))
            start_id = doc_ids[-1]
        threshold = 0.20
        if not force and len(doc_ids_to_delete) and len(doc_ids_to_delete) > len(object_ids) * threshold:
            logging.critical("Deleting %s docs, more than %d%% of total %s docs", len(doc_ids_to_delete), threshold * 100, len(object_ids))
            return
        logging.info("Deleting %s docs", len(doc_ids_to_delete))
        doc_ids_to_delete = list(doc_ids_to_delete)
        for i in range(0, len(doc_ids_to_delete), docs_per_group):
            doc_index.delete(doc_ids_to_delete[i:i + docs_per_group])

        # Add all events
        logging.info("Loading %s docs, in groups of %s", len(object_ids), docs_per_group)
        object_ids_list = list(object_ids)
        for i in range(0, len(object_ids_list), docs_per_group):
            group_object_ids = object_ids_list[i:i + docs_per_group]
            deferred.defer(cls._save_ids, group_object_ids)

    @classmethod
    def _save_ids(cls, object_ids):
        # TODO(lambert): how will we ensure we only update changed events?
        logging.info("Loading %s objects", len(object_ids))
        if cls._is_ndb():
            objects = cls.obj_type.get_by_ids(object_ids)
        else:
            objects = cls.obj_type.get_by_key_name(object_ids)
        if None in objects:
            logging.error("Lookup returned at least one None!")

        delete_ids = []
        doc_events = []
        logging.info("Constructing Documents")
        for obj_id, obj in zip(object_ids, objects):
            doc_event = cls._create_doc_event(obj)
            if not doc_event:
                delete_ids.append(obj_id)
                continue
            if doc_event.doc_id != cls._get_id(obj):
                logging.error("Error, created DocEvent with id %s instead of %s", doc_event.doc_id, cls._get_id(obj))
            doc_events.append(doc_event)

        logging.info("Adding %s documents", len(doc_events))
        cls.put_objects(doc_events)

        # These events could not be filtered out too early,
        # but only after looking up in this db+fb-event-data world
        logging.info("Cleaning up and deleting %s documents", len(delete_ids))
        cls.delete_ids(delete_ids)
