"""Conversión determinista entre índices ``(fila, columna)`` y casillas ``a1``..``h8``.

Única fuente de verdad para coordenadas. El dominio y la visión deben usar SIEMPRE estas
funciones en lugar de construir casillas a mano.

Convenio de índices (independiente de la orientación de captura):

- ``file_index``: 0..7 corresponde a las columnas ``a``..``h``.
- ``rank``: 1..8 tal como se numera en la notación (1 = base de las blancas).

La *orientación* (quién está abajo en la imagen) es responsabilidad del pipeline de visión;
este módulo trabaja siempre en el espacio canónico de coordenadas de ajedrez.
"""

from __future__ import annotations

from .spec import FILES, RANKS

__all__ = [
    "square_from_indices",
    "indices_from_square",
    "is_valid_square",
    "all_squares",
    "file_of",
    "rank_of",
]


def square_from_indices(file_index: int, rank: int) -> str:
    """Devuelve la casilla ``a1``..``h8`` a partir de índice de columna y fila.

    :param file_index: 0..7 (0 = ``a``).
    :param rank: 1..8.
    :raises ValueError: si los índices están fuera de rango.
    """
    if not 0 <= file_index <= 7:
        raise ValueError(f"file_index fuera de rango 0..7: {file_index}")
    if rank not in RANKS:
        raise ValueError(f"rank fuera de rango 1..8: {rank}")
    return f"{FILES[file_index]}{rank}"


def indices_from_square(square: str) -> tuple[int, int]:
    """Devuelve ``(file_index, rank)`` a partir de una casilla ``a1``..``h8``.

    :raises ValueError: si la casilla no es válida.
    """
    if not is_valid_square(square):
        raise ValueError(f"casilla inválida: {square!r}")
    file_char, rank_char = square[0], square[1]
    return FILES.index(file_char), int(rank_char)


def is_valid_square(square: str) -> bool:
    """Comprueba si ``square`` es una casilla válida ``a1``..``h8``."""
    if not isinstance(square, str) or len(square) != 2:
        return False
    file_char, rank_char = square[0], square[1]
    if file_char not in FILES:
        return False
    if not rank_char.isdigit():
        return False
    return int(rank_char) in RANKS


def file_of(square: str) -> str:
    """Devuelve la letra de columna (``a``..``h``) de la casilla."""
    return square[0]


def rank_of(square: str) -> int:
    """Devuelve la fila (1..8) de la casilla."""
    return int(square[1])


def all_squares() -> list[str]:
    """Devuelve las 64 casillas en orden fila 8 -> 1, columna a -> h (lectura visual)."""
    return [f"{f}{r}" for r in reversed(RANKS) for f in FILES]
