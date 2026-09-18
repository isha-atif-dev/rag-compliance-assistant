"""
Manual sanity check: can we actually connect to the Postgres container?
"""

from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print("Connected successfully!")
    print(result.fetchone())