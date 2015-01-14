MOBILE_IOS = 'MOBILE_IOS'
MOBILE_KINDLE = 'MOBILE_KINDLE'
MOBILE_ANDROID = 'MOBILE_ANDROID'
MOBILE_WINDOWS_PHONE = 'MOBILE_WINDOWS_PHONE'

def get_mobile_platform(user_agent):
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
