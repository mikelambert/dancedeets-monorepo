import oauth2 as oauth
import urlparse

import base_servlet
import app
from .. import db
from . import auth

request_token_url = 'https://twitter.com/oauth/request_token'
access_token_url = 'https://twitter.com/oauth/access_token'
authorize_url = 'https://twitter.com/oauth/authorize'


def twitter_oauth1(user_id, token_nickname, country_filter):
    consumer = oauth.Consumer(auth.consumer_key, auth.consumer_secret)
    client = oauth.Client(consumer)

    # Step 1: Get a request token. This is a temporary token that is used for
    # having the user authorize an access token and to sign the request to obtain
    # said access token.

    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))

    auth_tokens = db.OAuthToken.query(
        db.OAuthToken.user_id == user_id, db.OAuthToken.token_nickname == token_nickname, db.OAuthToken.application == db.APP_TWITTER
    ).fetch(1)
    if auth_tokens:
        auth_token = auth_tokens[0]
    else:
        auth_token = db.OAuthToken()
    auth_token.user_id = user_id
    auth_token.token_nickname = token_nickname
    auth_token.application = db.APP_TWITTER
    auth_token.temp_oauth_token = request_token['oauth_token']
    auth_token.temp_oauth_token_secret = request_token['oauth_token_secret']
    if country_filter:
        auth_token.country_filters += country_filter.upper()
    auth_token.put()

    # Step 2: Redirect to the provider. Since this is a CLI script we do not
    # redirect. In a web application you would redirect the user to the URL
    # below.

    return "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])


# user comes to:
# /sign-in-with-twitter/?
#        oauth_token=NPcudxy0yU5T3tBzho7iCotZ3cnetKwcTIRlX0iwRl0&
#        oauth_verifier=uw7NjWHT6OJ1MpJOXsHfNxoAhPKpgI8BlYDhxEjIBY


def twitter_oauth2(oauth_token, oauth_verifier):
    auth_tokens = db.OAuthToken.query(db.OAuthToken.temp_oauth_token == oauth_token, db.OAuthToken.application == db.APP_TWITTER).fetch(1)
    if not auth_tokens:
        return None
    auth_token = auth_tokens[0]
    # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # URL you can request the access token the user has approved. You use the
    # request token to sign this request. After this is done you throw away the
    # request token and use the access token returned. You should store this
    # access token somewhere safe, like a database, for future use.
    token = oauth.Token(oauth_token, auth_token.temp_oauth_token_secret)
    token.set_verifier(oauth_verifier)
    consumer = oauth.Consumer(auth.consumer_key, auth.consumer_secret)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))
    auth_token.oauth_token = access_token['oauth_token']
    auth_token.oauth_token_secret = access_token['oauth_token_secret']
    auth_token.valid_token = True
    auth_token.time_between_posts = 5 * 60  # every 5 minutes
    auth_token.put()
    return auth_token


@app.route('/twitter/oauth_start')
class TwitterOAuthStartHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        nickname = self.request.get('token_nickname')
        if not nickname:
            #TODO(lambert): Clean up
            self.response.write('Need token_nickname parameter')
            return
        country_filter = self.request.get('country_filter')
        url = twitter_oauth1(self.fb_uid, nickname, country_filter)
        self.redirect(url)


@app.route('/twitter/oauth_callback')
class TwitterOAuthCallbackHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        oauth_token = self.request.get('oauth_token')
        oauth_verifier = self.request.get('oauth_verifier')
        auth_token = twitter_oauth2(oauth_token, oauth_verifier)
        if auth_token:
            self.redirect('/twitter/oauth_success?nickname=' + auth_token.token_nickname)
        else:
            self.redirect('/twitter/oauth_failure')


@app.route('/twitter/oauth_success')
class TwitterOAuthSuccessHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        #TODO(lambert): Clean up
        self.response.write('Authorized!')


@app.route('/twitter/oauth_failure')
class TwitterOAuthFailureHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        #TODO(lambert): Clean up
        self.response.write("Failure, couldn't find auth token conection!")
