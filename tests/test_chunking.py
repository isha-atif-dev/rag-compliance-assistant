"""
Automated tests for the chunking service (Phase 2).

"""

from app.services.chunking import load_documents, chunk_documents


def test_load_documents_finds_all_files():
    """We generated exactly 20 policy documents, so loading should find all 20."""
    docs = load_documents("data")
    assert len(docs) == 20


def test_chunking_produces_chunks():
    """Chunking 20 real documents should produce more chunks than documents."""
    docs = load_documents("data")
    chunks = chunk_documents(docs)
    assert len(chunks) > len(docs)


def test_chunk_has_required_fields():
    """Every chunk must carry its source and a chunk_id, needed later for citations."""
    docs = load_documents("data")
    chunks = chunk_documents(docs)
    first_chunk = chunks[0]
    assert "source" in first_chunk
    assert "chunk_id" in first_chunk
    assert "text" in first_chunk