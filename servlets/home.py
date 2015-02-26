import base_servlet
from rankings import rankings
from search import search_base
from users import users

def get_location(fb_user):
    if fb_user['profile'].get('location'):
        facebook_location = fb_user['profile']['location']['name']
    else:
        facebook_location = None
    return facebook_location

class HomeHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def is_login_page(self):
        return True

    #TODO(lambert): move this into the same base / handler, so we don't do stupid redirects to /login
    def get(self):
        self.finish_preload()
        
        # If they're logged in, and have an account created, update and redirect
        if self.fb_uid:
            user = users.User.get_by_key_name(self.fb_uid)
            if user and not user.expired_oauth_token:
                location = ''
            else:
                location = ''
                # Treat them like a totally logged-out user since they have no user object yet
                self.fb_uid = None

        # Explicitly do not preload anything from facebook for this servlet
        # self.finish_preload()

        self.display['user_message'] = self.get_cookie('User-Message')

        city_rankings = rankings.get_thing_ranking(rankings.get_city_by_event_rankings(), rankings.LAST_MONTH)
        top_na_rankings = [x for x in city_rankings if 'United States' in x['key'] or 'Canada' in x['key'] or 'Mexico' in x['key']][:20]
        self.display['top_cities'] = [(x['key'], x['key'].split(', ')[0]) for x in top_na_rankings]
        # Do a better job of ranking cities/countries for these:
        self.display['top_european_countries'] = ['Czech Republic', 'Finland', 'France', 'Germany', 'Ireland', 'Italy', 'Norway', 'Poland', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom', 'Portugal']
        self.display['top_continents'] = ['Asia', 'Africa', 'Australia', 'South America']

        self.display['defaults'] = search_base.FrontendSearchQuery()
        self.display['defaults'].location = self.request.get('location')
        self.display['defaults'].keywords = self.request.get('keywords')
        self.display['defaults'].deb = self.request.get('deb')

        self.display['next'] = next
        self.render_template('onboard')
