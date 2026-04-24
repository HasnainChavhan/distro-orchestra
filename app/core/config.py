"""
DistroOrchestra — Core Configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DistroOrchestra"
    app_version: str = "1.0.0"
    debug: bool = False

    redis_url: str = "redis://localhost:6379"
    redis_pool_size: int = 20

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/distro"

    max_environments: int = 20
    command_timeout_seconds: int = 30
    max_retries: int = 3
    retry_base_delay: float = 1.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

    websocket_heartbeat_interval: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
