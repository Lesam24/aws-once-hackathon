"""Etiquetas de reconocimiento por casilla y su mapeo al dominio.

Las etiquetas siguen la enumeración de docs/ARCHITECTURE.md paso E:
``empty``, ``white_pawn`` ... ``black_king``, ``unknown``.
"""

from __future__ import annotations

from chess_contracts.spec import Color, PieceType

EMPTY = "empty"
UNKNOWN = "unknown"

_PIECE_BY_LABEL: dict[str, tuple[Color, PieceType]] = {
    "white_pawn": (Color.WHITE, PieceType.PAWN),
    "white_knight": (Color.WHITE, PieceType.KNIGHT),
    "white_bishop": (Color.WHITE, PieceType.BISHOP),
    "white_rook": (Color.WHITE, PieceType.ROOK),
    "white_queen": (Color.WHITE, PieceType.QUEEN),
    "white_king": (Color.WHITE, PieceType.KING),
    "black_pawn": (Color.BLACK, PieceType.PAWN),
    "black_knight": (Color.BLACK, PieceType.KNIGHT),
    "black_bishop": (Color.BLACK, PieceType.BISHOP),
    "black_rook": (Color.BLACK, PieceType.ROOK),
    "black_queen": (Color.BLACK, PieceType.QUEEN),
    "black_king": (Color.BLACK, PieceType.KING),
}

ALL_LABELS = (EMPTY, UNKNOWN, *_PIECE_BY_LABEL.keys())


def label_to_piece(label: str) -> tuple[Color, PieceType] | None:
    """Convierte una etiqueta a ``(color, tipo)`` o ``None`` si es empty/unknown."""
    return _PIECE_BY_LABEL.get(label)


def piece_to_label(color: Color, ptype: PieceType) -> str:
    """Convierte ``(color, tipo)`` en la etiqueta correspondiente."""
    return f"{color.value}_{ptype.value}"


def is_occupied_label(label: str) -> bool:
    return label in _PIECE_BY_LABEL
