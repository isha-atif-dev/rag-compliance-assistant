"""
Manual sanity check: confirm chunks actually landed in the database,
and peek at one row to see the real shape of stored data.
"""

from sqlalchemy import text
from app.db.database import engine

with engine.connect() as conn:
    count = conn.execute(text("SELECT COUNT(*) FROM document_chunks;")).scalar()
    print(f"Total chunks stored: {count}")

    row = conn.execute(text("SELECT source, chunk_id, text FROM document_chunks LIMIT 1;")).fetchone()
    print("\n--- Example stored row ---")
    print("Source:", row[0])
    print("Chunk ID:", row[1])
    print("Text:", row[2])