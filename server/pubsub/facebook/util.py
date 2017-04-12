import datetime
import logging

def processed_task(auth_token, result):
    if 'error' in result:
        error = result['error']
        if error.get('code') == 368 and error.get('error_subcode') == 1390008:
            logging.error('We are posting too fast to the facebook wall, so wait a day and try again later')
            next_post_time = datetime.datetime.now() + datetime.timedelta(days=1)
            auth_token = auth_token.key.get()
            auth_token.next_post_time = next_post_time
            # And space things out a tiny bit more!
            auth_token.time_between_posts += 5
            auth_token.put()
            return False
        return True
        logging.error("Facebook Post Error: %r", result)
    else:
        logging.info("Facebook result was %r", result)
        return True
