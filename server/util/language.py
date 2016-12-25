import cld2

def detect(text):
    text = text.encode('utf-8')
    isReliable, textBytesFound, details = cld2.detect(text)
    if isReliable:
        # top language, get the language code:
        # details: (('ENGLISH', 'en', 95, 1736.0), ('Unknown', 'un', 0, 0.0), ('Unknown', 'un', 0, 0.0))
        return details[0][1]
    else:
        return None
