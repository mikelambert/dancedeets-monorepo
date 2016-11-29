from google.appengine.ext import db


class Profile(db.Model):
    fb_uid = property(lambda x: int(x.key().name()))
    fb_name = db.StringProperty()

    dance_names = db.StringListProperty(indexed=False)

    def get_by_name(name):
        pass

    def get_by_id(id):
        pass

