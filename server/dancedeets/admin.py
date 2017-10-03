from flask import Flask
from flask_admin import Admin
from flask_admin.contrib import appengine

from dancedeets import keys

from dancedeets.classes.class_models import StudioClass
from dancedeets.event_attendees.popular_people import PRCityCategory
from dancedeets.event_attendees.popular_people import PRDebugAttendee
from dancedeets.event_scraper.potential_events import PotentialEvent
from dancedeets.event_scraper.thing_db import Source
from dancedeets.events.eventdata import DBEvent
from dancedeets.events.event_locations import LocationMapping
from dancedeets.events.featured import FeaturedResult
from dancedeets.fb_api import FacebookCachedObject
from dancedeets.loc.gmaps_cached import CachedGeoCode
from dancedeets.loc.gmaps_bwcompat import GeoCode
from dancedeets.pubsub.db import OAuthToken
from dancedeets.search.search import DisplayEvent
from dancedeets.servlets.static_db import StaticContent
from dancedeets.topics.topic_db import Topic
from dancedeets.users.users import User, UserFriendsAtSignup, UserMessage

app = Flask(__name__)
app.debug = True
app.secret_key = keys.get('flask_session_key')

admin = Admin(app, name="Admin")
for model in [
    CachedGeoCode, DBEvent, DisplayEvent, FacebookCachedObject, FeaturedResult, GeoCode, LocationMapping, OAuthToken, PRCityCategory,
    PRDebugAttendee, PotentialEvent, Source, StaticContent, StudioClass, Topic, User, UserFriendsAtSignup, UserMessage
]:
    admin.add_view(appengine.ModelView(model))

if __name__ == '__main__':

    # Start app
    app.run(debug=True)
