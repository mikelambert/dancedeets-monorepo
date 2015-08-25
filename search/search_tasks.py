import base_servlet
from users import users
from . import search
from . import email_events

class EmailAllUsersHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        email_events.mr_email_user(self.fbl)
    post=get

class EmailUserHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        user_ids = [x for x in self.request.get('user_ids').split(',') if x]
        load_users = users.User.get_by_ids(user_ids)
        email_events.email_user(self.fbl, load_users[0])
    post=get

class RefreshFulltextSearchIndex(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        index_future = bool(int(self.request.get('index_future', 1)))
        if index_future:
            search.construct_fulltext_search_index(index_future=index_future)
        else:
            assert False
