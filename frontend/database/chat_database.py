import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from shared.types import ChatMessage, ContextDict


class ChatDatabase:
    def __init__(self, db_path: str = "data/frontend.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        cursor = self.connection.cursor()

        # Create users table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            name TEXT,
            login_type TEXT DEFAULT 'anonymous',
            auth_provider TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        # Create conversations table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
        )

        # Create messages table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
        """
        )

        self.connection.commit()

    # User methods
    def create_user(
        self,
        id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        login_type: str = "anonymous",
        auth_provider: Optional[str] = None,
    ) -> int:
        """Create a new user and return their ID."""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()

        cursor.execute(
            """
        INSERT INTO users (id, email, name, login_type, auth_provider, created_at, last_login)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (id, email, name, login_type, auth_provider, now, now),
        )

        self.connection.commit()
        user_id = cursor.lastrowid
        if user_id is None:
            raise ValueError("Failed to create user: no ID returned")
        return user_id

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by their email."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            return dict(user)
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a user by their ID."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if user:
            return dict(user)
        return None

    def update_user_last_login(self, user_id: int) -> None:
        """Update a user's last login timestamp."""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()

        cursor.execute(
            """
        UPDATE users SET last_login = ? WHERE id = ?
        """,
            (now, user_id),
        )

        self.connection.commit()

    # Conversation methods
    def create_conversation(
        self, user_id: int, name: str, context: Optional[Dict] = None
    ) -> int:
        """Create a new conversation and return its ID."""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        context_json = json.dumps(context) if context else None

        cursor.execute(
            """
        INSERT INTO conversations (user_id, name, context, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
            (user_id, name, context_json, now, now),
        )

        self.connection.commit()
        conv_id = cursor.lastrowid
        if conv_id is None:
            raise ValueError("Failed to create conversation: no ID returned")
        return conv_id

    def get_conversation(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """Get a conversation by its ID."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
        conversation = cursor.fetchone()

        if conversation:
            result = dict(conversation)
            if result.get("context"):
                result["context"] = json.loads(result["context"])
            return result
        return None

    def get_user_conversations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all conversations for a user."""
        cursor = self.connection.cursor()
        cursor.execute(
            """
        SELECT * FROM conversations 
        WHERE user_id = ? 
        ORDER BY updated_at DESC
        """,
            (user_id,),
        )

        conversations = []
        for conversation in cursor.fetchall():
            conv_dict = dict(conversation)
            if conv_dict.get("context"):
                conv_dict["context"] = json.loads(conv_dict["context"])
            conversations.append(conv_dict)

        return conversations

    def update_conversation(
        self,
        conversation_id: int,
        name: Optional[str] = None,
        context: Optional[ContextDict] = None,
    ) -> None:
        """Update a conversation's name and/or context."""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)

        if context is not None:
            updates.append("context = ?")
            params.append(json.dumps(context.model_dump()))

        if not updates:
            return

        updates.append("updated_at = ?")
        params.append(now)
        params.append(conversation_id)

        query = f"UPDATE conversations SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)

        self.connection.commit()

    def update_conversation_context(
        self, conversation_id: int, context: ContextDict
    ) -> None:
        """Update only the context of a conversation."""
        name = (
            context.trading_context.strategy_name
            if context.trading_context
            else None
        )
        self.update_conversation(
            conversation_id=conversation_id, name=name, context=context
        )

    def delete_conversation(self, conversation_id: int) -> None:
        """Delete a conversation and all its messages."""
        cursor = self.connection.cursor()

        # Delete all messages in the conversation
        cursor.execute(
            "DELETE FROM messages WHERE conversation_id = ?", (conversation_id,)
        )

        # Delete the conversation
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))

        self.connection.commit()

    # Message methods
    def add_message(self, chat_message: ChatMessage) -> int:
        """Add a message to a conversation and return its ID."""
        cursor = self.connection.cursor()
        now = chat_message.created_at
        context_json = (
            json.dumps(chat_message.context.model_dump())
            if chat_message.context
            else None
        )

        cursor.execute(
            """
        INSERT INTO messages (conversation_id, role, content, context, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
            (
                chat_message.conversation_id,
                chat_message.role,
                chat_message.content,
                context_json,
                chat_message.created_at,
            ),
        )

        # Update the conversation's updated_at timestamp
        cursor.execute(
            """
        UPDATE conversations SET updated_at = ? WHERE id = ?
        """,
            (now, chat_message.conversation_id),
        )

        self.connection.commit()
        msg_id = cursor.lastrowid
        if msg_id is None:
            raise ValueError("Failed to add message: no ID returned")
        return msg_id

    def get_messages(self, conversation_id: int) -> List[ChatMessage]:
        """Get all messages for a conversation."""
        cursor = self.connection.cursor()
        cursor.execute(
            """
        SELECT * FROM messages 
        WHERE conversation_id = ? 
        ORDER BY created_at ASC
        """,
            (conversation_id,),
        )

        messages = []
        for message in cursor.fetchall():
            messages.append(ChatMessage.from_dict(message))

        return messages

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
