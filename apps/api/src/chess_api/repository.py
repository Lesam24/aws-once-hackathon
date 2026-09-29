"""Capa de persistencia.

El MVP usa un repositorio en memoria, pero se define como interfaz (``Protocol``) para
poder sustituirlo por PostgreSQL sin tocar la capa de servicio. El diseño respeta la
separación de tablas sugerida en docs/ARCHITECTURE.md §7:
``analyses``, ``feedback_events``, etc.
"""

from __future__ import annotations

import threading
from typing import Protocol, runtime_checkable

from chess_contracts.models import Analysis, FeedbackEvent


@runtime_checkable
class Repository(Protocol):
    """Interfaz de persistencia. Cualquier backend (memoria, Postgres) la implementa."""

    def save_analysis(self, analysis: Analysis) -> None: ...
    def get_analysis(self, analysis_id: str) -> Analysis | None: ...
    def list_analyses(self, limit: int = 50, offset: int = 0) -> list[Analysis]: ...
    def save_feedback(self, event: FeedbackEvent) -> None: ...
    def list_feedback(self, analysis_id: str) -> list[FeedbackEvent]: ...


class InMemoryRepository:
    """Repositorio en memoria, seguro para hilos. Válido para el MVP y los tests."""

    def __init__(self) -> None:
        self._analyses: dict[str, Analysis] = {}
        self._feedback: dict[str, list[FeedbackEvent]] = {}
        self._order: list[str] = []
        self._lock = threading.RLock()

    def save_analysis(self, analysis: Analysis) -> None:
        with self._lock:
            if analysis.id not in self._analyses:
                self._order.append(analysis.id)
            # copia defensiva para no compartir referencias mutables
            self._analyses[analysis.id] = analysis.model_copy(deep=True)

    def get_analysis(self, analysis_id: str) -> Analysis | None:
        with self._lock:
            stored = self._analyses.get(analysis_id)
            return stored.model_copy(deep=True) if stored else None

    def list_analyses(self, limit: int = 50, offset: int = 0) -> list[Analysis]:
        with self._lock:
            # más recientes primero
            ids = list(reversed(self._order))[offset : offset + limit]
            return [self._analyses[i].model_copy(deep=True) for i in ids]

    def save_feedback(self, event: FeedbackEvent) -> None:
        with self._lock:
            self._feedback.setdefault(event.analysis_id, []).append(
                event.model_copy(deep=True)
            )

    def list_feedback(self, analysis_id: str) -> list[FeedbackEvent]:
        with self._lock:
            return [e.model_copy(deep=True) for e in self._feedback.get(analysis_id, [])]


def build_repository(backend: str) -> Repository:
    """Fábrica de repositorios según la configuración."""
    if backend == "memory":
        return InMemoryRepository()
    # Punto de extensión: PostgresRepository(database_url) en una iteración posterior.
    raise NotImplementedError(f"Backend de persistencia no soportado: {backend!r}")
