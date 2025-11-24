from google.cloud import ndb


class Profile(ndb.Model):
    fb_uid = property(lambda x: int(x.key.string_id()))
    fb_name = ndb.StringProperty()

    dance_names = ndb.StringProperty(indexed=False, repeated=True)

    def get_by_name(name):
        pass

    def get_by_id(id):
        pass
