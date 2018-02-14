#!/usr/bin/python
"""Grab all the top dancers from the WSDC, for use as keywords"""

import json
import os
import urllib2

import dancedeets

ids = set()

dirname = os.path.join(os.path.dirname(dancedeets.__file__), '..', '..', 'scrapers', 'wsdc_dancers')
print dirname
if not os.path.exists(dirname):
    os.makedirs(dirname)

show_points = False


def get(id):
    filename = os.path.join(dirname, '%s.txt' % id)
    if os.path.exists(filename):
        data_string = open(filename).read()
    else:
        try:
            data_string = urllib2.urlopen('https://points.worldsdc.com/lookup/find', 'num=%s' % id).read()
        except urllib2.HTTPError as e:
            if 'Not Found' in str(e):
                data_string = ''
        open(filename, 'w').write(data_string)
    if not data_string:
        return None
    data = json.loads(data_string)
    return data


LIMIT = 11100  # 17500

for id in range(LIMIT):
    data = get(id)
    if not data:
        continue
    if data['type'] == 'dancer':
        if data['placements']:
            name = '%s %s' % (data['dancer']['first_name'], data['dancer']['last_name'])
            name = name.lower()

            divisions = data['placements'].get('West Coast Swing', [])
            div_points = dict((x['division']['name'], x['total_points']) for x in divisions)
            good_division_names = {
                'All-Stars': 20,
                'Champions': 8,
                'Invitational': 8,
                'Professional': 20,
                'Advanced': 50,
            }
            serious = False
            for div_name in good_division_names:
                if div_points.get(div_name, 0) > good_division_names[div_name]:
                    serious = True

            if serious:
                if show_points:
                    print id, name, json.dumps(div_points)
                else:
                    print name
