from google.appengine.ext import db

class User(db.Model):
    tags = db.StringListProperty()
    address = db.StringProperty()

def get_timezone_for_user(facebook):
    query = 'select timezone from user where uid = %s' % facebook.uid
    results = facebook.fql.query(query)
    return results[0]['timezone']

