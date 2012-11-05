import httplib2
import os.path
import webapp2

from oauth2client.appengine import oauth2decorator_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '../client_secrets.json')

http = httplib2.Http(memcache)
decorator = oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    'https://www.googleapis.com/auth/prediction',
    'Fill out %s' % CLIENT_SECRETS)

class OAuthSetupHandler(webapp2.RequestHandler):
  @decorator.oauth_required
  def get(self):
    user = users.get_current_user()
    try:
      http = decorator.http()
      self.response.out.write('oauth set up for user id %r!' % user.user_id())
    except AccessTokenRefreshError, e:
      self.response.out.write('oauth error! %s' % e)


application = webapp2.WSGIApplication(
    [
     ('/oauth_setup', OAuthSetupHandler),
    ],
    debug=True)

def main():
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
