import datetime
from lxml import etree

# local
import app
import base_servlet
from util import fb_mapreduce
from util import urls


def yield_sitemap_event(fbl, all_events):
    # Don't really need fbl, but makes everything easier

    for event in all_events:
        if not event.has_content():
            continue

        url_node = etree.Element('url')
        loc_node = etree.Element('loc')
        loc_node.text = urls.dd_event_url(event)
        if event.is_fb_event:
            last_mod_node = etree.Element('last_mod')
            last_mod_node.text = event.fb_event['info']['updated_time']
            url_node.append(last_mod_node)
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
        yield etree.tostring(url_node)


map_sitemap_event = fb_mapreduce.mr_wrap(yield_sitemap_event)
sitemap_event = fb_mapreduce.nomr_wrap(yield_sitemap_event)


@app.route('/tasks/generate_sitemaps')
class ReloadEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        queue = self.request.get('queue', 'fast-queue')
        time_period = self.request.get('time_period', None)

        filters = []
        if time_period:
            filters.append(('search_time_period', '=', time_period))
            name = 'Generate %s Sitemaps' % time_period
        else:
            name = 'Generate Sitemaps'
        fb_mapreduce.start_map(
            fbl=self.fbl,
            name=name,
            handler_spec='sitemaps.events.map_sitemap_event',
            entity_kind='events.eventdata.DBEvent',
            handle_batch_size=20,
            queue=queue,
            output_writer_spec='mapreduce.output_writers.GoogleCloudStorageOutputWriter',
            output_writer={
                'mime_type': 'text/plain',
                'bucket_name': 'dancedeets-hrd.appspot.com',
            },
        )

    post = get
