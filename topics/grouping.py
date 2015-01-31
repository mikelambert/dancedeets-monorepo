import collections

import locations
from logic import event_locations

def group_results_by_date(results):
    year_months = collections.defaultdict(lambda: collections.defaultdict(lambda: []))
    for result in results:
        start_month = result.start_time.date().replace(day=1)
        end_month = result.end_time.date().replace(day=1)
        cur_month = start_month
        while cur_month <= end_month:
            year_months[cur_month.year][cur_month.month].append(result)
            cur_month = cur_month.replace(month=cur_month.month+1)
    return year_months


def group_results_by_location(results):
    location_map = collections.defaultdict(lambda: [])
    for result in results:
        location_info = event_locations.LocationInfo(result.fb_event)
        name = locations.get_country_for_location(location_info.fb_address, long_name=True)
        location_map[name].append(result)
    return location_map
