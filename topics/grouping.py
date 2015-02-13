import collections
import datetime

from logic import event_locations

def group_results_by_date(results):
    year_months = collections.defaultdict(lambda: collections.defaultdict(lambda: []))
    for result in results:
        start_month = result.start_time.date().replace(day=1)
        if result.end_time:
            end_month = result.end_time.date().replace(day=1)
        else:
            end_month = start_month
        cur_month = start_month
        while cur_month <= end_month:
            month_key = cur_month.month
            year_months[cur_month.year][month_key].append(result)
            cur_month = datetime.date(cur_month.year + (cur_month.month / 12), ((cur_month.month % 12) + 1), 1)
    return year_months


def group_results_by_location(results):
    location_map = collections.defaultdict(lambda: [])
    location_infos = [event_locations.LocationInfo(x.fb_event) for x in results]
    geocodes = [x.geocode for x in location_infos]
    addresses = [x.country(long=True) if x else None for x in geocodes]
    #formatting.format_geocodes(geocodes)
    for address, result in zip(addresses, results):
        location_map[address].append(result)
    return location_map
