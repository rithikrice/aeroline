"""Configuration router."""

from fastapi import APIRouter, Depends

from app.auth import verify_api_key
from app.config import config
from app.schemas import ConfigResponse

router = APIRouter(prefix="/config", tags=["config"])


@router.get("", response_model=ConfigResponse, dependencies=[Depends(verify_api_key)])
async def get_config():
    """
    Get application configuration (without secrets).
    
    Returns configuration settings excluding sensitive data like passwords and API keys.
    """
    return ConfigResponse(**config.to_dict_safe())
