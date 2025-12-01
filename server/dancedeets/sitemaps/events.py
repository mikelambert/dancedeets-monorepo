"""
Sitemap generation utilities.

The main batch processing has been migrated to Cloud Run Jobs.
See: dancedeets.jobs.generate_sitemaps

This module retains the sitemap entry generation helper for use by the job.
"""
import datetime
from lxml import etree
import logging

from dancedeets.util import urls


def generate_sitemap_entry(event):
    """
    Generate a sitemap XML entry for a single event.

    Args:
        event: DBEvent instance

    Returns:
        XML string for the URL entry, or None if event should be skipped
    """
    if not event.has_content():
        return None

    url_node = etree.Element('url')
    loc_node = etree.Element('loc')
    loc_node.text = urls.dd_event_url(event)

    if event.is_fb_event:
        if 'updated_time' in event.fb_event.get('info', {}):
            lastmod_node = etree.Element('lastmod')
            updated = event.fb_event['info']['updated_time']
            updated = updated.replace('+0000', '+00:00')
            lastmod_node.text = updated
            url_node.append(lastmod_node)
        else:
            logging.debug('Event %s does not have updated_time', event.id)

    changefreq_node = etree.Element('changefreq')
    priority_node = etree.Element('priority')

    if event.end_time:
        end_time = event.end_time
    else:
        end_time = event.start_time + datetime.timedelta(hours=2)

    start_time_delta = event.start_time - datetime.datetime.now()
    end_time_delta = end_time - datetime.datetime.now()
    event_delta = end_time - event.start_time

    priority_node.text = '0.5'

    # Event is active and not a multi-week event:
    if event_delta.days < 7 and start_time_delta.days <= 1 and end_time_delta.days >= 0:
        changefreq_node.text = 'hourly'
    # If it ended awhile ago
    elif end_time_delta.days < -30:
        changefreq_node.text = 'yearly'
        priority_node.text = '0.1'
    elif end_time_delta.days < -10:
        changefreq_node.text = 'weekly'
    # If it's coming up soon
    elif start_time_delta.days < 30:
        changefreq_node.text = 'daily'
    else:
        changefreq_node.text = 'weekly'

    url_node.append(loc_node)
    url_node.append(changefreq_node)
    url_node.append(priority_node)

    return etree.tostring(url_node, encoding='unicode')
