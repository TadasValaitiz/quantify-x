from ctypes import Array
from typing import List, Optional, TypedDict, Union
from xml.dom.minidom import Document
from chromadb import Embeddings, IDs, Metadata, QueryResult
from database.vector_db import VectorDB


class CombinedQueryResult(TypedDict):
    ids: List[IDs]
    embeddings: Optional[
        Union[
            List[Embeddings],
            List[Embeddings],
        ]
    ]
    documents: List[List[Document]]
    metadatas: List[List[Metadata]]
    distances: List[List[float]]

class Rag:
    def __init__(self):
        self.db = VectorDB()
        self.collection = self.db.get_theory_collection()

    def query(self, queries: list[str]) -> QueryResult:
        # Query with where filter to get only chunks of size 1000
        return self.collection.query(
            query_texts=queries, n_results=10
        )
        
    def multi_query(self, queries: list[str]) -> CombinedQueryResult:
        bigger_context = self.collection.query(
            query_texts=queries, n_results=2, where={"chunk_size": 2000}
        )
        medium_context = self.collection.query(
            query_texts=queries, n_results=5, where={"chunk_size": 1000}
        )
        
        smaller_context = self.collection.query(
            query_texts=queries, n_results=10, where={"chunk_size": 500}
        )

        # Merge results
        merged_results = {
            "ids": [],
            "distances": [],
            "metadatas": [],
            "documents": [],
            "embeddings": None
        }

        # Helper function to safely get and extend lists
        def safe_extend(target_list, source_result, key):
            if source_result.get(key):
                target_list.extend(source_result[key])

        # Merge all results
        for context in [bigger_context, medium_context, smaller_context]:
            safe_extend(merged_results["ids"], context, "ids")
            safe_extend(merged_results["distances"], context, "distances")
            safe_extend(merged_results["metadatas"], context, "metadatas")
            safe_extend(merged_results["documents"], context, "documents")

        return CombinedQueryResult(
            ids=merged_results["ids"],
            distances=merged_results["distances"],
            metadatas=merged_results["metadatas"],
            documents=merged_results["documents"],
            embeddings=merged_results["embeddings"]
        )





if __name__ == "__main__":
    rag = Rag()
    results = rag.multi_query(['What is the best way to optimize trading strategy?'])

    distances = [
        distance for distances in results.get("distances") for distance in distances
    ]
    chunk_sizes = [
        metadata["chunk_size"]
        for metadatas in results.get("metadatas")
        for metadata in metadatas
    ]
    source = [
        metadata["source"]
        for metadatas in results.get("metadatas")
        for metadata in metadatas
    ]
    content = [
        document for documents in results.get("documents") for document in documents
    ]
    print(f"Distances: {distances}\n")
    print(f"Chunk sizes: {chunk_sizes}\n")
    print(f"Source: {source}\n")
    for i, c in enumerate(content):
        print(f"{c}\n\n\n")
