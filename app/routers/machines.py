"""Machines router for machine data ingestion and management."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import verify_api_key
from app.schemas import IngestRequest, IngestResponse, MachineData
from app.snowflake_client import get_snowflake_client
from app.ingestion.uci_ingest import UCIIngestor, SAMPLE_MACHINES

router = APIRouter(prefix="/machines", tags=["machines"])


@router.post("/ingest", response_model=IngestResponse, dependencies=[Depends(verify_api_key)])
async def ingest_machines(request: IngestRequest):
    """
    Ingest machine data from CSV or JSON.
    
    Accepts machine data in CSV or JSON format and loads it into MACHINES_RAW table.
    
    Args:
        request: Ingestion request with data and format
        
    Returns:
        Ingestion response with row count
    """
    ingestor = UCIIngestor()
    
    try:
        # Process data based on format
        if request.format == "csv":
            # Convert list of dicts to CSV string if needed
            if isinstance(request.data, list) and request.data:
                import pandas as pd
                df = pd.DataFrame(request.data)
                csv_content = df.to_csv(index=False)
                machines = ingestor.process_csv_content(csv_content)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid CSV data format"
                )
        else:  # JSON format
            machines = request.data
        
        # Validate machine data
        validated_machines = []
        for machine in machines:
            try:
                # Basic validation using Pydantic model
                machine_obj = MachineData(**machine)
                validated_machines.append(machine_obj.model_dump())
            except Exception as e:
                # Log validation error but continue with other records
                print(f"Validation error for machine record: {e}")
        
        if not validated_machines:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid machine records found"
            )
        
        # Ingest to Snowflake
        with get_snowflake_client() as client:
            rows_ingested = ingestor.ingest_to_snowflake(
                validated_machines,
                client,
                "MACHINES_RAW"
            )
        
        return IngestResponse(
            rows_ingested=rows_ingested,
            table="MACHINES_RAW"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting machine data: {str(e)}"
        )


@router.post("/ingest/sample", response_model=IngestResponse, dependencies=[Depends(verify_api_key)])
async def ingest_sample_machines():
    """
    Ingest sample machine data for testing.
    
    Loads predefined sample machine data into MACHINES_RAW table.
    """
    ingestor = UCIIngestor()
    
    try:
        with get_snowflake_client() as client:
            rows_ingested = ingestor.ingest_to_snowflake(
                SAMPLE_MACHINES,
                client,
                "MACHINES_RAW"
            )
        
        return IngestResponse(
            rows_ingested=rows_ingested,
            table="MACHINES_RAW"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting sample machines: {str(e)}"
        )


@router.post("/ingest/generate", response_model=IngestResponse, dependencies=[Depends(verify_api_key)])
async def generate_and_ingest_machines(n_records: int = 100):
    """
    Generate and ingest synthetic machine data.
    
    Args:
        n_records: Number of records to generate (default 100)
        
    Returns:
        Ingestion response with row count
    """
    ingestor = UCIIngestor()
    
    try:
        # Generate synthetic data
        df = ingestor.generate_sample_data(n_records)
        machines = df.to_dict("records")
        
        # Ingest to Snowflake
        with get_snowflake_client() as client:
            rows_ingested = ingestor.ingest_to_snowflake(
                machines,
                client,
                "MACHINES_RAW"
            )
        
        return IngestResponse(
            rows_ingested=rows_ingested,
            table="MACHINES_RAW"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating machine data: {str(e)}"
        )


@router.get("/status", dependencies=[Depends(verify_api_key)])
async def get_machine_status():
    """
    Get current machine status summary.
    
    Returns summary statistics about machines in the system.
    """
    try:
        with get_snowflake_client() as client:
            # Get machine counts by status
            query = """
            SELECT 
                COUNT(DISTINCT machine_id) as total_machines,
                SUM(CASE WHEN failure_label = 1 THEN 1 ELSE 0 END) as failed_machines,
                AVG(tool_wear) as avg_tool_wear,
                AVG(air_temp) as avg_air_temp,
                MAX(event_ts) as last_update
            FROM MACHINES_RAW
            WHERE event_ts >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
            """
            
            result = client.execute_sql(query)
            
            if result:
                return {
                    "total_machines": result[0].get("TOTAL_MACHINES", 0),
                    "failed_machines": result[0].get("FAILED_MACHINES", 0),
                    "avg_tool_wear": result[0].get("AVG_TOOL_WEAR", 0),
                    "avg_air_temp": result[0].get("AVG_AIR_TEMP", 0),
                    "last_update": result[0].get("LAST_UPDATE")
                }
            
            return {
                "total_machines": 0,
                "failed_machines": 0,
                "message": "No machine data available"
            }
            
    except Exception as e:
        # Return mock data if query fails
        return {
            "total_machines": 5,
            "failed_machines": 1,
            "avg_tool_wear": 125.5,
            "avg_air_temp": 298.5,
            "error": str(e)
        }
