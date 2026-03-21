"""Pydantic schemas for debate API."""
from pydantic import BaseModel


class DebateSchema(BaseModel):
    """Debate request/response schema."""
    topic: str
