import sys

sys.path += ['lib/']

from py_ms_cognitive import PyMsCognitiveWebSearch

def bing_lucky(query):
    search_service = PyMsCognitiveWebSearch('***REMOVED***', query)
    first_fifty_result = search_service.search(limit=3, format='json') #1-50
    return [(x.name, x.display_url) for x in first_fifty_result]
