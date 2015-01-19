# -*-*- encoding: utf-8 -*-*-

import json
import logging
import re
import urlparse
import oauth2 as oauth

from google.appengine.ext import ndb
import twitter

from events import eventdata
import fb_api
import keys
from util import dates
from util import urls

consumer_key = 'xzpiBnUCGqTWSqTgmE6XtLDpw'
consumer_secret = keys.get("twitter_consumer_secret") 

DATE_FORMAT = "%Y/%m/%d"
TIME_FORMAT = "%H:%M"

def publish_event(fbl, event_id):
    event_id = str(event_id)
    fb_event = fbl.get(fb_api.LookupEvent, event_id)
    e = eventdata.DBEvent.get_or_insert(event_id)

    # When we want to support complex queries on many types of events, perhaps we should use Prospective Search.
    auth_tokens = OAuthToken.query(OAuthToken.user_id=="701004", OAuthToken.application==APP_TWITTER, OAuthToken.token_nickname=="BigTwitter").fetch(1)
    if auth_tokens:
        try:
            twitter_post(auth_tokens[0], e, fb_event)
        except twitter.TwitterError as e:
            logging.error("Twitter Post Error: %s", e)
    else:
        logging.error("Could not find Mike's BigTwitter OAuthToken")
    auth_tokens = OAuthToken.query(OAuthToken.user_id=="701004", OAuthToken.application==APP_FACEBOOK).fetch(5)
    if auth_tokens:
        filtered_auth_tokens = [x for x in auth_tokens if x.token_nickname in ["1613128148918160", "1375421172766829", "110312662362915"]]
        if filtered_auth_tokens:
            auth_token = filtered_auth_tokens[0]
            result = facebook_post(auth_token, e, fb_event)
            if 'error' in result:
                logging.error("Facebook Post Error: %s", result)
            else:
                logging.info("Facebook result was %s", result)
        else:
            logging.error("Couldn't find good Facebook tokens to pubulish to: %s", auth_tokens)
    else:
        logging.error("Could not find a Facebook token")

def format_twitter_post(db_event, fb_event, handle=None):
    url = urls.fb_event_url(fb_event['info']['id'])
    title = fb_event['info']['name']
    city = db_event.actual_city_name

    start_time = dates.parse_fb_start_time(fb_event)
    #TODO(lambert): Some day, when we are doing more local relevant data, list the time here, and do it at the right time accounting for timezone offsets
    #if start_time.date() == datetime.date.today():
    #    datetime_string = start_time.strftime(TIME_FORMAT)
    #else:
    datetime_string = start_time.strftime(DATE_FORMAT)

    # twitter length is 22, so I use 23 to give buffer.
    # TODO(lambert): fetch help/configuration daily to find the current value
    # as described on https://dev.twitter.com/overview/t.co
    url_length = 23
    prefix = "%s: %s: " % (datetime_string, city)
    if handle:
        prefix = '%s %s' % (handle, prefix)        

    title_length = 140 - len(prefix) - len(u"… ") - url_length
    final_title = title[0:title_length]
    if final_title != title:
        final_title += u'…'
    return u"%s%s %s" % (prefix, final_title, url)

def twitter_post(auth_token, db_event, fb_event):
    t = twitter.Twitter(
        auth=twitter.OAuth(auth_token.oauth_token, auth_token.oauth_token_secret, consumer_key, consumer_secret))

    if db_event.latitude:
        latlong_kwargs = {'lat': db_event.latitude, 'long': db_event.longitude}
    else:
        latlong_kwargs = {}

    status = format_twitter_post(db_event, fb_event)
    t.statuses.update(status=status, **latlong_kwargs)

    description = fb_event['info'].get('description')
    twitter_handles = re.findall('\s@[A-za-z0-9_]+', description)
    twitter_handles = [x.strip() for x in twitter_handles if len(x) <= 1+15]
    for handle in twitter_handles:
        status = format_twitter_post(db_event, fb_event, handle=handle)
        t.statuses.update(status=status, **latlong_kwargs)

def facebook_post(auth_token, db_event, fb_event):
    link = urls.fb_event_url(fb_event['info']['id'])

    start_time = dates.parse_fb_start_time(fb_event)
    datetime_string = start_time.strftime('%s @ %s' % (DATE_FORMAT, TIME_FORMAT))

    post_values = {}
    #post_values['message'] = fb_event['info']['name']
    post_values['link'] = link#.replace('www.dancedeets.com', 'dev-dancedeets.com:8080')
    post_values['name'] = fb_event['info']['name'].encode('utf8')
    post_values['caption'] = datetime_string
    post_values['description'] = fb_event['info'].get('description', '').encode('utf8')
    cover = eventdata.get_largest_cover(fb_event)
    if cover:
        post_values['picture'] = cover['source']
    venue_id = fb_event['info'].get('venue', {}).get('id')
    if venue_id:
        post_values['place'] = venue_id
        # Can only tag people if there is a place tagged too
        if fb_event['info'].get('admins'):
            admin_ids = [x['id'] for x in fb_event['info']['admins']['data']]
            post_values['tags'] = ','.join(admin_ids)

    # At some point, set up feed targetting:
    #feed_targeting = {}
    #feed_targeting['cities'] = '' # int array
    #feed_targeting['countries'] = '', # two char country abbreviations
    #and 'regions' too?

    page_id = auth_token.token_nickname
    endpoint = '/v2.2/%s/feed' % page_id
    fb = fb_api.FBAPI(auth_token.oauth_token)
    result = fb.post(endpoint, None, post_values)
    return json.loads(result)


