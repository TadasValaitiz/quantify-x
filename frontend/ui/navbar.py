import streamlit as st
from typing import Dict, Any, Optional, Callable
from auth.types import FirebaseUserDict


def render_navbar(
    user_info: Optional[FirebaseUserDict],
    on_login: Callable[[], None],
    on_logout: Callable[[], None],
) -> None:
    """
    Render the top navigation bar with user account functionality.

    Args:
        user_info: User information dictionary or None if not logged in
        on_login: Callback for login action
        on_logout: Callback for logout action
    """
    # Create a container for the navbar
    navbar_container = st.container()

    with navbar_container:
        col1, col2, col3 = st.columns([1, 3, 1])

        # App logo/name
        with col1:
            st.markdown("### 🤖 AI Chat")

        # Spacer
        with col2:
            st.write("")

        # User account section
        with col3:
            if user_info:
                # User is logged in
                login_type = user_info.get("login_type", "anonymous")
                name = user_info.get("name", "Anonymous User")

                # Display user info and logout button
                with st.expander(f"👤 {name}"):
                    st.write(f"Login: {login_type}")
                    if st.button("Logout", key="logout_btn"):
                        on_logout()
            else:
                # User is not logged in
                if st.button("Login", key="login_btn"):
                    on_login()

    # Add a separator below the navbar
    st.markdown("---")
