"""
App-level configuration and authentication helper.
"""

import os
from fastapi import Header, HTTPException
from dotenv import load_dotenv
import logging

load_dotenv()

APP_API_KEY = os.getenv("APP_API_KEY")


def verify_api_key(x_api_key: str = Header(...)):
    """
    Dependency that checks the incoming request's X-API-Key header
    against our expected key. Raises 401 if missing or wrong.

    FastAPI runs this automatically before the route function, for any
    route that declares it as a dependency.
    """
    if x_api_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")



logging.basicConfig(
    filename="app.log",
    level=logging.WARNING,  # default for all libraries: only show real problems
    format="%(asctime)s - %(message)s",
)
logger = logging.getLogger("rag_app")
logger.setLevel(logging.INFO)  # but our own app's logs still show at INFO