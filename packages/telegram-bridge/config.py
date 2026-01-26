"""Configuration for Telegram Bridge service."""

from pathlib import Path
from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Telegram Bridge configuration."""

    # Telegram settings
    telegram_bot_token: SecretStr
    telegram_chat_id: str
    telegram_webhook_secret: str = ""  # Optional webhook secret for validation

    # Claude API settings
    anthropic_api_key: SecretStr
    claude_model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096

    # Service settings
    host: str = "0.0.0.0"
    port: int = 8420
    webhook_path: str = "/webhook/telegram"

    # Context settings - path to workspace for Claude context
    workspace_path: str = "."  # Override with your workspace path
    system_prompt_file: Optional[str] = None
    mcp_config_path: Optional[str] = None  # Override to use custom .mcp.json location

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def webhook_url(self) -> str:
        """Get the full webhook URL (override in deployment)."""
        return f"https://your-domain.com/telegram{self.webhook_path}"

    @property
    def mcp_json_path(self) -> str:
        """Get path to .mcp.json file."""
        if self.mcp_config_path:
            return self.mcp_config_path
        return str(Path(self.workspace_path) / ".mcp.json")


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
