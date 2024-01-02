import torch
from sentence_transformers import SentenceTransformer
from qdrant_client import models, QdrantClient


class QdrantVectorStore():

    def __init__(self,
                 name,
                 encoder_name="sentence-transformers/all-MiniLM-L6-v2",
                 storage=":memory"
                 ):
        self.qdrant = QdrantClient(storage)
        self.encoder=SentenceTransformer(encoder_name)
        self.name =name

        self.qdrant.recreate_collection(
                                            collection_name=self.name,
                                            vectors_config=models.VectorParams(
                                                size=self.encoder.get_sentence_embedding_dimension(),
                                                distance=models.Distance.COSINE,
                                            )
                                        )
    def index_documents(self,documents,fields):

        return self.qdrant.upload_records(
                                            collection_name=self.name,
                                            records=[
                                                models.Record(
                                                    id=idx, vector=self.encoder.encode(str([f"{field}: {doc[field]}, " for field in fields]).replace("['",'').replace("]'",'')).tolist(), payload=doc
                                                )
                                                for idx, doc in enumerate(documents)
                                            ],
                                        )
    def search(self,querry):
        hits = self.qdrant.search(
            collection_name=self.name,
            query_vector=self.encoder.encode_document(querry).tolist(),
            limit=3,
            )
        return [hit.payload for hit in hits]
