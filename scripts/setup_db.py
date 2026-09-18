"""
One-time setup script: enables the pgvector extension and creates the
table that will hold our chunks + their embeddings.

Run this once. Safe to run again later, it won't duplicate the table.
"""

from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.execute(text("DROP TABLE IF EXISTS document_chunks;"))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id SERIAL PRIMARY KEY,
            source TEXT NOT NULL,
            chunk_id TEXT NOT NULL UNIQUE,
            text TEXT NOT NULL,
            embedding vector(768)
        );
    """))
    conn.commit()
    print("Extension enabled and table recreated with 768-dim vectors.")