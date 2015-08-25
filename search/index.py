import logging

from google.appengine.ext import deferred
from google.appengine.ext import ndb
from google.appengine.api import search

MAX_OBJECTS = 100000

class BaseIndex(object):
    obj_type = None
    index_name = None

    @classmethod
    def _get_id(self, obj):
        raise NotImplementedError()

    @classmethod
    def _create_doc_event(cls, obj):
        raise NotImplementedError()

    @classmethod
    def _is_ndb(cls):
        return issubclass(cls, ndb.Model)

    @classmethod
    def search(cls, query):
        return search.Index(name=cls.index_name).search(query)

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
                index_objs.append(doc_event)
        doc_index = search.Index(name=cls.index_name)
        doc_index.put(index_objs)
        doc_index.delete(deindex_ids)

    @classmethod
    def delete_ids(cls, object_ids):
        logging.info("Deleting from search index: %s", object_ids)
        doc_index = search.Index(name=cls.index_name)
        doc_index.delete(object_ids)

    @classmethod
    def rebuild_from_query(cls, *query_params):
        logging.info("Loading Index")
        if cls._is_ndb():
            db_query = cls.obj_type.query(*query_params)
        else:
            db_query = cls.obj_type.all()
            for query_filter in query_params:
                db_query = db_query.filter(*query_filter)
        object_keys = db_query.fetch(MAX_OBJECTS, keys_only=True)
        if cls._is_ndb():
            object_ids = set(x.string_id() for x in object_keys)
        else:
            object_ids = set(x.name() for x in object_keys)

        logging.info("Loaded %s objects for indexing", len(object_ids))
        if len(object_ids) >= MAX_OBJECTS:
            logging.critical('Found %s objects. Increase the MAX_OBJECTS limit to search more events.', MAX_OBJECTS)

        doc_index = search.Index(name=cls.index_name)

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
        if len(doc_ids_to_delete) and len(doc_ids_to_delete) < len(object_ids) / 10:
            logging.critical("Deleting %s docs, more than 10% of total %s docs", len(doc_ids_to_delete), len(object_ids))
        logging.info("Deleting %s docs", len(doc_ids_to_delete))
        doc_ids_to_delete = list(doc_ids_to_delete)
        for i in range(0,len(doc_ids_to_delete), docs_per_group):
            doc_index.delete(doc_ids_to_delete[i:i+docs_per_group])

        # Add all events
        logging.info("Loading %s docs, in groups of %s", len(object_ids), docs_per_group)
        object_ids_list = list(object_ids)
        for i in range(0,len(object_ids_list), docs_per_group):
            group_object_ids = object_ids_list[i:i+docs_per_group]
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
            doc_events.append(doc_event)

        logging.info("Adding %s documents", len(doc_events))
        doc_index = search.Index(name=cls.index_name)
        doc_index.put(doc_events)

        # These events could not be filtered out too early,
        # but only after looking up in this db+fb-event-data world
        logging.info("Cleaning up and deleting %s documents", len(delete_ids))
        doc_index.delete(delete_ids)
