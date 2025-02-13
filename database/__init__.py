"""
Database package for handling SQLite and ChromaDB operations.
"""

__all__ = ["Database", "ChromaDB"]


def __getattr__(name):
    if name == "Database":
        from .database import Database

        return Database
    elif name == "ChromaDB":
        from .chroma import ChromaDB

        return ChromaDB
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
