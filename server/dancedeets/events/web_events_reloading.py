import json
import urllib


def fetch_bboy_lite(url):
    url = url
    data = urllib.urlopen(url).read()
    json_data = json.loads(data)
    # massage json_data
    return json_data


def reload_bboy_lite_jam(web_event):
    fetch_bboy_lite('http://jamyo.jamyooo.com/Lite/Jam/jam_detail?id=%s' % web_event.namespaced_id)
    return web_event.web_event


def reload_bboy_lite_course(web_event):
    fetch_bboy_lite('https://jamyo.jamyooo.com/Lite/Course/course_details?course_id=%s' % web_event.namespaced_id)
    return web_event.web_event