request_token_url = 'https://twitter.com/oauth/request_token'
access_token_url = 'https://twitter.com/oauth/access_token'
authorize_url = 'https://twitter.com/oauth/authorize'

APP_TWITTER = 'APP_TWITTER'
APP_FACEBOOK = 'APP_FACEBOOK' # a butchering of OAuthToken!
#...fb?
#...tumblr?

class OAuthToken(ndb.Model):
    user_id = ndb.StringProperty()
    token_nickname = ndb.StringProperty()
    application = ndb.StringProperty()
    temp_oauth_token = ndb.StringProperty()
    temp_oauth_token_secret = ndb.StringProperty()
    valid_token = ndb.BooleanProperty()
    oauth_token = ndb.StringProperty()
    oauth_token_secret = ndb.StringProperty()
    #search criteria? location? radius? search terms?
    #post on event find? post x hours before event? multiple values?


def twitter_oauth1(user_id, token_nickname):
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)

    # Step 1: Get a request token. This is a temporary token that is used for 
    # having the user authorize an access token and to sign the request to obtain 
    # said access token.

    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    request_token = dict(urlparse.parse_qsl(content))

    auth_tokens = OAuthToken.query(OAuthToken.user_id==str(user_id), OAuthToken.token_nickname==token_nickname, OAuthToken.application==APP_TWITTER).fetch(1)
    if auth_tokens:
        auth_token = auth_tokens[0]
    else:
        auth_token = OAuthToken()
    auth_token.user_id = str(user_id)
    auth_token.token_nickname = token_nickname
    auth_token.application = APP_TWITTER
    auth_token.temp_oauth_token = request_token['oauth_token']
    auth_token.temp_oauth_token_secret = request_token['oauth_token_secret']
    auth_token.put()

    # Step 2: Redirect to the provider. Since this is a CLI script we do not 
    # redirect. In a web application you would redirect the user to the URL
    # below.

    return "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])

#user comes to:
#/sign-in-with-twitter/?
#        oauth_token=NPcudxy0yU5T3tBzho7iCotZ3cnetKwcTIRlX0iwRl0&
#        oauth_verifier=uw7NjWHT6OJ1MpJOXsHfNxoAhPKpgI8BlYDhxEjIBY

def twitter_oauth2(oauth_token, oauth_verifier):
    auth_tokens = OAuthToken.query(OAuthToken.temp_oauth_token==oauth_token, OAuthToken.application==APP_TWITTER).fetch(1)
    if not auth_tokens:
        return None
    auth_token = auth_tokens[0]
    # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # URL you can request the access token the user has approved. You use the 
    # request token to sign this request. After this is done you throw away the
    # request token and use the access token returned. You should store this 
    # access token somewhere safe, like a database, for future use.
    token = oauth.Token(oauth_token,
        auth_token.temp_oauth_token_secret)
    token.set_verifier(oauth_verifier)
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))
    auth_token.oauth_token = access_token['oauth_token']
    auth_token.oauth_token_secret = access_token['oauth_token_secret']
    auth_token.valid_token = True
    auth_token.put()
    return auth_token


class LookupUserAccounts(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('accounts', cls.url('%s/accounts' % object_id)),
        ]
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid, object_id, 'OBJ_USER_ACCOUNTS')


def facebook_auth(fbl, page_uid):
    accounts = fbl.get(LookupUserAccounts, fbl.fb_uid, allow_cache=False)
    all_pages = accounts['accounts']['data']
    pages = [x for x in all_pages if x['id'] == page_uid]
    if not pages:
        raise ValueError("Failed to find page id in user's page permissions: %s" % page_uid)
    page = pages[0]
    print page
    page_token = page['access_token']

    auth_tokens = OAuthToken.query(OAuthToken.user_id==str(fbl.fb_uid), OAuthToken.token_nickname==str(page_uid), OAuthToken.application==APP_FACEBOOK).fetch(1)
    if auth_tokens:
        auth_token = auth_tokens[0]
    else:
        auth_token = OAuthToken()
    auth_token.user_id = str(fbl.fb_uid)
    auth_token.token_nickname = str(page_uid)
    auth_token.application = APP_FACEBOOK
    auth_token.valid_token = True
    auth_token.oauth_token = page_token
    auth_token.put()
    return auth_token

