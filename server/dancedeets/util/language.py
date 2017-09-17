import cld2
import logging
import re

illegalChars = re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')


def detect(text):
    text = illegalChars.sub('', text)

    text = text.encode('utf-8')
    try:
        isReliable, textBytesFound, details = cld2.detect(text)
    except:
        logging.exception('Error processing text: %r', text)
        return None

    if isReliable:
        # top language, get the language code:
        # details: (('ENGLISH', 'en', 95, 1736.0), ('Unknown', 'un', 0, 0.0), ('Unknown', 'un', 0, 0.0))
        return details[0][1]
    else:
        return None
