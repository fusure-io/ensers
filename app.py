import asyncio
import json
from aiohttp import web

from ensers.vector_db import QdrantVectorStore, QdrantSearch
from ensers.load_documents import LocalFileLoader

async def home(request):
    return web.json_response({'response': "Hi, there, thank you for using our NLP search tool; Ensers"})

async def load_documents(request):
    try:
        data = await request.json()

        dir_path = data.get('dir_path')
        name_of_database = data.get('name_of_database')
        q_drant_url = data.get('q_drant_url')
        documents = data.get('documents', [])
        fields = data.get('fields', [])

        file_loader = LocalFileLoader()
        documents = file_loader.load_docs(dir_path=dir_path, fields=fields)

        store = QdrantVectorStore(q_drant_url=q_drant_url, name=name_of_database)
        res = await store.index_documents(documents)
        return web.json_response({"response": res})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def search(request):
    try:
        data = await request.json()

        name_of_database = data.get('name_of_database')
        store = QdrantSearch(name=name_of_database)

        query = data.get('query')
        hits = await store.search(query)
        return web.json_response({'results': hits})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def openapi(request):
    return web.json_response({"msg": "Welcome to the OpenAPI documentation"})

app = web.Application(debug=True)

app.router.add_route('GET', '/', home)
app.router.add_route('POST', '/load_documents', load_documents)
app.router.add_route('POST', '/search', search)
app.router.add_route('GET', '/docs/', openapi)

if __name__ == '__main__':
    web.run_app(app)