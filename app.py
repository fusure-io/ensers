from flask import Flask
from flask_restful import Resource, Api
from .src.ensers import QdrantVectorStore

app = Flask(__name__)
api = Api(app)

class Index(Resource):
    def get(self,name_of_database,documents,fields):
        store=QdrantVectorStore(name=name_of_database);
        store.index_documents(documents,fields)
        return {'hello': 'world'}

class Search(Resource):
    def get(self,name_of_database,querry):
        store=QdrantVectorStore(name=name_of_database);
        hits=store.search(querry)
        return {'results': hits}

api.add_resource(Index, '/index')
api.add_resource(Search, '/search')

if __name__ == '__main__':
    app.run(debug=True)