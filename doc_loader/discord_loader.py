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
from typing import List
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from doc_loader.types import TradingStrategyDefinition
from doc_loader.prompts import strategy_evaluation

transformer = SentenceTransformer("all-MiniLM-L6-v2")


# Function to use models from Ollama
def load_ollama_llm(model_name="deepseek-r1", temperature=0.2):
    """
    Initialize a LangChain LLM using an Ollama model
    Args:
        model_name: The name of the model in Ollama
        temperature: Controls randomness (higher = more random)
        max_tokens: Maximum tokens to generate
    Returns:
        A LangChain LLM instance connected to Ollama
    """

    llm = OllamaLLM(
        model=model_name,
        temperature=temperature,
    )
    return llm


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


# Use this to load directly from Ollama (recommended if you already have it)
llm = load_openai_llm()
db = Database()


def log_trading_strategy(result: TradingStrategyDefinition):
    print(f"\nresult: {result.is_strategy} - {result.assistant_response_summary}")


def insert_into_db(message: MessageType, result: TradingStrategyDefinition) -> ():
    print(f"inserting into db: {result.is_strategy}")
    if result.is_strategy:
        strategy: StrategyType = {
            "id": None,
            "message_id": message.get("id"),
            "timestamp": message.get("timestamp"),
            "flags": message.get("flags"),
            "reactions": len(message.get("reactions", [])),
            "content": message.get("content"),
            "strategy": result.model_dump(),
        }
        db.insert_strategy(strategy)


def load_message(message: MessageType):
    parser = PydanticOutputParser(pydantic_object=TradingStrategyDefinition)
    format_instructions = parser.get_format_instructions()

    prompt_template = ChatPromptTemplate.from_template(strategy_evaluation)

    chain = (
        {
            "question": itemgetter("question"),
            "format_instructions": lambda _: format_instructions,
        }
        | prompt_template
        | llm
        | parser
        | RunnablePassthrough(log_trading_strategy)
        | RunnablePassthrough(partial(insert_into_db, message))
    )

    result: TradingStrategyDefinition = chain.invoke(
        {"question": message.get("content")}
    )

    print(f"chain result: {result}")
    sleep(1)


def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    print(f"num_tokens: {num_tokens}")
    return num_tokens


def check_langsmith():
    lang_chain = os.getenv("LANGCHAIN_API_KEY")
    lang_endpoint = os.getenv("LANGCHAIN_ENDPOINT")
    lang_tracing = os.getenv("LANGCHAIN_TRACING_V2")
    if not lang_chain or not lang_endpoint or not lang_tracing:
        raise ValueError("LangSmith environment variables is not set")


def main():
    messages = db.get_messages()

    check_langsmith()

    urls = []
    for i, message in enumerate(messages):
        if not message.get("message_reference"):
            if len(message.get("attachments", [])) > 0:
                url = message.get("attachments", [])[0].get("url")
                urls.append(url)
            
            if len(message.get("content")) > 500:
                try:
                    print(f"\nloading message: {message.get('content')}")
                    load_message(message=message)
                except Exception as e:
                    print(f"error: {e} - {message.get('id')} - {message.get('timestamp')} - {message.get('content')}")


if __name__ == "__main__":
    main()
