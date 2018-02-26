import getpass
import os

directory = '/Users/%s/Dropbox/dancedeets-development/nlp/' % getpass.getuser()

TEST_IDS_PATH = os.path.join(directory, 'test_ids')

CACHE_PATH = os.path.join(directory, 'cached_events')
