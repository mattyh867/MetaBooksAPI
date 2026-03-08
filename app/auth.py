from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).parent / "app/.env")

# ─── API Key Config ───────────────────────────────────────────────────────────
API_KEY = os.getenv("API_KEY", "bookvault-dev-key-123")  # fallback for development
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# ─── Dependency ───────────────────────────────────────────────────────────────
def verify_api_key(key: str = Security(api_key_header)):
    """
    Dependency that protects write endpoints.
    Include as: dependencies=[Depends(verify_api_key)]
    or as a parameter: api_key: str = Depends(verify_api_key)
    """
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include X-API-Key in your request headers."
        )
    if key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key."
        )
    return key