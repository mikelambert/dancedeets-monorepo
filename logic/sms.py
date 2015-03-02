from twilio.rest import TwilioRestClient 
# This is the right import for 3.5.2
from twilio import TwilioRestException

import keys

# put your own credentials here 
ACCOUNT_SID = "AC4fe8564ea12bfcb3af18df2ee99c2bd9"
AUTH_TOKEN = keys.get("twilio_auth_token")

class InvalidPhoneNumberException(Exception):
    pass

def send_email_link(phone_number):
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    try:
        client.messages.create(
            to=phone_number, 
            from_="+12566932623", 
            body="Download the DanceDeets App at http://www.dancedeets.com/mobile_apps?action=download",  
        )
    except TwilioRestException as e:
        if 'not a valid phone number' in e.msg:
            raise InvalidPhoneNumberException(e.msg)
        else:
            raise
