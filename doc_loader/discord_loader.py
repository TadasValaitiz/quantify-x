from functools import partial
from operator import itemgetter
from time import sleep

from database.database import Database
from shared.discord_types import MessageType, StrategyType
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from shared.types import TradingStrategyDefinition
from doc_loader.prompts import strategy_evaluation
from shared.utils import check_langsmith, load_openai_llm


llm = load_openai_llm()
db = Database()


def insert_into_db(message: MessageType, result: TradingStrategyDefinition):
    if result.is_strategy:
        strategy: StrategyType = {
            "id": None,
            "message_id": message.get("id"),
            "timestamp": message.get("timestamp"),
            "flags": message.get("flags"),
            "reactions": len(message.get("reactions", [])),
            "content": message.get("content"),
            "strategy": result,
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
        | RunnablePassthrough(partial(insert_into_db, message))
    )

    chain.invoke({"question": message.get("content")})
    sleep(1)


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
                    load_message(message=message)
                except Exception as e:
                    print(
                        f"error: {e} - {message.get('id')} - {message.get('timestamp')} - {message.get('content')}"
                    )


if __name__ == "__main__":
    main()
