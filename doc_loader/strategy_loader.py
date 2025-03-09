from functools import partial
from typing import List

from database.database import Database
from database.vector_db import VectorDB
from shared.discord_types import StrategyType
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from doc_loader.prompts import strategy_evaluation, rag_fusion
from shared.utils import reciprocal_rank_fusion, load_openai_llm, take_top_k


llm = load_openai_llm()
db = Database()
vector_db = VectorDB()


def load_strategies(ids: List[int]) -> List[StrategyType]:
    return db.list_strategies_by_ids(ids)


def rag_fusion_chain(question: str):
    rag_fusion_prompt = ChatPromptTemplate.from_template(rag_fusion)

    chain = (
        rag_fusion_prompt
        | llm
        | StrOutputParser()
        | (lambda x: x.split("\n"))
        | RunnablePassthrough(print)
        | vector_db.strategy_retriever().map()
        | reciprocal_rank_fusion
        | partial(take_top_k, k=5)
        | load_strategies
    )
    results = chain.invoke({"question": question})
    print(results)


def main():
    # strategies = db.list_strategies(limit=1000)
    # for strategy in strategies:
    #     print(strategy)
    #     vector_db.add_strategy(strategy)
    rag_fusion_chain("What is the best strategy for a scalping strategy?")


if __name__ == "__main__":
    main()
