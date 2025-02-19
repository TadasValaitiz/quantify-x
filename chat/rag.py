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
        return self.collection.query(query_texts=queries, n_results=20)

    def multi_query(self, queries: list[str]) -> CombinedQueryResult:
        paragraph_context = self.collection.query(
            query_texts=queries,
            n_results=5,
            where={"$and": [{"splitter": "paragraph"}, {"length": {"$gte": 500}}]},
        )

        small_chunks = self.collection.query(
            query_texts=queries,
            n_results=5,
            where={"$and": [{"chunk_size": 500}, {"length": {"$gte": 200}}]},
        )

        # Merge results
        merged_results = {
            "ids": [],
            "distances": [],
            "metadatas": [],
            "documents": [],
            "embeddings": None,
        }

        # Helper function to safely get and extend lists
        def safe_extend(target_list, source_result, key):
            if source_result.get(key):
                target_list.extend(source_result[key])

        # Merge all results
        for context in [paragraph_context, small_chunks]:
            safe_extend(merged_results["ids"], context, "ids")
            safe_extend(merged_results["distances"], context, "distances")
            safe_extend(merged_results["metadatas"], context, "metadatas")
            safe_extend(merged_results["documents"], context, "documents")

        return CombinedQueryResult(
            ids=merged_results["ids"],
            distances=merged_results["distances"],
            metadatas=merged_results["metadatas"],
            documents=merged_results["documents"],
            embeddings=merged_results["embeddings"],
        )


if __name__ == "__main__":
    rag = Rag()
    queries = [
        "Create trading strategy for crypto trading?",
        "I need to optimize weights?",
        "How to do backtesting?",
        "What trading strategies exist?",
        "What is the best technical indicators?",
        "What is the win rate of trading strategies?",
    ]

    for query in queries:
        result = rag.multi_query([query])
        print("*" * 100)
        print(f"Query: {query}\n")
        distances = [
            distance for distances in result.get("distances") for distance in distances
        ]
        chunk_sizes = [
            metadata["chunk_size"] if "chunk_size" in metadata else None
            for metadatas in result.get("metadatas")
            for metadata in metadatas
        ]
        source = [
            metadata["source"]
            for metadatas in result.get("metadatas")
            for metadata in metadatas
        ]

        splitter = [
            metadata["splitter"] if "splitter" in metadata else None
            for metadatas in result.get("metadatas")
            for metadata in metadatas
        ]
        length = [
            metadata["length"] if "length" in metadata else None
            for metadatas in result.get("metadatas")
            for metadata in metadatas
        ]
        content = [
            document for documents in result.get("documents") for document in documents
        ]

        print(f"Distances: {distances}")
        print(f"Chunk sizes: {chunk_sizes}")
        print(f"Sources: {source}")
        print(f"Splitters: {splitter}")
        print(f"Lengths: {length}")
        print("-" * 30)
        for i, c in enumerate(content):
            print(f"Distance: {distances[i]}")
            print(f"Chunk size: {chunk_sizes[i]}")
            print(f"Source: {source[i]}")
            print(f"Splitter: {splitter[i]}")
            print(f"Length: {length[i]}\n")
            print(f"{c}\n")
