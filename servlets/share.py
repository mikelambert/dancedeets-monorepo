import base_servlet

class ShareHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        self.display['share_url'] = 'http://www.dancedeets.com/?referral=%s' % self.user.fb_uid
        self.render_template('share')

