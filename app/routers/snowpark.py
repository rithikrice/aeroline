"""Snowpark router for demonstrating Snowpark integration."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import verify_api_key
from app.snowpark_client import get_snowpark_session
from app.snowpark_features import SnowparkFeatureEngine, deploy_snowpark_udfs
from app.snowpark_ml import SnowparkMLDeployer, initialize_snowpark_ml

router = APIRouter(prefix="/snowpark", tags=["snowpark"])

logger = logging.getLogger(__name__)


@router.get("/status", dependencies=[Depends(verify_api_key)])
async def get_snowpark_status():
    """
    Get Snowpark integration status.
    
    Returns status of Snowpark session, deployed UDFs, and stored procedures.
    """
    try:
        with get_snowpark_session() as sp_client:
            if not sp_client.session:
                return {
                    "status": "unavailable",
                    "message": "Snowpark session could not be established",
                    "fallback": "Using standard connector"
                }
            
            # Check if dynamic tables exist
            dynamic_tables = []
            for table in ["DT_FLIGHT_FEATS", "DT_MAINT_FEATS", "DT_RISK_JOIN"]:
                try:
                    result = sp_client.session.sql(
                        f"SHOW DYNAMIC TABLES LIKE '{table}'"
                    ).collect()
                    if result:
                        dynamic_tables.append(table)
                except:
                    pass
            
            # Check if UDFs exist
            udfs_deployed = []
            for udf_name in ["COMPUTE_FRS_SCORE", "COMPUTE_FLS_SCORE"]:
                try:
                    result = sp_client.session.sql(
                        f"SHOW USER FUNCTIONS LIKE '{udf_name}'"
                    ).collect()
                    if result:
                        udfs_deployed.append(udf_name)
                except:
                    pass
            
            # Check if procedures exist
            procedures_deployed = []
            for proc_name in ["PRESCRIBE_ACTIONS", "SNOWPARK_PRESCRIBE_ACTIONS", "SNOWPARK_BATCH_INFERENCE"]:
                try:
                    result = sp_client.session.sql(
                        f"SHOW PROCEDURES LIKE '{proc_name}'"
                    ).collect()
                    if result:
                        procedures_deployed.append(proc_name)
                except:
                    pass
            
            return {
                "status": "connected",
                "session_id": sp_client.session.get_current_session(),
                "warehouse": sp_client.session.get_current_warehouse(),
                "database": sp_client.session.get_current_database(),
                "schema": sp_client.session.get_current_schema(),
                "dynamic_tables": dynamic_tables,
                "udfs_deployed": udfs_deployed,
                "procedures_deployed": procedures_deployed,
                "capabilities": {
                    "dataframe_operations": True,
                    "ml_deployment": True,
                    "python_udfs": True,
                    "stored_procedures": True
                }
            }
            
    except Exception as e:
        logger.error(f"Error getting Snowpark status: {e}")
        return {
            "status": "error",
            "message": str(e),
            "fallback": "Using standard connector"
        }


@router.post("/initialize", dependencies=[Depends(verify_api_key)])
async def initialize_snowpark():
    """
    Initialize Snowpark components.
    
    Creates stages, deploys UDFs, and sets up stored procedures.
    """
    try:
        with get_snowpark_session() as sp_client:
            if not sp_client.session:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Snowpark session unavailable"
                )
            
            results = {}
            
            # Initialize ML components
            ml_results = initialize_snowpark_ml(sp_client.session)
            results["ml_initialization"] = ml_results
            
            # Deploy UDFs
            try:
                udf_results = deploy_snowpark_udfs(sp_client.session)
                results["udfs_deployed"] = udf_results
            except Exception as e:
                logger.warning(f"UDF deployment partially failed: {e}")
                results["udfs_deployed"] = {"error": str(e)}
            
            # Test DataFrame operations
            try:
                test_df = sp_client.session.sql("SELECT CURRENT_TIMESTAMP() as ts")
                test_df.collect()
                results["dataframe_operations"] = "working"
            except Exception as e:
                results["dataframe_operations"] = f"error: {str(e)}"
            
            return {
                "status": "initialized",
                "results": results
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing Snowpark: {str(e)}"
        )


@router.post("/compute-features", dependencies=[Depends(verify_api_key)])
async def compute_features_with_snowpark(
    feature_type: str = "both",
    save_to_table: bool = True
):
    """
    Compute features using Snowpark DataFrames.
    
    Args:
        feature_type: Type of features to compute ('flight', 'maintenance', 'both')
        save_to_table: Whether to save results to tables
        
    Returns:
        Feature computation summary
    """
    try:
        with get_snowpark_session() as sp_client:
            if not sp_client.session:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Snowpark session unavailable"
                )
            
            engine = SnowparkFeatureEngine(sp_client.session)
            results = {}
            
            # Compute flight features
            if feature_type in ["flight", "both"]:
                try:
                    flight_df = engine.compute_flight_features()
                    row_count = flight_df.count()
                    
                    if save_to_table:
                        flight_df.write.mode("overwrite").save_as_table("FLIGHT_FEATS")
                    
                    results["flight_features"] = {
                        "status": "success",
                        "rows_processed": row_count
                    }
                except Exception as e:
                    logger.error(f"Error computing flight features: {e}")
                    results["flight_features"] = {
                        "status": "error",
                        "message": str(e)
                    }
            
            # Compute maintenance features
            if feature_type in ["maintenance", "both"]:
                try:
                    maint_df = engine.compute_maintenance_features()
                    row_count = maint_df.count()
                    
                    if save_to_table:
                        maint_df.write.mode("overwrite").save_as_table("MAINT_FEATS")
                    
                    results["maintenance_features"] = {
                        "status": "success",
                        "rows_processed": row_count
                    }
                except Exception as e:
                    logger.error(f"Error computing maintenance features: {e}")
                    results["maintenance_features"] = {
                        "status": "error",
                        "message": str(e)
                    }
            
            return {
                "status": "completed",
                "feature_type": feature_type,
                "results": results
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error computing features: {str(e)}"
        )


@router.post("/compute-risk-join", dependencies=[Depends(verify_api_key)])
async def compute_risk_join_with_snowpark(save_to_table: bool = True):
    """
    Compute risk join using Snowpark DataFrames.
    
    Joins flight features, maintenance features, and job data to create
    comprehensive risk assessment.
    
    Args:
        save_to_table: Whether to save to RISK_JOIN table
        
    Returns:
        Risk join computation summary
    """
    try:
        with get_snowpark_session() as sp_client:
            if not sp_client.session:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Snowpark session unavailable"
                )
            
            engine = SnowparkFeatureEngine(sp_client.session)
            
            # Compute risk join
            risk_df = engine.compute_risk_join(save_to_table=save_to_table)
            row_count = risk_df.count()
            
            # Get summary statistics
            summary = risk_df.select(
                "FRS", "FLS", "action", "roi"
            ).to_pandas()
            
            action_counts = summary["action"].value_counts().to_dict()
            
            return {
                "status": "success",
                "rows_processed": row_count,
                "saved_to_table": save_to_table,
                "summary": {
                    "avg_frs": float(summary["FRS"].mean()),
                    "avg_fls": float(summary["FLS"].mean()),
                    "avg_roi": float(summary["roi"].mean()),
                    "action_distribution": action_counts
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error computing risk join: {str(e)}"
        )


@router.post("/run-procedure", dependencies=[Depends(verify_api_key)])
async def run_stored_procedure(
    procedure_name: str,
    *args
):
    """
    Run a Snowpark stored procedure.
    
    Args:
        procedure_name: Name of the procedure to run
        *args: Arguments to pass to procedure
        
    Returns:
        Procedure execution result
    """
    try:
        with get_snowpark_session() as sp_client:
            if not sp_client.session:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Snowpark session unavailable"
                )
            
            # Run procedure
            result = sp_client.call_stored_procedure(procedure_name, *args)
            
            return {
                "status": "success",
                "procedure": procedure_name,
                "result": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running procedure: {str(e)}"
        )


@router.get("/dataframe-demo", dependencies=[Depends(verify_api_key)])
async def dataframe_demo():
    """
    Demonstrate Snowpark DataFrame operations.
    
    Shows various DataFrame transformations and aggregations using Snowpark.
    """
    try:
        with get_snowpark_session() as sp_client:
            if not sp_client.session:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Snowpark session unavailable"
                )
            
            demos = {}
            
            # Demo 1: Simple aggregation
            try:
                from snowflake.snowpark.functions import avg, count, max as spark_max
                
                flights_df = sp_client.session.table("FLIGHTS_RAW")
                agg_result = flights_df.select(
                    count("*").alias("total_flights"),
                    avg("velocity").alias("avg_velocity"),
                    spark_max("baro_altitude").alias("max_altitude")
                ).collect()
                
                demos["aggregation"] = {
                    "total_flights": agg_result[0]["TOTAL_FLIGHTS"],
                    "avg_velocity": float(agg_result[0]["AVG_VELOCITY"]) if agg_result[0]["AVG_VELOCITY"] else 0,
                    "max_altitude": float(agg_result[0]["MAX_ALTITUDE"]) if agg_result[0]["MAX_ALTITUDE"] else 0
                }
            except Exception as e:
                demos["aggregation"] = {"error": str(e)}
            
            # Demo 2: Filtering and transformation
            try:
                from snowflake.snowpark.functions import col
                
                filtered_df = flights_df.filter(
                    col("velocity") > 200
                ).select(
                    "callsign", "velocity", "lat", "lon"
                ).limit(5)
                
                demos["filtering"] = {
                    "sample_flights": filtered_df.to_pandas().to_dict("records")
                }
            except Exception as e:
                demos["filtering"] = {"error": str(e)}
            
            # Demo 3: Window functions
            try:
                from snowflake.snowpark.window import Window
                from snowflake.snowpark.functions import row_number
                
                window_spec = Window.partition_by("callsign").order_by(col("snapshot_ts").desc())
                
                latest_df = flights_df.with_column(
                    "rn",
                    row_number().over(window_spec)
                ).filter(col("rn") == 1).select(
                    "callsign", "lat", "lon", "velocity"
                ).limit(5)
                
                demos["window_functions"] = {
                    "latest_positions": latest_df.to_pandas().to_dict("records")
                }
            except Exception as e:
                demos["window_functions"] = {"error": str(e)}
            
            return {
                "status": "success",
                "demos": demos,
                "note": "These operations execute in Snowflake using Snowpark DataFrames"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running DataFrame demo: {str(e)}"
        )


@router.get("/ml-info", dependencies=[Depends(verify_api_key)])
async def get_ml_info():
    """
    Get information about deployed ML models and capabilities.
    
    Returns info about Snowpark ML deployment status.
    """
    try:
        with get_snowpark_session() as sp_client:
            if not sp_client.session:
                return {
                    "status": "unavailable",
                    "message": "Snowpark session not available"
                }
            
            deployer = SnowparkMLDeployer(sp_client.session)
            
            # Get model info
            fls_info = deployer.get_model_info("fls_model")
            
            return {
                "status": "available",
                "capabilities": {
                    "model_deployment": True,
                    "batch_inference": True,
                    "python_udfs": True,
                    "stored_procedures": True
                },
                "models": {
                    "fls_model": fls_info
                },
                "stages": {
                    "model_stage": "@MODEL_STAGE",
                    "udf_stage": "@UDF_STAGE",
                    "sproc_stage": "@SPROC_STAGE"
                }
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

