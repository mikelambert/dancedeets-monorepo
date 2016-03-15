import base64
import datetime
import pickle

from google.appengine.ext import testbed

from event_scraper import add_entities
import fb_api
from search import search
from users import users
from users import user_creation

def create_event(event_id='1000001', start_time=None, location='NYC'):
    if not start_time:
        start_time = datetime.datetime.now()
    fields_str = '%2C'.join(fb_api.OBJ_EVENT_FIELDS)
    base_url = '/v2.2/%s' % event_id
    url = '%s?fields=%s' % (base_url, fields_str)

    picture_url = '%s/picture?redirect=false&type=large' % base_url

    fb_api.FBAPI.results.update({
            url:
                (200, {
                    "name": "Event Title",
                    "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S-0400"),
                    "id": event_id,
                }),
            '/?fields=images&ids=%7Bresult%3Dinfo%3A%24.cover.cover_id%7D':
                (400, {'error': {'message': 'Cannot specify an empty identifier', 'code': 2500, 'type': 'OAuthException'}}),
            picture_url:
                (200, {
                    "data": {
                        "url": "test image url",
                    }
                }),
    })


    fbl = fb_api.FBLookup(None, None)
    fb_event = fbl.get(fb_api.LookupEvent, event_id)
    event = add_entities.add_update_event(fb_event, fbl, override_address=location)
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
    base_url = '/v2.2/%s' % user_id
    url = '%s?fields=%s' % (base_url, fields_str)

    fb_api.FBAPI.results.update({
        url: (200, {
            'id': user_id,
            'name': 'Test User',
            'email': 'test@test.com'
        }),
        '%s/events?since=yesterday&fields=id,rsvp_status' % base_url: (200, {
            "data": {
            },
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

    user = user_creation.create_user_with_fbuser(user_id, fb_user, access_token, access_token_expires, location, send_email=True, client=client)
    return user
