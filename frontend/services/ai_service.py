from operator import itemgetter
import os
from typing import List, Dict, Any, Optional
import streamlit as st
from pydantic import SecretStr

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from .prompts import message_with_context


class StreamingCallback(BaseCallbackHandler):
    """Callback handler for streaming tokens to a StreamHandler."""

    def __init__(self, stream_handler):
        self.stream_handler = stream_handler

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Run on new token."""
        self.stream_handler.update(token)


class StreamHandler:
    """Handler for streaming responses to Streamlit."""

    def __init__(self, container):
        self.container = container
        self.text = ""
        self.reasoning = container.empty()

    def update(self, text_chunk: str) -> None:
        """Update the displayed text with a new chunk."""
        self.text += text_chunk
        self.reasoning.markdown(self.text + "▌")

    def finish(self) -> None:
        """Finalize the displayed text."""
        self.reasoning.markdown(self.text)

    def get_text(self) -> str:
        """Get the full text."""
        return self.text


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
        message,
        container,
        system_prompt: Optional[str] = None,
        model: str = "gpt-4o-mini-2024-07-18",
    ) -> str:
        """
        Generate a response with streaming to a Streamlit container.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            container: Streamlit container to stream to
            system_prompt: Optional system prompt to prepend

        Returns:
            The complete generated response as a string
        """
        stream_handler = StreamHandler(container)
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

            chain = (
                {
                    "context": "None",
                    "question": itemgetter("question"),
                }
                | ChatPromptTemplate.from_template(message_with_context)
                | llm
            )
            # Generate streaming response
            response = chain.invoke({"question": message})

            print(response)
            # Finalize the displayed text
            stream_handler.finish()
            return str(response.content)

        except Exception as e:
            st.error(f"Error generating streaming response: {e}")
            return str(e)
