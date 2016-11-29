import logging

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
    if fb_event['empty']:
        return False

    if is_public(fb_event):
        return True

    members_count = get_all_members_count(fb_event)

    event_type = fb_event['info'].get('type')
    if event_type:
        # event_type = {private, public, group, community}
        if event_type in ['private', 'group', 'community']:
            logging.error('Event %s has %s type with %s members', fb_event['info']['id'], event_type, members_count)
            if members_count >= 200:
                return True
        else:
            logging.error('Unknown event type: %s', event_type)
    else:
        #bwcompat
        privacy = fb_event['info'].get('privacy', 'OPEN')

        return (
            (privacy == 'FRIENDS' and members_count >= 60) or
            (privacy == 'SECRET' and members_count >= 200) or
            (privacy == 'CLOSED' and members_count >= 200) or
            False
        )

def is_public(fb_event):
    event_type = fb_event['info'].get('type')
    if event_type:
        return event_type == 'public'
    else:
        #bwcompat
        return fb_event['info'].get('privacy', 'OPEN') == 'OPEN'
