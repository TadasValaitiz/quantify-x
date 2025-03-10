from typing import List

from app.database import Database, VectorDB
from app.common.utils import load_openai_llm

from doc_loader.prompts import strategy_evaluation, rag_fusion


llm = load_openai_llm()
db = Database()
vector_db = VectorDB()


def main():
    strategies = db.list_strategies(limit=1000)
    for strategy in strategies:
        print(strategy)
        # vector_db.add_strategy(strategy)


if __name__ == "__main__":
    main()
