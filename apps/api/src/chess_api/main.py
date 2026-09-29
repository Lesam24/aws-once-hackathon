"""Aplicación FastAPI: ciclo de vida de análisis, transcripción, corrección y feedback."""

from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from chess_contracts.models import AccessMode

from . import __version__
from .config import settings
from .dependencies import get_service
from .schemas import (
    AnalysisResponse,
    ConfirmRequest,
    CorrectionRequest,
    FeedbackResponse,
    HealthResponse,
    HistoryItem,
    HistoryResponse,
    TranscriptionResponse,
)
from .service import AnalysisService, NotFoundError

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("chess_api")

app = FastAPI(title=settings.app_name, version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

P = settings.api_prefix


@app.get(f"{P}/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    return HealthResponse(app=settings.app_name, version=__version__)


@app.post(f"{P}/analyses", response_model=AnalysisResponse, tags=["analyses"])
async def create_analysis(
    image: UploadFile = File(...),
    mode: str = Form("blind"),
    service: AnalysisService = Depends(get_service),
) -> AnalysisResponse:
    """Sube una imagen de tablero y crea un análisis procesado end-to-end."""
    try:
        access_mode = AccessMode(mode)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Modo inválido: {mode!r}")

    data = await image.read()
    if len(data) < settings.min_image_bytes:
        raise HTTPException(status_code=422, detail="La imagen es demasiado pequeña o está vacía.")
    if len(data) > settings.max_image_bytes:
        raise HTTPException(status_code=413, detail="La imagen supera el tamaño máximo permitido.")

    analysis = service.create_analysis(data, mode=access_mode)
    return AnalysisResponse(analysis=analysis)


@app.get(f"{P}/analyses/{{analysis_id}}", response_model=AnalysisResponse, tags=["analyses"])
def get_analysis(
    analysis_id: str, service: AnalysisService = Depends(get_service)
) -> AnalysisResponse:
    try:
        return AnalysisResponse(analysis=service.get_analysis(analysis_id))
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get(
    f"{P}/analyses/{{analysis_id}}/transcription",
    response_model=TranscriptionResponse,
    tags=["analyses"],
)
def get_transcription(
    analysis_id: str, service: AnalysisService = Depends(get_service)
) -> TranscriptionResponse:
    try:
        analysis = service.get_analysis(analysis_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    if analysis.transcription is None:
        raise HTTPException(
            status_code=409,
            detail=f"El análisis no tiene transcripción (estado: {analysis.status.value}).",
        )
    return TranscriptionResponse(analysis_id=analysis_id, transcription=analysis.transcription)


@app.post(
    f"{P}/analyses/{{analysis_id}}/correction",
    response_model=FeedbackResponse,
    tags=["feedback"],
)
def submit_correction(
    analysis_id: str,
    body: CorrectionRequest,
    service: AnalysisService = Depends(get_service),
) -> FeedbackResponse:
    """(Modo vidente) Envía una corrección. No sobreescribe la predicción original."""
    try:
        event = service.submit_correction(
            analysis_id, body.corrected_board_state, user_id=body.user_id
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return FeedbackResponse(
        event=event,
        message="Corrección registrada. Pasará por curación antes de cualquier reentrenamiento.",
    )


@app.post(
    f"{P}/analyses/{{analysis_id}}/feedback/confirm",
    response_model=FeedbackResponse,
    tags=["feedback"],
)
def confirm_result(
    analysis_id: str,
    body: ConfirmRequest,
    service: AnalysisService = Depends(get_service),
) -> FeedbackResponse:
    """(Modo vidente) Confirma que la transcripción es correcta."""
    try:
        event = service.confirm(analysis_id, user_id=body.user_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return FeedbackResponse(event=event, message="Confirmación registrada.")


@app.get(f"{P}/history", response_model=HistoryResponse, tags=["history"])
def history(
    limit: int = 50,
    offset: int = 0,
    service: AnalysisService = Depends(get_service),
) -> HistoryResponse:
    analyses = service.list_history(limit=limit, offset=offset)
    items = [
        HistoryItem(
            id=a.id,
            status=a.status.value,
            mode=a.mode.value,
            created_at=a.created_at.isoformat(),
        )
        for a in analyses
    ]
    return HistoryResponse(items=items)
