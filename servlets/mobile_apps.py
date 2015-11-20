import app
import base_servlet
from logic import mobile
from logic import sms
from util import abbrev
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
        self.display['walkout_animation'] = self.get_walkout_animation(total_time, -1000)
        if message:
            self.display['messages'] = [message]
        if error:
            self.display['errors'] = [error]
        self.display['suppress_promos'] = True
        if self.request.get('prefix'):
            self.display['prefix'] = self.request.get('prefix')
        else:
            iso3166_country = self.request.headers.get("X-AppEngine-Country")
            full_country = abbrev.countries_abbrev2full.get(iso3166_country, '')
            if ', ' in full_country:
                parts = full_country.split(', ')
                if len(parts) == 2:
                    full_country = '%s, %s' % (parts[1], parts[0])
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
