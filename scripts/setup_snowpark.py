#!/usr/bin/env python3
"""Setup script for Snowpark integration."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
from app.snowpark_client import get_snowpark_session
from app.snowpark_features import deploy_snowpark_udfs
from app.snowpark_ml import initialize_snowpark_ml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def setup_stages(session):
    """Create necessary stages for Snowpark deployment."""
    logger.info("Creating stages...")
    
    stages = [
        ("@UDF_STAGE", "Stage for User Defined Functions"),
        ("@SPROC_STAGE", "Stage for Stored Procedures"),
        ("@MODEL_STAGE", "Stage for ML Models")
    ]
    
    for stage_name, description in stages:
        try:
            session.sql(
                f"CREATE STAGE IF NOT EXISTS {stage_name} "
                "COMMENT = %(comment)s",
                params={"comment": description}
            ).collect()
            logger.info(f"✓ Created {stage_name}")
        except Exception as e:
            logger.warning(f"✗ Could not create {stage_name}: {e}")


def verify_tables(session):
    """Verify required tables exist."""
    logger.info("Verifying tables...")
    
    tables = [
        "FLIGHTS_RAW",
        "MACHINES_RAW",
        "JOBS",
        "FLIGHT_FEATS",
        "MAINT_FEATS",
        "RISK_JOIN"
    ]
    
    for table_name in tables:
        try:
            result = session.sql(
                f"SELECT COUNT(*) as cnt FROM {table_name}"
            ).collect()
            count = result[0]["CNT"]
            logger.info(f"✓ {table_name}: {count} rows")
        except Exception as e:
            logger.warning(f"✗ {table_name} not accessible: {e}")


def verify_dynamic_tables(session):
    """Verify dynamic tables exist."""
    logger.info("Verifying dynamic tables...")
    
    dynamic_tables = [
        "DT_FLIGHT_FEATS",
        "DT_MAINT_FEATS",
        "DT_RISK_JOIN"
    ]
    
    for dt_name in dynamic_tables:
        try:
            session.sql(f"SHOW DYNAMIC TABLES LIKE '{dt_name}'").collect()
            logger.info(f"✓ {dt_name} exists")
        except Exception as e:
            logger.warning(f"✗ {dt_name} not found: {e}")


def main():
    """Main setup function."""
    logger.info("=" * 60)
    logger.info("SNOWPARK SETUP - AeroLine")
    logger.info("=" * 60)
    
    try:
        with get_snowpark_session() as sp_client:
            if not sp_client.session:
                logger.error("❌ Could not establish Snowpark session")
                logger.error("Please check your Snowflake credentials in .env")
                return 1
            
            session = sp_client.session
            logger.info(f"✓ Connected to Snowflake")
            logger.info(f"  Database: {session.get_current_database()}")
            logger.info(f"  Schema: {session.get_current_schema()}")
            logger.info(f"  Warehouse: {session.get_current_warehouse()}")
            logger.info("")
            
            # Step 1: Create stages
            logger.info("STEP 1: Creating Stages")
            logger.info("-" * 60)
            setup_stages(session)
            logger.info("")
            
            # Step 2: Verify tables
            logger.info("STEP 2: Verifying Tables")
            logger.info("-" * 60)
            verify_tables(session)
            logger.info("")
            
            # Step 3: Verify dynamic tables
            logger.info("STEP 3: Verifying Dynamic Tables")
            logger.info("-" * 60)
            verify_dynamic_tables(session)
            logger.info("")
            
            # Step 4: Deploy UDFs
            logger.info("STEP 4: Deploying UDFs")
            logger.info("-" * 60)
            try:
                udf_results = deploy_snowpark_udfs(session)
                for udf_name, status in udf_results.items():
                    if status:
                        logger.info(f"✓ Deployed {udf_name}")
                    else:
                        logger.warning(f"✗ Could not deploy {udf_name}")
            except Exception as e:
                logger.warning(f"✗ UDF deployment error: {e}")
            logger.info("")
            
            # Step 5: Initialize ML components
            logger.info("STEP 5: Initializing ML Components")
            logger.info("-" * 60)
            try:
                ml_results = initialize_snowpark_ml(session)
                for component, status in ml_results.items():
                    if status:
                        logger.info(f"✓ {component}")
                    else:
                        logger.warning(f"✗ {component}")
            except Exception as e:
                logger.warning(f"✗ ML initialization error: {e}")
            logger.info("")
            
            logger.info("=" * 60)
            logger.info("✅ SNOWPARK SETUP COMPLETE")
            logger.info("=" * 60)
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Start the API: make run-api")
            logger.info("2. Check status: curl http://localhost:8080/snowpark/status -H 'x-api-key: dev-key-123'")
            logger.info("3. View docs: http://localhost:8080/docs#/snowpark")
            logger.info("")
            
            return 0
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

