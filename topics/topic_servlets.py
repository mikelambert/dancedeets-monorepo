import logging
import re

import app
import base_servlet
import fb_api
from topics import grouping
from topics import topic_db
from search import search

@app.route('/topic/?')
class TopicListHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        topics = topic_db.Topic.query().fetch(500)
        self.display['topics'] = sorted(topics, key=lambda x: x.url_path)

        self.render_template('topic_list')

@app.route('/topic/([^/]+)/?')
class TopicHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self, name):
        topics = topic_db.Topic.query(topic_db.Topic.url_path==name).fetch(1)
        if not topics:
            self.response.set_status(404)
            return

        topic = topics[0]

        if topic.graph_id:
            # We shouldn't need any tokens to access pages
            fbl = fb_api.FBLookup(None, None)
            fb_source = fbl.get(topic_db.LookupTopicPage, topic.graph_id)
        else:
            fb_source = None


        def prefilter(doc_event):
            """Function for fitlering doc results, before we spend the energy to load the corresponding DBEvents.

            We only want on-topic events here:
            - Must contain keyword in the title
            - Must contain keyword on a line where it makes up >10% of the text (for judges, workshops, etc). We want to hide the resume-includes-classes-from-X people
            """
            logging.info("Prefiltering event %s", doc_event.doc_id)
            name = doc_event.field('name').value.lower()
            description = doc_event.field('description').value.lower()

            description_lines = description.split('\n')

            for keyword in topic.search_keywords:
                keyword_word_re = re.compile(r'\b%s\b' % keyword)
                if keyword_word_re.search(name):
                    return True
                for line in description_lines:
                    result = keyword_word_re.search(line)
                    # If the keyword is more than 10% of the text in the line:
                    # Examples:
                    #   "- HOUSE - KAPELA (Serial Stepperz/Wanted Posse)"
                    #   "5th November : EVENT Judged by HIRO :"
                    if result:
                        if 1.0 * len(keyword) / len(line) > 0.1:
                            return True
                        else:
                            logging.info("Found keyword %r on line, but not long enough: %r", keyword, line)

            logging.info("Prefilter dropping event %s with name: %r" % (doc_event.doc_id, name))
            return False

        keywords = ' OR '.join('"%s"' % x for x in topic.search_keywords)
        search_query = search.SearchQuery(keywords=keywords)
        # Need these fields for the prefilter
        search_query.extra_fields = ['name', 'description']
        search_results = search_query.get_search_results(prefilter=prefilter)

        self.display['topic_title'] = topic.override_title or (fb_source and fb_source['info']['name'])
        self.display['topic_image'] = topic.override_image or (fb_source and fb_source['picture']['data']['url'])
        self.display['topic_description'] = topic.override_description or (fb_source and fb_source['info'].get('about')) or ''

        self.display['all_results'] = search_results

        by_year = []
        for year, month_events in sorted(grouping.group_results_by_date(search_results).items()):
            by_year.append((year, sorted(month_events.items())))
        self.display['group_by_date'] = by_year
        by_country = sorted(grouping.group_results_by_location(search_results).items(), key=lambda x: (-len(x[1]), x[0]))
        self.display['group_by_location'] = by_country


        # TODO:
        # show points on map (future and past?)
        # show future events
        # show past events
        # show high quality and low quality events (most viable with 'past')
        # have an ajax filter on the page that lets me filter by location?
        self.display['fb_page'] = fb_source

        self.render_template('topic')


def get_id_from_url(url):
    if '#' in url:
        url = url.split('#')[1]
    if 'facebook.com' in url:
        url = url.split('facebook.com')[1]

    path_components = url.split('/')
    if path_components[1] == 'pages':
        page_id = path_components[3]
        return page_id
    else:
        page_name = path_components[1]
        return page_name

#"https://www.facebook.com/dancedeets"
#"https://www.facebook.com/pages/DanceDeets-Events/1613128148918160"

@app.route('/topic_add')
class AdminAddTopicHandler(base_servlet.BaseRequestHandler):

    def show_barebones_page(self):
        self.response.out.write('Bleh')

    def get(self):
        page_lookup_id = None
        if self.request.get('page_url'):
            page_lookup_id = get_id_from_url(self.request.get('page_url'))
        elif self.request.get('page_id'):
            page_lookup_id = self.request.get('page_id')
        else:
            self.add_error('Need to specify a page to create from')
        self.fbl.request(topic_db.LookupTopicPage, page_lookup_id, allow_cache=False)
        self.finish_preload()

        try:
            fb_page = self.fbl.fetched_data(topic_db.LookupTopicPage, page_lookup_id)
        except fb_api.NoFetchedDataException:
            return self.show_barebones_page()

        self.errors_are_fatal()

        real_page_id = fb_page['info']['id']

        topics = topic_db.Topic.query(topic_db.Topic.graph_id==real_page_id).fetch(1)
        topic = topics[0] if topics else topic_db.Topic()

        topic.graph_id = real_page_id
        topic.topic_class = topic_db.TOPIC_DANCER
        topic.search_keywords = self.request.get_all('search_keywords')
        topic.put()
        self.response.out.write('Added!')

