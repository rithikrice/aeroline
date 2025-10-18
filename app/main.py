"""Main FastAPI application for AeroLine."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, config, flights, machines, scores, actions, snowpark

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AeroLine API...")
    
    # Initialize models if needed
    from app.models.frs_model import frs_model
    from app.models.fls_model import fls_model
    logger.info("Models initialized")
    
    # Initialize Snowpark integration (non-blocking)
    try:
        from app.snowpark_client import get_snowpark_session
        with get_snowpark_session() as sp_client:
            if sp_client.session:
                logger.info("Snowpark integration available")
            else:
                logger.info("Snowpark unavailable, using standard connector")
    except Exception as e:
        logger.warning(f"Snowpark initialization skipped: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AeroLine API...")


# Create FastAPI app
app = FastAPI(
    title="AeroLine API",
    description="Snowflake-native air-to-floor risk orchestrator",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(config.router)
app.include_router(flights.router)
app.include_router(machines.router)
app.include_router(scores.router)
app.include_router(actions.router)
app.include_router(snowpark.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AeroLine API",
        "version": "1.0.0",
        "description": "Snowflake-native air-to-floor risk orchestrator with Snowpark integration",
        "endpoints": {
            "health": "/health",
            "config": "/config",
            "flights": "/flights",
            "machines": "/machines",
            "scores": "/scores",
            "prescriptions": "/prescriptions",
            "whatif": "/whatif",
            "snowpark": "/snowpark"
        },
        "snowpark_features": {
            "dataframe_operations": "/snowpark/dataframe-demo",
            "feature_engineering": "/snowpark/compute-features",
            "ml_deployment": "/snowpark/ml-info",
            "status": "/snowpark/status"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
