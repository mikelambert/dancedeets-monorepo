#!/usr/bin/python

import json

filename = 'dist/img/favicons/manifest.json'

f = open(filename)
manifest = json.loads(f.read())
manifest.update({
  "short_name": "DanceDeets",
  "prefer_related_applications": True,
  "related_applications": [
    {
    "platform": "play",
    "id": "com.dancedeets.android",
    },
  ],
})

open(filename, 'w').write(json.dumps(manifest, indent=2))
