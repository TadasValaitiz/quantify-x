# Import SQLite fix before any other imports
from sqlite_fix import *

import os
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

set_page_config()

env_vars = load_env_vars()
os.environ["OPENAI_API_KEY"] = env_vars["OPENAI_API_KEY"]


init_session_state()

db = ChatDatabase()
firebase_auth = FirebaseAuth()  
ai_service = AIService()
conversation_service = ConversationService(db, firebase_auth)


def handle_logout():
    """Handle user logout."""
    firebase_auth.logout()
    st.session_state.current_conversation_id = None
    st.rerun()


def main():
    """Main application function."""
    current_user = firebase_auth.get_current_user()
    
    render_navbar(user_info=current_user, on_logout=handle_logout)
    
    render_sidebar(user_info=current_user, conversation_service=conversation_service)
    
    render_page_content(
        user_info=current_user,
        conversation_service=conversation_service,
        ai_service=ai_service,
        firebase_auth=firebase_auth,
        db=db,
    )


if __name__ == "__main__":
    main()
