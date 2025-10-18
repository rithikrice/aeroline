"""Health check router."""

from fastapi import APIRouter, Depends

from app.auth import verify_api_key
from app.schemas import HealthResponse
from app.snowflake_client import get_snowflake_client

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns basic status without authentication.
    """
    return HealthResponse(status="ok")


@router.get("/detailed", response_model=HealthResponse, dependencies=[Depends(verify_api_key)])
async def detailed_health_check():
    """
    Detailed health check with Snowflake connectivity test.
    
    Requires API key authentication.
    """
    # Test Snowflake connection
    snowflake_status = "unknown"
    try:
        with get_snowflake_client() as client:
            result = client.execute_sql("SELECT 1")
            if result:
                snowflake_status = "connected"
    except Exception:
        snowflake_status = "disconnected"
    
    return HealthResponse(
        status="ok" if snowflake_status == "connected" else "degraded",
        snowflake=snowflake_status
    )
