from flask import Flask
from flask.ext.admin import Admin

from flask.ext.admin.contrib import appengine

from events.cities import City
from events.eventdata import DBEvent
from events.users import User, UserFriendsAtSignup, UserMessage
from fb_api import FacebookCachedObject
from loc.gmaps_cached import CachedGeoCode
from loc.gmaps_bwcompat import GeoCode
from logic.event_locations import LocationMapping
from logic.potential_events import PotentialEvent
from logic.pubsub import OAuthToken
from logic.thing_db import Source
from topics.topic_db import Topic

app = Flask(__name__)
app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

admin = Admin(app, name="Admin")
for model in [CachedGeoCode, City, DBEvent, FacebookCachedObject, GeoCode, LocationMapping, OAuthToken, PotentialEvent, Source, Topic, User, UserFriendsAtSignup, UserMessage]:
    admin.add_view(appengine.ModelView(model))


if __name__ == '__main__':

    # Start app
    app.run(debug=True)
