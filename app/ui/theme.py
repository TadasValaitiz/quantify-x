import streamlit as st
from typing import Dict, Any, Optional

# Default dark theme colors
DARK_THEME = {
    "primary": "#6C63FF",  # Purple for primary actions
    "secondary": "#4E4B70",  # Lighter purple for secondary elements
    "background": "#1E1E2E",  # Dark blue/purple for main background
    "surface": "#292A3E",  # Slightly lighter background for cards
    "text": "#E6E6FA",  # Light lavender for text
    "success": "#00BFA5",  # Teal for success messages
    "error": "#F07178",  # Coral for errors
    "warning": "#FFCB6B",  # Amber for warnings
    "info": "#82AAFF",  # Light blue for information
    "chat_user": "#6C63FF",  # User message bubble color
    "chat_bot": "#4E4B70",  # Bot message bubble color
    "sidebar": "#292A3E",  # Sidebar background color
    "border": "#3F3F5F",  # Border color
}


def apply_theme(custom_theme: Optional[Dict[str, str]] = None) -> None:
    """
    Apply theme to the Streamlit app.

    Args:
        custom_theme: Optional custom theme that overrides the default dark theme
    """
    # Use default theme if no custom theme is provided
    theme = DARK_THEME.copy()
    if custom_theme:
        theme.update(custom_theme)

    # Apply theme to Streamlit
    st.markdown(
        f"""
    <style>
        :root {{
            --primary-color: {theme["primary"]};
            --secondary-color: {theme["secondary"]};
            --background-color: {theme["background"]};
            --surface-color: {theme["surface"]};
            --text-color: {theme["text"]};
            --success-color: {theme["success"]};
            --error-color: {theme["error"]};
            --warning-color: {theme["warning"]};
            --info-color: {theme["info"]};
            --chat-user-color: {theme["chat_user"]};
            --chat-bot-color: {theme["chat_bot"]};
            --sidebar-color: {theme["sidebar"]};
            --border-color: {theme["border"]};
        }}
        
        /* Main page background */
        .stApp {{
            background-color: var(--background-color);
            color: var(--text-color);
        }}
        
        /* Sidebar styling */
        .css-1d391kg, .css-12oz5g7 {{
            background-color: var(--sidebar-color);
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-color);
        }}
        
        /* Input fields */
        .stTextInput > div > div > input {{
            background-color: var(--surface-color);
            color: var(--text-color);
            border-color: var(--border-color);
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: var(--primary-color);
            color: var(--text-color);
            border: none;
        }}
        
        .stButton > button:hover {{
            background-color: var(--secondary-color);
        }}
        
        /* Chat message bubbles */
        .user-message {{
            background-color: var(--chat-user-color);
            color: white;
            border-radius: 15px 15px 0 15px;
            padding: 10px 15px;
            margin-bottom: 10px;
            max-width: 80%;
            margin-left: auto;
            margin-right: 10px;
        }}
        
        .bot-message {{
            background-color: var(--chat-bot-color);
            color: white;
            border-radius: 15px 15px 15px 0;
            padding: 10px 15px;
            margin-bottom: 10px;
            max-width: 80%;
            margin-left: 10px;
        }}
        
        /* Dividers */
        hr {{
            border-color: var(--border-color);
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def get_theme_colors() -> Dict[str, str]:
    """
    Get the current theme colors.

    Returns:
        Dictionary of theme colors
    """
    return DARK_THEME.copy()
