# AI Chat Application

A Streamlit-based chatbot application using OpenAI's o3-mini model with reasoning display capabilities.

## Features

- 🔒 User authentication (anonymous login)
- 💬 Create, view, and delete conversations
- 🤖 AI chat powered by OpenAI o3-mini model with streaming
- 🎨 Dark theme UI
- 🗃️ Persistent storage with SQLite

## Setup Instructions

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

### Running the Application

Start the Streamlit app:

```
cd frontend
streamlit run app.py
```

## Project Structure

```
frontend/
├── app.py                      # Main Streamlit application entry point
├── database/
│   ├── __init__.py
│   └── database.py             # Database connection and operations
├── auth/
│   ├── __init__.py
│   └── firebase_auth.py        # Authentication logic
├── ui/
│   ├── __init__.py
│   ├── theme.py                # UI theme customization
│   ├── sidebar.py              # Sidebar with conversation list
│   ├── chat.py                 # Chat interface component
│   └── navbar.py               # Top navigation bar
├── services/
│   ├── __init__.py
│   └── ai_service.py           # Integration with OpenAI/LangChain
├── utils/
│   ├── __init__.py
│   └── helpers.py              # Utility functions
└── requirements.txt            # Project dependencies
```

## Future Enhancements

- Additional social login providers (Google, GitHub, etc.)
- Conversation export/import
- Custom themes and user preferences
- Advanced AI settings (temperature, context window, etc.)
- Support for multiple AI providers

## License

MIT
