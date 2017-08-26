from google.appengine.ext import ndb


class Favorite(ndb.Model):
    # key: 'user_id::event_id'
    user_id = ndb.StringProperty()
    event_id = ndb.StringProperty()

    date_created = ndb.DateTimeProperty(auto_now_add=True)


def get_favorite_event_ids_for_user(user_id):
    # Get 1000 most recent favorite ids
    favorite_keys = Favorite.query(Favorite.user_id == user_id).order(-Favorite.date_created).fetch(1000, keys_only=True)
    event_ids = [x.string_id().split('::')[1] for x in favorite_keys]
    return event_ids


def _generate_keyname(user_id, event_id):
    return '%s::%s' % (user_id, event_id)


def _generate_favorite(user_id, event_id):
    f = Favorite(id=_generate_keyname(user_id, event_id))
    f.user_id = user_id
    f.event_id = event_id
    f.put()
    return f


def add_favorite(user_id, event_id):
    return _generate_favorite(user_id, event_id)


def delete_favorite(user_id, event_id):
    key_name = _generate_keyname(user_id, event_id)
    key = ndb.Key('Favorite', key_name)
    key.delete()
