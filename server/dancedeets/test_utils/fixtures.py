import base64
import datetime
import pickle

from google.appengine.ext import testbed

from dancedeets.events import eventdata
from dancedeets.events import event_updates
from dancedeets.event_scraper import add_entities
from dancedeets import fb_api
from dancedeets.search import search
from dancedeets.users import users
from dancedeets.users import user_creation


def create_event(event_id='1000001', start_time=None, location='NYC'):
    if not start_time:
        start_time = datetime.datetime.now()
    fields_str = '%2C'.join(fb_api.OBJ_EVENT_FIELDS)
    base_url = '/v2.9/%s' % event_id
    url = '%s?fields=%s' % (base_url, fields_str)

    picture_url = '%s/picture?redirect=false&type=large' % base_url

    wall_fields_str = '%2C'.join(fb_api.OBJ_EVENT_WALL_FIELDS)
    wall_url = '%s/feed?fields=%s&limit=1000' % (base_url, wall_fields_str)

    fb_api.FBAPI.results.update({
        url: (200, {
            "name": "Event Title",
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S-0400"),
            "id": event_id,
        }),
        '/v2.9/?fields=images%2Cwidth%2Cheight&ids=%7Bresult%3Dinfo%3A%24.cover.id%7D': (
            400, {
                'error': {
                    'message': 'Cannot specify an empty identifier',
                    'code': 2500,
                    'type': 'OAuthException'
                }
            }
        ),
        picture_url: (200, {
            "data": {
                "url": "test: image url",
            }
        }),
        wall_url: (200, {
            'data': []
        })
    })

    fbl = fb_api.FBLookup(None, None)
    fb_event = fbl.get(fb_api.LookupEvent, event_id)
    event = add_entities.add_update_event(fb_event, fbl, override_address=location)
    return event


def create_web_event(event_id='tokyo-dance-life:1000001', json_body={}):
    event = eventdata.DBEvent(id=event_id)
    event.creating_method = eventdata.CM_WEB_SCRAPE
    full_json_body = {
        'start_time': '2020-10-10T00:00:00Z',
        'end_time': '2020-10-10T12:00:00Z',
        'name': 'name',
        'description': 'description',
        'photo': None,
        'location_address': 'Tokyo, Japan',
    }
    full_json_body.update(json_body)
    event_updates.update_and_save_web_events([(event, full_json_body)])
    return event


def index_events(testbed_instance):
    search.construct_fulltext_search_index()

    taskq = testbed_instance.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
    tasks = taskq.GetTasks("default")
    taskq.FlushQueue("default")
    while tasks:
        for task in tasks:
            (func, args, opts) = pickle.loads(base64.b64decode(task["body"]))
            func(*args)
        tasks = taskq.GetTasks("default")
    taskq.FlushQueue("default")


def create_user(user_id='701004', access_token='Access Token', access_token_expires=None, location='NYC'):
    fields_str = '%2C'.join(fb_api.OBJ_USER_FIELDS)
    base_url = '/v2.9/%s' % user_id
    url = '%s?fields=%s' % (base_url, fields_str)

    fb_api.FBAPI.results.update({
        url: (200, {
            'id': user_id,
            'name': 'Test User',
            'email': 'test@test.com',
            'timezone': -8,
        }),
        '%s/events?since=yesterday&fields=id,rsvp_status&limit=3000' % base_url: (200, {
            "data": {},
        }),
        '%s/friends' % base_url: (200, {}),
        '%s/permissions' % base_url: (200, {}),
    })

    existing_user = users.User.get_by_id(user_id)
    assert not existing_user, "Found user: %s" % existing_user

    if not access_token_expires:
        access_token_expires = datetime.datetime.now() + datetime.timedelta(days=60)

    client = 'test'

    fbl = fb_api.FBLookup(None, None)
    fb_user = fbl.get(fb_api.LookupUser, user_id)

    ip = '127.0.0.1'
    user = user_creation.create_user_with_fbuser(
        user_id, fb_user, access_token, access_token_expires, location, ip, send_email=True, client=client
    )
    return user
