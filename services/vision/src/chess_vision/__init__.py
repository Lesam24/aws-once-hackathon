"""chess_vision — pipeline de visión con recognizer de piezas intercambiable."""

from __future__ import annotations

from .labels import ALL_LABELS, EMPTY, UNKNOWN, label_to_piece, piece_to_label
from .pipeline import PIPELINE_VERSION, ImageError, VisionPipeline
from .recognizers import (
    PieceRecognizer,
    SquareImage,
    SquareLabel,
    StubRecognizer,
    UncertainRecognizer,
)

__all__ = [
    "VisionPipeline",
    "ImageError",
    "PIPELINE_VERSION",
    "PieceRecognizer",
    "StubRecognizer",
    "UncertainRecognizer",
    "SquareImage",
    "SquareLabel",
    "label_to_piece",
    "piece_to_label",
    "ALL_LABELS",
    "EMPTY",
    "UNKNOWN",
]
