from functools import partial
from operator import itemgetter
import os
from time import sleep

from pydantic import SecretStr
from database.database import Database
from shared.discord_types import MessageType, StrategyType
import tiktoken
from sentence_transformers import SentenceTransformer
from langchain_ollama import OllamaLLM
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import List, Tuple
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from shared.types import TradingStrategyDefinition
from doc_loader.prompts import strategy_evaluation
from langchain_core.documents import Document


def check_langsmith():
    lang_chain = os.getenv("LANGCHAIN_API_KEY")
    lang_endpoint = os.getenv("LANGCHAIN_ENDPOINT")
    lang_tracing = os.getenv("LANGCHAIN_TRACING_V2")
    if not lang_chain or not lang_endpoint or not lang_tracing:
        raise ValueError("LangSmith environment variables is not set")

def load_openai_llm(
    model_name: str = "gpt-4o-mini-2024-07-18",
):
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        secret_key = SecretStr(env_key)
    else:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return ChatOpenAI(
        model=model_name,
        api_key=secret_key,  # Convert string to SecretStr
        temperature=0.0,
        streaming=True,
    )

def load_ollama_llm(model_name="deepseek-r1", temperature=0.2):
    llm = OllamaLLM(
        model=model_name,
        temperature=temperature,
    )
    return llm

def reciprocal_rank_fusion(results: List[List[Document]], k=60):
    """Reciprocal_rank_fusion that takes multiple lists of ranked documents
    and an optional parameter k used in the RRF formula"""

    # Initialize a dictionary to hold fused scores for each unique document
    fused_scores = {}
    docs_map = {}
    # Iterate through each list of ranked documents
    for docs in results:
        # Iterate through each document in the list, with its rank (position in the list)
        for rank, doc in enumerate(docs):
            # Convert the document to a string format to use as a key (assumes documents can be serialized to JSON)
            doc_id = doc.id
            docs_map[doc_id] = doc
            # If the document is not yet in the fused_scores dictionary, add it with an initial score of 0
            if doc_id not in fused_scores:
                fused_scores[doc_id] = 0
            # Retrieve the current score of the document, if any
            previous_score = fused_scores[doc_id]
            # Update the score of the document using the RRF formula: 1 / (rank + k)
            fused_scores[doc_id] += 1 / (rank + k)

    # Sort the documents based on their fused scores in descending order to get the final reranked results
    reranked_results = [
        (docs_map[doc_id], score)
        for doc_id, score in sorted(
            fused_scores.items(), key=lambda x: x[1], reverse=True
        )
    ]

    # Return the reranked results as a list of tuples, each containing the document and its fused score
    return reranked_results

def take_top_k(ranked_docs: List[Tuple[Document, float]], k: int = 5) -> List[int]:
    return [doc.metadata.get("id", -1) for doc, score in ranked_docs[:k]]

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens