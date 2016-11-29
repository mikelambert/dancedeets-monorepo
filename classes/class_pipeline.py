# class_indexing_pipeline

import datetime
import logging

from google.appengine.api import mail

from pipeline import common
from pipeline import pipeline
import scrapinghub

import app
import base_servlet
import keys
from classes import class_index
from util import fixed_pipelines


def get_spiders():
    return [
        # NY
        'PMT', 'Evolution', 'Peridance', 'BDC', 'EXPG',
        # LA
        'NeighborhoodStudio', 'Millenium', 'EDGE', 'DebbieReynolds', 'Boogiezone', 'IDA', 'mL', 'TheLab',
    ]
    # This depends on Twisted, which depends on zope.interface and lxml. And that whole ball of wax fails when run in the appengine dev sandbox.
    # We can't import any of classes/scrapers/ (since it all ultimately depends on scrapy), so there's no great way to get a list of classes.
    # Instead, class_pipeline_test does depend on it safely within nosetests, and verifies the above list matches what we get from scrapy's API)
    # from scrapy.utils.project import get_project_settings
    # from scrapy.crawler import CrawlerRunner
    # runner = CrawlerRunner(get_project_settings())
    # return runner.spider_loader.list()


def get_shub_project():
    conn = scrapinghub.Connection(keys.get('scrapinghub_key'))
    project = scrapinghub.Project(conn, 27474)
    return project


def start_spiders(spiders):
    project = get_shub_project()
    job_keys = []
    for spider in spiders:
        job_id = project.schedule(spider)
        job_keys.append(job_id)
    logging.info("Scheduled jobs: %s", job_keys)
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
        project = get_shub_project()
        jobs = [project.job(x) for x in job_keys]
        unfinished = [x for x in jobs if x.info['state'] != 'finished']
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
        project = get_shub_project()
        jobs = [project.job(x) for x in job_keys]

        error_lines = {}

        for spider_job in jobs:
            if not spider_job.info['items_scraped']:
                error_lines.setdefault(spider_job.info['spider'], []).append('Could not find any items.')

            for line in spider_job.log():
                if line['level'] >= 40:
                    error_lines.setdefault(spider_job.info['spider'], []).append(line['message'])

        if not error_lines:
            return

        rendered = ["The following crawl errors occurred:"]
        for crawler, errors in error_lines.iteritems():
            rendered += ["%s:" % crawler]
            rendered += errors
            rendered += []

        body = '\n'.join(rendered)
        logging.warning("%s", body)

        message = mail.EmailMessage(
            sender="DanceDeets Reports <reports@dancedeets.com>",
            subject="Crawl Errors for %s" % run_time.strftime('%b %d, %Y: %H:%M'),
            to='reports@dancedeets.com',
            body=body,
        )
        message.send()


@app.route('/tasks/crawl_and_index_classes')
class CrawlAndIndexClassesHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        pipeline = CrawlAndIndexClassesJob()
        pipeline.start(queue_name='slow-queue')
        self.response.out.write('OK')
    post=get
