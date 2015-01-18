import base_servlet
from logic import pubsub

class TwitterOAuthStartHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        nickname = self.request.get('token_nickname')
        if not nickname:
            #TODO(lambert): Clean up
            self.response.write('Need token_nickname parameter')
            return
        url = pubsub.twitter_oauth1(self.fb_uid, nickname)
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
        #pubsub.authed_twitter_post(auth_token, None, None)

class TwitterOAuthFailureHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        #TODO(lambert): Clean up
        self.response.write("Failure, couldn't find auth token conection!")
        #pubsub.authed_twitter_post(auth_token, None, None)
