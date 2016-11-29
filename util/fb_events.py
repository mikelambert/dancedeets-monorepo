def get_all_members_count(fb_event):
    data = fb_event.get('fql_info', {}).get('data')
    if data and data[0].get('all_members_count'):
        return data[0]['all_members_count']
    else:
        if 'info' in fb_event and fb_event['info'].get('invited_count'):
            return fb_event['info']['invited_count']
        else:
            return None

def is_public_ish(fb_event):
    # Don't allow SECRET events
    return not fb_event['empty'] and (
        is_public(fb_event) or
        (fb_event['info'].get('privacy', 'OPEN') == 'FRIENDS' and
         get_all_members_count(fb_event) >= 60) or
        (fb_event['info'].get('privacy', 'OPEN') == 'SECRET' and
         get_all_members_count(fb_event) >= 200) or
        (fb_event['info'].get('privacy', 'OPEN') == 'CLOSED' and
         get_all_members_count(fb_event) >= 200) or
        False
    )

def is_public(fb_event):
    return fb_event['info'].get('privacy', 'OPEN') == 'OPEN'
