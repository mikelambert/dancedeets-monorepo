# class_indexing_pipeline

import datetime
import logging

from google.appengine.api import mail

from hubstorage import client
from hubstorage import job
from pipeline import common
from pipeline import pipeline

import app
import base_servlet
import keys
from classes import class_index
from util import fixed_pipelines

def get_spiders():
    return ['PMT', 'Evolution', 'Peridance', 'BDC', 'StudioV', 'NeighborhoodStudio', 'Millenium', 'EDGE', 'DebbieReynolds', 'EXPG', 'Boogiezone', 'IDA']
    # This depends on Twisted, which depends on zope.interface and lxml. And that whole ball of wax fails when run in the appengine dev sandbox.
    # We can't import any of classes/scrapers/ (since it all ultimately depends on scrapy), so there's no great way to get a list of classes.
    # Instead, class_pipeline_test does depend on it safely within nosetests, and verifies the above list matches what we get from scrapy's API)
    #from scrapy.utils.project import get_project_settings
    #from scrapy.crawler import CrawlerRunner
    #runner = CrawlerRunner(get_project_settings())
    #return runner.spider_loader.list()

def start_spiders(spiders):
    hs_client = client.HubstorageClient(keys.get('scrapinghub_key'))

    job_keys = []
    for spider in spiders:
        job = hs_client.push_job(27474, spider)
        job_keys.append(job.key)
    return job_keys

class CrawlAndIndexClassesJob(fixed_pipelines.Pipeline):
    def run(self):
        run_time = datetime.datetime.now()
        # Find all spiders by looking at modules on disk
        spiders = get_spiders()

        # Trigger new spider jobs on scrapinghub
        job_keys = start_spiders(spiders)

        # Wait for crawls to finish
        jobs_completed = yield WaitForJobs(job_keys)

        # In parallel, trigger reindex and emailing-of-errors
        yield ReindexClasses(job_keys, jobs_completed)
        yield EmailErrors(run_time, job_keys, jobs_completed)

class WaitForJobs(fixed_pipelines.Pipeline):
    def run(self, job_keys):
        hs_client = client.HubstorageClient(keys.get('scrapinghub_key'))
        jobs = [job.Job(hs_client, x) for x in job_keys]
        unfinished = [x for x in jobs if x.metadata['state'] != 'finished']
        logging.info("Waiting for %s unfinished spiders", len(unfinished))
        if unfinished:
            # Try again in 30 seconds
            with pipeline.InOrder():
                yield common.Delay(seconds=30)
                yield WaitForJobs(job_keys)
        else:
            yield common.Return(True)

class ReindexClasses(fixed_pipelines.Pipeline):
    def run(self, job_keys, jobs_completed):
        class_index.StudioClassIndex.rebuild_from_query()

class EmailErrors(fixed_pipelines.Pipeline):
    def run(self, run_time, job_keys, jobs_completed):
        hs_client = client.HubstorageClient(keys.get('scrapinghub_key'))
        jobs = [job.Job(hs_client, x) for x in job_keys]

        error_lines = {}
        for spider_job in jobs:
            for line in list(spider_job.logs.iter_values()):
                if line['level'] >= 40:
                    error_lines.setdefault(spider_job.metadata['spider'], []).append(line['message'])

        if not error_lines:
            return

        rendered = ["The following crawl errors occurred:"]
        for crawler, errors in error_lines.iteritems():
            rendered += ["%s:" % crawler]
            rendered += [errors]
            rendered += []

        message = mail.EmailMessage(
            sender="DanceDeets <dancedeets@dancedeets.com>",
            subject="Crawl Errors for %s" % run_time.strftime('%b %d, %Y: %H:%M'),
            to='dancedeets@dancedeets.com',
            html='\n'.join(rendered)
        )
        message.send()


@app.route('/tasks/crawl_and_index_classes')
class CrawlAndIndexClassesHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):

        pipeline = CrawlAndIndexClassesJob()
        pipeline.start(queue_name='slow-queue')
        self.response.out.write('OK')
    post=get
