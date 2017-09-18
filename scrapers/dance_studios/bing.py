import sys

sys.path += ['lib/']

from py_ms_cognitive import PyMsCognitiveWebSearch

from dancedeets import keys

def bing_lucky(query):
    search_service = PyMsCognitiveWebSearch(keys.get('bing_api_key'), query)
    first_fifty_result = search_service.search(limit=10, format='json') #1-50
    return [(x.name, x.display_url) for x in first_fifty_result]
