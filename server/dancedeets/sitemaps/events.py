import datetime
from lxml import etree
import logging

# local
from dancedeets import app
from dancedeets import base_servlet
from dancedeets.util import fb_mapreduce
from dancedeets.util import urls


def yield_sitemap_event(fbl, all_events):
    # Don't really need fbl, but makes everything easier

    for event in all_events:
        if not event.has_content():
            continue

        url_node = etree.Element('url')
        loc_node = etree.Element('loc')
        loc_node.text = urls.dd_event_url(event)
        if event.is_fb_event:
            if 'updated_time' in event.fb_event['info']:
                lastmod_node = etree.Element('lastmod')
                updated = event.fb_event['info']['updated_time']
                updated = updated.replace('+0000', '+00:00')
                lastmod_node.text = updated
                url_node.append(lastmod_node)
            else:
                logging.info('Event %s does not have updated_time: %s' % (event.id, event.fb_event))
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
        # prints out as one line
        yield '%s\n' % etree.tostring(url_node)


map_sitemap_event = fb_mapreduce.mr_wrap(yield_sitemap_event)
sitemap_event = fb_mapreduce.nomr_wrap(yield_sitemap_event)


@app.route('/tasks/generate_sitemaps')
class ReloadEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        queue = self.request.get('queue', 'fast-queue')
        time_period = self.request.get('time_period', None)
        vertical = self.request.get('vertical', None)

        filters = []
        if vertical:
            filters.append(('verticals', '=', vertical))
            vertical_string = '%s ' % vertical
        else:
            vertical_string = ''

        if time_period:
            filters.append(('search_time_period', '=', time_period))
            name = 'Generate %s %sSitemaps' % (time_period, vertical_string)
        else:
            name = 'Generate %sSitemaps' % vertical_string
        fb_mapreduce.start_map(
            fbl=self.fbl,
            name=name,
            handler_spec='dancedeets.sitemaps.events.map_sitemap_event',
            entity_kind='dancedeets.events.eventdata.DBEvent',
            handle_batch_size=20,
            filters=filters,
            queue=queue,
            output_writer_spec='mapreduce.output_writers.GoogleCloudStorageOutputWriter',
            output_writer={
                'mime_type': 'text/plain',
                'bucket_name': 'dancedeets-hrd.appspot.com',
            },
        )

    post = get
