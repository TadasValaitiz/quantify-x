import streamlit as st
from auth.types import FirebaseUserDict
from typing import Optional
from database.types import ChatMessage
from services import ConversationService,ChatService


def render_page_content(
    user_info: Optional[FirebaseUserDict],
    conversation_service: ConversationService,
):
    print(f"render: {st.session_state}")

    if user_info is None:
        st.write("Please log in to continue.")
    else:
        render_conversation(conversation_service)

def render_conversation(conversation_service: ConversationService):
    current_conversation_id = st.session_state.current_conversation_id
    if current_conversation_id is None:
        st.title("No Conversation Selected")
    else:
        chat_service = ChatService(current_conversation_id)
        render_chat_messages(chat_service)
        chat_input(chat_service)

def chat_input(chat_service: ChatService):
    if user_message := st.chat_input("Type your message here..."):
        chat_service.add_user_message(user_message)
        with st.chat_message("user"):
            st.write(user_message)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                st.write("assistant message")
        st.rerun()

def render_chat_messages(chat_service: ChatService):
    for message in chat_service.get_messages():
        with st.chat_message(message.role):
            st.write(message.content)
