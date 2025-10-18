"""UCI AI4I Predictive Maintenance data ingestion module."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from app.snowflake_client import SnowflakeClient

logger = logging.getLogger(__name__)


class UCIIngestor:
    """Ingestor for UCI AI4I Predictive Maintenance dataset."""
    
    def __init__(self):
        """Initialize UCI ingestor."""
        self.dataset_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv"
    
    def fetch_dataset(self) -> pd.DataFrame:
        """
        Fetch UCI AI4I dataset.
        
        Returns:
            DataFrame with machine data
        """
        try:
            # Try to fetch from UCI repository
            df = pd.read_csv(self.dataset_url)
            logger.info(f"Fetched {len(df)} records from UCI dataset")
            return df
        except Exception as e:
            logger.warning(f"Could not fetch UCI dataset: {e}")
            # Return sample data as fallback
            return self.generate_sample_data()
    
    def generate_sample_data(self, n_records: int = 100) -> pd.DataFrame:
        """
        Generate sample machine data for testing.
        
        Args:
            n_records: Number of records to generate
            
        Returns:
            DataFrame with synthetic machine data
        """
        np.random.seed(42)
        
        # Generate timestamps
        base_time = datetime.utcnow() - timedelta(hours=24)
        timestamps = [base_time + timedelta(minutes=5*i) for i in range(n_records)]
        
        # Generate machine IDs (5 machines)
        machine_ids = [f"M-{str(i%5 + 1).zfill(2)}" for i in range(n_records)]
        
        # Generate machine types
        types = np.random.choice(["L", "M", "H"], n_records, p=[0.5, 0.3, 0.2])
        
        # Generate sensor readings with some correlation
        air_temp = np.random.normal(298, 2, n_records)
        process_temp = air_temp + np.random.normal(11, 1, n_records)
        
        # Rotational speed varies by machine type
        speed_base = {"L": 1400, "M": 1500, "H": 1600}
        rotational_speed = [
            np.random.normal(speed_base[t], 50) for t in types
        ]
        
        # Torque and tool wear
        torque = np.random.normal(50, 5, n_records)
        tool_wear = np.random.uniform(0, 250, n_records)
        
        # Generate failure labels (5% failure rate)
        failure_label = np.random.choice([0, 1], n_records, p=[0.95, 0.05])
        
        # Add some correlation: high tool wear increases failure probability
        high_wear_idx = np.where(tool_wear > 200)[0]
        for idx in high_wear_idx:
            if np.random.random() < 0.3:  # 30% chance of failure with high wear
                failure_label[idx] = 1
        
        # Create DataFrame
        df = pd.DataFrame({
            "machine_id": machine_ids,
            "type": types,
            "air_temp": air_temp,
            "process_temp": process_temp,
            "rotational_speed": rotational_speed,
            "torque": torque,
            "tool_wear": tool_wear,
            "failure_label": failure_label,
            "event_ts": timestamps
        })
        
        logger.info(f"Generated {len(df)} sample machine records")
        return df
    
    def process_csv_content(self, csv_content: str) -> List[Dict]:
        """
        Process CSV content string into machine records.
        
        Args:
            csv_content: CSV content as string
            
        Returns:
            List of machine records
        """
        try:
            import io
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Ensure required columns exist
            required_cols = [
                "machine_id", "type", "air_temp", "process_temp",
                "rotational_speed", "torque", "tool_wear", "failure_label"
            ]
            
            for col in required_cols:
                if col not in df.columns:
                    logger.warning(f"Missing column {col}, adding default values")
                    if col == "machine_id":
                        df[col] = [f"M-{i:02d}" for i in range(len(df))]
                    elif col == "type":
                        df[col] = "M"
                    elif col == "failure_label":
                        df[col] = 0
                    else:
                        df[col] = 0.0
            
            # Add event timestamp if missing
            if "event_ts" not in df.columns:
                df["event_ts"] = datetime.utcnow()
            else:
                df["event_ts"] = pd.to_datetime(df["event_ts"])
            
            machines = df.to_dict("records")
            logger.info(f"Processed {len(machines)} machine records from CSV")
            return machines
            
        except Exception as e:
            logger.error(f"Error processing CSV content: {e}")
            return []
    
    def transform_uci_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform UCI dataset format to our schema.
        
        Args:
            df: Raw UCI dataset DataFrame
            
        Returns:
            Transformed DataFrame
        """
        # Map UCI column names to our schema
        column_mapping = {
            "Air temperature [K]": "air_temp",
            "Process temperature [K]": "process_temp",
            "Rotational speed [rpm]": "rotational_speed",
            "Torque [Nm]": "torque",
            "Tool wear [min]": "tool_wear",
            "Machine failure": "failure_label",
            "Type": "type"
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Add machine ID if not present
        if "machine_id" not in df.columns:
            if "Product ID" in df.columns:
                df["machine_id"] = df["Product ID"]
            else:
                df["machine_id"] = [f"M-{i:04d}" for i in range(len(df))]
        
        # Add event timestamp
        if "event_ts" not in df.columns:
            # Distribute timestamps over past 24 hours
            base_time = datetime.utcnow() - timedelta(hours=24)
            time_increment = timedelta(hours=24) / len(df)
            df["event_ts"] = [base_time + i * time_increment for i in range(len(df))]
        
        # Select only required columns
        required_cols = [
            "machine_id", "type", "air_temp", "process_temp",
            "rotational_speed", "torque", "tool_wear", 
            "failure_label", "event_ts"
        ]
        
        # Keep only columns that exist
        cols_to_keep = [col for col in required_cols if col in df.columns]
        df = df[cols_to_keep]
        
        return df
    
    def ingest_to_snowflake(
        self,
        machines: List[Dict],
        client: SnowflakeClient,
        table_name: str = "MACHINES_RAW"
    ) -> int:
        """
        Ingest machine data to Snowflake.
        
        Args:
            machines: List of machine records
            client: Snowflake client
            table_name: Target table name
            
        Returns:
            Number of rows ingested
        """
        if not machines:
            return 0
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(machines)
            
            # Ensure timestamp column is datetime
            if "event_ts" in df.columns:
                df["event_ts"] = pd.to_datetime(df["event_ts"])
            
            # Write to Snowflake
            rows_written = client.write_pandas_df(
                df,
                table_name,
                overwrite=False  # Append to existing data
            )
            
            logger.info(f"Ingested {rows_written} machine records to {table_name}")
            return rows_written
            
        except Exception as e:
            logger.error(f"Error ingesting to Snowflake: {e}")
            return 0


# Sample data for testing/demo
SAMPLE_MACHINES = [
    {
        "machine_id": "M-01",
        "type": "L",
        "air_temp": 298.3,
        "process_temp": 309.1,
        "rotational_speed": 1375.0,
        "torque": 48.2,
        "tool_wear": 12,
        "failure_label": 0,
        "event_ts": datetime.utcnow()
    },
    {
        "machine_id": "M-02",
        "type": "M",
        "air_temp": 301.1,
        "process_temp": 312.4,
        "rotational_speed": 1450.0,
        "torque": 52.1,
        "tool_wear": 22,
        "failure_label": 1,
        "event_ts": datetime.utcnow()
    },
    {
        "machine_id": "M-03",
        "type": "H",
        "air_temp": 299.9,
        "process_temp": 311.8,
        "rotational_speed": 1390.0,
        "torque": 47.8,
        "tool_wear": 16,
        "failure_label": 0,
        "event_ts": datetime.utcnow()
    }
]
