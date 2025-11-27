"""Email sending via Mailchimp Transactional API (formerly Mandrill).

This replaces the deprecated mandrill library with mailchimp-transactional.
The API is compatible with the old Mandrill API.
"""

import logging

import mailchimp_transactional as MailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError

from dancedeets import keys

# Initialize the client
_client = None


def _get_client():
    """Get or initialize the Mailchimp Transactional client."""
    global _client
    if _client is None:
        api_key = keys.get('mandrill_api_key')
        _client = MailchimpTransactional.Client(api_key)
    return _client


def send_message(message):
    """Send an email message via Mailchimp Transactional.

    Args:
        message: A dict containing the email message in Mandrill format:
            - from_email: Sender email
            - from_name: Sender name
            - to: List of recipient dicts with 'email' and optionally 'name', 'type'
            - subject: Email subject
            - html: HTML body
            - text: Plain text body (optional)
            - headers: Custom headers (optional)
            - attachments: List of attachments (optional)
            - tags: List of tags for analytics (optional)

    Returns:
        List of send results, or None on error.
    """
    client = _get_client()

    try:
        result = client.messages.send({"message": message})
        logging.info('Message Contents: %s', message)
        logging.info('Message Result: %s', result)
        return result
    except ApiClientError as e:
        logging.error('A Mailchimp Transactional error occurred: %s: %s', e.__class__.__name__, e.text)
        logging.error('Erroring message is %s', message)
        return None
    except Exception as e:
        logging.error('An unexpected error occurred sending email: %s: %s', e.__class__.__name__, str(e))
        logging.error('Erroring message is %s', message)
        return None
