"""
Pydantic schemas defining the shape of API requests and responses.

FastAPI uses these to automatically validate incoming data (rejecting
bad requests before they reach our code) and to document the API.
"""

from pydantic import BaseModel


class AskRequest(BaseModel):
    """What the client must send: just a question, as text."""
    question: str


class Citation(BaseModel):
    """One source document used to answer, with a short snippet of the
    actual retrieved text, so the UI can show more than just a filename."""
    source: str
    snippet: str


class AskResponse(BaseModel):
    """What we send back: the grounded answer, the documents available
    to it, and a richer citations list (source + snippet) for display."""
    answer: str
    sources_available: list[str]
    citations: list[Citation]