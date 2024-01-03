import torch
from sentence_transformers import SentenceTransformer
from qdrant_client import models, AsyncQdrantClient

encoder_name="sentence-transformers/all-MiniLM-L6-v2"
qdrant_api="http://localhost:6333"
memory_storage=":memory:"

class QdrantVectorStore:

    def async __init__(self,
                 name,
                 q_drant_url=qdrant_api,
                 encoder_name=encoder_name,
                 use_Memory=False):
        if use_Memory == False:
            self.qdrant = AsyncQdrantClient(q_drant_url)
        else:
            self.qdrant = AsyncQdrantClient(memory_storage)

        self.encoder=SentenceTransformer(encoder_name)
        self.name =name

        try:
            await self.qdrant.create_collection(
                                                collection_name=self.name,
                                                vectors_config=models.VectorParams(
                                                    size=self.encoder.get_sentence_embedding_dimension(),
                                                    distance=models.Distance.COSINE,
                                                )
                                            )
        except Exception as e:
            print(e)
        
    def async index_documents(self,documents):
        
        try:
            await self.qdrant.upsert(
                                                collection_name=self.name,
                                                records=[
                                                    models.Record(
                                                        id=idx, vector=self.encoder.encode(doc.page_content).tolist(), payload={
                                                           "page_content":doc.page_content,
                                                           "metadata":doc.metadata
                                                        }
                                                    )
                                                    for idx, doc in enumerate(documents)
                                                ]
                                            )
            return "Success! Document indexed successfully."
        except Exception as e:
            return "error"+str(e)


class QdrantSearch:
    def __init__(self, name,encoder_name=encoder_name,q_drant_url=qdrant_api,use_Memory=False):
        self.name = name
        self.encoder = SentenceTransformer(encoder_name, device="cpu")

        if use_Memory == False:
            self.qdrant = AsyncQdrantClient(q_drant_url)
        else:
            self.qdrant = AsyncQdrantClient(memory_storage)

    def async search(self,querry):
            try:
                hits = await self.qdrant.search(
                    collection_name=self.name,
                    query_vector=self.encoder.encode(querry).tolist(),
                    limit=5,
                    )
                return [hit.payload for hit in hits]
            except Exception as e:
                return "error"+str(e)
