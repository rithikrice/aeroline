"""API authentication module."""

from fastapi import Header, HTTPException, status
from typing import Optional

from app.config import config


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Verify API key from request header.
    
    Args:
        x_api_key: API key from x-api-key header
        
    Returns:
        The verified API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Please provide x-api-key header.",
        )
    
    if x_api_key != config.app.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    return x_api_key
