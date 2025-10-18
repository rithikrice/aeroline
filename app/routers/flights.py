"""Flights router for flight data ingestion and management."""

import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import verify_api_key
from app.schemas import IngestRequest, IngestResponse, FlightData
from app.snowflake_client import get_snowflake_client
from app.ingestion.opensky_ingest import OpenSkyIngestor, SAMPLE_FLIGHTS

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("/ingest", response_model=IngestResponse, dependencies=[Depends(verify_api_key)])
async def ingest_flights(request: IngestRequest):
    """
    Ingest flight data from CSV or JSON.
    
    Accepts flight data in CSV or JSON format and loads it into FLIGHTS_RAW table.
    
    Args:
        request: Ingestion request with data and format
        
    Returns:
        Ingestion response with row count
    """
    ingestor = OpenSkyIngestor()
    
    try:
        # Process data based on format
        if request.format == "csv":
            # Convert list of dicts to CSV string if needed
            if isinstance(request.data, list) and request.data:
                import pandas as pd
                df = pd.DataFrame(request.data)
                csv_content = df.to_csv(index=False)
                flights = ingestor.process_csv_content(csv_content)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid CSV data format"
                )
        else:  # JSON format
            flights = request.data
        
        # Validate flight data
        validated_flights = []
        for flight in flights:
            try:
                # Basic validation using Pydantic model
                flight_obj = FlightData(**flight)
                validated_flights.append(flight_obj.model_dump())
            except Exception as e:
                # Log validation error but continue with other records
                print(f"Validation error for flight record: {e}")
        
        if not validated_flights:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid flight records found"
            )
        
        # Ingest to Snowflake
        with get_snowflake_client() as client:
            rows_ingested = ingestor.ingest_to_snowflake(
                validated_flights,
                client,
                "FLIGHTS_RAW"
            )
        
        return IngestResponse(
            rows_ingested=rows_ingested,
            table="FLIGHTS_RAW"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting flight data: {str(e)}"
        )


@router.post("/ingest/sample", response_model=IngestResponse, dependencies=[Depends(verify_api_key)])
async def ingest_sample_flights():
    """
    Ingest sample flight data for testing.
    
    Loads predefined sample flight data into FLIGHTS_RAW table.
    """
    ingestor = OpenSkyIngestor()
    
    try:
        with get_snowflake_client() as client:
            rows_ingested = ingestor.ingest_to_snowflake(
                SAMPLE_FLIGHTS,
                client,
                "FLIGHTS_RAW"
            )
        
        return IngestResponse(
            rows_ingested=rows_ingested,
            table="FLIGHTS_RAW"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting sample flights: {str(e)}"
        )


@router.get("/live", dependencies=[Depends(verify_api_key)])
async def fetch_live_flights(
    lamin: float = -90,
    lomin: float = -180,
    lamax: float = 90,
    lomax: float = 180
):
    """
    Fetch live flight data from OpenSky Network.
    
    Args:
        lamin: Minimum latitude for bounding box
        lomin: Minimum longitude for bounding box
        lamax: Maximum latitude for bounding box
        lomax: Maximum longitude for bounding box
        
    Returns:
        List of current flight states
    """
    ingestor = OpenSkyIngestor()
    
    try:
        bbox = {
            "lamin": lamin,
            "lomin": lomin,
            "lamax": lamax,
            "lomax": lomax
        }
        
        flights = await ingestor.fetch_live_data(bbox)
        
        if not flights:
            # Return sample data as fallback
            return {
                "source": "sample",
                "flights": SAMPLE_FLIGHTS[:10],
                "total": len(SAMPLE_FLIGHTS[:10])
            }
        
        return {
            "source": "live",
            "flights": flights[:100],  # Limit to 100 records
            "total": len(flights)
        }
        
    except Exception as e:
        # Return sample data on error
        return {
            "source": "sample",
            "flights": SAMPLE_FLIGHTS,
            "total": len(SAMPLE_FLIGHTS),
            "error": str(e)
        }
