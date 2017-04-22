import mandrill

import keys

mandrill_client = mandrill.Mandrill(keys.get('mandrill_api_key'))

def send_message(message):
    result = mandrill_client.messages.send(message=message, async=False)
    return result
