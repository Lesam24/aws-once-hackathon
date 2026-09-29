"""Configuración de la API mediante pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CHESS_", env_file=".env", extra="ignore")

    app_name: str = "Chess Accessibility API"
    api_prefix: str = "/api/v1"

    # Límites de ingestión de imágenes.
    max_image_bytes: int = 10 * 1024 * 1024  # 10 MB
    min_image_bytes: int = 64

    # CORS (frontend de desarrollo).
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Persistencia. "memory" para el MVP; "postgres" queda preparado.
    storage_backend: str = "memory"
    database_url: str | None = None

    log_level: str = "INFO"


settings = Settings()
