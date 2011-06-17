#!/usr/bin/python

creator_tags = {}

for line in open('dbevents.txt').readlines():
    event_id, creator_id, style_tags = line.strip().split(';')
    style_tags_list = [x for x in style_tags.split(',') if not x.startswith('STYLE_')]
    if style_tags_list == ['']:
        continue # we need to delete these from the source data somehow
    creator_tags.setdefault(creator_id, set()).update(style_tags_list)

filename_map = {
    'CHOREO': 'choreo_auto_ids.txt',
    'FREESTYLE': 'freestyle_auto_ids.txt',
    'DANCE': 'dance_auto_ids.txt',
}

file_map = dict((k, open(v, 'w')) for (k, v) in filename_map.iteritems())

for creator_id, tags in creator_tags.iteritems():
    style_types = set(x.split('_')[0] for x in tags)
    stype_type = None
    if len(style_types) > 1:
        style_type = 'DANCE'
    else:
        style_type = list(style_types)[0]
    file_map[style_type].write('%s\n' % creator_id)

