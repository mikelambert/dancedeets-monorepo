import re

import app
import base_servlet
import fb_api
from profiles import profile
from profiles import tags


class BaseProfileHandler(base_servlet.BaseRequestHandler):
    def initialize(self, request, response):
        super(BaseProfileHandler, self).initialize(request, response)
        self.profile_username = re.match(r'/profile/([^/]+)', self.request.path).group(1)
        self.fbl.request(fb_api.LookupProfile, self.profile_username)
        self.display['profile_username'] = self.profile_username

    def get_profile_user(self):
        return self.fbl.fetched_data(fb_api.LookupProfile, self.profile_username)


@app.route('/profile/[^/]*')
class ProfileHandler(BaseProfileHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()

        fb_profile = self.get_profile_user()
        fb_profile_uid = fb_profile['profile']['id']

        user_profile = profile.Profile.get_by_key_name(fb_profile_uid)

        primary_name = fb_profile['profile']['name']
        if user_profile:
            primary_name = user_profile.dance_names[0]
            self.display['dance_names'] = user_profile.dance_names
        self.display['primary_name'] = primary_name
        self.display['real_name'] = fb_profile['profile']['name']

        self.display['owner'] = (self.fb_user and self.fb_user['profile']['id'] == fb_profile_uid)

        video_tags = tags.ProfileVideoTag.gql('where fb_uid=:fb_uid', fb_uid=fb_profile_uid).fetch(100)

        self.display['video_tags'] = video_tags

        return self.render_template('profile')


@app.route('/profile/[^/]*/add_tag')
class ProfileAddTagHandler(BaseProfileHandler):
    def post(self):
        self.finish_preload()
        fb_profile = self.get_profile_user()
        fb_profile_uid = fb_profile['profile']['id']
        video_site, video_id = tags.parse_url(self.request.get('video_url'))
        video_tag = tags.ProfileVideoTag(fb_uid=fb_profile_uid, video_site=video_site, video_id=video_id)
        video_tag.put()
