def fb_event_url(eid):
    return 'http://www.dancedeets.com%s' % fb_relative_event_url(eid)

def fb_relative_event_url(eid):
    return '/events/%s/' % str(eid)

def raw_fb_event_url(eid):
    return 'http://www.facebook.com/events/%s/' % str(eid)

def dd_admin_event_url(eid):
    return 'http://www.dancedeets.com/events/admin_edit?event_id=%s' % eid

def dd_admin_source_url(eid):
    return 'http://www.dancedeets.com/sources/admin_edit?source_id=%s' % eid

def fb_event_image_url(eid, size='large'):
    return 'https://graph.facebook.com/%s/picture?type=%s' % (eid, size)
