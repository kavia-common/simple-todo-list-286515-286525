from datetime import datetime
from typing import Any, Dict, List, Optional

from .db import get_connection


def _row_to_dict(row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_todos() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT id, title, description, completed, created_at, updated_at FROM todos ORDER BY id DESC"
        )
        rows = cur.fetchall()
        return [_row_to_dict(r) for r in rows]


def get_todo(todo_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT id, title, description, completed, created_at, updated_at FROM todos WHERE id = ?",
            (todo_id,),
        )
        row = cur.fetchone()
        return _row_to_dict(row) if row else None


def create_todo(title: str, description: str = "", completed: bool = False) -> Dict[str, Any]:
    with get_connection() as conn:
        now = datetime.utcnow().isoformat(timespec="seconds")
        cur = conn.execute(
            """
            INSERT INTO todos (title, description, completed, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, description or "", int(bool(completed)), now, now),
        )
        new_id = cur.lastrowid
        cur = conn.execute(
            "SELECT id, title, description, completed, created_at, updated_at FROM todos WHERE id = ?",
            (new_id,),
        )
        row = cur.fetchone()
        return _row_to_dict(row)


def update_todo(todo_id: int, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not fields:
        return get_todo(todo_id)

    set_clauses = []
    params: List[Any] = []
    if "title" in fields and fields["title"] is not None:
        set_clauses.append("title = ?")
        params.append(fields["title"])
    if "description" in fields and fields["description"] is not None:
        set_clauses.append("description = ?")
        params.append(fields["description"])
    if "completed" in fields and fields["completed"] is not None:
        set_clauses.append("completed = ?")
        params.append(int(bool(fields["completed"])))

    if not set_clauses:
        return get_todo(todo_id)

    # Always update updated_at
    set_clauses.append("updated_at = ?")
    params.append(datetime.utcnow().isoformat(timespec="seconds"))

    params.append(todo_id)

    with get_connection() as conn:
        cur = conn.execute(f"UPDATE todos SET {', '.join(set_clauses)} WHERE id = ?", params)
        if cur.rowcount == 0:
            return None
        cur = conn.execute(
            "SELECT id, title, description, completed, created_at, updated_at FROM todos WHERE id = ?",
            (todo_id,),
        )
        row = cur.fetchone()
        return _row_to_dict(row) if row else None


def delete_todo(todo_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        return cur.rowcount > 0
