import base_servlet
import fb_api
from events import eventdata
from logic import pubsub


class TwitterOAuthStartHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        nickname = self.request.get('token_nickname')
        if not nickname:
            #TODO(lambert): Clean up
            self.response.write('Need token_nickname parameter')
            return
        country_filter = self.request.get('country_filter')
        url = pubsub.twitter_oauth1(self.fb_uid, nickname, country_filter)
        self.redirect(url)

class TwitterOAuthCallbackHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        oauth_token = self.request.get('oauth_token')
        oauth_verifier = self.request.get('oauth_verifier')
        auth_token = pubsub.twitter_oauth2(oauth_token, oauth_verifier)
        if auth_token:
            self.redirect('/twitter/oauth_success?nickname=' + auth_token.token_nickname)
        else:
            self.redirect('/twitter/oauth_failure')

class TwitterOAuthSuccessHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        #TODO(lambert): Clean up
        self.response.write('Authorized!')

class TwitterOAuthFailureHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        #TODO(lambert): Clean up
        self.response.write("Failure, couldn't find auth token conection!")

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

class FacebookPostHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        page_id = self.request.get('page_id')

        event_id = self.request.get('event_id')
        fb_event = self.fbl.get(fb_api.LookupEvent, event_id)

        db_event = eventdata.DBEvent.get_by_key_name(event_id)
        auth_tokens = pubsub.OAuthToken.query(pubsub.OAuthToken.user_id==self.fb_uid, pubsub.OAuthToken.token_nickname==page_id).fetch(1)
        if auth_tokens:
            result = pubsub.facebook_post(auth_tokens[0], db_event, fb_event)
            if 'error' in result:
                self.response.write(result)
            else:
                self.response.write('Success!')
