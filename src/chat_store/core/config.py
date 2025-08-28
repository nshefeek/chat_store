from functools import lru_cache
from typing import List

from pydantic import PostgresDsn, RedisDsn, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_HOST: str = "localhost"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: SecretStr = SecretStr("postgres")
    DATABASE_NAME: str = "postgres"
    DATABASE_PORT: int = 5432
    DATABASE_URI: PostgresDsn | None = None

    PGADMIN_DEFAULT_EMAIL: str = "admin@chat-store.com"
    PGADMIN_DEFAULT_PASSWORD: str = "admin123"

    @model_validator(mode="before")
    def parse_db_uri(cls, values) -> "DatabaseConfig":
        values["DATABASE_URI"] = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values["DATABASE_USER"],
            password=values["DATABASE_PASSWORD"],
            host=values["DATABASE_HOST"],
            path=values["DATABASE_NAME"],
            port=int(values["DATABASE_PORT"]),
        )
        return values


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: SecretStr = SecretStr("redis")
    REDIS_URI: RedisDsn | None = None

    @model_validator(mode="before")
    def parse_redis_uri(cls, values) -> "RedisConfig":
        values["REDIS_URI"] = RedisDsn.build(
            scheme="redis",
            host=values["REDIS_HOST"],
            port=int(values["REDIS_PORT"]),
            password=values["REDIS_PASSWORD"],
        )
        return values


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    API_KEY: str = "api_key"


class Config(BaseSettings):

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Chat Store"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    ADMIN_EMAIL: str = "admin@chat-store.com"
    ADMIN_PASSWORD: SecretStr = SecretStr("password123")

    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:8000"]

    RATE_LIMITER_ENABLED: bool = True
    RATE_LIMITER_MAX_REQUESTS: int = 100    
    RATE_LIMITER_TIMEFRAME: int = 60
    
    # Rate limiting configuration
    RATE_LIMIT_CREATE_SESSION: str = "10/minute"
    RATE_LIMIT_LIST_SESSIONS: str = "30/minute"
    RATE_LIMIT_CREATE_MESSAGE: str = "50/minute"
    RATE_LIMIT_GET_MESSAGES: str = "100/minute"
    RATE_LIMIT_RESUME_MESSAGE: str = "5/minute"
    RATE_LIMIT_UPDATE_SESSION: str = "20/minute"
    RATE_LIMIT_DELETE_SESSION: str = "10/minute"
    RATE_LIMIT_TOGGLE_FAVORITE: str = "20/minute"

    auth: AuthConfig = AuthConfig()
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()

    @model_validator(mode="before")
    @classmethod
    def assemble_cors_origins(cls, values) -> "Config":
        if isinstance(values, dict):
            cors_origins = values.get("BACKEND_CORS_ORIGINS")
            if isinstance(cors_origins, str):
                if cors_origins.startswith("["):
                    # Handle JSON array string
                    import json
                    try:
                        values["BACKEND_CORS_ORIGINS"] = json.loads(cors_origins)
                    except json.JSONDecodeError:
                        values["BACKEND_CORS_ORIGINS"] = [cors_origins]
                else:
                    # Handle comma-separated string
                    values["BACKEND_CORS_ORIGINS"] = [i.strip() for i in cors_origins.split(",")]
        return values

    @model_validator(mode="after")
    def validate_configuration(self) -> "Config":
        """Validate configuration settings."""
        if self.RATE_LIMITER_ENABLED and not self.redis.REDIS_URI:
            raise ValueError("Redis URI is required when rate limiting is enabled")
        
        if not self.auth.API_KEY or len(self.auth.API_KEY) < 8:
            raise ValueError("API key must be at least 8 characters long")
        
        if not self.database.DATABASE_URI:
            raise ValueError("Database URI is required")
        
        return self


@lru_cache
def get_config() -> Config:
    return Config()

config = get_config()