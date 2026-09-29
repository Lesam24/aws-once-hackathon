"""Wiring de dependencias (singletons de repositorio, pipeline y servicio)."""

from __future__ import annotations

from functools import lru_cache

from chess_vision import VisionPipeline, StubRecognizer

from .config import settings
from .repository import Repository, build_repository
from .service import AnalysisService


@lru_cache(maxsize=1)
def get_repository() -> Repository:
    return build_repository(settings.storage_backend)


@lru_cache(maxsize=1)
def get_pipeline() -> VisionPipeline:
    # MVP: recognizer stub determinista. Se sustituye por el modelo entrenado sin
    # cambiar el contrato ni los endpoints.
    return VisionPipeline(recognizer=StubRecognizer())


@lru_cache(maxsize=1)
def get_service() -> AnalysisService:
    return AnalysisService(repository=get_repository(), pipeline=get_pipeline())


def reset_singletons() -> None:
    """Limpia los singletons (usado en tests para aislar estado)."""
    get_repository.cache_clear()
    get_pipeline.cache_clear()
    get_service.cache_clear()
