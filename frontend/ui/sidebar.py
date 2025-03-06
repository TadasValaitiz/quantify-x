import streamlit as st
from typing import List, Dict, Any, Optional, Callable
import datetime
from auth.types import FirebaseUserDict
from services import ConversationService


def render_sidebar(
    user_info: Optional[FirebaseUserDict],
    conversation_service: ConversationService,
) -> None:
    """
    Render the sidebar with conversation list and controls.

    Args:
        conversations: List of conversation dictionaries
        on_select_conversation: Callback for when a conversation is selected
        on_new_conversation: Callback for creating a new conversation
        on_delete_conversation: Callback for deleting a conversation
        current_conversation_id: Currently selected conversation ID
    """
    with st.sidebar:
        if user_info is not None:
            render_conversation_list(conversation_service)


def render_conversation_list(conversation_service: ConversationService):
    current_conversation_id = st.session_state.current_conversation_id
    if st.button(
        "New Conversation", key="new_conversation_btn", use_container_width=True
    ):
        conversation_service.handle_new_conversation()
        st.rerun()

    # Conversations list
    conversations = conversation_service.get_conversations()
    if not conversations:
        st.info("No conversations yet. Start a new one!")
    else:
        for conv in conversations:
            col1, col2 = st.columns([5, 1])

            # Format conversation display
            conv_id = conv["id"]
            conv_name = conv["name"]
            updated_at = datetime.datetime.fromisoformat(conv["updated_at"])
            updated_str = updated_at.strftime("%b %d, %H:%M")

            # Highlight current conversation
            if current_conversation_id == conv_id:
                conv_name = f"**{conv_name}**"

            # Conversation button
            with col1:
                if st.button(
                    f"{conv_name}",
                    key=f"conv_{conv_id}",
                    use_container_width=True,
                ):
                    conversation_service.handle_select_conversation(conv_id)
                    st.rerun()

            # Delete button
            with col2:
                if st.button("🗑️", key=f"yes_{conv_id}"):
                    conversation_service.handle_delete_conversation(conv_id)
                    st.rerun()
