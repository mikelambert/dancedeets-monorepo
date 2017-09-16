import sys

sys.path += ['lib/']

from py_ms_cognitive import PyMsCognitiveWebSearch

def bing_lucky(query):
    search_service = PyMsCognitiveWebSearch('***REMOVED***', query)
    first_fifty_result = search_service.search(limit=5, format='json') #1-50
    return first_fifty_result[0].name, first_fifty_result[0].display_url
