import site
site.addsitedir('lib-local')

import dateparser
import datetime
import json
import os
import re
import urllib
from . import namespaces

urls = {
    namespaces.CHINA_JWJAM_JAM: 'http://jamyo.jamyooo.com/Lite/Jam/jam_detail?id=%s',
    namespaces.CHINA_JWJAM_COURSE: 'http://jamyo.jamyooo.com/Lite/Course/course_details?course_id=%s',
}


def fetch_jwjam(namespace, id):
    url = urls[namespace] % id

    typename = 'jam' if namespace == namespaces.CHINA_JWJAM_JAM else 'course'
    json_filename = os.path.join(os.path.dirname(__file__), '../../../scrapers/bboylite/download-%s/%s.json' % (typename, id))
    if os.path.exists(json_filename):
        data = open(json_filename).read()
    else:
        data = urllib.urlopen(url).read()
    try:
        json_data = json.loads(data)['data']
    except ValueError:
        return None

    # Throw our our most egregiously-fake data fetches
    if not json_data['location']:
        return None
    phone = (json_data['phone'] or '').replace('-', '')
    if phone and len(phone) != 11:
        return None
    if json_data['title'] == '':
        return None
    if json_data['startDate'] == '0000-00-00 00:00:00':
        return None
    # set on jwjam-course
    if json_data.get('isTest'):
        return None

    item = {}
    item['country'] = 'CN'
    item['namespace'] = namespace
    item['namespaced_id'] = json_data['id']
    item['name'] = json_data['title']

    # set on jwjam-jam
    item['description'] = json_data.get('content') or ''
    if json_data['phone']:
        item['description'] += 'Phone Number: %s\n\n%s' % (json_data['phone'], item['description'])
    item['photo'] = json_data['pic']
    item['photo'] = re.sub(r'\?.*$', '', item['photo'])

    # Save the raw data, for use later if desired
    item['raw'] = json_data
    # TODO: handle all images in json_data['jam_gallery'], so they can be proxied correctly

    item['start_time'] = json_data['startDate']
    end_date = json_data['endDate']

    if end_date and end_date != '0000-00-00 00:00:00':
        item['end_time'] = end_date
    else:
        item['end_time'] = item['start_time']

    if not re.match(r'^\d+\.\d+,\d+\.\d+$', json_data['location']):
        return None

    location_parts = [float(x) for x in json_data['location'].split(',')]
    item['latitude'] = location_parts[1]
    item['longitude'] = location_parts[0]

    item['location_address'] = json_data['address']
    item['location_name'] = json_data['address']

    # Only return our item if it has 'good' data
    if item['name'] and item['start_time'] and item['photo']:
        return item
    else:
        return None


def fetch_jwjam_jam(web_event):
    item = fetch_jwjam(namespaces.CHINA_JWJAM_JAM, web_event.namespaced_id)
    return item or web_event.web_event


def fetch_jwjam_course(web_event):
    item = fetch_jwjam(namespaces.CHINA_JWJAM_COURSE, web_event.namespaced_id)
    return item or web_event.web_event
