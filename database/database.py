from shared import MessageType, StrategyType, TradingStrategyDefinition
import sqlite3
import json
from typing import List, Optional, Dict, Any, Union, TypedDict, cast
from datetime import datetime, timezone


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
                CREATE TABLE IF NOT EXISTS discord_strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    flags INTEGER NOT NULL DEFAULT 0,
                    reactions INTEGER NOT NULL DEFAULT 0,
                    content TEXT NOT NULL,
                    strategy_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
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

    def get_messages(self, timestamp_from: Optional[int] = None) -> List[MessageType]:
        with self.conn:
            if timestamp_from is not None:
                # Convert Unix timestamp (milliseconds) to ISO 8601 string format
                # If timestamp is in seconds, convert to milliseconds
                if (
                    timestamp_from < 10**12
                ):  # Heuristic to detect seconds vs milliseconds
                    timestamp_from *= 1000
                dt = datetime.fromtimestamp(timestamp_from / 1000.0, tz=timezone.utc)
                timestamp_str = dt.isoformat()

                cursor = self.conn.execute(
                    "SELECT raw_json FROM discord_md_raw WHERE timestamp >= ? ORDER BY timestamp DESC",
                    (timestamp_str,),
                )
            else:
                cursor = self.conn.execute(
                    "SELECT raw_json FROM discord_md_raw WHERE timestamp < '2024-11-17T22:12:26.787000+00:00' ORDER BY timestamp DESC"
                )

            messages: List[MessageType] = []
            for row in cursor.fetchall():
                # Convert the JSON string back to a MessageType dict
                message_dict = json.loads(row[0])
                messages.append(message_dict)

            return messages

    def insert_strategy(self, strategy: StrategyType):
        """
        Insert a strategy into the database.
        Returns the ID of the newly inserted strategy.
        """
        current_time = datetime.now(timezone.utc).isoformat()
        with self.conn:
            cursor = self.conn.execute(
                """
                INSERT INTO discord_strategies (
                    message_id, timestamp, flags, reactions, content, strategy_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    strategy["message_id"],
                    strategy["timestamp"],
                    strategy["flags"],
                    strategy["reactions"],
                    strategy["content"],
                    strategy["strategy"].model_dump_json(),
                    current_time,
                ),
            )
            return cursor.lastrowid

    def get_strategy(self, strategy_id: int) -> Optional[StrategyType]:
        """
        Get a specific strategy by ID.
        Returns None if not found.
        """
        cursor = self.conn.execute(
            """
            SELECT id, message_id, timestamp, flags, reactions, content, strategy_json 
            FROM discord_strategies
            WHERE id = ?
            """,
            (strategy_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "message_id": row[1],
            "timestamp": row[2],
            "flags": row[3],
            "reactions": row[4],
            "content": row[5],
            "strategy": TradingStrategyDefinition(**json.loads(row[6])),
        }

    def list_strategies(self, limit: int = 100, offset: int = 0) -> List[StrategyType]:
        """
        List strategies with pagination.
        """
        cursor = self.conn.execute(
            """
            SELECT id, message_id, timestamp, flags, reactions, content, strategy_json 
            FROM discord_strategies
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )

        strategies = []
        for row in cursor:
            strategies.append(
                {
                    "id": row[0],
                    "message_id": row[1],
                    "timestamp": row[2],
                    "flags": row[3],
                    "reactions": row[4],
                    "content": row[5],
                    "strategy": TradingStrategyDefinition(**json.loads(row[6])),
                }
            )

        return strategies

    def list_strategies_by_ids(self, ids: List[int]) -> List[StrategyType]:
        """
        List strategies that match the given IDs.

        Args:
            ids: List of strategy IDs to retrieve

        Returns:
            List of matching strategies
        """
        if not ids:
            return []

        placeholders = ",".join("?" * len(ids))
        query = f"""
            SELECT id, message_id, timestamp, flags, reactions, content, strategy_json 
            FROM discord_strategies 
            WHERE id IN ({placeholders})
            ORDER BY timestamp DESC
        """

        cursor = self.conn.execute(query, ids)

        return [
            {
                "id": row[0],
                "message_id": row[1],
                "timestamp": row[2],
                "flags": row[3],
                "reactions": row[4],
                "content": row[5],
                "strategy": TradingStrategyDefinition(**json.loads(row[6])),
            }
            for row in cursor
        ]

    def get_strag(self, strat_id: int) -> Optional[StrategyType]:
        """
        Shorthand method for get_strategy.

        Args:
            strat_id: ID of the strategy to retrieve

        Returns:
            Strategy if found, None otherwise
        """
        return self.get_strategy(strat_id)

    def get_strag_by_msg(self, message_id: str) -> Optional[StrategyType]:
        """
        Get a strategy by its associated message ID.

        Args:
            message_id: The message ID to look up

        Returns:
            Strategy if found, None otherwise
        """
        cursor = self.conn.execute(
            """
            SELECT id, message_id, timestamp, flags, reactions, content, strategy_json 
            FROM discord_strategies
            WHERE message_id = ?
            LIMIT 1
            """,
            (message_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "message_id": row[1],
            "timestamp": row[2],
            "flags": row[3],
            "reactions": row[4],
            "content": row[5],
            "strategy": TradingStrategyDefinition(**json.loads(row[6])),
        }

    def strategy_count(self) -> int:
        """
        Return the total number of strategies in the database.
        """
        cursor = self.conn.execute("SELECT COUNT(*) FROM discord_strategies")
        return cursor.fetchone()[0]

    def delete_strategy(self, strategy_id: int) -> bool:
        """
        Delete a strategy from the database.

        Args:
            strategy_id: ID of the strategy to delete

        Returns:
            True if strategy was deleted, False otherwise
        """
        with self.conn:
            cursor = self.conn.execute(
                "DELETE FROM discord_strategies WHERE id = ?", (strategy_id,)
            )
            return cursor.rowcount > 0

    def close(self):
        self.conn.close()
