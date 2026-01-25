"""Configuration for cPanel/WHM MCP server."""

from pathlib import Path
from typing import Optional

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CpanelConfig(BaseSettings):
    """cPanel/WHM server configuration from environment variables."""

    # WHM URL (e.g., https://server.example.com:2087)
    whm_url: str

    # API token (preferred authentication method)
    api_token: SecretStr

    # WHM username (for API token auth header)
    username: str = "root"

    # Connection settings
    request_timeout: float = 30.0

    # Security
    allow_insecure: bool = False  # Allow self-signed certs

    model_config = SettingsConfigDict(
        env_prefix="CPANEL_",
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
    )

    @field_validator("whm_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate WHM URL format."""
        if not v.startswith(("https://", "http://")):
            raise ValueError("WHM URL must start with https:// or http://")
        # Remove trailing slash
        return v.rstrip("/")

    def get_api_url(self, function: str, api_version: int = 1) -> str:
        """Build full WHM API URL for a function.

        WHM API format: https://server:2087/json-api/{function}?api.version={version}
        """
        return f"{self.whm_url}/json-api/{function}?api.version={api_version}"

    def get_cpanel_api_url(self, account: str, module: str, function: str) -> str:
        """Build cPanel UAPI URL for account-level operations.

        Format: https://server:2087/execute/{module}/{function}?cpanel.user={account}
        """
        return f"{self.whm_url}/execute/{module}/{function}?cpanel_jsonapi_user={account}"


# Global configuration instance
_config: Optional[CpanelConfig] = None


def get_config() -> CpanelConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = CpanelConfig()
    return _config


def init_config(config: Optional[CpanelConfig] = None) -> CpanelConfig:
    """Initialize configuration from environment or provided config."""
    global _config
    _config = config or CpanelConfig()
    return _config
