import argparse
import logging
import site
import sys


site.addsitedir('lib')

logging.basicConfig(level=logging.DEBUG)

from google.cloud import datastore
from google.cloud.datastore import query
from google.cloud.datastore import helpers

import apache_beam as beam
from apache_beam.io.gcp.datastore.v1.datastoreio import ReadFromDatastore
from apache_beam.utils.pipeline_options import GoogleCloudOptions
from apache_beam.utils.pipeline_options import PipelineOptions
from apache_beam.utils.pipeline_options import SetupOptions

"""
python -m delete_old

python -m delete_old --log=DEBUG --project dancedeets-hrd job-name=popular-people --runner DataflowRunner --staging_location $BUCKET/staging --temp_location $BUCKET/temp --output $BUCKET/output --sdk_location $SDK --setup_file ./setup.py --num_workers=5
"""

#TODO: Factor these out into a module
def ConvertToEntity(element):
    return helpers.entity_from_protobuf(element)

def ConvertFromEntity(entity):
    return helpers.entity_to_protobuf(entity)

def OldPRRecord(people_ranking, old_date):
    if 'created_date' not in people_ranking:
        yield people_ranking
    else:
        naive_dt = people_ranking['created_date']
        if naive_dt < old_date:
            yield people_ranking

class DeleteFromDatastore(beam.DoFn):
    def start_bundle(self):
        self.client = datastore.Client()

    def process(self, entity):
        self.client.delete(entity.key)

def delete_from_datastore(project, pipeline_options, run_locally):
    """Creates a pipeline that reads entities from Cloud Datastore."""
    p = beam.Pipeline(options=pipeline_options)
    # Create a query to read entities from datastore.
    client = datastore.Client()

    if run_locally:
        pass
        #q.add_filter('category', '=', 'BEBOP')

    q = client.query(kind='PRDebugAttendee')
    query.order = ['-created_date']
    results = list(q.fetch(1))
    if not results:
        logging.error('No PRDebugAttendee objects found')
        return


    newest_date = results[0]['created_date']
    logging.info('Deleting elements older than %s', newest_date)

    q1 = client.query(kind='PRDebugAttendee')
    q2 = client.query(kind='PRCityCategory')
    datastore_1 = p | 'read PRDebugAttendee from datastore' >> ReadFromDatastore(project, query._pb_from_query(q1), num_splits=400)
    datastore_2 = p | 'read PRCityCategory from datastore' >> ReadFromDatastore(project, query._pb_from_query(q2), num_splits=400)
    # Set up our map/reduce pipeline
    output = (
        (datastore_1, datastore_2)
        | beam.Flatten()
        | 'convert to entity' >> beam.Map(ConvertToEntity)
        # Find the events we want to count, and expand all the admins/attendees
        | 'find old rankings' >> beam.FlatMap(OldPRRecord, newest_date)
        # And save it all back to the database
    )
    if not run_locally:
        output | 'delete from datastore' >> beam.ParDo(DeleteFromDatastore())
        """
        (output
            | 'convert from entity' >> beam.Map(ConvertFromEntity)
            | 'write to datastore' >> WriteToDatastore(client.project)
        )
        """

    # Actually run the pipeline (all operations above are deferred).
    result = p.run()
    # Wait until completion, main thread would access post-completion job results.
    result.wait_until_finish()
    return result

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run_locally',
        dest='run_locally',
        default='',
        help='Run data subset and do not save.')
    known_args, pipeline_args = parser.parse_known_args()
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    gcloud_options = pipeline_options.view_as(GoogleCloudOptions)
    delete_from_datastore('dancedeets-hrd', gcloud_options, known_args.run_locally)

if __name__ == '__main__':
    run()
