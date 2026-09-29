"""Recognizers de piezas intercambiables.

El pipeline depende únicamente de la interfaz ``PieceRecognizer``. Sustituir el modelo
(baseline clásico, CNN, detector multicategoría, VLM de segundo nivel) no requiere cambiar
el contrato ``BoardState`` ni el motor de transcripción.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .labels import EMPTY, UNKNOWN, is_occupied_label, piece_to_label


@dataclass
class SquareImage:
    """Una casilla segmentada lista para clasificar.

    ``pixels`` es opcional para poder ejecutar el pipeline sin OpenCV/numpy. Cuando hay un
    modelo real, contendrá el recorte de la casilla (p. ej. un ``numpy.ndarray``).
    """

    square: str
    pixels: object | None = None


@dataclass
class SquareLabel:
    square: str
    label: str
    confidence: float


@runtime_checkable
class PieceRecognizer(Protocol):
    """Interfaz que debe implementar cualquier modelo de reconocimiento de piezas."""

    #: Identificador de versión del modelo (para trazabilidad).
    version: str

    def recognize(self, squares: list[SquareImage]) -> list[SquareLabel]:
        """Clasifica cada casilla como ``empty``, una pieza, o ``unknown``."""
        ...


@dataclass
class StubRecognizer:
    """Recognizer determinista para desarrollo y pruebas end-to-end.

    No mira los píxeles: devuelve una posición conocida (por defecto, la posición inicial
    estándar del ajedrez). Permite construir y probar API, frontend y transcripción antes
    de tener un modelo entrenado.
    """

    version: str = "stub@1"
    position: dict[str, str] = field(default_factory=lambda: dict(_INITIAL_POSITION))
    default_confidence: float = 0.99

    def recognize(self, squares: list[SquareImage]) -> list[SquareLabel]:
        out: list[SquareLabel] = []
        for sq in squares:
            label = self.position.get(sq.square, EMPTY)
            conf = self.default_confidence if is_occupied_label(label) else 1.0
            out.append(SquareLabel(square=sq.square, label=label, confidence=conf))
        return out


@dataclass
class UncertainRecognizer:
    """Recognizer que marca todo como ``unknown``. Útil para probar el flujo de incertidumbre."""

    version: str = "uncertain@1"
    confidence: float = 0.4

    def recognize(self, squares: list[SquareImage]) -> list[SquareLabel]:
        return [
            SquareLabel(square=sq.square, label=UNKNOWN, confidence=self.confidence)
            for sq in squares
        ]


def _standard_initial_position() -> dict[str, str]:
    from chess_contracts.spec import Color, PieceType

    pos: dict[str, str] = {}
    back = [
        PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
        PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK,
    ]
    files = "abcdefgh"
    for i, ptype in enumerate(back):
        pos[f"{files[i]}1"] = piece_to_label(Color.WHITE, ptype)
        pos[f"{files[i]}2"] = piece_to_label(Color.WHITE, PieceType.PAWN)
        pos[f"{files[i]}7"] = piece_to_label(Color.BLACK, PieceType.PAWN)
        pos[f"{files[i]}8"] = piece_to_label(Color.BLACK, ptype)
    return pos


_INITIAL_POSITION = _standard_initial_position()
