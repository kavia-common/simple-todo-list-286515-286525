from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    title: str = Field(..., description="Short title for the todo item", examples=["Buy milk"])
    description: Optional[str] = Field(
        default="",
        description="Optional extended description or notes for the todo item",
        examples=["Remember to get low-fat milk"],
    )
    completed: bool = Field(
        default=False,
        description="Whether the todo item is marked as completed",
        examples=[False, True],
    )


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated title for the todo item")
    description: Optional[str] = Field(None, description="Updated description for the todo item")
    completed: Optional[bool] = Field(None, description="Updated completion status")


class Todo(TodoBase):
    id: int = Field(..., description="Unique identifier for the todo item", examples=[1])
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
