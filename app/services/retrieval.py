"""
Retrieval service for the RAG pipeline.

Takes a user's question, embeds it using the same model used for the
stored chunks, and asks pgvector for the most similar chunks by
meaning (nearest neighbours in embedding space). This is Phase 3's
actual payoff: Document -> Chunking -> Embedding -> Storage -> [retrieval] -> Generation.
"""

from sentence_transformers import SentenceTransformer
from sqlalchemy import text

from app.db.database import engine

_model = None


def get_model():
    """
    Load the embedding model once and reuse it, instead of reloading
    it from disk on every single search call (loading is slow, using
    it is fast).
    """
    global _model
    if _model is None:
        _model = SentenceTransformer("all-mpnet-base-v2")
    return _model


def embedding_to_pgvector_literal(embedding):
    """Same helper as store_chunks.py: turns a list of floats into pgvector's text format."""
    return "[" + ",".join(str(float(x)) for x in embedding) + "]"


def search(question: str, top_k: int = 3):
    """
    Return the top_k chunks most similar in meaning to the question.

    Uses pgvector's <-> operator, which calculates distance between
    vectors (smaller distance = more similar). Results are ordered
    closest-first.
    """
    model = get_model()
    question_embedding = model.encode(question)
    embedding_literal = embedding_to_pgvector_literal(question_embedding)

    with engine.connect() as conn:
        results = conn.execute(
            text("""
                SELECT source, chunk_id, text,
                       embedding <-> CAST(:query_embedding AS vector) AS distance
                FROM document_chunks
                ORDER BY distance ASC
                LIMIT :top_k;
            """),
            {"query_embedding": embedding_literal, "top_k": top_k},
        ).fetchall()

    return [
        {"source": r.source, "chunk_id": r.chunk_id, "text": r.text, "distance": r.distance}
        for r in results
    ]


def keyword_search(question: str, top_k: int = 15):
    """
    Keyword-based search using Postgres full-text search.

    Finds chunks containing the actual words from the question, ranked by
    how well the terms match. Complements vector search: vector search finds
    meaning but can miss exact domain terms like "SAR" or specific policy
    names buried among similarly-worded documents.
    """
    with engine.connect() as conn:
        results = conn.execute(
            text("""
                SELECT source, chunk_id, text,
                       ts_rank(to_tsvector('english', text), plainto_tsquery('english', :question)) AS score
                FROM document_chunks
                WHERE to_tsvector('english', text) @@ plainto_tsquery('english', :question)
                ORDER BY score DESC
                LIMIT :top_k;
            """),
            {"question": question, "top_k": top_k},
        ).fetchall()
    return [
        {"source": r.source, "chunk_id": r.chunk_id, "text": r.text, "score": r.score}
        for r in results
    ]


def hybrid_search(question: str, top_k: int = 3, candidate_k: int = 15):
    """
    Combines vector search (meaning) and keyword search (exact terms) using
    Reciprocal Rank Fusion (RRF).

    Vector distance and keyword rank scores aren't on comparable scales, so
    instead of combining raw scores, RRF combines rank *positions*:
        rrf_score = 1/(60 + rank_in_vector_list) + 1/(60 + rank_in_keyword_list)

    A chunk ranked highly in both lists rises to the top. A chunk strong in
    only one list still gets a smaller boost. 60 is a standard constant used
    in RRF, it just softens the difference between rank 1 and rank 2 so a
    single list's top pick doesn't automatically dominate.
    """
    vector_results = search(question, top_k=candidate_k)
    keyword_results = keyword_search(question, top_k=candidate_k)

    scores = {}
    chunks_by_id = {}

    for rank, r in enumerate(vector_results, start=1):
        scores[r["chunk_id"]] = scores.get(r["chunk_id"], 0) + 1 / (60 + rank)
        chunks_by_id[r["chunk_id"]] = r

    for rank, r in enumerate(keyword_results, start=1):
        scores[r["chunk_id"]] = scores.get(r["chunk_id"], 0) + 1 / (60 + rank)
        chunks_by_id[r["chunk_id"]] = r

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [chunks_by_id[chunk_id] for chunk_id, _ in ranked[:top_k]]