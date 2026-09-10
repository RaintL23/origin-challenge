from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    twelve_data_api_key: str = ""
    jwt_secret: str = "dev-secret-change-me"
    jwt_expire_minutes: int = 60
    jwt_algorithm: str = "HS256"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    database_url: str = "postgresql://postgres:postgres@127.0.0.1:5432/challenge_acciones"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
