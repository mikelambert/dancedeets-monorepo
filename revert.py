#!/usr/bin/python

import commands
import logging
import re
import subprocess
import sys

logging.getLogger().setLevel(logging.INFO)


def run(cmd):
    logging.info('Running: %s', cmd)
    status, output = commands.getstatusoutput(cmd)
    if status:
        raise IOError('Error %s running command:\n%s:\n%s' % (status, cmd, output))
    return output


def get_versions():
    output = run('gcloud app modules list default')

    def split(l):
        return re.split(r'\s+', l)

    output_lines = output.split('\n')
    keys = split(output_lines[0])

    versions = []
    for line in output_lines[1:]:
        values = split(line)
        d = dict(zip(keys, values))
        if re.match(r'^\d+t\d+$', d['VERSION']):
            versions.append(d['VERSION'])
        if d['TRAFFIC_SPLIT'] == '1.0':
            live = d['VERSION']

    versions.sort()
    return versions, live


def get_previous_version(versions, live):
    new_version = versions.index(live)
    if new_version == 0:
        raise ValueError('No old versions to revert to, %s is the oldest version!' % live)
    prev_version = versions[new_version - 1]
    return prev_version

if len(sys.argv) > 1:
    target_version = sys.argv[1]
else:
    versions, live = get_versions()
    logging.info('Versions:')
    for v in versions:
        logging.info('%s  %s', v, v == live)
    target_version = get_previous_version(versions, live)

try:
    output = run('gcloud app modules start default --version=%s' % target_version)
except IOError as e:
    if 'already started' not in e.args[0]:
        raise

cmd = 'gcloud app modules set-default default --version=%s' % target_version
logging.info('Running: %s' % cmd)
# For some reason the 'yes | ...' never actually finishes. This actually does
p = subprocess.Popen(args=cmd.split(' '), stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = p.communicate(input='Y\n')
logging.info(stderr)
