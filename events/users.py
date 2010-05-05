from google.appengine.ext import db

class User(db.Model):
    tags = db.StringListProperty()
    address = db.StringProperty()


