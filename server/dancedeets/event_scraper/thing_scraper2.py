"""
Source scraping and event processing.

This functionality has been migrated to Cloud Run Jobs.
See: dancedeets.jobs.scrape_and_classify

This module is kept for backwards compatibility but the mapreduce
handlers have been removed. Use the Cloud Run Job instead.
"""
import logging

from dancedeets import app
from dancedeets import base_servlet


@app.route('/tasks/scrape_sources_and_process_events')
class LoadPotentialEventsFromWallPostsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    """
    Legacy handler - scraping has been migrated to Cloud Run Jobs.

    Use: python -m dancedeets.jobs.runner --job=scrape_and_classify
    """
    def get(self):
        logging.warning(
            'This endpoint is deprecated. '
            'Use Cloud Run Job: dancedeets.jobs.scrape_and_classify instead.'
        )
        self.response.out.write('DEPRECATED: Use Cloud Run Job scrape_and_classify instead')
