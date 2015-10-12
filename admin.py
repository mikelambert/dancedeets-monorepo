from flask import Flask
from flask.ext.admin import Admin

from flask.ext.admin.contrib import appengine

import keys

from classes.class_models import StudioClass
from events.eventdata import DBEvent
from events.event_locations import LocationMapping
from event_scraper.potential_events import PotentialEvent
from event_scraper.thing_db import Source
from rankings.cities import City
from fb_api import FacebookCachedObject
from loc.gmaps_cached import CachedGeoCode
from loc.gmaps_bwcompat import GeoCode
from pubsub.pubsub import OAuthToken
from search.search import DisplayEvent
from topics.topic_db import Topic
from users.users import User, UserFriendsAtSignup, UserMessage

app = Flask(__name__)
app.debug = True
app.secret_key = keys.get('flask_session_key')

admin = Admin(app, name="Admin")
for model in [CachedGeoCode, City, DBEvent, DisplayEvent, FacebookCachedObject, GeoCode, LocationMapping, OAuthToken, PotentialEvent, Source, StudioClass, Topic, User, UserFriendsAtSignup, UserMessage]:
    admin.add_view(appengine.ModelView(model))


if __name__ == '__main__':

    # Start app
    app.run(debug=True)
