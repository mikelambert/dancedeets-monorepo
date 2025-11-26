import logging

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from dancedeets import keys

# put your own credentials here
ACCOUNT_SID = "AC4fe8564ea12bfcb3af18df2ee99c2bd9"
AUTH_TOKEN = keys.get("twilio_auth_token")


class InvalidPhoneNumberException(Exception):
    pass


def send_email_link(phone_number):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    try:
        logging.info("Sending SMS to %s", phone_number)
        client.messages.create(
            to=phone_number,
            from_="+12566932623",
            body="Download the DanceDeets App at https://www.dancedeets.com/mobile_apps?action=download",
        )
    except TwilioRestException as e:
        if 'not a valid phone number' in str(e):
            raise InvalidPhoneNumberException(str(e))
        else:
            raise
