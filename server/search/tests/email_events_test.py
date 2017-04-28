import os
import socket
import subprocess
import tempfile
import time

import fb_api
from search import email_events
from test_utils import fixtures
from test_utils import unittest
import render_server

def get_free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def wait_for_string_in_file(search_string, f):
    while True:
        f.seek(0)
        stdout = f.read()
        if search_string in stdout:
            break
        time.sleep(1)

class TestSearch(unittest.TestCase):
    def setUp(self):
        super(TestSearch, self).setUp()
        self.old_port = render_server.PORT
        render_server.PORT = get_free_port()
        if os.environ.get('TRAVIS'):
            node = '/nodejs/bin/node'
        else:
            node = '/usr/local/bin/node'
        args = [node, '../runNode.js', './node_server/renderServer.js' ,'--port', unicode(render_server.PORT)]
        output = tempfile.TemporaryFile()
        self.server = subprocess.Popen(args, stdout=output, stderr=subprocess.STDOUT)
        address = '127.0.0.1:%s' % render_server.PORT
        wait_for_string_in_file(address, output)

    def tearDown(self):
        render_server.PORT = self.old_port
        self.server.terminate()
        super(TestSearch, self).tearDown()

    def runTest(self):
        user = fixtures.create_user()
        event = fixtures.create_event()
        fixtures.index_events(self.testbed)

        fbl = user.get_fblookup()
        # Fetch it now so it's cached before email_for_user accesses it
        fbl.get(fb_api.LookupUser, user.fb_uid)

        message = email_events.email_for_user(user, fbl, should_send=False)
        self.assertTrue(message, "Emailer did not email the user")
        self.assertIn('http://www.dancedeets.com/events/%s/' % event.fb_event_id, message['html'])

