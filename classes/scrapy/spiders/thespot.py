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
        rrule._until = datetime.today() + datetime.timedelta(years=1)
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
        future_horizon = datetime.datetime.now() + datetime.timedelta(days=14)
        ical_body = response.body
        calendar = icalendar.Calendar.from_ical(ical_body.replace('\xc2\xa0', ' ').encode('iso-8859-1'))
        today = datetime.datetime.today()
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
                    teacher = None
                item = items.StudioClass()
                item['style'] = name
                item['teacher'] = teacher
                item['start_time'] = event.decoded('dtstart')
                if 'dtend' in event:
                    item['end_time'] = event.decoded('dtend')
                else:
                    item['end_time'] = event.decoded('dtstart') + datetime.timedelta(hours=6)
                if not 'rrule' in event:
                    yield item
                else:
                    rrule = expand_rrule(event)
                    duration = item['end_time'] - item['start_time']
                    for recurrence in rrule:
                        if today < recurrence and recurrence < future_horizon:
                            newitem = item.copy()
                            newitem['start_time'] = recurrence
                            newitem['end_time'] = recurrence + duration
                            yield newitem
            except Exception, e:
                print "Found error processing ical event: ", e
                print event
                raise

