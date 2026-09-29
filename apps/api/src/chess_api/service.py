"""Capa de servicio: orquesta el ciclo de vida del análisis y el feedback.

Estado del análisis: ``created -> processing -> completed / failed``.

Reglas invariantes:
- La predicción original nunca se sobreescribe por una corrección.
- El feedback entra como ``pending`` y no reentrena el modelo en producción.
- Cada análisis y evento registra ``model_version`` y ``pipeline_version``.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from chess_contracts.models import (
    AccessMode,
    Analysis,
    AnalysisStatus,
    BoardState,
    FeedbackEvent,
    FeedbackType,
    ReviewStatus,
)
from chess_contracts.transcription import transcribe
from chess_contracts.validation import validate_board
from chess_vision import ImageError, VisionPipeline

from .repository import Repository

logger = logging.getLogger("chess_api.service")


class NotFoundError(Exception):
    """El recurso solicitado no existe."""


class AnalysisService:
    def __init__(self, repository: Repository, pipeline: VisionPipeline) -> None:
        self._repo = repository
        self._pipeline = pipeline

    # -- Ciclo de vida del análisis ---------------------------------------------------

    def create_analysis(
        self, image_bytes: bytes, mode: AccessMode = AccessMode.BLIND
    ) -> Analysis:
        """Crea un análisis y lo procesa end-to-end (síncrono en el MVP)."""
        analysis_id = uuid.uuid4().hex
        analysis = Analysis(
            id=analysis_id,
            status=AnalysisStatus.CREATED,
            mode=mode,
            image_ref=f"mem://{analysis_id}",
        )
        self._repo.save_analysis(analysis)
        logger.info("analysis %s created (mode=%s)", analysis_id, mode.value)

        return self._process(analysis, image_bytes)

    def _process(self, analysis: Analysis, image_bytes: bytes) -> Analysis:
        analysis.status = AnalysisStatus.PROCESSING
        analysis.updated_at = datetime.now(timezone.utc)
        self._repo.save_analysis(analysis)

        try:
            vision = self._pipeline.run(image_bytes)
            board = self._pipeline.to_board_state(vision)
            validation = validate_board(board)
            transcription = transcribe(board)

            analysis.vision_result = vision
            analysis.board_state = board
            analysis.validation = validation
            analysis.transcription = transcription
            analysis.model_version = vision.model_version
            analysis.pipeline_version = vision.pipeline_version
            analysis.status = AnalysisStatus.COMPLETED
            logger.info("analysis %s completed", analysis.id)
        except ImageError as exc:
            analysis.status = AnalysisStatus.FAILED
            analysis.error = str(exc)
            logger.warning("analysis %s failed: %s", analysis.id, exc)
        except Exception as exc:  # defensivo: no perder el registro ante fallo inesperado
            analysis.status = AnalysisStatus.FAILED
            analysis.error = f"Error interno del pipeline: {exc}"
            logger.exception("analysis %s crashed", analysis.id)
        finally:
            analysis.updated_at = datetime.now(timezone.utc)
            self._repo.save_analysis(analysis)

        return analysis

    def get_analysis(self, analysis_id: str) -> Analysis:
        analysis = self._repo.get_analysis(analysis_id)
        if analysis is None:
            raise NotFoundError(f"Análisis no encontrado: {analysis_id}")
        return analysis

    def list_history(self, limit: int = 50, offset: int = 0) -> list[Analysis]:
        return self._repo.list_analyses(limit=limit, offset=offset)

    # -- Corrección y feedback --------------------------------------------------------

    def submit_correction(
        self,
        analysis_id: str,
        corrected: BoardState,
        user_id: str | None = None,
    ) -> FeedbackEvent:
        """Registra una corrección sin sobreescribir la predicción original."""
        analysis = self.get_analysis(analysis_id)
        event = FeedbackEvent(
            id=uuid.uuid4().hex,
            analysis_id=analysis_id,
            feedback_type=FeedbackType.CORRECTION,
            user_id=user_id,
            original_board_state=analysis.board_state,  # preservada intacta
            corrected_board_state=corrected,
            model_version=analysis.model_version,
            pipeline_version=analysis.pipeline_version,
            review_status=ReviewStatus.PENDING,  # feedback diferido
        )
        self._repo.save_feedback(event)
        logger.info("correction recorded for analysis %s (event %s)", analysis_id, event.id)
        return event

    def confirm(self, analysis_id: str, user_id: str | None = None) -> FeedbackEvent:
        """Confirma que la transcripción es correcta (feedback positivo)."""
        analysis = self.get_analysis(analysis_id)
        event = FeedbackEvent(
            id=uuid.uuid4().hex,
            analysis_id=analysis_id,
            feedback_type=FeedbackType.CONFIRM,
            user_id=user_id,
            original_board_state=analysis.board_state,
            corrected_board_state=None,
            model_version=analysis.model_version,
            pipeline_version=analysis.pipeline_version,
            review_status=ReviewStatus.PENDING,
        )
        self._repo.save_feedback(event)
        logger.info("confirmation recorded for analysis %s (event %s)", analysis_id, event.id)
        return event

    def list_feedback(self, analysis_id: str) -> list[FeedbackEvent]:
        self.get_analysis(analysis_id)  # valida existencia
        return self._repo.list_feedback(analysis_id)
