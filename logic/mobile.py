IOS_URL = 'https://itunes.apple.com/us/app/dancedeets/id955212002?mt=8'
ANDROID_URL = 'https://play.google.com/store/apps/details?id=com.dancedeets.android'

MOBILE_IOS = 'MOBILE_IOS'
MOBILE_KINDLE = 'MOBILE_KINDLE'
MOBILE_ANDROID = 'MOBILE_ANDROID'
MOBILE_WINDOWS_PHONE = 'MOBILE_WINDOWS_PHONE'

def get_mobile_platform(user_agent):
    if not user_agent:
        user_agent = 'Unknown'
    user_agent = user_agent.lower()
    if 'iphone' in user_agent or 'ipod' in user_agent or 'ipad' in user_agent:
        return MOBILE_IOS
    elif 'silk/' in user_agent:
        return MOBILE_KINDLE
    elif 'android' in user_agent:
        return MOBILE_ANDROID
    elif 'windows nt' in user_agent and 'touch' in user_agent:
        return MOBILE_WINDOWS_PHONE
    else:
        return None
