import chromadb
from chromadb.api import ClientAPI
from chromadb import Collection
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


class VectorDB:
    db: ClientAPI
    vectorStore: Chroma

    def __init__(self):
        self.db = chromadb.PersistentClient("./chroma-db")

    def get_theory_collection(self) -> Collection:
        try:
            return self.db.get_collection("trading_theory")
        except Exception as e:
            print(f"Error getting trading theory collection: {e}")
            return self.db.create_collection("trading_theory")

    def vectorstore(self, collection_name: str):
        return Chroma(
            client=self.db,
            collection_name=collection_name,
            embedding_function=OpenAIEmbeddings(),
        )
