"""
MCP AI Agent 配置管理模組
負責系統配置的載入、驗證與管理
"""

import os
from typing import Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv


class Config(BaseModel):
    """MCP AI Agent 配置設定類別"""

    # Gemini API 配置
    gemini_api_key: str = Field(..., description="Google Gemini API 金鑰")
    gemini_model: str = Field(default="gemini-1.5-pro", description="使用的 Gemini 模型")

    # MCP 伺服器配置
    mcp_server_host: str = Field(default="localhost", description="MCP 伺服器主機位址")
    mcp_server_port: int = Field(default=8080, description="MCP 伺服器連接埠")

    # 安全性配置
    enable_risk_assessment: bool = Field(default=True, description="啟用風險評估")
    require_confirmation: bool = Field(default=True, description="危險操作需要確認")
    dangerous_commands_whitelist: list = Field(default_factory=list, description="危險命令白名單")

    # 監控配置
    monitoring_interval: int = Field(default=30, description="監控間隔（秒）")
    cpu_threshold: float = Field(default=80.0, description="CPU 使用率告警閾值")
    memory_threshold: float = Field(default=85.0, description="記憶體使用率告警閾值")
    disk_threshold: float = Field(default=90.0, description="磁碟使用率告警閾值")

    # 日誌配置
    log_level: str = Field(default="INFO", description="日誌級別")
    log_file: Optional[str] = Field(default=None, description="日誌檔案路徑")

    @classmethod
    def from_env(cls) -> "Config":
        """從環境變數載入配置"""
        load_dotenv()

        # 必要欄位
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("需要設定 GEMINI_API_KEY 環境變數")

        # 從環境變數建置配置字典
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

        # 處理危險命令白名單
        whitelist_str = os.getenv("DANGEROUS_COMMANDS_WHITELIST", "")
        if whitelist_str:
            config_dict["dangerous_commands_whitelist"] = [
                cmd.strip() for cmd in whitelist_str.split(",") if cmd.strip()
            ]

        return cls(**config_dict)