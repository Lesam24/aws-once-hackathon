"""Modelos de request/response de la API (envoltorios sobre los contratos v1)."""

from __future__ import annotations

from pydantic import BaseModel

from chess_contracts.models import (
    Analysis,
    BoardState,
    FeedbackEvent,
    Transcription,
)


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
    version: str


class CorrectionRequest(BaseModel):
    corrected_board_state: BoardState
    user_id: str | None = None
    note: str | None = None


class ConfirmRequest(BaseModel):
    user_id: str | None = None


class FeedbackResponse(BaseModel):
    event: FeedbackEvent
    message: str


class TranscriptionResponse(BaseModel):
    analysis_id: str
    transcription: Transcription


class HistoryItem(BaseModel):
    id: str
    status: str
    mode: str
    created_at: str


class HistoryResponse(BaseModel):
    items: list[HistoryItem]


class AnalysisResponse(BaseModel):
    analysis: Analysis
