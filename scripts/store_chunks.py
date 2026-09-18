"""
Phase 3: embed and store all chunks.

Loads the 20 policy documents, splits them into chunks (same logic as
Phase 2), generates an embedding for each chunk using all-MiniLM-L6-v2,
and permanently stores each chunk + its embedding in the
document_chunks table (Postgres + pgvector, running in Docker).

Safe to rerun: chunks that already exist (same chunk_id) are skipped,
not duplicated.
"""

from sentence_transformers import SentenceTransformer
from sqlalchemy import text

from app.db.database import engine
from app.services.chunking import load_documents, chunk_documents


def embedding_to_pgvector_literal(embedding):
    """
    Convert a list of floats (one embedding) into the text format
    pgvector expects for storage, e.g. "[0.12,0.34,-0.05]".
    """
    return "[" + ",".join(str(float(x)) for x in embedding) + "]"


def main():
    print("Loading documents...")
    docs = load_documents("data")

    print("Chunking documents...")
    chunks = chunk_documents(docs)
    print(f"{len(chunks)} chunks ready to embed.")

    print("Loading embedding model (all-mpnet-base-v2)...")
    model = SentenceTransformer("all-mpnet-base-v2")

    print("Generating embeddings for all chunks...")
    texts = [c["embedding_text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    print("Storing chunks + embeddings in Postgres...")
    with engine.connect() as conn:
        for chunk, embedding in zip(chunks, embeddings):
            conn.execute(
                text("""
                    INSERT INTO document_chunks (source, chunk_id, text, embedding)
                    VALUES (:source, :chunk_id, :text, CAST(:embedding AS vector))
                    ON CONFLICT (chunk_id) DO UPDATE
                    SET text = EXCLUDED.text,
                        embedding = EXCLUDED.embedding;
                """),
                {
                    "source": chunk["source"],
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "embedding": embedding_to_pgvector_literal(embedding),
                },
            )
        conn.commit()

    print("Done. All chunks embedded and stored.")


if __name__ == "__main__":
    main()