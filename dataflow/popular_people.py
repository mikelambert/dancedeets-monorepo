import logging
import site
import sys

"""
pip install 'git+https://github.com/apache/beam.git#egg=1.0&subdirectory=sdks/python' -t lib
pip install googledatastore -t lib
pip install google-cloud-datastore --user (cant use lib/)

python -m popular_people --log=DEBUG
"""

site.addsitedir('lib')

logging.basicConfig(level=logging.DEBUG)

from google.cloud import datastore
from google.cloud.datastore import query
from google.cloud.datastore import helpers

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io.gcp.datastore.v1.datastoreio import ReadFromDatastore
from apache_beam.io.gcp.datastore.v1.datastoreio import WriteToDatastore
from apache_beam.metrics import Metrics
from apache_beam.metrics.metric import MetricsFilter
from apache_beam.utils.pipeline_options import GoogleCloudOptions
from apache_beam.utils.pipeline_options import PipelineOptions
from apache_beam.utils.pipeline_options import SetupOptions


empty_line_counter = Metrics.counter('main', 'empty_lines')
word_length_counter = Metrics.counter('main', 'word_lengths')
word_counter = Metrics.counter('main', 'total_words')

class WordExtractingDoFn(beam.DoFn):
  """Parse each line of input text into words."""

  def process(self, element):
    """Returns an iterator over words in contents of Cloud Datastore entity.
    The element is a line of text.  If the line is blank, note that, too.
    Args:
      element: the input element to be processed
    Returns:
      The processed element.
    """
    print 'a', element
    entity = helpers.entity_from_protobuf(element)
    print 'b', entity
    yield []

def read_from_datastore(project, pipeline_options):
  """Creates a pipeline that reads entities from Cloud Datastore."""
  p = beam.Pipeline(options=pipeline_options)
  # Create a query to read entities from datastore.
  client = datastore.Client()
  q = client.query(kind='DBEvent')

  run_locally = True
  if run_locally:
    q.key_filter(client.key('DBEvent', '999'), '>')
    q.key_filter(client.key('DBEvent', 'A'), '<')

  # Read entities from Cloud Datastore into a PCollection.
  lines = p | 'read from datastore' >> ReadFromDatastore(project, query._pb_from_query(q))

  # Count the occurrences of each word.
  print '1', lines
  counts = (lines
            | 'split' >> (beam.ParDo(WordExtractingDoFn())
                          .with_output_types(unicode))
            )
#            | 'pair_with_one' >> beam.Map(lambda x: (x, 1))
#            | 'group' >> beam.GroupByKey()
#            | 'count' >> beam.Map(lambda (word, ones): (word, sum(ones))))

  print '2', counts
  # Format the counts into a PCollection of strings.
  output = counts | 'format' >> beam.Map(lambda (word, c): '%s: %s' % (word, c))

  # Write the output using a "Write" transform that has side effects.
  # pylint: disable=expression-not-assigned
  output | 'write' >> beam.io.WriteToText(file_path_prefix='/Users/lambert/test/',
                                          num_shards=0)

  # Actually run the pipeline (all operations above are deferred).
  result = p.run()
  print '3', result
  # Wait until completion, main thread would access post-completion job results.
  result.wait_until_finish()
  print '4', result
  return result

def run():
  pipeline_options = PipelineOptions(sys.argv)
  pipeline_options.view_as(SetupOptions).save_main_session = True
  gcloud_options = pipeline_options.view_as(GoogleCloudOptions)
  read_from_datastore('dancedeets-hrd', gcloud_options)

if __name__ == '__main__':
    run()
