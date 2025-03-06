import os
import time
import streamlit as st
from typing import Dict, Any, Optional, List

# Internal modules
from auth import FirebaseAuth
from database import ChatDatabase
from services import AIService
from ui import (
    apply_theme,
    render_sidebar,
    render_chat,
    render_navbar,
    get_streaming_container,
)
from utils import (
    load_env_vars,
    generate_conversation_name,
    init_session_state,
    set_page_config,
)


# Initialize Streamlit page configuration
set_page_config()

# Initialize environment variables
env_vars = load_env_vars()
os.environ["OPENAI_API_KEY"] = env_vars["OPENAI_API_KEY"]

# Apply custom theme
apply_theme()

# Initialize session state
init_session_state()

# Initialize database and services
db = ChatDatabase()
auth = FirebaseAuth()
ai_service = AIService(model="o3-mini-2025-01-31")


def handle_login():
    """Handle user login."""
    success, user_info = auth.anonymous_login()

    print(f"User info: {user_info}")
    if user_info:
        # Create or retrieve user in the databas
        st.session_state.user_id = user_info["localId"]
        user = db.get_user_by_id(user_info["localId"])

        if user:
            # Existing user
            db.update_user_last_login(user["local_id"])
        else:
            # New user
            db.create_user(
                id=user_info["localId"],
                email=user_info["email"],
                name=user_info["name"],
                login_type=user_info["login_type"],
                auth_provider=user_info["auth_provider"],
            )

        time.sleep(1)
        st.rerun()


def handle_logout():
    """Handle user logout."""
    auth.logout()
    st.session_state.user_id = None
    st.session_state.current_conversation_id = None
    st.rerun()


def handle_new_conversation():
    """Create a new conversation."""
    if not st.session_state.user_id:
        st.warning("Please log in to start a conversation.")
        return

    name = generate_conversation_name()
    conv_id = db.create_conversation(user_id=st.session_state.user_id, name=name)

    st.session_state.current_conversation_id = conv_id
    st.rerun()


def handle_select_conversation(conversation_id: int):
    """Handle selecting a conversation."""
    st.session_state.current_conversation_id = conversation_id
    st.rerun()


def handle_delete_conversation(conversation_id: int):
    """Handle deleting a conversation."""
    db.delete_conversation(conversation_id)

    if st.session_state.current_conversation_id == conversation_id:
        st.session_state.current_conversation_id = None

    st.rerun()


def handle_rename_conversation(new_name: str):
    """Handle renaming a conversation."""
    if not st.session_state.current_conversation_id:
        return

    db.update_conversation(
        conversation_id=st.session_state.current_conversation_id, name=new_name
    )

    st.rerun()


def handle_send_message(message_text: str):
    """Handle sending a new message."""
    if not st.session_state.current_conversation_id or not message_text.strip():
        return

    # Add user message to database
    db.add_message(
        conversation_id=st.session_state.current_conversation_id,
        role="user",
        content=message_text,
    )

    # Mark that we're sending a message to avoid rerun issues
    st.session_state.is_sending_message = True
    st.rerun()


def main():
    """Main application function."""
    # Get current user if logged in
    current_user = auth.get_current_user()
    print(f"Current user: {current_user}")

    # Render navigation bar
    render_navbar(
        user_info=current_user, on_login=handle_login, on_logout=handle_logout
    )

    # Get user conversations (if logged in)
    conversations = []
    if current_user:
        conversations = db.get_user_conversations(current_user.get("localId"))

    # Render sidebar with conversations
    render_sidebar(
        conversations=conversations,
        on_select_conversation=handle_select_conversation,
        on_new_conversation=handle_new_conversation,
        on_delete_conversation=handle_delete_conversation,
        current_conversation_id=st.session_state.current_conversation_id,
    )

    # Main content area
    if not st.session_state.user_id:
        st.write("Please log in to start chatting.")
    elif not st.session_state.current_conversation_id:
        st.write("Select or create a conversation to start chatting.")
    else:
        # Get current conversation and messages
        conversation = db.get_conversation(st.session_state.current_conversation_id)
        messages = []

        if conversation:
            messages = db.get_messages(st.session_state.current_conversation_id)

            # Render chat interface
            render_chat(
                messages=messages,
                conversation_name=conversation["name"],
                on_send_message=handle_send_message,
                on_rename_conversation=handle_rename_conversation,
            )

            # Handle AI response if a message was just sent
            if st.session_state.is_sending_message:
                # Get messages for AI context
                ai_messages = [
                    {"role": msg["role"], "content": msg["content"]} for msg in messages
                ]

                # Create streaming container and generate response
                stream_container = get_streaming_container()
                ai_response = ai_service.generate_response_stream(
                    messages=ai_messages, container=stream_container
                )

                # Add AI response to database
                db.add_message(
                    conversation_id=st.session_state.current_conversation_id,
                    role="assistant",
                    content=ai_response,
                )

                # Reset sending flag
                st.session_state.is_sending_message = False
                st.rerun()


if __name__ == "__main__":
    main()
