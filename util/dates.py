from pytz.gae import pytz

def localize_timestamp(dt, timezone_str="America/Los_Angeles"):
    timezone = pytz.timezone(timezone_str)
    localized_dt = timezone.localize(dt)
    final_dt = dt + localized_dt.tzinfo.utcoffset(localized_dt)
    return final_dt

