import os
import time
import streamlit as st
from typing import Dict, Any, Optional, List
from auth import FirebaseAuth, FirebaseUserDict
from database import ChatDatabase
from services import AIService, ConversationService
from ui import (
    render_sidebar,
    render_navbar,
    render_page_content,
)
from utils import (
    load_env_vars,
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


def handle_logout():
    """Handle user logout."""
    firebase_auth.logout()
    st.session_state.current_conversation_id = None
    st.rerun()


def main():
    """Main application function."""
    # Get current user if logged in
    current_user = firebase_auth.get_current_user()

    # Render navigation bar
    render_navbar(user_info=current_user, on_logout=handle_logout)

    # Get user conversations (if logged in)

    # Render sidebar with conversations
    render_sidebar(user_info=current_user, conversation_service=conversation_service)
    # Render chat interface
    render_page_content(
        user_info=current_user,
        conversation_service=conversation_service,
        ai_service=ai_service,
        firebase_auth=firebase_auth,
        db=db,
    )


if __name__ == "__main__":
    main()
