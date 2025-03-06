import os
from typing import List, Dict, Any, Optional
import openai
import streamlit as st


class StreamHandler:
    """Handler for streaming responses to Streamlit."""

    def __init__(self, container):
        self.container = container
        self.text = ""
        self.placeholder = container.empty()

    def update(self, text_chunk: str) -> None:
        """Update the displayed text with a new chunk."""
        self.text += text_chunk
        self.placeholder.markdown(self.text + "▌")

    def finish(self) -> None:
        """Finalize the displayed text."""
        self.placeholder.markdown(self.text)

    def get_text(self) -> str:
        """Get the full text."""
        return self.text


class AIService:
    """Service for interacting with AI models using OpenAI API directly."""

    def __init__(self, model: str = "o3-mini-2025-01-31"):
        """Initialize the AI service with a specific model."""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.model = model
        # Set the API key at the module level
        openai.api_key = openai_api_key

    def generate_response(
        self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response without streaming.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            system_prompt: Optional system prompt to prepend

        Returns:
            The generated response as a string
        """
        # Convert messages to the format expected by OpenAI
        openai_messages = []

        # Add system prompt if provided
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})

        # Add the rest of the messages
        for msg in messages:
            openai_messages.append({"role": msg["role"], "content": msg["content"]})

        try:
            # Using OpenAI API v0.28.1 syntax
            response = openai.ChatCompletion.create(
                model=self.model, messages=openai_messages, temperature=0.7
            )

            # In v0.28.1, the response structure is different
            content = response.choices[0].message["content"]
            return content if content is not None else ""
        except Exception as e:
            st.error(f"Error generating response: {e}")
            return "Sorry, I couldn't generate a response. Please try again."

    def generate_response_stream(
        self,
        messages: List[Dict[str, str]],
        container,
        system_prompt: Optional[str] = None,
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
        # Convert messages to the format expected by OpenAI
        openai_messages = []

        # Add system prompt if provided
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})

        # Add the rest of the messages
        for msg in messages:
            openai_messages.append({"role": msg["role"], "content": msg["content"]})

        stream_handler = StreamHandler(container)

        try:
            # Using OpenAI API v0.28.1 syntax for streaming
            response_stream = openai.ChatCompletion.create(
                model=self.model, messages=openai_messages, temperature=0.7, stream=True
            )

            # Process the streaming response for v0.28.1
            for chunk in response_stream:
                if chunk.get("choices") and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta and delta["content"]:
                        stream_handler.update(delta["content"])

            stream_handler.finish()
            return stream_handler.get_text()
        except Exception as e:
            st.error(f"Error generating streaming response: {e}")
            return "Sorry, I couldn't generate a response. Please try again."
