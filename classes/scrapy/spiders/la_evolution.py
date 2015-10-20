import datetime
import dateutil
import re

import icalendar
from .. import items

def expand_rrule(event):
    rrulestr = event['RRULE'].to_ical().decode('utf-8')
    start = event.decoded('dtstart')
    if isinstance(start, datetime.datetime):
        start = start.replace(tzinfo=None)
    rrule = dateutil.rrule.rrulestr(rrulestr, dtstart=start)
    if not set(['UNTIL', 'COUNT']).intersection(
            event['RRULE'].keys()):
        # pytz.timezones don't know any transition dates after 2038
        # either
        rrule._until = datetime.datetime.today() + datetime.timedelta(days=366)
    elif rrule._until and rrule._until.tzinfo:
        rrule._until = rrule._until.replace(tzinfo=None)
    return rrule

class Evolution(items.StudioScraper):
    name = 'Evolution'
    allowed_domains = ['calendar.google.com']
    latlong = (34.1718212, -118.3664417)
    address = '10816 Burbank Blvd, North Hollywood, CA 91601'

    start_urls = [
        'https://calendar.google.com/calendar/ical/evolutiondancestudios%40gmail.com/public/basic.ics',
    ]

    def parse_classes(self, response):
        past_horizon = datetime.datetime.today().date()
        future_horizon = datetime.datetime.today().date() + datetime.timedelta(days=14)
        ical_body = response.body.decode('utf-8')
        calendar = icalendar.Calendar.from_ical(ical_body)
        for event in calendar.subcomponents:
            try:
                if not isinstance(event, icalendar.Event):
                    continue
                #TODO: What do we want to do with the longform event['description']
                summary = str(event['summary'])
                instructor_re = r' (?:w/|with) (.*?)(?: -|$)'
                match = re.search(instructor_re, summary)
                if match:
                    teacher = match.group(1)
                    name = re.sub(instructor_re, '', summary)
                else:
                    name = summary
                    match = re.search(r'(?:Instructors?|Teachers?): ([^\n]*)', event['description'])
                    if match:
                        teacher = match.group(1).strip()
                    else:
                        teacher = None
                if not self._street_style(name):
                    continue
                item = items.StudioClass()
                item['style'] = name
                item['teacher'] = teacher
                item['start_time'] = event.decoded('dtstart')
                if 'dtend' in event:
                    item['end_time'] = event.decoded('dtend')
                else:
                    item['end_time'] = event.decoded('dtstart') + datetime.timedelta(hours=6)
                if not 'rrule' in event:
                    event_date = item['start_time']
                    if isinstance(event_date, datetime.datetime):
                        event_date = event_date.date()
                    if past_horizon < event_date and event_date < future_horizon:
                        yield item
                else:
                    rrule = expand_rrule(event)
                    duration = item['end_time'] - item['start_time']
                    for recurrence in rrule:
                        event_date = recurrence.date()
                        if past_horizon < event_date and event_date < future_horizon:
                            newitem = item.copy()
                            newitem['start_time'] = recurrence
                            newitem['end_time'] = recurrence + duration
                            yield newitem
            except Exception, e:
                print "Found error processing ical event: ", e
                print event
                raise

