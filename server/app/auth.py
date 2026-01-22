"""API Key authentication"""
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings

# API Key header configuration
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the API key from the X-API-Key header.

    In development mode (no API_KEY configured), authentication is skipped.
    In production, a valid API key is required.
    """
    # Skip auth if no API key is configured (development mode)
    if not settings.api_key:
        return ""

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include 'X-API-Key' header.",
        )

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return api_key


# Dependency to use in protected routes
RequireApiKey = Depends(verify_api_key)
