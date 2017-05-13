import logging

from scrapy.exceptions import IgnoreRequest
from scrapy.spidermiddlewares import httperror

logger = logging.getLogger(__name__)

class BetterHttpErrorMiddleware(httperror.HttpErrorMiddleware):
    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, httperror.HttpError):
            logger.info(
                "Ignoring response %(response)r: HTTP status code is not handled or not allowed. Has body:\n%(response_contents)s",
                {'response': response, 'response_contents': response.body}, extra={'spider': spider},
            )
            return []
