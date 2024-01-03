import torch
from sentence_transformers import SentenceTransformer
from qdrant_client import models, QdrantClient

encoder_name="sentence-transformers/all-MiniLM-L6-v2"
qdrant_api="http://localhost:6333"
memory_storage=":memory:"

class QdrantVectorStore:

    def __init__(self,
                 name,
                 q_drant_url=qdrant_api,
                 encoder_name=encoder_name,
                 use_Memory=False):
        if use_Memory == False:
            self.qdrant = QdrantClient(q_drant_url)
        else:
            self.qdrant = QdrantClient(memory_storage)

        self.encoder=SentenceTransformer(encoder_name)
        self.name =name

        try:
            self.qdrant.recreate_collection(
                                                collection_name=self.name,
                                                vectors_config=models.VectorParams(
                                                    size=self.encoder.get_sentence_embedding_dimension(),
                                                    distance=models.Distance.COSINE,
                                                )
                                            )
        except Exception as e:
            print(e)
        
    def index_documents(self,documents):
        
        try:
            return self.qdrant.upload_records(
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
        except Exception as e:
            return "error"+str(e)


class QdrantSearch:
    def __init__(self, name,encoder_name=encoder_name,q_drant_url=qdrant_api,use_Memory=False):
        self.name = name
        self.encoder = SentenceTransformer(encoder_name, device="cpu")

        if use_Memory == False:
            self.qdrant = QdrantClient(q_drant_url)
        else:
            self.qdrant = QdrantClient(memory_storage)

    def search(self,querry):
            try:
                hits = self.qdrant.search(
                    collection_name=self.name,
                    query_vector=self.encoder.encode(querry).tolist(),
                    limit=5,
                    )
                return [hit.payload for hit in hits]
            except Exception as e:
                return "error"+str(e)
