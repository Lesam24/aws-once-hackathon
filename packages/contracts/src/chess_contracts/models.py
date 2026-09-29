"""Contratos de datos versionados (v1) del sistema.

Estos modelos son el contrato entre frontend, backend, visión y transcripción. Se validan
con Pydantic v2 y pueden exportarse a JSON Schema (ver ``json_schemas.py``).

Cadena de transformación:

    Image -> VisionResult -> BoardState -> ValidationResult -> Transcription
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .coordinates import is_valid_square
from .spec import (
    FORMAT_VERSION,
    ArrowDirection,
    BoardOrientation,
    Color,
    HighlightColor,
    PieceType,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class _Base(BaseModel):
    model_config = ConfigDict(use_enum_values=False, extra="forbid")


# --------------------------------------------------------------------------------------
# Entidades del tablero
# --------------------------------------------------------------------------------------


class Piece(_Base):
    """Una pieza en una casilla, con la confianza del reconocimiento."""

    color: Color
    type: PieceType
    square: str = Field(..., description="Casilla a1..h8")
    confidence: float = Field(1.0, ge=0.0, le=1.0)

    @field_validator("square")
    @classmethod
    def _validate_square(cls, v: str) -> str:
        if not is_valid_square(v):
            raise ValueError(f"casilla inválida: {v!r}")
        return v


class Highlight(_Base):
    """Casilla resaltada, modelada como entidad independiente del estado de piezas."""

    square: str
    color: HighlightColor
    confidence: float = Field(1.0, ge=0.0, le=1.0)

    @field_validator("square")
    @classmethod
    def _validate_square(cls, v: str) -> str:
        if not is_valid_square(v):
            raise ValueError(f"casilla inválida: {v!r}")
        return v


class Arrow(_Base):
    """Flecha dirigida entre dos casillas."""

    from_square: str
    to_square: str
    direction: ArrowDirection = ArrowDirection.FORWARD
    confidence: float = Field(1.0, ge=0.0, le=1.0)

    @field_validator("from_square", "to_square")
    @classmethod
    def _validate_square(cls, v: str) -> str:
        if not is_valid_square(v):
            raise ValueError(f"casilla inválida: {v!r}")
        return v


class BoardState(_Base):
    """Representación canónica de una posición. Contrato entre visión y transcripción.

    La IA NO produce texto directamente: produce este `BoardState`.
    """

    contract_version: str = "1.0"
    orientation: BoardOrientation = BoardOrientation.UNKNOWN
    pieces: list[Piece] = Field(default_factory=list)
    highlights: list[Highlight] = Field(default_factory=list)
    arrows: list[Arrow] = Field(default_factory=list)
    model_version: Optional[str] = None
    pipeline_version: Optional[str] = None


# --------------------------------------------------------------------------------------
# Resultado de visión (antes de normalizar a BoardState)
# --------------------------------------------------------------------------------------


class BoardDetection(_Base):
    """Salida de la etapa de detección geométrica del tablero."""

    board_bbox: tuple[float, float, float, float] = Field(
        ..., description="x, y, width, height"
    )
    corners: list[tuple[float, float]] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class SquarePrediction(_Base):
    """Predicción por casilla: pieza, color o ``unknown``/``empty``."""

    square: str
    label: str = Field(..., description="empty | white_pawn | ... | unknown")
    confidence: float = Field(0.0, ge=0.0, le=1.0)

    @field_validator("square")
    @classmethod
    def _validate_square(cls, v: str) -> str:
        if not is_valid_square(v):
            raise ValueError(f"casilla inválida: {v!r}")
        return v


class VisionResult(_Base):
    """Salida completa del pipeline de visión, previa a la normalización."""

    contract_version: str = "1.0"
    detection: Optional[BoardDetection] = None
    orientation: BoardOrientation = BoardOrientation.UNKNOWN
    squares: list[SquarePrediction] = Field(default_factory=list)
    model_version: Optional[str] = None
    pipeline_version: Optional[str] = None


# --------------------------------------------------------------------------------------
# Validación
# --------------------------------------------------------------------------------------


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ValidationIssue(_Base):
    code: str
    message: str
    severity: Severity = Severity.WARNING
    square: Optional[str] = None


class ValidationResult(_Base):
    contract_version: str = "1.0"
    ok: bool = True
    issues: list[ValidationIssue] = Field(default_factory=list)


# --------------------------------------------------------------------------------------
# Transcripción
# --------------------------------------------------------------------------------------


class TranscriptionLine(_Base):
    """Una línea de la transcripción con su token braille y forma legible."""

    text: str = Field(..., description="Token braille, ej. 'Re⠂'")
    square: Optional[str] = None
    readable: Optional[str] = Field(
        None, description="Descripción para lector de pantalla, ej. 'Rey e1'"
    )


class Transcription(_Base):
    """Salida final del motor de transcripción."""

    contract_version: str = "1.0"
    format_version: str = FORMAT_VERSION
    white_lines: list[TranscriptionLine] = Field(default_factory=list)
    black_lines: list[TranscriptionLine] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)
    arrows: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    narrative: str = Field(
        "",
        description=(
            "Descripción en prosa continua (con comas y puntos) apta para leerse en voz "
            "alta o pasarse a braille. Ej.: 'Piezas blancas: rey en e1, dama en d1. …'"
        ),
    )
    braille_block: str = Field(
        "",
        description=(
            "Transcripción braille en el formato oficial de la ONCE: tokens en línea "
            "separados por espacios, con 'Blancas:' / 'Negras:' y las casillas resaltadas "
            "y flechas descritas aparte. Es la salida principal para línea braille."
        ),
    )

    def as_text(self) -> str:
        """Renderiza la transcripción como texto lineal (una línea por token)."""
        parts: list[str] = []
        if self.white_lines:
            parts.append("Blancas:")
            parts.extend(line.text for line in self.white_lines)
        if self.black_lines:
            parts.append("Negras:")
            parts.extend(line.text for line in self.black_lines)
        if self.highlights:
            parts.append("Resaltadas:")
            parts.extend(self.highlights)
        if self.arrows:
            parts.append("Flechas:")
            parts.extend(self.arrows)
        if self.warnings:
            parts.append("Avisos:")
            parts.extend(self.warnings)
        return "\n".join(parts)


# --------------------------------------------------------------------------------------
# Análisis, corrección, feedback e historial
# --------------------------------------------------------------------------------------


class AnalysisStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AccessMode(str, Enum):
    BLIND = "blind"
    SIGHTED = "sighted"


class Analysis(_Base):
    """Registro de un análisis de imagen y su ciclo de vida."""

    id: str
    status: AnalysisStatus = AnalysisStatus.CREATED
    mode: AccessMode = AccessMode.BLIND
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    image_ref: Optional[str] = None
    vision_result: Optional[VisionResult] = None
    board_state: Optional[BoardState] = None
    validation: Optional[ValidationResult] = None
    transcription: Optional[Transcription] = None
    model_version: Optional[str] = None
    pipeline_version: Optional[str] = None
    error: Optional[str] = None


class ReviewStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    USED_FOR_TRAINING = "used_for_training"


class FeedbackType(str, Enum):
    CONFIRM = "confirm"
    CORRECTION = "correction"


class FeedbackEvent(_Base):
    """Observación independiente de feedback. Nunca modifica el modelo en producción."""

    id: str
    analysis_id: str
    feedback_type: FeedbackType
    user_id: Optional[str] = None
    anonymous_session_id: Optional[str] = None
    original_board_state: Optional[BoardState] = None
    corrected_board_state: Optional[BoardState] = None
    created_at: datetime = Field(default_factory=_utcnow)
    model_version: Optional[str] = None
    pipeline_version: Optional[str] = None
    review_status: ReviewStatus = ReviewStatus.PENDING


class Correction(_Base):
    """Corrección enviada por una persona vidente sobre un análisis."""

    corrected_board_state: BoardState
    user_id: Optional[str] = None
    note: Optional[str] = None
