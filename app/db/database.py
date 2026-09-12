"""
Database connection setup.

Creates the SQLAlchemy engine and session used to talk to the Postgres
(with pgvector) database running in Docker. Everything else that needs
to read or write to the database goes through this file, so there's
only ever one place the connection itself is configured.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  # reads variables from .env into the environment

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()