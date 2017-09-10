# We import these for their side-effects in adding routes to the wsgi app
import battle_brackets.signup_servlets
import brackets.servlets
import classes.class_pipeline
import classes.class_servlets
import event_attendees.popular_people
import event_scraper.keyword_search
import event_scraper.source_servlets
import event_scraper.scraping_tasks
import event_scraper.thing_scraper2
import event_scraper.webhooks
import events.event_reloading_tasks
import events.find_access_tokens
import favorites.servlets
import logic.unique_attendees
import mail.webhooks
import ml.gprediction_servlets
import notifications.added_events
import notifications.rsvped_events
import pubsub.pubsub_tasks
import pubsub.facebook.auth_setup
import pubsub.twitter.auth_setup
import pubsub.weekly_images
import rankings.rankings_servlets
import search.search_servlets
import search.search_tasks
import search.style_servlets
import search.search_source
import servlets.admin
import servlets.api
import servlets.calendar
import servlets.event
import servlets.event_proxy
import servlets.feedback
import servlets.login
import servlets.mobile_apps
import servlets.private_apis
import servlets.promote
import servlets.profile_page
import servlets.static
import servlets.static_db
import servlets.tools
import servlets.youtube_simple_api
import topics.topic_servlets
import tutorials.servlets
import users.user_event_tasks
import users.user_servlets
import users.user_tasks
import util.batched_mapperworker
import util.ah_handlers
import web_events.fb_events_servlets
import web_events.web_events_servlets
