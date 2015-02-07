import base_servlet
from logic import mobile
from logic import sms
from util import country_dialing_codes

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
            elif mobile_platform == mobile.MOBILE_KINDLE:
                self.render_page(error="Sorry, we do not support Amazon Kindles.")
            elif mobile_platform == mobile.MOBILE_ANDROID:
                self.redirect(ANDROID_URL)
            elif mobile_platform == mobile.MOBILE_WINDOWS_PHONE:
                self.render_page(error="Sorry, we do not support Windows Phones.")
            else:
                self.render_page(error="Could not detect the correct mobile app for your device. Please select the appropriate download button below.")
        else:
            self.render_page()

    def render_page(self, message=None, error=None):
        total_time = 10
        self.display['country_codes'] = sorted(country_dialing_codes.mapping.items())
        self.display['total_time'] = total_time
        self.display['walkout_animation'] = self.get_walkout_animation(total_time, -1000)
        self.display['android_url'] = ANDROID_URL
        self.display['ios_url'] = IOS_URL
        if message:
            self.display['messages'] = [message]
        if error:
            self.display['errors'] = [error]
        self.display['suppress_promos'] = True
        self.display['prefix'] = self.request.get('prefix')
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
            try:
                sms.send_email_link(phone)
            except sms.InvalidPhoneNumberException:
                self.render_page(error="You entered an invalid phone number.")
                return

            self.render_page(message="Thank you, your SMS should be arriving shortly. Just open the link on your phone to download the DanceDeets app.")

    def get_walkout_animation(self, total_time, total_distance):
        jumps = int(total_time / 0.5)
        if jumps * 0.5 != total_time:
            raise ValueError("total_time(%s) must be multiple of 0.5" % total_time)
        loop_pct = 100.0 / jumps
        half_loop_pct = loop_pct / 2

        jump_distance = total_distance / jumps

        stages = []
        for i in range(jumps):
            this_loop_pct = i*loop_pct
            this_half_loop_pct = this_loop_pct + half_loop_pct
            this_distance = i*jump_distance
            animation_stage = """
            %(half_loop_pct)s%% {
                left: %(distance)spx;
            }
            %(loop_pct)s%% {
                left: %(distance)spx;
                -webkit-animation-timing-function: linear;
                animation-timing-function: linear;
            }
            """ % dict(half_loop_pct=this_half_loop_pct, loop_pct=this_loop_pct, distance=this_distance)
            stages.append(animation_stage)

        stages.append("""
            100%% {
                left: %(distance)spx;
            }
        """ % dict(distance=total_distance))
        keyframes = ''.join(stages)
        animations = "@-webkit-keyframes walkOut {%s}\n@keyframes walkOut {%s}" % (keyframes, keyframes)
        return animations
