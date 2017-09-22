import datetime
import logging

from dancedeets.event_attendees import event_attendee_classifier
from dancedeets.events import eventdata
from dancedeets.users import users
from dancedeets.util import fb_events
from .facebook import event as facebook_event
from .facebook import fb_util
from .twitter import event as twitter_event
from . import db

blacklisted_countries = [
    # Africa
    "DZ",
    "AO",
    "BJ",
    "BW",
    "BF",
    "BI",
    "CM",
    "CV",
    "CF",
    "KM",
    "CD",
    "DJ",
    "EG",
    "GQ",
    "ER",
    "ET",
    "GA",
    "GM",
    "GH",
    "GN",
    "GW",
    "CI",
    "KE",
    "LS",
    "LR",
    "LY",
    "MG",
    "MW",
    "ML",
    "MR",
    "MU",
    "MA",
    "MZ",
    "NA",
    "NE",
    "NG",
    "of",
    "RE",
    "RW",
    "SH",
    "ST",
    "SN",
    "SC",
    "SL",
    "SO",
    "ZA",
    "SS",
    "SD",
    "SZ",
    "TZ",
    "TG",
    "TN",
    "UG",
    "EH",
    "ZM",
    "ZW",
    # Oceania
    "AS",
    "AU",
    "CK",
    "TL",
    "FJ",
    "PF",
    "GU",
    "KI",
    "MH",
    "FM",
    "NR",
    "NC",
    "NZ",
    "NU",
    "NF",
    "MP",
    "PW",
    "PG",
    "PN",
    "WS",
    "SB",
    "TK",
    "TV",
    "VU",
]


def _should_post_event_common(auth_token, db_event):
    geocode = db_event.get_geocode()
    if not geocode:
        # Don't post events without a location. It's too confusing...
        return False
    event_country = geocode.country()
    if auth_token and auth_token.country_filters and event_country not in auth_token.country_filters:
        logging.info("Skipping event due to country filters")
        return False

    return True


def _event_has_enough_attendees(db_event):
    # Ignore web events, since Japan/Korea web_events probably take up too much of the feed,
    # and there are already existing ways those people are likely to find local events
    if not db_event.is_fb_event:
        return False
    user = users.User.get_by_id('701004')
    fbl = user.get_fblookup()
    matcher = event_attendee_classifier.get_matcher(fbl, db_event.fb_event)
    logging.info('Checking event %s and found %s overlap_ids', db_event.id, len(matcher.overlap_ids))
    if len(matcher.overlap_ids) < 30:
        return False
    return True


def should_post_event_to_account(auth_token, db_event):
    if not _should_post_event_common(auth_token, db_event):
        return False
    # Add some filters based on number-attendees
    if db_event.attendee_count < 100:
        return False

    # Country filter blacklist
    geocode = db_event.get_geocode()
    if not geocode:
        # Don't post events without a location. It's too confusing...
        return False
    event_country = geocode.country()
    if event_country in blacklisted_countries:
        return False

    return True


def should_post_on_event_wall(auth_token, db_event):
    if not _should_post_event_common(auth_token, db_event):
        return False
    # Additional filtering for FB Wall postings, since they are heavily-rate-limited by FB.
    # We can't post into individual user's events...so this actually discards most of the events anyway
    if not db_event.is_fb_event:
        logging.info("Event is not FB event")
        return False
    if not db_event.is_page_owned:
        logging.info("Event is not owned by page")
        return False
    if not db_event.public:
        logging.info("Event is not public")
        return False
    if db_event.attendee_count < 5:
        logging.warning("Skipping event due to <5 attendees: %s", db_event.attendee_count)
        return False
    if db_event.attendee_count > 600:
        logging.warning("Skipping event due to 600+ attendees: %s", db_event.attendee_count)
        return False
    return True


def post_event(auth_token, data):
    event_id = data['event_id']
    db_event = eventdata.DBEvent.get_by_id(event_id)
    if _should_still_post_about_event(auth_token, db_event):
        return _post_event(auth_token, db_event)
    else:
        return False


def _should_still_post_about_event(auth_token, db_event):
    if not db_event:
        logging.warning("Failed to post event: %s, dbevent deleted in dancedeets", db_event)
        return False
    if not db_event.has_content():
        logging.warning("Failed to post event: %s, due to %s", db_event.id, db_event.empty_reason)
        return False
    if (db_event.end_time or db_event.start_time) < datetime.datetime.now():
        logging.info('Not publishing %s because it is in the past.', db_event.id)
        return False
    #TODO: Store the actual attendees counts and match info in the event itself,
    # so that we don't need to recompute it here just to do this filtering.
    if not auth_token.application == db.APP_TWITTER:
        if not _event_has_enough_attendees(db_event):
            return False
    return True


def _post_event(auth_token, db_event):
    if auth_token.application == db.APP_TWITTER:
        return twitter_event.twitter_post(auth_token, db_event)
    elif auth_token.application == db.APP_FACEBOOK:
        result = facebook_event.facebook_post(auth_token, db_event)
        # Re-run these checks here, since they're fast, and things may have changed in the interim if the queue is long
        if not should_post_event_to_account(db_event):
            return True
        return fb_util.processed_task(auth_token, result)
    elif auth_token.application == db.APP_FACEBOOK_WALL:
        result = facebook_event.post_on_event_wall(db_event)
        return fb_util.processed_task(auth_token, result)
    else:
        logging.error("Unknown application for OAuthToken: %s", auth_token.application)
        return False
    return True
