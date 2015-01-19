import logging
import re

import base_servlet
import fb_api
from topics import topic_db
from logic import search

class TopicHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self, name):
        topics = topic_db.Topic.query(topic_db.Topic.name==name).fetch(1)
        if not topics:
            self.response.status_code = 404
            return

        topic = topics[0]

        if topic.graph_id:
            # We shouldn't need any tokens to access pages
            fbl = fb_api.FBLookup(None, None)
            fb_source = fbl.get(topic_db.LookupTopicPage, topic.graph_id)
        else:
            fb_source = None


        def prefilter(pseudo_db_event):
            """Function for fitlering db results, before we spend the energy to load the corresponding Facebook data objects.

            We only want on-topic events here:
            - Must contain keyword in the title
            - Must contain keyword on a line where it makes up >20% of the text (for judges, workshops, etc). We want to hide the resume-includes-classes-from-X people
            """
            search_result = pseudo_db_event._search_result
            title_description = search_result.field('keywords').value
            title, description = title_description.split('\n\n', 1)
            description_lines = description.split('\n')

            for keyword in topic.search_keywords:
                keyword_word_re = re.compile(r'\b%s\b' % keyword)
                if keyword_word_re.search(title):
                    return True
                for line in description_lines:
                    result = keyword_word_re.search(line)
                    if result and 1.0 * len(keyword) / len(line) > 0.2:
                        return True

            logging.info("Prefilter dropping event %s with title: %r" % (pseudo_db_event.fb_event_id, title))
            return False

        keywords = ' OR '.join(topic.search_keywords)
        search_query = search.SearchQuery(keywords=keywords)
        search_results = search_query.get_search_results(self.fbl, prefilter=prefilter)

        self.display['title'] = topic.override_title or (fb_source and fb_source['info']['name'])
        self.display['image'] = topic.override_image or (fb_source and fb_source['picture']['data']['url'])
        self.display['description'] = topic.override_description or (fb_source and fb_source['info']['about'])

        self.display['search_results'] = search_results


        # TODO:
        # show points on map (future and past?)
        # show future events
        # show past events
        # show high quality and low quality events (most viable with 'past')
        # have an ajax filter on the page that lets me filter by location?
        self.display['fb_page'] = fb_source

        self.render_template('topic')
