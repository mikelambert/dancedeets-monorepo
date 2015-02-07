import collections
import datetime

from loc import gmaps_api
from loc import formatting
from logic import event_locations

def group_results_by_date(results):
    year_months = collections.defaultdict(lambda: collections.defaultdict(lambda: []))
    for result in results:
        start_month = result.start_time.date().replace(day=1)
        end_month = result.end_time.date().replace(day=1)
        cur_month = start_month
        while cur_month <= end_month:
            year_months[cur_month.year][cur_month.month].append(result)
            cur_month = datetime.date(cur_month.year + (cur_month.month / 12), ((cur_month.month % 12) + 1), 1)
    return year_months


def group_results_by_location(results):
    location_map = collections.defaultdict(lambda: [])
    location_infos = [event_locations.LocationInfo(x.fb_event) for x in results]
    geocodes = [gmaps_api.get_geocode(address=x.actual_city()) for x in location_infos]
    addresses = formatting.format_geocodes(geocodes)
    for address, result in zip(addresses, results):
        location_map[address].append(result)
    return location_map
