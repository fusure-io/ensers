from flask import Flask,request
from flask_restful import Resource, Api
from src import ensers 
app = Flask(__name__)
api = Api(app)

class Home(Resource):
    def get(self):
      return {'response': "Hi, there, thank your for using our NLP search tool; Ensers"}


class Index(Resource):
    def post(self,name_of_database,documents,fields):
        try:
            store=ensers.QdrantVectorStore(name=name_of_database);
            store.index_documents(documents,fields)
            return {'response': 'success'}
        except Exception as e:
            return {'error': str(e)}

class Search(Resource):
    def post(self):
        try:
            name_of_database=request.form['data']['name_of_database']
            print(request.form['data'])
            querry=request.form['data']['querry']
            store=ensers.QdrantVectorStore(name=name_of_database);
            hits=store.search(querry)
            return {'results': hits}
        except Exception as e:
            return {'error': str(e)}
        
api.add_resource(Home, '/')
api.add_resource(Index, '/index')
api.add_resource(Search, '/search')

if __name__ == '__main__':
    app.run(debug=True)