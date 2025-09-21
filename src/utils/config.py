"""
Configuration management for MCP AI Agent
"""

import os
from typing import Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv


class Config(BaseModel):
    """Configuration settings for MCP AI Agent"""

    # Gemini API Configuration
    gemini_api_key: str = Field(..., description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-1.5-pro", description="Gemini model to use")

    # MCP Server Configuration
    mcp_server_host: str = Field(default="localhost", description="MCP server host")
    mcp_server_port: int = Field(default=8080, description="MCP server port")

    # Security Configuration
    enable_risk_assessment: bool = Field(default=True, description="Enable risk assessment")
    require_confirmation: bool = Field(default=True, description="Require confirmation for risky operations")
    dangerous_commands_whitelist: list = Field(default_factory=list, description="Whitelisted dangerous commands")

    # Monitoring Configuration
    monitoring_interval: int = Field(default=30, description="Monitoring interval in seconds")
    cpu_threshold: float = Field(default=80.0, description="CPU usage threshold for alerts")
    memory_threshold: float = Field(default=85.0, description="Memory usage threshold for alerts")
    disk_threshold: float = Field(default=90.0, description="Disk usage threshold for alerts")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        load_dotenv()

        # Required fields
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        # Build config dict from environment
        config_dict = {
            "gemini_api_key": gemini_api_key,
            "gemini_model": os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
            "mcp_server_host": os.getenv("MCP_SERVER_HOST", "localhost"),
            "mcp_server_port": int(os.getenv("MCP_SERVER_PORT", "8080")),
            "enable_risk_assessment": os.getenv("ENABLE_RISK_ASSESSMENT", "true").lower() == "true",
            "require_confirmation": os.getenv("REQUIRE_CONFIRMATION", "true").lower() == "true",
            "monitoring_interval": int(os.getenv("MONITORING_INTERVAL", "30")),
            "cpu_threshold": float(os.getenv("CPU_THRESHOLD", "80.0")),
            "memory_threshold": float(os.getenv("MEMORY_THRESHOLD", "85.0")),
            "disk_threshold": float(os.getenv("DISK_THRESHOLD", "90.0")),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_file": os.getenv("LOG_FILE")
        }

        # Handle dangerous commands whitelist
        whitelist_str = os.getenv("DANGEROUS_COMMANDS_WHITELIST", "")
        if whitelist_str:
            config_dict["dangerous_commands_whitelist"] = [
                cmd.strip() for cmd in whitelist_str.split(",") if cmd.strip()
            ]

        return cls(**config_dict)