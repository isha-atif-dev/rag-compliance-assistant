"""
API routes for the RAG pipeline.

Defines the /ask endpoint: takes a question, runs it through hybrid
retrieval and grounded generation, returns the answer with sources.
Requires a valid API key (via verify_api_key) and logs each request.
"""

from fastapi import APIRouter, Depends

from app.models.schemas import AskRequest, AskResponse
from app.services.retrieval import hybrid_search
from app.services.generation import generate_answer
from app.core.config import verify_api_key, logger

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest, _: None = Depends(verify_api_key)):
    """
    POST /ask
    Header: X-API-Key: <your key>
    Body: {"question": "..."}
    Returns: {"answer": "...", "sources_available": [...]}
    """
    logger.info(f"Question received: {request.question}")

    chunks = hybrid_search(request.question, top_k=5)
    result = generate_answer(request.question, chunks)

    logger.info(f"Answer generated, sources used: {result['sources_available']}")

    return AskResponse(
        answer=result["answer"],
        sources_available=result["sources_available"],
    )