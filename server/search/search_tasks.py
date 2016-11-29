import app
import base_servlet
from users import users
from . import search
from . import email_events

@app.route('/tasks/email_all_users')
class EmailAllUsersHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        email_events.mr_email_user(self.fbl)
    post=get

@app.route('/tasks/email_user')
class EmailUserHandler(base_servlet.UserOperationHandler):
    user_operation = lambda self, fbl, load_users: [email_events.email_user(fbl, x) for x in load_users]

@app.route('/tasks/refresh_fulltext_search_index')
class RefreshFulltextSearchIndex(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        index_future = bool(int(self.request.get('index_future', 1)))
        if index_future:
            search.construct_fulltext_search_index(index_future=index_future)
        else:
            assert False
