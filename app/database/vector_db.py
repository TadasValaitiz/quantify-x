import chromadb
from chromadb.api import ClientAPI
from chromadb import Collection
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr
from common import StrategyType


class VectorDB:
    db: ClientAPI

    def __init__(self, openai_api_key: str | None):
        self.db = chromadb.PersistentClient("data/chroma-db")
        self.openai_api_key = openai_api_key

    def get_theory_collection(self) -> Collection:
        try:
            return self.db.get_collection("trading_theory")
        except Exception as e:
            print(f"Error getting trading theory collection: {e}")
            return self.db.create_collection("trading_theory")

    def vectorstore(self, collection_name: str):
        if self.openai_api_key is None:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        return Chroma(
            client=self.db,
            collection_name=collection_name,
            embedding_function=OpenAIEmbeddings(api_key=SecretStr(self.openai_api_key)),
        )

    def strategy_store(self):
        return self.vectorstore("strategy")

    def strategy_retriever(self):
        return self.strategy_store().as_retriever(
            search_kwargs={
                "k": 5,
                "filter": {"theme": "strategy"},
            },
        )

    def add_strategy(self, strategy: StrategyType):
        strategy_def = strategy.get("strategy")
        content = strategy_def.to_vector_db_search()
        id = f"{strategy['id']}"
        metadatas = {
            "id": id,
            "message_id": strategy["message_id"],
            "type": "discord_message",
            "theme": "strategy",
            "length": len(content),
            "source": f"db://discord_strategies/{id}",
            "strategy_type": (
                str(strategy_def.strategy_type) if strategy_def.strategy_type else ""
            ),
            "external_source": (
                ",".join(strategy_def.source_urls) if strategy_def.source_urls else ""
            ),
        }

        return self.strategy_store().add_texts(
            texts=[content], ids=[id], metadatas=[metadatas]
        )
