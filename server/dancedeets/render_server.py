import hashlib
import json
import logging
import os
import requests
import time

# We want to always use the render server, since we may be rendering things that we aren't sending clientside code to render
RENDER = True
PORT = 8090
RENDER_URL = 'http://localhost:%s/render'
RENDER_MJML_URL = 'http://localhost:%s/mjml-render'


class ComponentSourceFileNotFound(Exception):
    pass


class RenderedComponent(object):
    def __init__(self, markup, head, props):
        self.markup = markup
        self.head = head
        self.props = props
        self.error = None

    def __str__(self):
        return self.markup

    def __unicode__(self):
        return str(self.markup)


class RenderException(Exception):
    pass


class MjmlRenderException(RenderException):
    pass


def render_jsx(template_name, props=None, static_html=False):
    path = os.path.abspath(os.path.join('dist/js-server/', template_name))

    if props is not None:
        serialized_props = json.dumps(props)
    else:
        serialized_props = None

    empty_response = RenderedComponent('', None, serialized_props)

    if not os.path.exists(path):
        # Gracefully handle missing server-side bundle - client-side will render instead
        logging.warning('Server-side React bundle not found: %s - falling back to client-side rendering', path)
        empty_response.error = 'Server-side bundle not found: {}'.format(path)
        return empty_response

    url = RENDER_URL % PORT

    if props is not None:
        serialized_props = json.dumps(props)
    else:
        serialized_props = None

    empty_response = RenderedComponent('', None, serialized_props)
    if not RENDER:
        return empty_response

    options = {
        'path': path,
        'serializedProps': serialized_props,
        'toStaticMarkup': static_html,
    }
    serialized_options = json.dumps(options)
    options_hash = hashlib.sha1(serialized_options.encode('utf-8')).hexdigest()

    all_request_headers = {'content-type': 'application/json'}

    start = time.time()
    try:
        res = requests.post(url, data=serialized_options, headers=all_request_headers, params={'hash': options_hash})
    except requests.ConnectionError:
        empty_response.error = 'Could not connect to render server at {}'.format(url)
        return empty_response
    finally:
        logging.info('Rendering react template %s took %0.3f seconds', template_name, time.time() - start)

    if res.status_code != 200:
        empty_response.error = 'Unexpected response from render server at {} - {}: {}'.format(url, res.status_code, res.text)
        return empty_response

    obj = res.json()
    markup = obj.get('markup', None)
    err = obj.get('error', None)

    if err:
        if 'message' in err and 'stack' in err:
            empty_response.error = 'Message: {}\n\nStack trace: {}'.format(err['message'], err['stack'])
            return empty_response
        empty_response.error = err
        return empty_response

    if markup is None:
        empty_response.error = 'Render server failed to return markup. Returned: {}'.format(obj)
        return empty_response

    return RenderedComponent(markup, obj.get('head', None), serialized_props)


def render_mjml(mjml):
    url = RENDER_MJML_URL % PORT

    options = {
        'mjml': mjml,
    }
    serialized_options = json.dumps(options)

    all_request_headers = {'content-type': 'application/json'}

    try:
        res = requests.post(
            url,
            data=serialized_options,
            headers=all_request_headers,
        )
    except requests.ConnectionError:
        error = 'Could not connect to render server at {}'.format(url)
        raise MjmlRenderException(error)

    if res.status_code != 200:
        error = 'Unexpected response from render server at {} - {}: {}'.format(url, res.status_code, res.text)
        raise MjmlRenderException(error)

    obj = res.json()
    html = obj.get('html', None)
    return html
