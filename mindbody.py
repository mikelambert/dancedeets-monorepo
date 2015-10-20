import suds.client

import keys

SOURCE_NAME = "DanceDeets"
SOURCE_PASSWORD = keys.get("mindbody_api_password")

_CLIENTS = {}
def get_client(service_name):
    global _CLIENTS
    if service_name not in _CLIENTS:
        url = "https://api.mindbodyonline.com/0_5/" + service_name + "Service.asmx?wsdl"
        _CLIENTS[service_name] = suds.client.Client(url)
    return _CLIENTS[service_name]

def fill_credentials(client, request, site_ids):
    source_creds = client.factory.create('SourceCredentials')
    source_creds.SourceName = SOURCE_NAME
    source_creds.Password = SOURCE_PASSWORD
    source_creds.SiteIDs.int = site_ids

    request.XMLDetail = 'Full'
    request.SourceCredentials = source_creds


def get_request(client, request_name, site_ids):
    request = client.factory.create(request_name)
    if hasattr(request, 'Request'):
        request = request.Request
    fill_credentials(client, request, site_ids)
    return request

def get_activation_link(site_ids):
    client = get_client("Site")
    request = get_request(client, "GetActivationCode", site_ids)
    result = client.service.GetActivationCode(request)
    return result.ActivationLink

def get_classes(start_time, end_time, hide_canceled_classes, site_ids):
    service = get_client("Class")
    request = get_request(service, "GetClasses", site_ids)

    request.StartDateTime = start_time
    request.EndDateTime = end_time
    request.HideCanceledClasses = hide_canceled_classes

    # This improves speed from 3 seconds to 2 seconds, so the additional debugging advantages outweigh the speed benefits
    #request.XMLDetail = 'Bare'
    #request.Fields = BasicRequestHelper.FillArrayType(service, ["Classes.ClassDescription.Name", "Classes.StartDateTime", "Classes.EndDateTime", "Classes.Staff.Name"], "String")
    return service.service.GetClasses(request)
