import datetime
import dateutil
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

class TheSpotDanceCenter(items.StudioScraper):
    name = 'TheSpot'
    allowed_domains = ['localender.com']
    latlong = (40.7434126, -73.9976959)
    address = '161 W 22nd Street, New York, NY'

    start_urls = [
        'http://www.localendar.com/public/TheSpotDanceCenter.ics',
    ]

    def parse_classes(self, response):
        past_horizon = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        ical_body = response.body.decode('utf-8')
        calendar = icalendar.Calendar.from_ical(ical_body)
        for event in calendar.subcomponents:
            try:
                if not isinstance(event, icalendar.Event):
                    continue
                summary = event['summary']
                if '-' in summary:
                    name, teacher = summary.split('-', 1)
                elif ' with ' in summary:
                    name, teacher = summary.split(' with ', 1)
                else:
                    name = summary
                    teacher = ''
                item = items.StudioClass()
                item['style'] = name
                item['teacher'] = teacher.strip()
                item['start_time'] = event.decoded('dtstart')
                if 'dtend' in event:
                    item['end_time'] = event.decoded('dtend')
                else:
                    item['end_time'] = event.decoded('dtstart') + datetime.timedelta(hours=6)
                if not 'rrule' in event:
                    event_date = item['start_time']
                    if isinstance(event_date, datetime.date):
                        event_date = datetime.datetime.combine(event_date.date(), datetime.time.min)
                    if past_horizon <= event_date and event_date <= self._future_horizon():
                        yield item
                else:
                    rrule = expand_rrule(event)
                    duration = item['end_time'] - item['start_time']
                    for recurrence in rrule:
                        event_date = recurrence
                        if past_horizon <= event_date and event_date <= self._future_horizon():
                            newitem = item.copy()
                            newitem['start_time'] = recurrence
                            newitem['end_time'] = recurrence + duration
                            yield newitem
            except Exception, e:
                print "Found error processing ical event: ", e
                print event
                raise

