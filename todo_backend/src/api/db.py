import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator, Optional

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "todo.db")


def get_db_path() -> str:
    """
    Resolve the database path from environment variable DB_PATH, falling back to a sensible default
    located under src/ directory as todo.db.
    """
    db_path = os.getenv("DB_PATH", "").strip()
    if not db_path:
        return DEFAULT_DB_PATH
    return db_path


def _ensure_parent_dir(path: str) -> None:
    """Ensure the parent directory of the DB file exists."""
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def initialize_db() -> None:
    """
    Initialize the SQLite database with the required schema if it doesn't already exist.
    Creates a 'todos' table with fields: id, title, description, completed, created_at, updated_at.
    """
    db_path = get_db_path()
    _ensure_parent_dir(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """
    Context manager to get a SQLite connection with row factory set to sqlite3.Row.
    Ensures foreign keys and WAL mode are configured for better concurrency.
    """
    db_path = get_db_path()
    _ensure_parent_dir(db_path)
    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # Recommended pragmas
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        yield conn
        conn.commit()
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()
