import base_servlet
from logic import mobile
from logic import sms



IOS_URL = 'https://itunes.apple.com/us/app/dancedeets/id955212002?mt=8'
ANDROID_URL = 'https://play.google.com/store/apps/details?id=com.dancedeets.android'

class MobileAppsHandler(base_servlet.BaseRequestHandler):

    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()

        action = self.request.get('action')
        if action == 'download':
            mobile_platform = mobile.get_mobile_platform(self.request.user_agent)
            if mobile_platform == mobile.MOBILE_IOS:
                self.redirect(IOS_URL)
                handled = True
            elif mobile_platform == mobile.MOBILE_KINDLE:
                self.render_page(error="Sorry, we do not support Amazon Kindles.")
            elif mobile_platform == mobile.MOBILE_ANDROID:
                self.redirect(ANDROID_URL)
                handled = True
            elif mobile_platform == mobile.MOBILE_WINDOWS_PHONE:
                self.render_page(error="Sorry, we do not support Windows Phones.")
                handled = False
            else:
                self.render_page(error="Could not detect the correct mobile app for your device. Please select the appropriate download button below.")
        else:
            self.render_page()

    def render_page(self, message=None, error=None):
        self.display['android_url'] = ANDROID_URL
        self.display['ios_url'] = IOS_URL
        if message:
            self.display['messages'] = [message]
        if error:
            self.display['errors'] = [error]
        self.display['suppress_promos'] = True
        self.render_template('mobile_apps')

    def post(self):
        self.finish_preload()
        action = self.request.get('action')
        if action == 'send_sms':
            phone = self.request.get('phone')
            sms.send_email_link(phone)
            self.render_page(message="Thank you, your SMS should be arriving shortly. Just open the link on your phone to download the DanceDeets app.")
