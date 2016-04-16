from flask import Flask
from flask_graphql import GraphQL
import graphene
import keys

app = Flask(__name__)
app.debug = True
app.secret_key = keys.get('flask_session_key')

# http://dev.dancedeets.com:8080/graphql?query={rebels%20{name,ships(first:1%20after:%22YXJyYXljb25uZWN0aW9uOjA=%22){edges{cursor,node{name}}}}}
import starwars

GraphQL(app, schema=starwars.schema)

if __name__ == '__main__':

    # Start app
    app.run(debug=True)
