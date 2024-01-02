from flask import Flask,request
from flask_restful import Resource, Api,reqparse
from ensers import vector_db, load_documents
app = Flask(__name__)
api = Api(app)

class Home(Resource):
    def get(self):
      return {'response': "Hi, there, thank your for using our NLP search tool; Ensers"}

class LoadDocuments(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir_path', type=str, required=True, help='Path to Local folder containing documents you want to search on')
        parser.add_argument('data_is_structured', type=bool, required=False, help='Whether the data is structured or not. Please leave blank if the folder contains both sructured and unstructured data')
        parser.add_argument('name_of_database', type=str, required=True, help='Name of the database')
        parser.add_argument('q_drant_url', type=str, required=False, help='url of the database')
        parser.add_argument('documents', type=list, required=True, help='List of documents')
        parser.add_argument('fields', type=list, required=True, help='List of fields')

        args = parser.parse_args()
        try:
            args = request.get_json() 

            dir_path = args.get('dir_path')
            data_is_structured = args.get('data_is_structured')
            name_of_database = args.get('name_of_database')
            q_drant_url = args.get('q_drant_url')
            documents = args.get('documents', [])
            fields = args.get('fields', [])
            
            try:
                file_loader = LocalLoader()
                if data_is_structured == True:
                    structured_data = file_loader.load_structured(dir_path)
                elif data_is_structured == False:
                    un_structured_data = file_loader.load_unstructured(dir_path)
                else:
                    structured_data = file_loader.load_structured(dir_path)
                    un_structured_data = file_loader.load_structured(dir_path)
            except Exception as e:
                return {'error': str(e)}

            store = vector_db.QdrantVectorStore(q_drant_url=q_drant_url,name=name_of_database)
            res=store.index_documents(documents, fields)
        except:
            res=store.index_documents(documents, fields)
            return {'response': res}
        except Exception as e:
            return {'error': str(e)}

class Search(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name_of_database', type=str, required=True, help='Name of the database')
        parser.add_argument('q_drant_url', type=str, required=False, help='url of the database')
        parser.add_argument('use_memory', type=str, required=False, help='url of the database')
        parser.add_argument('querry', type=str, required=True, help='term to search for')

        args = parser.parse_args()
        try:
            store = vector_db.QdrantSearch(name=args['name_of_database'])
            hits=store.search(args['querry'])
            return {'results': hits}
        except Exception as e:
            return {'error': str(e)}
        
api.add_resource(Home, '/')
api.add_resource(LoadDocuments, '/load_documents')
api.add_resource(Search, '/search')

if __name__ == '__main__':
    app.run(debug=True)