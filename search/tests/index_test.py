import base64
import pickle
import unittest

from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.ext import testbed

from search import index
from test_utils import fb_api_stub


class TestModel(ndb.Model):
    the_id = property(lambda x: str(x.key.string_id()))
    indexable = ndb.BooleanProperty()
    field1 = ndb.StringProperty()
    field2 = ndb.StringProperty()

    @classmethod
    def get_by_ids(cls, id_list, keys_only=False):
        if not id_list:
            return []
        keys = [ndb.Key(cls, x) for x in id_list]
        if keys_only:
            return cls.query(cls.key.IN(keys)).fetch(len(keys), keys_only=True)
        else:
            return ndb.get_multi(keys)

class TestIndex(index.BaseIndex):
    obj_type = TestModel
    index_name = 'DummyIndex'

    @classmethod
    def _get_id(cls, obj):
        return obj.the_id

    @classmethod
    def _create_doc_event(cls, obj):
        if not obj.indexable:
            return None

        doc_event = search.Document(
            doc_id=obj.the_id,
            fields=[
                search.TextField(name='field1', value=obj.field1),
                search.TextField(name='field2', value=obj.field2),
            ],
            )
        return doc_event


class BaseTestSearch(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        #TODO(lambert): move this into some testbed wrapper code, or port upstream
        # This is a bug in the code versions between appengine and its libraries:
        # mapreduce requires a DEFAULT_VERSION_HOSTNAME
        self.testbed.setup_env(overwrite=True,
            DEFAULT_VERSION_HOSTNAME='localhost',
        )


    def tearDown(self):
        self.fb_api.deactivate()

class TestIndexFunctionality(BaseTestSearch):
    def run_taskqueue(self):
        taskq = self.taskqueue_stub
        tasks = taskq.GetTasks("default")
        taskq.FlushQueue("default")
        while tasks:
            for task in tasks:
                (func, args, opts) = pickle.loads(base64.b64decode(task["body"]))
                func(*args)
            tasks = taskq.GetTasks("default")
        taskq.FlushQueue("default")

    def runTest(self):
        query = search.Query(query_string="field1")

        # Empty the index
        TestIndex.rebuild_from_query()
        self.run_taskqueue()
        self.assertListEqual([], TestIndex.search(query).results)

        # Add an indexable object and verify we can query for it
        tm = TestModel.get_or_insert("key")
        tm.indexable = True
        tm.field1 = "field1"
        tm.field2 = None
        tm.put()
        TestIndex.rebuild_from_query()
        self.run_taskqueue()
        results = TestIndex.search(query).results
        self.assertEqual(1, len(results))
        self.assertEqual("key", results[0].doc_id)
        self.assertEqual(None, results[0].field("field2").value)

        # Now mark it unindexable and verify it gets deleted
        tm.indexable = False
        tm.put()
        TestIndex.rebuild_from_query()
        self.run_taskqueue()
        results = TestIndex.search(query).results
        self.assertListEqual([], results)

        # Now mark it indexable with a new field, and verify it all gets index appropriately
        tm.indexable = True
        tm.field2 = "extra_search"
        tm.put()
        TestIndex.update_index([tm])
        TestIndex.rebuild_from_query()
        self.run_taskqueue()
        results = TestIndex.search(query).results
        self.assertEqual(1, len(results))
        self.assertEqual("key", results[0].doc_id)
        self.assertEqual("extra_search", results[0].field("field2").value)

        # Now test our deletion function for good measure
        TestIndex.delete_ids(tm.the_id)
        self.assertListEqual([], TestIndex.search(query).results)
