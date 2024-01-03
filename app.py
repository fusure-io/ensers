from quart import Quart, request, jsonify
from quart_openapi import Pint, Resource, Api, Blueprint

from ensers.vector_db import QdrantVectorStore, QdrantSearch
from ensers.load_documents import LocalFileLoader

app = Pint(__name__)
api = Api(app)

class Home(Resource):
    async def get(self):
        return {'response': "Hi, there, thank you for using our NLP search tool; Ensers"}

class LoadDocuments(Resource):
    async def post(self):
        try:
            args = await request.get_json()

            dir_path = args.get('dir_path')
            name_of_database = args.get('name_of_database')
            q_drant_url = args.get('q_drant_url')
            documents = args.get('documents', [])
            fields = args.get('fields', [])

            file_loader = LocalFileLoader()
            documents = file_loader.load_docs(dir_path=dir_path, fields=fields)

            store = QdrantVectorStore(q_drant_url=q_drant_url, name=name_of_database)
            res = await store.index_documents(documents)
            return {"response": res}
        except Exception as e:
            return {'error': str(e)}

class Search(Resource):
    async def post(self):
        try:
            args = await request.get_json()

            name_of_database = args.get('name_of_database')
            store = QdrantSearch(name=name_of_database)

            querry = args.get('querry')
            hits = await store.search(querry)
            return {'results': hits}
        except Exception as e:
            return {'error': str(e)}

api.add_resource(Home, '/')
api.add_resource(LoadDocuments, '/load_documents')
api.add_resource(Search, '/search')

# Define a Blueprint for OpenAPI documentation
docs = Blueprint('docs', 'docs', url_prefix='/docs')

@docs.route('/')
async def openapi():
    return jsonify({"msg": "Welcome to the OpenAPI documentation"})

app.register_blueprint(docs)

if __name__ == '__main__':
    app.run(debug=True)