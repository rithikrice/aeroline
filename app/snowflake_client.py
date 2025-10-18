"""Snowflake database client with connection management."""

import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Generator
import time

import pandas as pd
import snowflake.connector
from snowflake.connector import DictCursor, SnowflakeConnection
from snowflake.connector.errors import (
    ProgrammingError,
    OperationalError,
    DatabaseError,
)

from app.config import config

logger = logging.getLogger(__name__)


class SnowflakeClient:
    """Snowflake database client with retry logic and connection management."""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize Snowflake client.
        
        Args:
            max_retries: Maximum number of retry attempts for transient errors
            retry_delay: Delay in seconds between retry attempts
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection: Optional[SnowflakeConnection] = None
    
    def __enter__(self) -> "SnowflakeClient":
        """Enter context manager."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and close connection."""
        self.close()
    
    def connect(self) -> None:
        """Establish connection to Snowflake."""
        try:
            self.connection = snowflake.connector.connect(
                account=config.snowflake.account,
                user=config.snowflake.user,
                password=config.snowflake.password,
                role=config.snowflake.role,
                warehouse=config.snowflake.warehouse,
                database=config.snowflake.database,
                schema=config.snowflake.schema,
            )
            logger.info("Connected to Snowflake successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            raise
    
    def close(self) -> None:
        """Close Snowflake connection."""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Disconnected from Snowflake")
            except Exception as e:
                logger.error(f"Error closing Snowflake connection: {e}")
            finally:
                self.connection = None
    
    def _is_transient_error(self, error: Exception) -> bool:
        """
        Check if error is transient and should be retried.
        
        Args:
            error: The exception to check
            
        Returns:
            True if error is transient, False otherwise
        """
        if isinstance(error, OperationalError):
            # Connection errors, timeouts, etc.
            return True
        if isinstance(error, DatabaseError):
            # Check for specific error codes that indicate transient issues
            error_code = getattr(error, "errno", None)
            if error_code in [250001, 250002, 250003]:  # Network errors
                return True
        return False
    
    def execute_sql(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute SQL query with retry logic.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            
        Returns:
            List of dictionaries containing query results
            
        Raises:
            Exception: If query fails after all retry attempts
        """
        if not self.connection:
            raise RuntimeError("Not connected to Snowflake")
        
        for attempt in range(self.max_retries):
            try:
                cursor = self.connection.cursor(DictCursor)
                try:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    # For queries that return results
                    if cursor.rowcount is not None and cursor.rowcount >= 0:
                        results = cursor.fetchall()
                        return results
                    else:
                        # For DDL/DML statements
                        return []
                finally:
                    cursor.close()
                    
            except Exception as e:
                if self._is_transient_error(e) and attempt < self.max_retries - 1:
                    logger.warning(
                        f"Transient error on attempt {attempt + 1}: {e}. Retrying..."
                    )
                    time.sleep(self.retry_delay * (attempt + 1))
                    # Reconnect if connection was lost
                    if not self.connection or self.connection.is_closed():
                        self.connect()
                else:
                    logger.error(f"Query failed: {e}")
                    raise
        
        raise Exception(f"Query failed after {self.max_retries} attempts")
    
    def fetch_df(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute query and return results as pandas DataFrame.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            
        Returns:
            Query results as DataFrame
        """
        results = self.execute_sql(query, params)
        if results:
            return pd.DataFrame(results)
        return pd.DataFrame()
    
    def write_pandas_df(
        self, 
        df: pd.DataFrame, 
        table_name: str,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        overwrite: bool = False
    ) -> int:
        """
        Write pandas DataFrame to Snowflake table.
        
        Args:
            df: DataFrame to write
            table_name: Target table name
            database: Optional database name (uses config default if not provided)
            schema: Optional schema name (uses config default if not provided)
            overwrite: If True, replace table contents; if False, append
            
        Returns:
            Number of rows written
        """
        if not self.connection:
            raise RuntimeError("Not connected to Snowflake")
        
        try:
            # Use write_pandas from snowflake.connector
            success, nchunks, nrows, _ = snowflake.connector.pandas_tools.write_pandas(
                conn=self.connection,
                df=df,
                table_name=table_name,
                database=database or config.snowflake.database,
                schema=schema or config.snowflake.schema,
                overwrite=overwrite,
                auto_create_table=True,
            )
            
            if success:
                logger.info(f"Successfully wrote {nrows} rows to {table_name}")
                return nrows
            else:
                raise Exception(f"Failed to write DataFrame to {table_name}")
                
        except Exception as e:
            logger.error(f"Error writing DataFrame to Snowflake: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if table exists in current database/schema.
        
        Args:
            table_name: Name of table to check
            
        Returns:
            True if table exists, False otherwise
        """
        query = """
        SELECT COUNT(*) as count
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = %(schema)s
        AND TABLE_NAME = %(table)s
        """
        
        result = self.execute_sql(
            query,
            {"schema": config.snowflake.schema, "table": table_name.upper()}
        )
        
        return result[0]["COUNT"] > 0 if result else False


@contextmanager
def get_snowflake_client() -> Generator[SnowflakeClient, None, None]:
    """
    Context manager for Snowflake client.
    
    Yields:
        Connected Snowflake client
    """
    client = SnowflakeClient()
    try:
        client.connect()
        yield client
    finally:
        client.close()
