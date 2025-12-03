import os
from typing import List

from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .db import initialize_db, get_db_path
from .models import Todo, TodoCreate, TodoUpdate
from .repository import create_todo, delete_todo, get_todo, list_todos, update_todo

# Initialize DB on startup
initialize_db()


class HealthResponse(BaseModel):
    message: str = Field(..., description="Health status message")


openapi_tags = [
    {
        "name": "health",
        "description": "Service readiness and health checks.",
    },
    {
        "name": "todos",
        "description": "CRUD operations for todo items.",
    },
]

app = FastAPI(
    title="Todo Backend API",
    description=(
        "FastAPI backend for a simple todo application. Provides CRUD operations for todos, "
        "persisted in SQLite. The database path can be configured via the DB_PATH environment variable."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# Keep CORS permissive for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, scope this more tightly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get(
    "/",
    response_model=HealthResponse,
    summary="Health Check",
    tags=["health"],
    responses={
        200: {"description": "Service is healthy"},
    },
)
def health_check():
    """
    Health check endpoint to verify that the service is running.

    Returns:
        HealthResponse: JSON containing a simple status message.
    """
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get(
    "/config",
    summary="Runtime configuration",
    description="Return current backend configuration helpful for debugging.",
    tags=["health"],
)
def get_config():
    """
    Returns configuration details that are safe to expose for debugging.

    Returns:
        dict: includes resolved SQLite DB path.
    """
    return {
        "db_path": get_db_path(),
        "env_db_path": os.getenv("DB_PATH", None),
    }


# PUBLIC_INTERFACE
@app.get(
    "/todos",
    response_model=List[Todo],
    summary="List all todos",
    description="Retrieve all todo items, ordered by newest first.",
    tags=["todos"],
)
def api_list_todos():
    """
    List all todo items from the database.

    Returns:
        List[Todo]: Array of todo items.
    """
    return list_todos()


# PUBLIC_INTERFACE
@app.post(
    "/todos",
    response_model=Todo,
    summary="Create a new todo",
    description="Create a new todo item with a title, optional description, and completion state.",
    tags=["todos"],
    status_code=201,
)
def api_create_todo(payload: TodoCreate):
    """
    Create a new todo item.

    Parameters:
        payload (TodoCreate): Title (required), description (optional), completed (optional).

    Returns:
        Todo: The created todo item with ID and timestamps.
    """
    created = create_todo(
        title=payload.title,
        description=payload.description or "",
        completed=payload.completed,
    )
    return created


# PUBLIC_INTERFACE
@app.get(
    "/todos/{todo_id}",
    response_model=Todo,
    summary="Get a todo by ID",
    description="Retrieve a single todo item by its unique identifier.",
    tags=["todos"],
)
def api_get_todo(
    todo_id: int = Path(..., ge=1, description="ID of the todo item"),
):
    """
    Get a single todo.

    Parameters:
        todo_id (int): ID of the todo to fetch.

    Returns:
        Todo: The todo item if found.

    Raises:
        HTTPException 404: If the todo does not exist.
    """
    item = get_todo(todo_id)
    if not item:
        raise HTTPException(status_code=404, detail="Todo not found")
    return item


# PUBLIC_INTERFACE
@app.patch(
    "/todos/{todo_id}",
    response_model=Todo,
    summary="Update fields of a todo",
    description="Partially update one or more fields (title, description, completed) of a todo item.",
    tags=["todos"],
)
def api_update_todo(
    todo_id: int = Path(..., ge=1, description="ID of the todo item"),
    payload: TodoUpdate = ...,
):
    """
    Update a todo item.

    Parameters:
        todo_id (int): ID of the todo to update.
        payload (TodoUpdate): Fields to update.

    Returns:
        Todo: The updated todo item.

    Raises:
        HTTPException 404: If the todo does not exist.
    """
    updated = update_todo(todo_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated


# PUBLIC_INTERFACE
@app.delete(
    "/todos/{todo_id}",
    summary="Delete a todo",
    description="Delete a todo item by its ID.",
    tags=["todos"],
    status_code=204,
    responses={
        204: {"description": "Successfully deleted"},
        404: {"description": "Todo not found"},
    },
)
def api_delete_todo(
    todo_id: int = Path(..., ge=1, description="ID of the todo item"),
):
    """
    Delete a todo item.

    Parameters:
        todo_id (int): ID of the todo to delete.

    Returns:
        None: Empty body with 204 status upon success.

    Raises:
        HTTPException 404: If the todo does not exist.
    """
    ok = delete_todo(todo_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Todo not found")
    return None
