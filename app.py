from flask import Flask,request
from flask_restful import Api, Resource, reqparse
from flasgger import Swagger
from ensers.vector_db import QdrantVectorStore, QdrantSearch
from ensers.load_documents import LocalFileLoader
import os
import json
port = int(os.environ.get('ENSERS_PORT', 5001))

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

class Home(Resource):
    def get(self):
        """
        Home endpoint.
        ---
        responses:
          200:
            description: A welcome message.
            examples:
              response: "Hi, there, thank you for using our NLP search tool; Ensers"
        """
        return {'response': "Hi, there, thank you for using our NLP search tool; Ensers"}

class LoadDocuments(Resource):
    def post(self):
        """
        Load documents into the Qdrant database.
        ---
        consumes:
          - application/json

        parameters:
          - in: body
            name: params
            type: string
            required: true
            description: An json object containing\n\n
                dir_path - Path to the local folder containing documents.\n
                name_of_database - A name to be assigned to your search database.\n
                q_drant_url - host url of a running Qdrant database. Leave blank to use\n
                fields - If you are searching over json files, you can enter prefered keys of your json object to be indexed.
            description: An json object containing\n\n
                {\n
                - ***dir_path*** - Path to the local folder containing documents. This field is **Required**\n\n 
                - ***name_of_database*** -  A name to be assigned to your search database. This field is **Required**\n
                - ***q_drant_url*** - host url of a running Qdrant database. This is if you have a running instance of a qdrant database,\n
                     with indexed documents. This field is **Optional** Leave blank to use an initialized search database\n
                - ***fields*** - If you are searching over json objects,
                        You can specify which keys of the object are put in the search database.\n
                        by default all keys are used. This field is **Optional**.\n\n
                }
            example: {
                "dir_path":"/workspaces/ensers/test",
                "name_of_database":"db"
            }
        responses:
          200:
            description: Documents indexed successfully.
            examples:
              response: "Documents indexed successfully"
          400:
            description: Bad request.
            examples:
              error: "Invalid request. Missing required parameter 'name_of_database'."
        """
        parser = reqparse.RequestParser()
        parser.add_argument('dir_path', type=str, required=True, help='Path to Local folder containing documents you want to search on')
        parser.add_argument('name_of_database', type=str, required=True, help='Name of the database')
        parser.add_argument('q_drant_url', type=str, required=False, help='url of the database')
        parser.add_argument('fields', type=list, required=False, help='List of fields')

        args = parser.parse_args()

        try:
            args = request.get_json()

            dir_path = args.get('dir_path')
            name_of_database = args.get('name_of_database')
            q_drant_url = args.get('q_drant_url')
            documents = args.get('documents', [])
            fields = args.get('fields', [])

            file_loader = LocalFileLoader()
            unstructured_docs,structured_docs,no_of_unstructured_docs,no_of_structured_docs = file_loader.load_docs(dir_path=dir_path)
            store = QdrantVectorStore(q_drant_url=q_drant_url, name=name_of_database)

            if no_of_unstructured_docs == 0 and no_of_structured_docs == 0:
                return {"response": """The directory you provided appears to be empty or has
                                        none of the supported pdf,txt,docx or json files """}
            elif no_of_unstructured_docs == 0:
                res = store.index_documents(structured_docs,fields,True)
            elif no_of_structured_docs == 0:
                res = store.index_documents(unstructured_docs,fields,False)
            else:
                res = store.index_documents(structured_docs,fields,True)
                res = store.index_documents(unstructured_docs,fields,False)

            return {"response": res}
        except Exception as e:
            return {'error': str(e)}

class Search(Resource):
    def post(self):
        """
        Search for documents in the Qdrant database.
        ---
        parameters:
          - name: params
            in: body
            type: string
            required: true
            description: An json object containing\n\n
                {\n
                - ***querry*** - Term to search for. This field is **Required**\n\n 
                - ***name_of_database*** -  A name to be assigned to your search database. This field is **Required**\n
                - ***q_drant_url*** - host url of a running Qdrant database. This field is **Optional** Leave blank to use a default search database\n
                - ***use_memory*** - Whether to use memory option for the Qdrant database. This field is **Optional**. We dont recommend using memory unless you are trying out ensers.\n\n
                }
            example: {
                "querry":"examples of movies on aliens?",
                "name_of_database":"db"
            }

        responses:
          200:
            description: Search results.
            examples:
              results:
                - document_id: 1
                  score: 0.85
                - document_id: 2
                  score: 0.75
          400:
            description: Bad request.
            examples:
              error: "Invalid request. Missing required parameter 'name_of_database'."
        """
        parser = reqparse.RequestParser()
        parser.add_argument('name_of_database', type=str, required=True, help='Name of the database')
        parser.add_argument('q_drant_url', type=str, required=False, help='url of the database')
        parser.add_argument('use_memory', type=str, required=False, help='url of the database')
        parser.add_argument('querry', type=str, required=True, help='term to search for')

        args = parser.parse_args()
        try:
            store = QdrantSearch(name=args['name_of_database'])
            hits = store.search(args['querry'])
            return {'results': hits}
        except Exception as e:
            return {'error': str(e)}

api.add_resource(Home, '/')
api.add_resource(LoadDocuments, '/load_documents')
api.add_resource(Search, '/search')

if __name__ == '__main__':
    app.run(debug=True,port=port)
