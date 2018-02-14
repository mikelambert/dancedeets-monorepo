#!/usr/bin/python

import json
import os
import urllib2

ids = set()
#for i in range(ord('a'), ord('z') + 1):
#    c = chr(i)
#    names = json.loads(urllib2.urlopen('https://points.worldsdc.com/lookup/autocomplete?q=%s' % c).read())
#    ids.update([x['wscid'] for x in names])

#ids = sorted(list(ids))

if not os.path.exists('wsdc_dancers'):
    os.makedirs('wsdc_dancers')


def get(id):
    filename = 'wsdc_dancers/%s.txt' % id
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


for id in range(17500):
    data = get(id)
    if not data:
        continue
    if data['type'] == 'dancer':
        if data['placements']:
            divisions = data['placements'].get('West Coast Swing', [])
            div_points = dict((x['division']['name'], x['total_points']) for x in divisions)
            good_division_names = {'All-Stars': 30, 'Champions': 10, 'Invitational': 10, 'Professional': 30}
            serious = False
            for div_name in good_division_names:
                if div_points.get(div_name, 0) > good_division_names[div_name]:
                    serious = True

            if serious:
                name = '%s %s' % (data['dancer']['first_name'], data['dancer']['last_name'])
                name = name.lower()
                print id, name, json.dumps(div_points)
