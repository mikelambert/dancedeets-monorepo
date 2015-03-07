import sys

from .. import gmaps_api

_real_backend = None

def activate():
    global _real_backend
    _real_backend = gmaps_api.gmaps_backend
    gmaps_api.gmaps_backend = sys.modules[__name__]

def deactivate():
    global _real_backend
    gmaps_api.gmaps_backend = _real_backend

def fetch_raw(**kwargs):
    #TODO(lambert): expand this out, as necessary
    return {
        "status": "OK",
        "results": [
            {
                "geometry": {
                    "location_type": "APPROXIMATE",
                    "bounds": {
                        "northeast": {
                            "lat": 40.9152556,
                            "lng": -73.7002721
                        },
                        "southwest": {
                            "lat": 40.4913699,
                            "lng": -74.2590899
                        }
                    },
                    "viewport": {
                        "northeast": {
                            "lat": 40.9152556,
                            "lng": -73.7002721
                        },
                        "southwest": {
                            "lat": 40.4913699,
                            "lng": -74.2590899
                        }
                    },
                    "location": {
                        "lat": 40.7127837,
                        "lng": -74.0059413
                    }
                },
                "address_components": [
                    {
                        "long_name": "New York",
                        "types": [
                            "locality",
                            "political"
                        ],
                        "short_name": "NY"
                    },
                    {
                        "long_name": "Kings County",
                        "types": [
                            "administrative_area_level_2",
                            "political"
                        ],
                        "short_name": "Kings County"
                    },
                    {
                        "long_name": "New York",
                        "types": [
                            "administrative_area_level_1",
                            "political"
                        ],
                        "short_name": "NY"
                    },
                    {
                        "long_name": "United States",
                        "types": [
                            "country",
                            "political"
                        ],
                        "short_name": "US"
                    }
                ],
                "place_id": "ChIJOwg_06VPwokRYv534QaPC8g",
                "formatted_address": "New York, NY, USA",
                "types": [
                    "locality",
                    "political"
                ]
            }
        ]
    }
