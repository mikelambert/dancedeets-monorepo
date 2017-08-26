import logging
import mandrill

import keys

mandrill_client = mandrill.Mandrill(keys.get('mandrill_api_key'))


def send_message(message):
    try:
        result = mandrill_client.messages.send(message=message, async=False)
        logging.info('Message Contents: %s', message)
        logging.info('Message Result: %s', result)
    except mandrill.Error, e:
        logging.error('A mandrill error occurred: %s: %s', e.__class__, e)
    return result
