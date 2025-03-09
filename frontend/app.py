import os
import time
import streamlit as st
from typing import Dict, Any, Optional, List

# Internal modules
from auth import FirebaseAuth
from database import ChatDatabase
from services import AIService, ConversationService
from ui import (
    apply_theme,
    render_sidebar,
    render_chat,
    render_navbar,
    get_streaming_container,
    render_page_content,
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

# # Apply custom theme
# apply_theme()

# Initialize session state
init_session_state()

# Initialize database and services
db = ChatDatabase()
firebase_auth = FirebaseAuth()  # Keep FirebaseAuth for compatibility
ai_service = AIService()
conversation_service = ConversationService(db, firebase_auth)


def handle_login():
    """Handle user login."""
    # Use Firebase auth for now
    success, user_info = firebase_auth.anonymous_login()

    if success and user_info:
        # Create or retrieve user in the database
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
    firebase_auth.logout()
    st.session_state.current_conversation_id = None
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
    current_user = firebase_auth.get_current_user()

    # Render navigation bar
    render_navbar(
        user_info=current_user, on_login=handle_login, on_logout=handle_logout
    )

    # Get user conversations (if logged in)

    # Render sidebar with conversations
    render_sidebar(user_info=current_user, conversation_service=conversation_service)
    # Render chat interface
    render_page_content(
        user_info=current_user,
        conversation_service=conversation_service,
        ai_service=ai_service,
        firebase_auth=firebase_auth,
    )


if __name__ == "__main__":
    main()
