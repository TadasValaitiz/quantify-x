from typing import Optional
from database import ChatDatabase
import streamlit as st
from auth import FirebaseAuth
from shared import ContextDict
from utils import (
    load_env_vars,
    generate_conversation_name,
    init_session_state,
    set_page_config,
)


class ConversationService:
    def __init__(self, db: ChatDatabase, auth: FirebaseAuth):
        self.db = db
        self.auth = auth

    def handle_new_conversation(self):
        """Create a new conversation."""
        current_user = self.auth.get_current_user()

        if not current_user:
            raise ValueError("Please log in to start a conversation.")

        name = generate_conversation_name()
        conv_id = self.db.create_conversation(
            user_id=current_user.get("localId"), name=name
        )

        st.session_state.current_conversation_id = conv_id

    def handle_select_conversation(self, conversation_id: int):
        """Handle selecting a conversation."""
        st.session_state.current_conversation_id = conversation_id

    def handle_delete_conversation(self, conversation_id: int):
        """Handle deleting a conversation."""
        self.db.delete_conversation(conversation_id)

        if st.session_state.current_conversation_id == conversation_id:
            st.session_state.current_conversation_id = None

    def handle_rename_conversation(self, new_name: str):
        """Handle renaming a conversation."""
        if not st.session_state.current_conversation_id:
            return

        self.db.update_conversation(
            conversation_id=st.session_state.current_conversation_id, name=new_name
        )

    def get_conversation_context(self, conversation_id: int) -> Optional[ContextDict]:
        """Get a conversation by its ID.

        Args:
            conversation_id: The ID of the conversation to retrieve

        Returns:
            The conversation data dictionary or None if not found
        """
        dict = self.db.get_conversation(conversation_id)
        if dict and dict.get("context"):
            context = dict.get("context", {})
            user_strategy = context.get("user_strategy", None)
            rag_strategies = context.get("rag_strategies", [])
            route = context.get("route", None)
            conversations = context.get("conversations", [])
            evaluation = context.get("evaluation", None)

            return ContextDict(
                user_strategy=user_strategy,
                rag_strategies=rag_strategies,
                route=route,
                conversations=conversations,
                evaluation=evaluation,
            )
        return None

    def get_conversations(self):
        """Get all conversations for the current user."""
        current_user = self.auth.get_current_user()
        if not current_user:
            raise ValueError("Please log in to get conversations.")

        # Get user ID and convert it to the required type
        user_id = current_user.get("localId")
        # Here we're assuming the database expects an integer user ID
        # You'll need to modify this based on your actual database implementation
        return self.db.get_user_conversations(user_id)
