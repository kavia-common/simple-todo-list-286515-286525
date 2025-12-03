# Todo Backend (FastAPI)

This service provides CRUD APIs for a Todo app, persisting data in SQLite.

How the database is resolved:
- The backend checks the environment variable DB_PATH.
- If DB_PATH is not set or empty, it defaults to: simple-todo-list-286515-286525/todo_backend/src/todo.db (relative to the repo root).
- On startup, the service initializes the database and ensures the todos table exists.

Environment variables:
- DB_PATH: Absolute or relative path to a SQLite file (e.g., /workspace/database/myapp.db).

Quick start:
1) Install deps (inside backend container/env):
   pip install -r requirements.txt
2) Run the server:
   uvicorn src.api.main:app --host 0.0.0.0 --port 3001
3) Check health:
   GET http://localhost:3001/
4) Inspect config (see resolved DB path):
   GET http://localhost:3001/config
5) API docs:
   http://localhost:3001/docs

Notes:
- The todos table is created automatically if missing.
- Response models include id, title, optional description, completed, created_at, updated_at.
