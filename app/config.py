"""Configuration management for AeroLine application."""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class SnowflakeConfig:
    """Snowflake connection configuration."""
    
    account: str
    user: str
    password: str
    role: str
    warehouse: str
    database: str
    schema: str


@dataclass
class AppConfig:
    """Application configuration."""
    
    api_key: str
    opensky_base: str
    opensky_auth_user: Optional[str]
    opensky_auth_pass: Optional[str]
    
    # Cost model defaults
    default_otif_value: float = 10_000.0
    default_expedite_cost: float = 3_000.0
    default_downtime_cost_per_hour: float = 1_500.0
    
    # Risk score weights
    frs_lambda: float = 1.0
    frs_alpha: float = 0.7
    fls_beta: float = 0.3
    
    # FRS feature weights
    frs_eta_weight: float = 0.6
    frs_route_weight: float = 0.3
    frs_speed_weight: float = 0.1
    
    # Risk thresholds
    high_frs_threshold: float = 0.7
    critical_frs_threshold: float = 0.8
    high_fls_threshold: float = 0.6
    critical_fls_threshold: float = 0.65


@dataclass
class Config:
    """Complete application configuration."""
    
    snowflake: SnowflakeConfig
    app: AppConfig
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        snowflake_config = SnowflakeConfig(
            account=os.getenv("SNOWFLAKE_ACCOUNT", ""),
            user=os.getenv("SNOWFLAKE_USER", ""),
            password=os.getenv("SNOWFLAKE_PASSWORD", ""),
            role=os.getenv("SNOWFLAKE_ROLE", "DEVELOPER"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "AEROLINE_WH"),
            database=os.getenv("SNOWFLAKE_DATABASE", "AEROLINE_DB"),
            schema=os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
        )
        
        app_config = AppConfig(
            api_key=os.getenv("API_KEY", "dev-key-123"),
            opensky_base=os.getenv(
                "OPENSKY_BASE", "https://opensky-network.org/api/states/all"
            ),
            opensky_auth_user=os.getenv("OPENSKY_AUTH_USER"),
            opensky_auth_pass=os.getenv("OPENSKY_AUTH_PASS"),
        )
        
        return cls(snowflake=snowflake_config, app=app_config)
    
    def to_dict_safe(self) -> dict:
        """Return configuration as dictionary without sensitive data."""
        return {
            "snowflake": {
                "account": self.snowflake.account,
                "role": self.snowflake.role,
                "warehouse": self.snowflake.warehouse,
                "database": self.snowflake.database,
                "schema": self.snowflake.schema,
            },
            "app": {
                "opensky_base": self.app.opensky_base,
                "default_otif_value": self.app.default_otif_value,
                "default_expedite_cost": self.app.default_expedite_cost,
                "default_downtime_cost_per_hour": self.app.default_downtime_cost_per_hour,
                "risk_thresholds": {
                    "high_frs": self.app.high_frs_threshold,
                    "critical_frs": self.app.critical_frs_threshold,
                    "high_fls": self.app.high_fls_threshold,
                    "critical_fls": self.app.critical_fls_threshold,
                },
            },
        }


# Global configuration instance
config = Config.from_env()
