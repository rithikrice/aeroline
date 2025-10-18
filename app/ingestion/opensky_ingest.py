"""OpenSky Network data ingestion module."""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import httpx

from app.config import config
from app.snowflake_client import SnowflakeClient

logger = logging.getLogger(__name__)


class OpenSkyIngestor:
    """Ingestor for OpenSky Network flight data."""
    
    def __init__(self):
        """Initialize OpenSky ingestor."""
        self.base_url = config.app.opensky_base
        self.auth = None
        
        # Set up authentication if provided
        if config.app.opensky_auth_user and config.app.opensky_auth_pass:
            self.auth = (config.app.opensky_auth_user, config.app.opensky_auth_pass)
    
    async def fetch_live_data(self, bbox: Optional[Dict] = None) -> List[Dict]:
        """
        Fetch live flight data from OpenSky Network.
        
        Args:
            bbox: Optional bounding box dict with keys: lamin, lomin, lamax, lomax
            
        Returns:
            List of flight records
        """
        try:
            params = {}
            if bbox:
                params.update({
                    "lamin": bbox.get("lamin", -90),
                    "lomin": bbox.get("lomin", -180),
                    "lamax": bbox.get("lamax", 90),
                    "lomax": bbox.get("lomax", 180)
                })
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    auth=self.auth,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                states = data.get("states", [])
                
                # Convert to standardized format
                flights = []
                timestamp = datetime.fromtimestamp(data.get("time", datetime.utcnow().timestamp()))
                
                for state in states:
                    flight = {
                        "snapshot_ts": timestamp,
                        "icao24": state[0],
                        "callsign": (state[1] or "").strip(),
                        "origin_country": state[2],
                        "time_position": state[3],
                        "last_contact": state[4],
                        "lon": state[5],
                        "lat": state[6],
                        "baro_altitude": state[7],
                        "on_ground": state[8],
                        "velocity": state[9],
                        "true_track": state[10],
                        "vertical_rate": state[11],
                        "sensors": state[12] if len(state) > 12 else None,
                        "geo_altitude": state[13] if len(state) > 13 else None,
                        "squawk": state[14] if len(state) > 14 else None,
                        "spi": state[15] if len(state) > 15 else None,
                        "position_source": state[16] if len(state) > 16 else None
                    }
                    flights.append(flight)
                
                logger.info(f"Fetched {len(flights)} flights from OpenSky")
                return flights
                
        except httpx.RequestError as e:
            logger.error(f"Error fetching OpenSky data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in OpenSky fetch: {e}")
            return []
    
    def load_replay_data(self, filepath: str) -> List[Dict]:
        """
        Load flight data from CSV replay file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of flight records
        """
        try:
            df = pd.read_csv(filepath)
            
            # Convert timestamp strings to datetime if needed
            if "snapshot_ts" in df.columns:
                df["snapshot_ts"] = pd.to_datetime(df["snapshot_ts"])
            
            # Convert to list of dicts
            flights = df.to_dict("records")
            
            logger.info(f"Loaded {len(flights)} flights from replay file")
            return flights
            
        except Exception as e:
            logger.error(f"Error loading replay data: {e}")
            return []
    
    def process_csv_content(self, csv_content: str) -> List[Dict]:
        """
        Process CSV content string into flight records.
        
        Args:
            csv_content: CSV content as string
            
        Returns:
            List of flight records
        """
        try:
            import io
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Convert timestamp strings to datetime if needed
            if "snapshot_ts" in df.columns:
                df["snapshot_ts"] = pd.to_datetime(df["snapshot_ts"])
            
            # Handle array columns (sensors)
            if "sensors" in df.columns:
                df["sensors"] = df["sensors"].apply(
                    lambda x: json.loads(x) if isinstance(x, str) and x.startswith("[") else []
                )
            
            flights = df.to_dict("records")
            logger.info(f"Processed {len(flights)} flights from CSV")
            return flights
            
        except Exception as e:
            logger.error(f"Error processing CSV content: {e}")
            return []
    
    def ingest_to_snowflake(
        self,
        flights: List[Dict],
        client: SnowflakeClient,
        table_name: str = "FLIGHTS_RAW"
    ) -> int:
        """
        Ingest flight data to Snowflake.
        
        Args:
            flights: List of flight records
            client: Snowflake client
            table_name: Target table name
            
        Returns:
            Number of rows ingested
        """
        if not flights:
            return 0
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(flights)
            
            # Ensure timestamp column is datetime
            if "snapshot_ts" in df.columns:
                df["snapshot_ts"] = pd.to_datetime(df["snapshot_ts"])
            
            # Convert arrays to JSON strings for Snowflake
            if "sensors" in df.columns:
                df["sensors"] = df["sensors"].apply(
                    lambda x: json.dumps(x) if isinstance(x, (list, dict)) else None
                )
            
            # Write to Snowflake
            rows_written = client.write_pandas_df(
                df,
                table_name,
                overwrite=False  # Append to existing data
            )
            
            logger.info(f"Ingested {rows_written} flight records to {table_name}")
            return rows_written
            
        except Exception as e:
            logger.error(f"Error ingesting to Snowflake: {e}")
            return 0


# Sample data for testing/demo
SAMPLE_FLIGHTS = [
    {
        "snapshot_ts": datetime.utcnow(),
        "icao24": "39a123",
        "callsign": "AI1234",
        "origin_country": "India",
        "time_position": 1694440800,
        "last_contact": 1694440815,
        "lon": 77.59,
        "lat": 12.97,
        "baro_altitude": 2500,
        "on_ground": False,
        "velocity": 205,
        "true_track": 70,
        "vertical_rate": 1.2,
        "geo_altitude": 2600,
        "squawk": "1234",
        "spi": False,
        "position_source": 0
    },
    {
        "snapshot_ts": datetime.utcnow(),
        "icao24": "3c4b56",
        "callsign": "LH760",
        "origin_country": "Germany",
        "time_position": 1694441400,
        "last_contact": 1694441410,
        "lon": 72.88,
        "lat": 19.09,
        "baro_altitude": 7800,
        "on_ground": False,
        "velocity": 240,
        "true_track": 92,
        "vertical_rate": 2.1,
        "geo_altitude": 8000,
        "squawk": "2345",
        "spi": False,
        "position_source": 0
    }
]
