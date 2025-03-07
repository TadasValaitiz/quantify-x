from typing import Dict, Optional
from database.chat_database import ChatDatabase
import streamlit as st
from shared.types import ChatMessage, TradingContextCollection, ContextDict


class ChatService:
    def __init__(self, conversation_id: int):
        self.conversation_id = conversation_id
        self.db = ChatDatabase()

    def get_messages(self):
        messages: list[ChatMessage] = st.session_state.get(
            "conversation_messages", {}
        ).get(self.conversation_id, [])

        if not messages:
            messages = self.db.get_messages(self.conversation_id)
            if "conversation_messages" not in st.session_state:
                st.session_state["conversation_messages"] = {}
            st.session_state["conversation_messages"][self.conversation_id] = messages

        return messages

    def add_user_message(self, content: str):
        message = ChatMessage.new_message(self.conversation_id, "user", content, None)
        self.db.add_message(message)
        self.append_session_state(message)
        return message

    def add_assistant_message(self, content: str, context: Optional[ContextDict]):
        message = ChatMessage.new_message(
            self.conversation_id, "assistant", content, context
        )
        self.db.add_message(message)
        self.append_session_state(message)
        if context:
            self.update_conversation_context(context)
            self.db.update_conversation_context(self.conversation_id, context)

        return message

    def add_context_message(self, context: ContextDict):
        message = ChatMessage.new_message(self.conversation_id, "ai", "", context)
        self.db.add_message(message)
        self.append_session_state(message)
        return message

    def append_session_state(self, value: ChatMessage):
        if "conversation_messages" not in st.session_state:
            st.session_state["conversation_messages"] = {}
        if self.conversation_id not in st.session_state["conversation_messages"]:
            st.session_state["conversation_messages"][self.conversation_id] = []
        st.session_state["conversation_messages"][self.conversation_id].append(value)

    def update_conversation_context(self, value: ContextDict):
        if "conversation_context" not in st.session_state:
            st.session_state["conversation_context"] = {}
        st.session_state["conversation_context"][self.conversation_id] = value
