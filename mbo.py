#!/usr/bin/env python

import datetime

import mindbody

SITE_IDS = [-99]
print mindbody.get_activation_link(SITE_IDS)

start = datetime.datetime.combine(datetime.date.today(), datetime.time())
end = start + datetime.timedelta(days=10)
result = mindbody.get_classes(start_time=start, end_time=end, hide_canceled_classes=True, site_ids=SITE_IDS)
if result.Status != 'Success':
    print result.Status
    print result.Message
if result.TotalPageCount != 1:
    print "Too many results for our query, got %s pages of data back" % result.TotalPageCount
classes = result.Classes.Class


for studio_class in classes:
    address = '%s, %s' % (studio_class.Location.Address, studio_class.Location.Address2)
    latlong = (studio_class.Location.Latitude, studio_class.Location.Longitude)
    print studio_class.ClassDescription.Name
    print studio_class.StartDateTime
    print studio_class.EndDateTime
    print studio_class.Staff.Name
    print studio_class.Location.Name
    #print studio_class.
    print address
    print latlong
    print

