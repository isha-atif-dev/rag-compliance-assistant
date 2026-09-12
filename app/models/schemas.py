"""
Pydantic schemas defining the shape of API requests and responses.

FastAPI uses these to automatically validate incoming data (rejecting
bad requests before they reach our code) and to document the API.
"""

from pydantic import BaseModel


class AskRequest(BaseModel):
    """What the client must send: just a question, as text."""
    question: str


class AskResponse(BaseModel):
    """What we send back: the grounded answer, plus which documents were available to it."""
    answer: str
    sources_available: list[str]