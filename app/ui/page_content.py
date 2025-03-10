import streamlit as st
from shared import ChatMessage, ContextDict
from auth import FirebaseUserDict, FirebaseAuth
from typing import Optional
from services import ConversationService, ChatService, AIService, StreamHandler
from ui.login import login_page
from database import ChatDatabase

welcome = """

Your AI-powered assistant for developing and evaluating trading strategies.

### What You Can Do:

* **Build Trading Strategies** - Create custom strategies with specific entry/exit conditions
* **Research Technical Indicators** - Learn about indicators and how to apply them effectively
* **Evaluate Performance** - Get AI-powered feedback on your strategy's strengths and weaknesses
* **Compare with Existing Approaches** - See how your ideas stack up against established methods

Start by New Conversation and describe your trading idea!
"""

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
        st.markdown(welcome)
        if st.button("Start New Conversation"):
            conversation_service.handle_new_conversation()
            st.rerun()
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
                response = ai_service.generate_response_stream(
                    message=message.content,
                    initial_context=context,
                    stream_handler=handler,
                )
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
        render_chat_message(message)

def render_chat_message(message: ChatMessage):
    if message.role == "assistant" and message.context is not None:
        if len(message.context.rag_strategies) >0:
                with st.chat_message(message.role):
                        for strategy in message.context.rag_strategies:
                            with st.expander("RAG Strategies"):
                                st.markdown(strategy.message_str())
        if message.context.user_strategy is not None:
                with st.chat_message(message.role):
                    with st.expander("User Strategy"):
                        st.markdown(message.context.user_strategy.message_str(short=False))
 
    with st.chat_message(message.role):
            st.markdown(message.to_message_str())