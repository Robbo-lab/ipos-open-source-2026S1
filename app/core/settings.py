"""
Centralised configuration settings for the application.
Holds runtime configuration values used across the application and tests.
"""
from dataclasses import dataclass


@dataclass
class Settings:
    """
    Configuration settings for the application.
    """
    host: str = "localhost"
    port: int = 8003
    mcp_base_url: str = "http://localhost:8003"
    mcp_protocol_version: str = "2025-06-18"


settings = Settings()