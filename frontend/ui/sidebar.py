import streamlit as st
from typing import List, Dict, Any, Optional, Callable
import datetime


def render_sidebar(
    conversations: List[Dict[str, Any]],
    on_select_conversation: Callable[[int], None],
    on_new_conversation: Callable[[], None],
    on_delete_conversation: Callable[[int], None],
    current_conversation_id: Optional[int] = None,
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
        st.title("Conversations")

        # New conversation button
        if st.button(
            "New Conversation", key="new_conversation_btn", use_container_width=True
        ):
            on_new_conversation()

        st.markdown("---")

        # Conversations list
        if not conversations:
            st.info("No conversations yet. Start a new one!")
        else:
            for conv in conversations:
                col1, col2 = st.columns([4, 1])

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
                        f"{conv_name}\n{updated_str}",
                        key=f"conv_{conv_id}",
                        use_container_width=True,
                    ):
                        on_select_conversation(conv_id)

                # Delete button
                with col2:
                    if st.button("🗑️", key=f"del_{conv_id}"):
                        # Instead of nested columns for confirmation, use the session state
                        if "confirm_delete" not in st.session_state:
                            st.session_state.confirm_delete = None

                        # If already confirming, delete it
                        if st.session_state.confirm_delete == conv_id:
                            on_delete_conversation(conv_id)
                            st.session_state.confirm_delete = None
                            st.rerun()
                        else:
                            # Set as confirming
                            st.session_state.confirm_delete = conv_id
                            st.rerun()

                # Show confirmation UI outside the columns
                if st.session_state.get("confirm_delete") == conv_id:
                    st.warning(f"Delete '{conv_name}'?")
                    if st.button("Yes, delete", key=f"yes_{conv_id}"):
                        on_delete_conversation(conv_id)
                        st.session_state.confirm_delete = None
                        st.rerun()
                    if st.button("No, cancel", key=f"no_{conv_id}"):
                        st.session_state.confirm_delete = None
                        st.rerun()

                st.markdown("---")
