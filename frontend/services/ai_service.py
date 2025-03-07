from operator import itemgetter
import os
from typing import List, Dict, Any, Optional
import streamlit as st
from pydantic import BaseModel, Field, SecretStr

from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from shared.types import ChatMessage, ContextDict, TradingContextCollection

from .prompts import message_with_context, message_with_context_collection


class StreamHandler:
    """Handler for streaming responses to Streamlit."""

    def __init__(self):
        self.text = ""
        self.reasoning = ""
        self.steps = []

    def reasoning_update(self, text_chunk: str) -> None:
        """Update the displayed text with a new chunk."""
        self.text += text_chunk
        print(text_chunk)
        self.reasoning = self.text + "▌"

    def reasoning_finish(self) -> None:
        """Finalize the displayed text."""
        print(f"reasoning_finish: {self.text}")
        self.reasoning = self.text

    def step_update(self, step: str) -> None:
        """Update important step info"""
        self.steps.append(step)

    def get_steps(self) -> List[str]:
        """Get the steps."""
        return self.steps

    def get_text(self) -> str:
        """Get the full text."""
        return self.text


class StreamingCallback(BaseCallbackHandler):
    """Callback handler for streaming tokens to a StreamHandler."""

    def __init__(self, stream_handler: StreamHandler):
        self.stream_handler = stream_handler

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Run on new token."""
        self.stream_handler.reasoning_update(token)

    def on_llm_end(self, response, **kwargs) -> None:
        """Run when LLM ends running"""
        print(f"on_llm_end: {response}")
        self.stream_handler.reasoning_finish()


class AIService:
    """Service for interacting with AI models using Langchain."""

    def __init__(self):
        """Initialize the AI service with a specific model."""

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.openai_api_key = SecretStr(openai_api_key)
        else:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

    def generate_response_stream(
        self,
        message: ChatMessage,
        stream_handler: StreamHandler,
        model: str = "gpt-4o-mini-2024-07-18",
        context: Optional[ContextDict] = None,
    ) -> str | TradingContextCollection:
        """
        Generate a response with streaming to a Streamlit container.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            container: Streamlit container to stream to
            system_prompt: Optional system prompt to prepend

        Returns:
            The complete generated response as a string
        """
        streaming_callback = StreamingCallback(stream_handler)

        try:
            # Configure LLM for streaming
            llm = ChatOpenAI(
                model=model,
                api_key=self.openai_api_key,  # Convert string to SecretStr
                temperature=0.2,
                streaming=True,
                callbacks=[streaming_callback],
            )

            parser = PydanticOutputParser(pydantic_object=TradingContextCollection)
            format_instructions = parser.get_format_instructions()

            # Create a prompt that includes format instructions
            prompt_template = ChatPromptTemplate.from_template(
                message_with_context_collection
            )

            chain = (
                {
                    "context": itemgetter("context"),
                    "question": itemgetter("question"),
                    "format_instructions": lambda _: format_instructions,
                }
                | prompt_template
                | llm
                | parser
            )
            context_str = context.to_prompt_context() if context else ""

            response: TradingContextCollection = chain.invoke(
                {"question": message.content, "context": context_str}
            )
            return response

        except Exception as e:
            st.error(f"Error generating streaming response: {e}")
            return str(e)
