"""Snowpark-based feature engineering for FRS and FLS."""

import logging
from typing import Dict, Optional
import math

from snowflake.snowpark import DataFrame, Session
from snowflake.snowpark.functions import (
    col, lit, when, avg, stddev, variance, max as spark_max,
    min as spark_min, count, current_timestamp, udf, sqrt, exp, abs as spark_abs
)
from snowflake.snowpark.types import FloatType
from snowflake.snowpark.window import Window

from app.config import config

logger = logging.getLogger(__name__)


class SnowparkFeatureEngine:
    """Snowpark-based feature engineering for risk scores."""
    
    def __init__(self, session: Session):
        """
        Initialize feature engine with Snowpark session.
        
        Args:
            session: Active Snowpark session
        """
        self.session = session
    
    def compute_flight_features(
        self, 
        flights_df: Optional[DataFrame] = None,
        table_name: str = "FLIGHTS_RAW"
    ) -> DataFrame:
        """
        Compute flight features using Snowpark DataFrames.
        
        Args:
            flights_df: Optional Snowpark DataFrame with flight data
            table_name: Table name if df not provided
            
        Returns:
            DataFrame with computed features and FRS
        """
        try:
            # Get flight data
            if flights_df is None:
                flights_df = self.session.table(table_name)
            
            # Filter recent data (last 24 hours)
            flights_df = flights_df.filter(
                col("snapshot_ts") >= current_timestamp() - lit("INTERVAL '24 HOURS'")
            )
            
            # Define window for per-callsign aggregations
            callsign_window = Window.partition_by("callsign").order_by("snapshot_ts")
            
            # Calculate features
            features_df = flights_df.with_column(
                "eta_drift_min",
                when(
                    col("velocity") > 0,
                    # Simplified ETA calculation (assuming SFO destination)
                    ((self._haversine_distance(
                        col("lat"), col("lon"), 
                        lit(37.6213), lit(-122.3790)
                    ) * 1000 / col("velocity")) - 7200) / 60
                ).otherwise(lit(0))
            ).with_column(
                "route_dev_km",
                # Simplified route deviation
                self._haversine_distance(
                    col("lat"), col("lon"),
                    lit(37.6213), lit(-122.3790)
                )
            ).with_column(
                "avg_velocity",
                avg(col("velocity")).over(callsign_window)
            ).with_column(
                "stddev_velocity", 
                stddev(col("velocity")).over(callsign_window)
            ).with_column(
                "speed_zscore",
                when(
                    col("stddev_velocity") > 0,
                    (col("velocity") - col("avg_velocity")) / col("stddev_velocity")
                ).otherwise(lit(0))
            )
            
            # Calculate FRS using weighted sigmoid
            features_df = features_df.with_column(
                "FRS",
                self._sigmoid(
                    lit(config.app.frs_eta_weight) * self._normalize_feature(col("eta_drift_min") / 60, -1, 1) +
                    lit(config.app.frs_route_weight) * self._normalize_feature(col("route_dev_km") / 100, 0, 1) +
                    lit(config.app.frs_speed_weight) * self._normalize_feature(col("speed_zscore") / 3, -1, 1)
                )
            )
            
            # Select relevant columns
            result_df = features_df.select(
                col("snapshot_ts"),
                col("icao24"),
                col("callsign"),
                col("lat"),
                col("lon"),
                col("eta_drift_min"),
                col("route_dev_km"),
                col("speed_zscore"),
                col("FRS"),
                current_timestamp().alias("computed_at")
            )
            
            logger.info("Computed flight features using Snowpark")
            return result_df
            
        except Exception as e:
            logger.error(f"Error computing flight features with Snowpark: {e}")
            raise
    
    def compute_maintenance_features(
        self,
        machines_df: Optional[DataFrame] = None,
        table_name: str = "MACHINES_RAW"
    ) -> DataFrame:
        """
        Compute maintenance features using Snowpark DataFrames.
        
        Args:
            machines_df: Optional Snowpark DataFrame with machine data
            table_name: Table name if df not provided
            
        Returns:
            DataFrame with computed features and FLS
        """
        try:
            # Get machine data
            if machines_df is None:
                machines_df = self.session.table(table_name)
            
            # Filter recent data (last 24 hours)
            machines_df = machines_df.filter(
                col("event_ts") >= current_timestamp() - lit("INTERVAL '24 HOURS'")
            )
            
            # Define window for rolling statistics
            machine_window = Window.partition_by("machine_id").order_by("event_ts").rows_between(-9, 0)
            
            # Calculate z-scores and features
            features_df = machines_df.with_column(
                "avg_air_temp",
                avg(col("air_temp")).over(machine_window)
            ).with_column(
                "stddev_air_temp",
                stddev(col("air_temp")).over(machine_window)
            ).with_column(
                "air_temp_zscore",
                when(
                    col("stddev_air_temp") > 0,
                    (col("air_temp") - col("avg_air_temp")) / col("stddev_air_temp")
                ).otherwise(lit(0))
            ).with_column(
                "avg_process_temp",
                avg(col("process_temp")).over(machine_window)
            ).with_column(
                "stddev_process_temp",
                stddev(col("process_temp")).over(machine_window)
            ).with_column(
                "process_temp_zscore",
                when(
                    col("stddev_process_temp") > 0,
                    (col("process_temp") - col("avg_process_temp")) / col("stddev_process_temp")
                ).otherwise(lit(0))
            ).with_column(
                "avg_torque",
                avg(col("torque")).over(machine_window)
            ).with_column(
                "stddev_torque",
                stddev(col("torque")).over(machine_window)
            ).with_column(
                "torque_zscore",
                when(
                    col("stddev_torque") > 0,
                    (col("torque") - col("avg_torque")) / col("stddev_torque")
                ).otherwise(lit(0))
            ).with_column(
                "tool_wear_normalized",
                col("tool_wear") / lit(250.0)
            ).with_column(
                "speed_variance",
                variance(col("rotational_speed")).over(machine_window)
            ).with_column(
                "temp_deviation",
                (spark_abs(col("air_temp_zscore")) + spark_abs(col("process_temp_zscore"))) / lit(2)
            )
            
            # Calculate FLS using heuristic sigmoid
            # FLS = sigmoid(0.4*temp + 0.3*wear + 0.2*speed + 0.1*torque)
            features_df = features_df.with_column(
                "FLS",
                self._sigmoid(
                    lit(0.4) * self._normalize_feature(col("temp_deviation"), 0, 3) +
                    lit(0.3) * col("tool_wear_normalized") +
                    lit(0.2) * self._normalize_feature(col("speed_variance") / 100, 0, 1) +
                    lit(0.1) * self._normalize_feature(col("torque_zscore") / 3, -1, 1)
                )
            )
            
            # Select relevant columns
            result_df = features_df.select(
                col("event_ts"),
                col("machine_id"),
                col("air_temp_zscore"),
                col("process_temp_zscore"),
                col("torque_zscore"),
                col("tool_wear_normalized"),
                col("temp_deviation"),
                col("speed_variance"),
                col("FLS"),
                current_timestamp().alias("computed_at")
            )
            
            logger.info("Computed maintenance features using Snowpark")
            return result_df
            
        except Exception as e:
            logger.error(f"Error computing maintenance features with Snowpark: {e}")
            raise
    
    def compute_risk_join(
        self,
        save_to_table: bool = True,
        table_name: str = "RISK_JOIN"
    ) -> DataFrame:
        """
        Compute risk join table combining FRS and FLS with job data.
        
        Args:
            save_to_table: Whether to save result to table
            table_name: Target table name
            
        Returns:
            DataFrame with risk join data
        """
        try:
            # Get jobs
            jobs_df = self.session.table("JOBS")
            
            # Get latest flight features
            flight_features = self.session.table("FLIGHT_FEATS")
            
            # Get latest machine features  
            maint_features = self.session.table("MAINT_FEATS")
            
            # Get latest FRS per callsign
            latest_frs = (
                flight_features
                .group_by("callsign")
                .agg(spark_max("snapshot_ts").alias("max_ts"))
            )
            
            flight_latest = flight_features.join(
                latest_frs,
                (flight_features["callsign"] == latest_frs["callsign"]) &
                (flight_features["snapshot_ts"] == latest_frs["max_ts"]),
                "inner"
            ).select(
                flight_features["callsign"],
                flight_features["FRS"]
            )
            
            # Get latest FLS per machine
            latest_fls = (
                maint_features
                .group_by("machine_id")
                .agg(spark_max("event_ts").alias("max_ts"))
            )
            
            maint_latest = maint_features.join(
                latest_fls,
                (maint_features["machine_id"] == latest_fls["machine_id"]) &
                (maint_features["event_ts"] == latest_fls["max_ts"]),
                "inner"
            ).select(
                maint_features["machine_id"],
                maint_features["FLS"]
            )
            
            # Join everything
            risk_df = (
                jobs_df
                .join(
                    flight_latest,
                    jobs_df["inbound_flight_callsign"] == flight_latest["callsign"],
                    "left"
                )
                .join(
                    maint_latest,
                    jobs_df["machine_id"] == maint_latest["machine_id"],
                    "left"
                )
            )
            
            # Add default risk scores and cost parameters
            risk_df = risk_df.with_column(
                "FRS",
                when(col("FRS").is_null(), lit(0.5)).otherwise(col("FRS"))
            ).with_column(
                "FLS",
                when(col("FLS").is_null(), lit(0.5)).otherwise(col("FLS"))
            ).with_column(
                "otif_value",
                lit(config.app.default_otif_value)
            ).with_column(
                "expedite_cost",
                lit(config.app.default_expedite_cost)
            ).with_column(
                "downtime_cost",
                lit(config.app.default_downtime_cost_per_hour * 2)
            )
            
            # Calculate ROI and action (simplified)
            risk_df = risk_df.with_column(
                "roi",
                col("otif_value") - col("expedite_cost") - col("downtime_cost") -
                (lit(0.7) * col("FRS") + lit(0.3) * col("FLS")) * lit(5000)
            ).with_column(
                "action",
                when(
                    (col("FRS") > lit(0.7)) & (col("FLS") > lit(0.6)), 
                    lit("RESCHEDULE")
                ).when(
                    (col("FRS") > lit(0.8)) & (col("expedite_cost") < col("otif_value") * lit(0.25)),
                    lit("EXPEDITE")
                ).when(
                    col("FLS") > lit(0.65),
                    lit("PULL_SPARES")
                ).otherwise(lit("NO_ACTION"))
            ).with_column(
                "updated_at",
                current_timestamp()
            )
            
            # Select final columns
            final_df = risk_df.select(
                jobs_df["job_id"],
                jobs_df["machine_id"],
                jobs_df["inbound_flight_callsign"].alias("callsign"),
                col("FRS"),
                col("FLS"),
                col("otif_value"),
                col("expedite_cost"),
                col("downtime_cost"),
                col("roi"),
                col("action"),
                col("updated_at")
            )
            
            if save_to_table:
                final_df.write.mode("overwrite").save_as_table(table_name)
                logger.info(f"Saved risk join to table: {table_name}")
            
            return final_df
            
        except Exception as e:
            logger.error(f"Error computing risk join with Snowpark: {e}")
            raise
    
    @staticmethod
    def _haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate haversine distance between two points."""
        from snowflake.snowpark.functions import sin, cos, asin, radians, pow as spark_pow
        
        # Convert to radians
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (
            spark_pow(sin(dlat / lit(2)), lit(2)) +
            cos(lat1_rad) * cos(lat2_rad) * spark_pow(sin(dlon / lit(2)), lit(2))
        )
        
        c = lit(2) * asin(sqrt(a))
        
        # Earth radius in km
        return lit(6371) * c
    
    @staticmethod
    def _sigmoid(x):
        """Sigmoid activation function."""
        # sigmoid(x) = 1 / (1 + exp(-x))
        return lit(1) / (lit(1) + exp(-x))
    
    @staticmethod
    def _normalize_feature(x, min_val, max_val):
        """Normalize feature to [-1, 1] or [0, 1] range."""
        from snowflake.snowpark.functions import greatest, least
        
        # Clip to range
        clipped = greatest(least(x, lit(max_val)), lit(min_val))
        return clipped


def deploy_snowpark_udfs(session: Session) -> Dict[str, bool]:
    """
    Deploy Snowpark UDFs for feature computation.
    
    Args:
        session: Active Snowpark session
        
    Returns:
        Dictionary with deployment status for each UDF
    """
    results = {}
    
    try:
        # UDF for FRS calculation
        @udf(name="COMPUTE_FRS_SCORE", 
             return_type=FloatType(),
             input_types=[FloatType(), FloatType(), FloatType()],
             is_permanent=True,
             replace=True,
             stage_location="@UDF_STAGE")
        def compute_frs_score(eta_drift: float, route_dev: float, speed_zscore: float) -> float:
            """Compute FRS from features."""
            # Weights from config
            eta_weight = 0.6
            route_weight = 0.3
            speed_weight = 0.1
            
            # Normalize and combine
            eta_norm = max(-1, min(1, eta_drift / 60))
            route_norm = max(0, min(1, route_dev / 100))
            speed_norm = max(-1, min(1, speed_zscore / 3))
            
            weighted_sum = (
                eta_weight * eta_norm + 
                route_weight * route_norm + 
                speed_weight * speed_norm
            )
            
            # Sigmoid
            frs = 1 / (1 + math.exp(-weighted_sum))
            return float(frs)
        
        session.udf.register(compute_frs_score)
        results["COMPUTE_FRS_SCORE"] = True
        logger.info("Deployed COMPUTE_FRS_SCORE UDF")
        
    except Exception as e:
        logger.warning(f"Could not deploy COMPUTE_FRS_SCORE UDF: {e}")
        results["COMPUTE_FRS_SCORE"] = False
    
    try:
        # UDF for FLS calculation
        @udf(name="COMPUTE_FLS_SCORE",
             return_type=FloatType(),
             input_types=[FloatType(), FloatType(), FloatType(), FloatType()],
             is_permanent=True,
             replace=True,
             stage_location="@UDF_STAGE")
        def compute_fls_score(
            temp_deviation: float, 
            tool_wear_norm: float, 
            speed_var: float,
            torque_zscore: float
        ) -> float:
            """Compute FLS from features."""
            # Weights
            temp_weight = 0.4
            wear_weight = 0.3
            speed_weight = 0.2
            torque_weight = 0.1
            
            # Normalize
            temp_norm = max(0, min(1, temp_deviation / 3))
            speed_norm = max(0, min(1, speed_var / 100))
            torque_norm = max(-1, min(1, torque_zscore / 3))
            
            weighted_sum = (
                temp_weight * temp_norm +
                wear_weight * tool_wear_norm +
                speed_weight * speed_norm +
                torque_weight * torque_norm
            )
            
            # Sigmoid
            fls = 1 / (1 + math.exp(-weighted_sum))
            return float(fls)
        
        session.udf.register(compute_fls_score)
        results["COMPUTE_FLS_SCORE"] = True
        logger.info("Deployed COMPUTE_FLS_SCORE UDF")
        
    except Exception as e:
        logger.warning(f"Could not deploy COMPUTE_FLS_SCORE UDF: {e}")
        results["COMPUTE_FLS_SCORE"] = False
    
    return results

