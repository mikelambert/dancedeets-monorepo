from mapreduce import util
from mapreduce import input_readers

class FilteredInputReader(input_readers.DatastoreInputReader):

    def _iter_key_range(self, k_range):
        cursor = None
        while True:
            query = k_range.make_ascending_query(
                util.for_name(self._entity_kind))
            self.filter_query(query)
            if cursor:
                query.with_cursor(cursor)

            results = query.fetch(limit=self._batch_size)
            if not results:
                break

            for model_instance in results:
                key = model_instance.key()
                yield key, model_instance
            cursor = query.cursor()

    def filter_query(self, query):
        raise NotImplementedError("filter_query() not implemented in %s" % self.__class__)
