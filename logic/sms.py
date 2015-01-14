from twilio.rest import TwilioRestClient 

import keys

# put your own credentials here 
ACCOUNT_SID = "AC4fe8564ea12bfcb3af18df2ee99c2bd9" 
AUTH_TOKEN = keys.get("twilio_auth_token") 
 

def send_email_link(phone_number):
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 
    client.messages.create(
        to=phone_number, 
        from_="+12566932623", 
        body="Download the DanceDeets App at http://www.dancedeets.com/mobile_apps?action=download",  
    )
