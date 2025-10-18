"""Snowpark client for modern Snowflake integration."""

import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Generator

from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, udf, sproc
from snowflake.snowpark.types import (
    StructType, 
    StructField, 
    StringType, 
    FloatType, 
    IntegerType,
    TimestampType
)
import pandas as pd

from app.config import config

logger = logging.getLogger(__name__)


class SnowparkClient:
    """Snowpark client for DataFrame-based Snowflake operations."""
    
    def __init__(self):
        """Initialize Snowpark client."""
        self.session: Optional[Session] = None
        self._connection_params = {
            "account": config.snowflake.account,
            "user": config.snowflake.user,
            "password": config.snowflake.password,
            "role": config.snowflake.role,
            "warehouse": config.snowflake.warehouse,
            "database": config.snowflake.database,
            "schema": config.snowflake.schema,
        }
    
    def __enter__(self) -> "SnowparkClient":
        """Enter context manager."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and close session."""
        self.close()
    
    def connect(self) -> None:
        """Establish Snowpark session."""
        try:
            self.session = Session.builder.configs(self._connection_params).create()
            logger.info("Snowpark session created successfully")
            
            # Set session parameters for optimal performance
            self.session.sql("ALTER SESSION SET QUERY_TAG = 'AEROLINE_APP'").collect()
            
        except Exception as e:
            logger.error(f"Failed to create Snowpark session: {e}")
            raise
    
    def close(self) -> None:
        """Close Snowpark session."""
        if self.session:
            try:
                self.session.close()
                logger.info("Snowpark session closed")
            except Exception as e:
                logger.error(f"Error closing Snowpark session: {e}")
            finally:
                self.session = None
    
    def get_table_df(self, table_name: str, limit: Optional[int] = None):
        """
        Get Snowpark DataFrame for a table.
        
        Args:
            table_name: Name of the table
            limit: Optional limit on rows
            
        Returns:
            Snowpark DataFrame
        """
        if not self.session:
            raise RuntimeError("Snowpark session not connected")
        
        df = self.session.table(table_name)
        
        if limit:
            df = df.limit(limit)
        
        return df
    
    def execute_dataframe_query(self, query: str):
        """
        Execute SQL query and return Snowpark DataFrame.
        
        Args:
            query: SQL query string
            
        Returns:
            Snowpark DataFrame
        """
        if not self.session:
            raise RuntimeError("Snowpark session not connected")
        
        return self.session.sql(query)
    
    def write_dataframe(
        self, 
        df: pd.DataFrame, 
        table_name: str,
        mode: str = "append",
        auto_create_table: bool = True
    ) -> None:
        """
        Write pandas DataFrame to Snowflake table using Snowpark.
        
        Args:
            df: Pandas DataFrame to write
            table_name: Target table name
            mode: Write mode ('append', 'overwrite', 'errorifexists')
            auto_create_table: Whether to auto-create table if not exists
        """
        if not self.session:
            raise RuntimeError("Snowpark session not connected")
        
        try:
            # Convert pandas DataFrame to Snowpark DataFrame
            snowpark_df = self.session.create_dataframe(df)
            
            # Write to table
            snowpark_df.write.mode(mode).save_as_table(
                table_name,
                mode=mode
            )
            
            logger.info(f"Successfully wrote {len(df)} rows to {table_name}")
            
        except Exception as e:
            logger.error(f"Error writing DataFrame to Snowflake: {e}")
            raise
    
    def deploy_python_udf(
        self,
        func,
        name: str,
        return_type,
        input_types: List,
        packages: Optional[List[str]] = None,
        replace: bool = True
    ) -> None:
        """
        Deploy Python function as Snowflake UDF using Snowpark.
        
        Args:
            func: Python function to deploy
            name: UDF name in Snowflake
            return_type: Snowpark return type
            input_types: List of Snowpark input types
            packages: Optional list of packages to include
            replace: Whether to replace if exists
        """
        if not self.session:
            raise RuntimeError("Snowpark session not connected")
        
        try:
            # Register UDF
            udf_obj = self.session.udf.register(
                func=func,
                name=name,
                return_type=return_type,
                input_types=input_types,
                packages=packages or [],
                is_permanent=True,
                replace=replace,
                stage_location="@UDF_STAGE"
            )
            
            logger.info(f"Successfully deployed UDF: {name}")
            
        except Exception as e:
            logger.warning(f"Could not deploy UDF {name}: {e}")
            # Non-fatal - UDF might already exist or permissions issue
    
    def deploy_stored_procedure(
        self,
        func,
        name: str,
        return_type,
        input_types: List,
        packages: Optional[List[str]] = None,
        replace: bool = True
    ) -> None:
        """
        Deploy Python function as Snowflake stored procedure.
        
        Args:
            func: Python function to deploy
            name: Procedure name in Snowflake
            return_type: Snowpark return type
            input_types: List of Snowpark input types  
            packages: Optional list of packages to include
            replace: Whether to replace if exists
        """
        if not self.session:
            raise RuntimeError("Snowpark session not connected")
        
        try:
            # Register stored procedure
            sproc_obj = self.session.sproc.register(
                func=func,
                name=name,
                return_type=return_type,
                input_types=input_types,
                packages=packages or [],
                is_permanent=True,
                replace=replace,
                stage_location="@SPROC_STAGE"
            )
            
            logger.info(f"Successfully deployed stored procedure: {name}")
            
        except Exception as e:
            logger.warning(f"Could not deploy stored procedure {name}: {e}")
            # Non-fatal - procedure might already exist
    
    def call_stored_procedure(self, procedure_name: str, *args) -> Any:
        """
        Call a stored procedure.
        
        Args:
            procedure_name: Name of the procedure
            *args: Arguments to pass to procedure
            
        Returns:
            Result from procedure
        """
        if not self.session:
            raise RuntimeError("Snowpark session not connected")
        
        try:
            result = self.session.call(procedure_name, *args)
            return result
        except Exception as e:
            logger.error(f"Error calling procedure {procedure_name}: {e}")
            raise
    
    def refresh_dynamic_table(self, table_name: str) -> bool:
        """
        Refresh a dynamic table.
        
        Args:
            table_name: Name of dynamic table
            
        Returns:
            True if successful, False otherwise
        """
        if not self.session:
            raise RuntimeError("Snowpark session not connected")
        
        try:
            self.session.sql(f"ALTER DYNAMIC TABLE {table_name} REFRESH").collect()
            logger.info(f"Refreshed dynamic table: {table_name}")
            return True
        except Exception as e:
            logger.warning(f"Could not refresh dynamic table {table_name}: {e}")
            return False


@contextmanager
def get_snowpark_session() -> Generator[SnowparkClient, None, None]:
    """
    Context manager for Snowpark session.
    
    Yields:
        Connected Snowpark client
    """
    client = SnowparkClient()
    try:
        client.connect()
        yield client
    except Exception as e:
        logger.error(f"Snowpark session error: {e}")
        # Return client anyway for graceful fallback
        yield client
    finally:
        client.close()

