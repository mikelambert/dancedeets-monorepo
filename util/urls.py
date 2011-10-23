def fb_event_url(eid):
    return 'http://www.dancedeets.com/events/redirect?event_id=%s' % eid

def raw_fb_event_url(eid):
    return 'http://www.facebook.com/event.php?eid=%s' % eid

def dd_admin_event_url(eid):
    return 'http://www.dancedeets.com/events/admin_edit?event_id=%s' % eid

def dd_admin_source_url(eid):
    return 'http://www.dancedeets.com/sources/admin_edit?source_id=%s' % eid

def fb_user_url(uid):
    return 'http://www.facebook.com/profile.php?id=%s' % uid

