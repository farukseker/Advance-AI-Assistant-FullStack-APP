from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from config import QDRANT_URI


class QdrantStorage:
    def __init__(self, url=QDRANT_URI, collection_name="docs", dim=3072):
        self.client = QdrantClient(url=url, timeout=30)
        self.collection = collection_name
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upsert(self, ids, vectors, payloads):
        points = [
            PointStruct(
                id=ids[i],
                vector=vectors[i],
                payload=payloads[i]
            )
            for i in range(len(ids))
        ]
        self.client.upsert(self.collection, points=points)

    def search(
            self,
            query_vector,
            top_k: int = 5,
            filename: str = None  # Opsiyonel filename filtresi
    ):
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        # Filter oluştur (filename varsa)
        search_filter = None
        if filename:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=filename)
                    )
                ]
            )

        results = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            query_filter=search_filter,
            limit=top_k,
            with_payload=True,
        )

        contexts = []
        sources = set()

        for point in results.points:
            text = point.payload.get("text", "")
            if not text:
                continue

            source = point.payload.get("source", "")

            contexts.append(text)
            sources.add(source)

        return {"contexts": contexts, "sources": list(sources)}

    def delete_by_ids(self, ids: List[str]) -> None:
        from qdrant_client.models import PointIdsList

        self.client.delete(
            collection_name=self.collection,
            points_selector=PointIdsList(
                points=ids,
            ),
        )

__all__ = "QdrantStorage",