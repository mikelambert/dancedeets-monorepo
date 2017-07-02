import app
import base_servlet

from loc import names
from logic import mobile
from logic import sms
from util import country_dialing_codes

@app.route('/mobile_apps')
class MobileAppsHandler(base_servlet.BaseRequestHandler):

    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()

        action = self.request.get('action')
        if action == 'download':
            mobile_platform = mobile.get_mobile_platform(self.request.user_agent)
            if mobile_platform == mobile.MOBILE_IOS:
                self.redirect(mobile.IOS_URL)
            elif mobile_platform == mobile.MOBILE_KINDLE:
                self.render_page(error="Sorry, we do not support Amazon Kindles.")
            elif mobile_platform == mobile.MOBILE_ANDROID:
                self.redirect(mobile.ANDROID_URL)
            elif mobile_platform == mobile.MOBILE_WINDOWS_PHONE:
                self.render_page(error="Sorry, we do not support Windows Phones.")
            else:
                self.render_page(error="Could not detect the correct mobile app for your device. Please select the appropriate download button below.")
        else:
            self.render_page()

    def render_page(self, message=None, error=None):
        total_time = 10

        self.display['country_codes'] = sorted(country_dialing_codes.mapping.items())
        self.display['android_url'] = mobile.ANDROID_URL
        self.display['ios_url'] = mobile.IOS_URL
        self.display['total_time'] = total_time
        if message:
            self.display['messages'] = [message]
        if error:
            self.display['errors'] = [error]
        self.display['suppress_promos'] = True
        if self.request.get('prefix'):
            self.display['prefix'] = self.request.get('prefix')
        else:
            iso3166_country = self.request.headers.get("X-AppEngine-Country")
            full_country = names.get_country_name(iso3166_country)
            self.display['prefix'] = country_dialing_codes.mapping.get(full_country, '')
        self.display['phone'] = self.request.get('phone')
        self.render_template('mobile_apps')

    def post(self):
        self.finish_preload()
        action = self.request.get('action')
        if action == 'send_sms':
            prefix = self.request.get('prefix')
            phone = self.request.get('phone')
            if not prefix:
                self.render_page(error="Please select a country.")
                return
            if not phone:
                self.render_page(error="Please enter a phone number.")
                return
            try:
                sms.send_email_link('+' + prefix + phone.lstrip('0'))
            except sms.InvalidPhoneNumberException:
                self.render_page(error="You entered an invalid phone number.")
                return

            self.render_page(message="Thank you, your SMS should be arriving shortly. Just open the link on your phone to download the DanceDeets app.")
