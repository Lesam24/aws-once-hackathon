"""Conversión determinista relacionada con braille.

Única fuente de verdad para el mapa fila -> braille. La tabla vive en ``spec.py``; aquí
están las funciones de conversión y la construcción del token braille de una casilla.
"""

from __future__ import annotations

from .coordinates import is_valid_square, rank_of, file_of
from .spec import (
    BRAILLE_TO_RANK,
    PIECE_TO_LETTER,
    RANK_TO_BRAILLE,
    PieceType,
)

__all__ = [
    "rank_to_braille",
    "braille_to_rank",
    "square_to_braille",
    "piece_token",
]


def rank_to_braille(rank: int) -> str:
    """Devuelve el carácter braille (número en posición baja) de una fila 1..8."""
    try:
        return RANK_TO_BRAILLE[rank]
    except KeyError as exc:
        raise ValueError(f"fila fuera de rango 1..8: {rank}") from exc


def braille_to_rank(char: str) -> int:
    """Devuelve la fila 1..8 correspondiente a un carácter braille."""
    try:
        return BRAILLE_TO_RANK[char]
    except KeyError as exc:
        raise ValueError(f"carácter braille no reconocido: {char!r}") from exc


def square_to_braille(square: str) -> str:
    """Convierte una casilla ``a1``..``h8`` a ``<letra columna><braille fila>``.

    Ej.: ``"e1"`` -> ``"e⠂"``. Nota: la columna se representa con la letra latina tal
    como indica la especificación; solo la fila se transcribe a braille.
    """
    if not is_valid_square(square):
        raise ValueError(f"casilla inválida: {square!r}")
    return f"{file_of(square)}{rank_to_braille(rank_of(square))}"


def piece_token(piece_type: PieceType, square: str, *, with_piece_letter: bool = True) -> str:
    """Construye el token de una pieza en una casilla.

    :param with_piece_letter: si ``True`` antepone la letra de pieza (R/D/A/C/T/P).
        Si ``False`` (variante de formato de peones), solo devuelve la casilla braille.

    Ej.: ``piece_token(PieceType.KING, "e1")`` -> ``"Re⠂"``.
    """
    coord = square_to_braille(square)
    if not with_piece_letter:
        return coord
    return f"{PIECE_TO_LETTER[piece_type]}{coord}"
