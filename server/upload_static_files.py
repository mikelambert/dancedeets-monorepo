#!/usr/bin/python

import getpass
from itertools import chain
import json
import os
import subprocess


def get_static_files():
    manifest = json.loads(open('dist/manifest.json').read())
    source_files = manifest.values()
    source_files = [os.path.abspath(os.path.join('dist/js', x)) for x in source_files]
    new_source_files = list(chain.from_iterable([x, '%s.map' % x] for x in source_files))
    return set(new_source_files)


all_static_files = get_static_files()


def cleanup(path):
    for filename in os.listdir(path):
        abs_filename = os.path.abspath(os.path.join(path, filename))
        if abs_filename not in all_static_files:
            print 'Removing %s' % abs_filename
            os.remove(abs_filename)


cleanup('dist/js')
cleanup('dist/css/')

# -m run copies in parallel
# -P preserve mtimes
# -n don't overwrite existing files
# -z compress files on upload
# -R recursive
cmd = '/Users/%s/google-cloud-sdk/bin/gsutil -m cp -P -n -z css,js,json,map -R dist/{js,css,img,fonts,*.json} gs://dancedeets-static/' % getpass.getuser(
)
subprocess.check_output(cmd, shell=True)
