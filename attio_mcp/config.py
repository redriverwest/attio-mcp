"""Configuration management for Attio MCP server."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Attio API Configuration
    attio_api_key: str
    attio_api_base_url: str = "https://api.attio.com/v2"

    # MCP Server Authentication (optional - if not set, auth is disabled)
    mcp_bearer_token: str | None = None

    # Server Configuration
    log_level: str = "INFO"
    mcp_transport: str = "stdio"
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8000


# Global settings instance
settings = Settings()
