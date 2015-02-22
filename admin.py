from flask import Flask
from flask.ext.admin import Admin

from flask.ext.admin.contrib import appengine

from events import eventdata
from topics import topic_db

app = Flask(__name__)
app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

admin = Admin(app, name="Admin")
admin.add_view(appengine.ModelView(topic_db.Topic))
admin.add_view(appengine.ModelView(eventdata.DBEvent))

if __name__ == '__main__':

    # Start app
    app.run(debug=True)
