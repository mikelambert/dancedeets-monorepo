
import fb_api
from ..pubsub import OAuthToken
from ..pubsub import APP_FACEBOOK

import app
import base_servlet
from events import eventdata
from .. import pubsub

class LookupUserAccounts(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('accounts', cls.url('%s/accounts' % object_id)),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid or 'None', object_id, 'OBJ_USER_ACCOUNTS')


def facebook_auth(fbl, page_uid, country_filter):
    accounts = fbl.get(LookupUserAccounts, fbl.fb_uid, allow_cache=False)
    all_pages = accounts['accounts']['data']
    pages = [x for x in all_pages if x['id'] == page_uid]
    if not pages:
        all_page_ids = [x['id'] for x in all_pages]
        raise ValueError("Failed to find page id %s in user's page permissions: %s" % (page_uid, all_page_ids))
    page = pages[0]
    page_token = page['access_token']

    auth_tokens = OAuthToken.query(OAuthToken.user_id == fbl.fb_uid, OAuthToken.token_nickname == page_uid, OAuthToken.application == APP_FACEBOOK).fetch(1)
    if auth_tokens:
        auth_token = auth_tokens[0]
    else:
        auth_token = OAuthToken()
    auth_token.user_id = fbl.fb_uid
    auth_token.token_nickname = page_uid
    auth_token.application = APP_FACEBOOK
    auth_token.valid_token = True
    auth_token.oauth_token = page_token
    auth_token.time_between_posts = 5 * 60
    if country_filter:
        auth_token.country_filters += country_filter.upper()
    auth_token.put()
    return auth_token

@app.route('/facebook/page_start')
class FacebookPageSetupHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        page_uid = self.request.get('page_uid')
        country_filter = self.request.get('country_filter')
        if not page_uid:
            #TODO(lambert): Clean up
            self.response.write('Need page_uid parameter')
            return
        pubsub.facebook_auth(self.fbl, page_uid, country_filter)
        #TODO(lambert): Clean up
        self.response.write('Authorized!')

@app.route('/tools/facebook_post')
class FacebookPostHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        page_id = self.request.get('page_id')

        event_id = self.request.get('event_id')
        db_event = eventdata.DBEvent.get_by_id(event_id)
        auth_tokens = pubsub.OAuthToken.query(pubsub.OAuthToken.user_id==self.fb_uid, pubsub.OAuthToken.token_nickname==page_id).fetch(1)
        if auth_tokens:
            result = pubsub.facebook_post(auth_tokens[0], db_event)
            if 'error' in result:
                self.response.write(result)
            else:
                self.response.write('Success!')
