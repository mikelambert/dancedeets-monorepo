# mbo.py

import datetime
import suds.client

import keys

siteIDs = [-99]

SOURCE_NAME = "DanceDeets"
SOURCE_PASSWORD = keys.get("mindbody_api_password")

USER_NAME = "Siteowner"
USER_PASSWORD = "apitest1234"

SITE_IDS = [-99]

def BuildWsdlUrl(serviceName):
    return "https://api.mindbodyonline.com/0_5/" + serviceName + "Service.asmx?wsdl"

def GetActivationLink():
    service = suds.client.Client(BuildWsdlUrl("Site"))
    request = GetRequest(service, "GetActivationCode")
    result = service.service.GetActivationCode(request)
    return result.ActivationLink


def FillDefaultCredentials(service, request, siteIDs):
    sourceCreds = service.factory.create('SourceCredentials')
    sourceCreds.SourceName = SOURCE_NAME
    sourceCreds.Password = SOURCE_PASSWORD
    sourceCreds.SiteIDs.int = siteIDs

    userCreds = service.factory.create('UserCredentials')
    userCreds.Username = USER_NAME
    userCreds.Password = USER_PASSWORD
    userCreds.SiteIDs.int = siteIDs

    request.SourceCredentials = sourceCreds
    request.UserCredentials = userCreds
    request.XMLDetail = "Full"
    request.PageSize = 200
    request.CurrentPageIndex = 0

    return request

def GetRequest(service, requestName):
    request = service.factory.create(requestName)
    if hasattr(request, 'Request'):
        request = request.Request
    return FillDefaultCredentials(service, request, siteIDs)

print GetActivationLink()


def GetClasses(
    startDateTime,
    endDateTime,
    hideCanceledClasses,
    pageSize):
    service = suds.client.Client(BuildWsdlUrl("Class"))

    request = GetRequest(service, "GetClasses")

    request.StartDateTime = startDateTime
    request.EndDateTime = endDateTime
    request.HideCanceledClasses = hideCanceledClasses

    # This improves speed from 3 seconds to 2 seconds, so the additional debugging we get from not using it is worth it
    #request.XMLDetail = 'Bare'
    #request.Fields = BasicRequestHelper.FillArrayType(service, ["Classes.ClassDescription.Name", "Classes.StartDateTime", "Classes.EndDateTime", "Classes.Staff.Name"], "String")
    return service.service.GetClasses(request)


start = datetime.datetime.combine(datetime.date.today(), datetime.time())
end = start + datetime.timedelta(days=10)
result = GetClasses(startDateTime=start, endDateTime=end, hideCanceledClasses=True, pageSize=200)
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

