#!/usr/bin/python

import json

filename = 'dist/img/favicons/manifest.json'

with open(filename) as f:
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

with open(filename, 'w') as f:
    f.write(json.dumps(manifest, indent=2))
