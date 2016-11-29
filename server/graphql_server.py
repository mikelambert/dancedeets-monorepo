from flask import Flask
from flask_graphql import GraphQL
import graphene
from graphene import relay
import keys

app = Flask(__name__)
app.debug = True
app.secret_key = keys.get('flask_session_key')

# http://dev.dancedeets.com:8080/graphql?query={rebels%20{name,ships(first:1%20after:%22YXJyYXljb25uZWN0aW9uOjA=%22){edges{cursor,node{name}}}}}
#from starwars import schema

schema = graphene.Schema(name='Nonexistant Schema')
class Query(graphene.ObjectType):
    node = relay.NodeField()

schema.query = Query
#schema.mutation = Mutation
GraphQL(app, schema=schema)

if __name__ == '__main__':

    # Start app
    app.run(debug=True)
