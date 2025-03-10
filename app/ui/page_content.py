import streamlit as st
from auth import FirebaseUserDict, FirebaseAuth
from typing import Optional
from shared import ContextDict
from services import ConversationService, ChatService, AIService, StreamHandler
from ui.login import login_page
from database import ChatDatabase


def render_page_content(
    user_info: Optional[FirebaseUserDict],
    conversation_service: ConversationService,
    ai_service: AIService,
    firebase_auth: FirebaseAuth,
    db: ChatDatabase,
):

    if user_info is None:
        login_page(firebase_auth, db)
    else:
        render_conversation(conversation_service, ai_service)


def render_conversation(
    conversation_service: ConversationService, ai_service: AIService
):
    current_conversation_id = st.session_state.current_conversation_id
    if current_conversation_id is None:
        st.title("No Conversation Selected")
    else:
        context = conversation_service.get_conversation_context(current_conversation_id)
        chat_service = ChatService(current_conversation_id)
        render_chat_messages(chat_service)
        chat_input(chat_service, ai_service, context)


def chat_input(
    chat_service: ChatService, ai_service: AIService, context: Optional[ContextDict]
):
    if user_message := st.chat_input("Type your message here..."):
        message = chat_service.add_user_message(user_message)
        with st.chat_message("user"):
            st.write(user_message)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                handler = StreamHandler()
                print(f"Generating response for message: {message.content}")
                response = ai_service.generate_response_stream(
                    message=message.content,
                    initial_context=context,
                    stream_handler=handler,
                )
                print(f"Response: {response}")
                if isinstance(response, ContextDict):
                    ctx: ContextDict = response
                    lastAnswer = response.last_qa_answer()
                    content = lastAnswer if lastAnswer else "No answer found"
                    message = chat_service.add_assistant_message(content, ctx)
                    st.markdown(message.to_message_str())
                else:
                    message = chat_service.add_error_msg(response)
                    st.markdown(response)
        st.rerun()


def render_chat_messages(chat_service: ChatService):
    for message in chat_service.get_messages():
        with st.chat_message(message.role):
            st.markdown(message.to_message_str())
