from database import ChatDatabase
import streamlit as st
from auth.firebase_auth import FirebaseAuth
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
        st.rerun()

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

    def get_conversations(self):
        """Get all conversations for the current user."""
        current_user = self.auth.get_current_user()
        if not current_user:
            raise ValueError("Please log in to get conversations.")

        return self.db.get_user_conversations(current_user.get("localId"))
