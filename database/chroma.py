import chromadb
from chromadb import Client, ClientAPI


class ChromaDB:
    db: ClientAPI

    def __init__(self):
        self.db = chromadb.PersistentClient("./chroma-db")

    def get_theory_collection(self):
        try:
            return self.db.get_collection("trading_theory")
        except Exception as e:
            print(f"Error getting trading theory collection: {e}")
            return self.db.create_collection("trading_theory")
