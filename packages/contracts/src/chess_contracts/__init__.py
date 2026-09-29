"""chess_contracts — contratos de datos versionados y dominio determinista.

Ver README.md del paquete. Todo aquí es puro (sin OpenCV/IA/BD).
"""

from __future__ import annotations

from . import braille, coordinates, spec
from .models import (
    AccessMode,
    Analysis,
    AnalysisStatus,
    Arrow,
    BoardDetection,
    BoardState,
    Color,
    Correction,
    FeedbackEvent,
    FeedbackType,
    Highlight,
    Piece,
    ReviewStatus,
    Severity,
    SquarePrediction,
    Transcription,
    TranscriptionLine,
    ValidationIssue,
    ValidationResult,
    VisionResult,
)
from .spec import (
    ArrowDirection,
    BoardOrientation,
    HighlightColor,
    PieceType,
    FORMAT_VERSION,
)
from .transcription import TranscriptionOptions, transcribe
from .validation import validate_board

__version__ = "1.0.0"

__all__ = [
    "spec",
    "braille",
    "coordinates",
    # models
    "AccessMode",
    "Analysis",
    "AnalysisStatus",
    "Arrow",
    "ArrowDirection",
    "BoardDetection",
    "BoardOrientation",
    "BoardState",
    "Color",
    "Correction",
    "FeedbackEvent",
    "FeedbackType",
    "Highlight",
    "HighlightColor",
    "Piece",
    "PieceType",
    "ReviewStatus",
    "Severity",
    "SquarePrediction",
    "Transcription",
    "TranscriptionLine",
    "ValidationIssue",
    "ValidationResult",
    "VisionResult",
    "FORMAT_VERSION",
    # engines
    "transcribe",
    "TranscriptionOptions",
    "validate_board",
    "__version__",
]
