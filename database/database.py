import sqlite3
import json
from typing import List
from scraper.discord_types import MessageType


class Database:
    def __init__(self, db_path: str = "messages.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS discord_md_raw (
                    id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author_id TEXT NOT NULL,
                    author_username TEXT NOT NULL,
                    author_global_name TEXT,
                    attachments_json TEXT,
                    reactions_json TEXT,
                    raw_json TEXT NOT NULL,
                    flags INTEGER NOT NULL DEFAULT 0,
                    message_reference_json TEXT,
                    thread_json TEXT,
                    thread_message BOOLEAN GENERATED ALWAYS AS (message_reference_json IS NOT NULL),
                    has_thread BOOLEAN GENERATED ALWAYS AS (thread_json IS NOT NULL)
                )
            """
            )
            self.conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp ON discord_md_raw (timestamp)
            """
            )
            self.conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_channel ON discord_md_raw (channel_id)
            """
            )
            self.conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_flags ON discord_md_raw (flags)
            """
            )
            self.conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_thread_message ON discord_md_raw (thread_message)
            """
            )
            self.conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_has_thread ON discord_md_raw (has_thread)
            """
            )

    def insert_message(self, message: MessageType):
        with self.conn:
            self.conn.execute(
                """
                INSERT OR IGNORE INTO discord_md_raw (
                    id, channel_id, timestamp, content,
                    author_id, author_username, author_global_name,
                    attachments_json, reactions_json, raw_json,
                    flags, message_reference_json, thread_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    message["id"],
                    message["channel_id"],
                    message["timestamp"],
                    message["content"],
                    message["author"]["id"],
                    message["author"]["username"],
                    message["author"].get("global_name"),
                    json.dumps(message.get("attachments", [])),
                    json.dumps(message.get("reactions", [])),
                    json.dumps(message),
                    message.get("flags", 0),
                    json.dumps(message.get("message_reference")),
                    json.dumps(message.get("thread")),
                ),
            )

    def message_count(self):
        with self.conn:
            cursor = self.conn.execute("SELECT COUNT(*) FROM discord_md_raw")
            return cursor.fetchone()[0]

    def close(self):
        self.conn.close()
