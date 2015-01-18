import base_servlet
from logic import pubsub

class TwitterOAuthStartHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        url = pubsub.twitter_oauth1(self.fb_uid, 'Post to Twitter')
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
        self.response.write('Authorized!')
        #pubsub.authed_twitter_post(auth_token, None, None)

class TwitterOAuthFailureHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        self.response.write("Failure, couldn't find auth token conection!")
        #pubsub.authed_twitter_post(auth_token, None, None)
