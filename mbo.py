#!/usr/bin/env python

import datetime
import suds.client

import keys

siteIDs = [-99]

SOURCE_NAME = "DanceDeets"
SOURCE_PASSWORD = keys.get("mindbody_api_password")

USER_NAME = "Siteowner"
USER_PASSWORD = "apitest1234"

SITE_IDS = [-99]

def get_client(service_name):
    url = "https://api.mindbodyonline.com/0_5/" + service_name + "Service.asmx?wsdl"
    return suds.client.Client(url)

def fill_credentials(service, request, siteIDs):
    source_creds = service.factory.create('SourceCredentials')
    source_creds.SourceName = SOURCE_NAME
    source_creds.Password = SOURCE_PASSWORD
    source_creds.SiteIDs.int = siteIDs

    user_creds = service.factory.create('UserCredentials')
    user_creds.Username = USER_NAME
    user_creds.Password = USER_PASSWORD
    user_creds.SiteIDs.int = siteIDs

    request.XMLDetail = 'Full'
    request.SourceCredentials = source_creds
    request.UserCredentials = user_creds


def get_request(service, request_name):
    request = service.factory.create(request_name)
    if hasattr(request, 'Request'):
        request = request.Request
    fill_credentials(service, request, siteIDs)
    return request

def get_activation_link():
    service = get_client("Site")
    request = get_request(service, "GetActivationCode")
    result = service.service.GetActivationCode(request)
    return result.ActivationLink


def get_classes(
    startDateTime,
    endDateTime,
    hideCanceledClasses,
    pageSize):
    service = get_client("Class")
    request = get_request(service, "GetClasses")

    request.StartDateTime = startDateTime
    request.EndDateTime = endDateTime
    request.HideCanceledClasses = hideCanceledClasses

    # This improves speed from 3 seconds to 2 seconds, so the additional debugging advantages outweigh the speed benefits
    #request.XMLDetail = 'Bare'
    #request.Fields = BasicRequestHelper.FillArrayType(service, ["Classes.ClassDescription.Name", "Classes.StartDateTime", "Classes.EndDateTime", "Classes.Staff.Name"], "String")
    return service.service.GetClasses(request)

print get_activation_link()

start = datetime.datetime.combine(datetime.date.today(), datetime.time())
end = start + datetime.timedelta(days=10)
result = get_classes(startDateTime=start, endDateTime=end, hideCanceledClasses=True, pageSize=200)
if result.Status != 'Success':
    print result.Status
    print result.Message
if result.TotalPageCount != 1:
    print "Too many results for our query, got %s pages of data back" % result.TotalPageCount
classes = result.Classes.Class


for studio_class in classes:
    print studio_class.ClassDescription.Name
    print studio_class.StartDateTime
    print studio_class.EndDateTime
    print studio_class.Staff.Name
    print

