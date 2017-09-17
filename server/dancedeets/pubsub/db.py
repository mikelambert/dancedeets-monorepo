from google.appengine.ext import ndb

APP_TWITTER = 'APP_TWITTER'
APP_TWITTER_DEV = 'APP_TWITTER_DEV'  # disabled twitter dev
APP_FACEBOOK = 'APP_FACEBOOK'  # a butchering of OAuthToken!
APP_FACEBOOK_WALL = 'APP_FACEBOOK_WALL'  # a further butchering!
APP_FACEBOOK_WEEKLY = 'APP_FACEBOOK_WEEKLY'  # weekly posts!


class OAuthToken(ndb.Model):
    user_id = ndb.StringProperty()
    token_nickname = ndb.StringProperty()
    application = ndb.StringProperty()
    temp_oauth_token = ndb.StringProperty()
    temp_oauth_token_secret = ndb.StringProperty()
    valid_token = ndb.BooleanProperty()
    oauth_token = ndb.StringProperty()
    oauth_token_secret = ndb.StringProperty()
    # Can we post the same thing multiple times (developer mode)
    allow_reposting = ndb.BooleanProperty()

    time_between_posts = ndb.IntegerProperty()  # In seconds!
    next_post_time = ndb.DateTimeProperty()

    json_data = ndb.JsonProperty()

    # search criteria? location? radius? search terms?
    # post on event find? post x hours before event? multiple values?

    def queue_id(self):
        return str(self.key.id())

    @property
    def country_filters(self):
        if self.json_data is None:
            self.json_data = {}
        return self.json_data.setdefault('country_filters', [])
