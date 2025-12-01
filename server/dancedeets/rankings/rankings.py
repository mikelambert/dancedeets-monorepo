"""
City/country rankings utilities.

The batch ranking computation has been migrated to Cloud Run Jobs.
See: dancedeets.jobs.compute_rankings

This module retains:
- TIME_PERIODS and constants for display
- retrieve_summary(): Get cached ranking totals
- compute_city_template_rankings(): Format rankings for templates
"""
import datetime

from dancedeets.util import memcache


# Time period constants
LAST_WEEK = "LAST_WEEK"
LAST_MONTH = "LAST_MONTH"
ALL_TIME = "ALL_TIME"

TIME_PERIODS = [
    ALL_TIME,
    LAST_MONTH,
    LAST_WEEK,
]

string_translations = {
    ALL_TIME: "all time",
    LAST_MONTH: "last month",
    LAST_WEEK: "last week",
}


def get_time_periods(timestamp):
    """Get applicable time periods for a given timestamp."""
    if timestamp > datetime.datetime.now() - datetime.timedelta(days=7):
        yield LAST_WEEK
    if timestamp > datetime.datetime.now() - datetime.timedelta(days=31):
        yield LAST_MONTH
    yield ALL_TIME


TOTALS_KEY = "StatTotals"
TOTALS_EXPIRY = 6 * 3600


def retrieve_summary():
    """
    Retrieve cached ranking summary.

    Returns cached totals or empty dict if not available.
    Rankings are computed by the Cloud Run Job: dancedeets.jobs.compute_rankings
    """
    totals = memcache.get(TOTALS_KEY)
    if not totals:
        # Rankings not yet computed - return empty totals
        totals = dict(total_events=0, total_users=0)
    return totals


def _compute_sum(all_rankings, time_period):
    """Compute total count across all cities for a time period."""
    total_count = 0
    for city, times in all_rankings.items():
        count = times.get(time_period, 0)
        total_count += count
    return total_count


def compute_city_template_rankings(
    all_rankings, time_period, vertical=None, use_url=True
):
    """
    Format city rankings for template display.

    Args:
        all_rankings: Dict of city -> time_period -> count
        time_period: Which time period to display
        vertical: Event vertical for admin URLs
        use_url: Whether to include URLs in output

    Returns:
        List of dicts with city, count, and url
    """
    city_ranking = []
    for city, times in all_rankings.items():
        if city == "Unknown":
            continue
        count = times.get(time_period, 0)
        if count:
            if use_url == "ADMIN":
                url = "/tools/recent_events?vertical=%s&city=%s" % (vertical, city)
            elif use_url:
                url = "/city/%s" % city
            else:
                url = None
            city_ranking.append(dict(city=city, count=count, url=url))
    city_ranking = sorted(city_ranking, key=lambda x: (-x["count"], x["city"]))
    return city_ranking
