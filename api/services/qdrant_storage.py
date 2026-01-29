from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PointIdsList
)
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

    def delete_by_source(self, filename: str):
        self.client.delete(
            collection_name=self.collection,
            points_selector=rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="source",
                        match=rest.MatchValue(value=filename)
                    )
                ]
            )
        )

    def upsert(self, ids, vectors, payloads):
        """Add or update documents in the collection"""
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
            filename: str = None
    ):
        """Search for similar documents"""
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
        """Delete specific documents by their IDs"""
        self.client.delete(
            collection_name=self.collection,
            points_selector=PointIdsList(points=ids),
        )

    def delete_by_source(self, filename: str) -> int:
        """Delete all documents from a specific source file

        Args:
            filename: Name of the source file to delete

        Returns:
            Number of documents deleted
        """
        # First, get all point IDs for this source
        ids_to_delete = self.get_ids_by_source(filename)

        if not ids_to_delete:
            print(f"No documents found for source: {filename}")
            return 0

        # Delete using the filter
        self.client.delete(
            collection_name=self.collection,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=filename)
                    )
                ]
            ),
        )

        print(f"Deleted {len(ids_to_delete)} documents from source: {filename}")
        return len(ids_to_delete)

    def get_ids_by_source(self, filename: str) -> List[str]:
        """Get all document IDs for a specific source file"""
        results = self.client.scroll(
            collection_name=self.collection,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=filename)
                    )
                ]
            ),
            limit=10000,
            with_payload=False,
            with_vectors=False
        )

        return [str(point.id) for point in results[0]]

    def list_sources(self) -> List[Dict[str, any]]:
        """List all unique source files in the collection with document counts"""
        # Get all points with their payloads
        all_points, _ = self.client.scroll(
            collection_name=self.collection,
            limit=10000,
            with_payload=True,
            with_vectors=False
        )

        # Count documents per source
        source_counts = {}
        for point in all_points:
            source = point.payload.get("source", "unknown")
            source_counts[source] = source_counts.get(source, 0) + 1

        # Format the result
        sources_list = [
            {"filename": source, "document_count": count}
            for source, count in sorted(source_counts.items())
        ]

        return sources_list

    def get_collection_info(self) -> Dict:
        """Get information about the collection"""
        info = self.client.get_collection(self.collection)
        return {
            "name": self.collection,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status
        }

    def clear_collection(self) -> None:
        """Delete all documents from the collection"""
        self.client.delete_collection(self.collection)
        # Recreate the collection
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
        )
        print(f"Collection {self.collection} cleared and recreated")


__all__ = ["QdrantStorage"]