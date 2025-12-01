"""
Class crawling and indexing pipeline.

This functionality has been migrated to Cloud Workflows and Cloud Run Jobs.
See:
- Workflow: workflows/crawl_and_index_classes.yaml
- Jobs: dancedeets.jobs.start_spiders
        dancedeets.jobs.reindex_classes
        dancedeets.jobs.email_crawl_errors

This module is kept for backwards compatibility but the Pipeline
handlers have been removed. Use Cloud Workflows instead.
"""
import logging

from dancedeets import app
from dancedeets import base_servlet


@app.route('/tasks/crawl_and_index_classes')
class CrawlAndIndexClassesHandler(base_servlet.BaseTaskRequestHandler):
    """
    Legacy handler - crawling has been migrated to Cloud Workflows.

    Use Cloud Workflow: crawl_and_index_classes
    Or individual jobs:
    - python -m dancedeets.jobs.runner --job=start_spiders
    - python -m dancedeets.jobs.runner --job=reindex_classes
    - python -m dancedeets.jobs.runner --job=email_crawl_errors
    """
    def get(self):
        logging.warning(
            'This endpoint is deprecated. '
            'Use Cloud Workflow: crawl_and_index_classes instead.'
        )
        self.response.out.write('DEPRECATED: Use Cloud Workflow crawl_and_index_classes instead')

    post = get
