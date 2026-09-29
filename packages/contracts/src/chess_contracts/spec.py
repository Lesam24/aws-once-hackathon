"""Constantes de la especificación braille del ajedrez (Reto Ajedrez ONCE).

Fuente: docs/BRAILLE_SPEC.md y docs/PROMPT.md, basado en el Documento técnico B8 de la
Comisión Braille Española.

Este módulo NO debe contener lógica; solo las constantes de la especificación. La lógica
de conversión vive en ``braille.py`` y ``coordinates.py`` para mantener una única fuente
de verdad y facilitar los tests deterministas.
"""

from __future__ import annotations

from enum import Enum
from types import MappingProxyType
from typing import Mapping

# --------------------------------------------------------------------------------------
# Columnas y filas
# --------------------------------------------------------------------------------------

#: Columnas de izquierda a derecha (posición de las blancas abajo).
FILES: tuple[str, ...] = ("a", "b", "c", "d", "e", "f", "g", "h")

#: Filas válidas, 1..8 comenzando desde la posición de las blancas.
RANKS: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8)

# --------------------------------------------------------------------------------------
# Números en posición baja (braille) para las filas 1..8
# --------------------------------------------------------------------------------------

#: Mapa fila -> carácter braille (número en posición baja). Fuente de verdad.
RANK_TO_BRAILLE: Mapping[int, str] = MappingProxyType(
    {
        1: "\u2802",  # ⠂
        2: "\u2806",  # ⠆
        3: "\u2812",  # ⠒
        4: "\u2832",  # ⠲
        5: "\u2822",  # ⠢
        6: "\u2816",  # ⠖
        7: "\u2836",  # ⠶
        8: "\u2826",  # ⠦
    }
)

#: Mapa inverso braille -> fila.
BRAILLE_TO_RANK: Mapping[str, int] = MappingProxyType(
    {v: k for k, v in RANK_TO_BRAILLE.items()}
)

# --------------------------------------------------------------------------------------
# Piezas
# --------------------------------------------------------------------------------------


class PieceType(str, Enum):
    """Tipos de pieza en el dominio (independiente del color)."""

    KING = "king"
    QUEEN = "queen"
    BISHOP = "bishop"
    KNIGHT = "knight"
    ROOK = "rook"
    PAWN = "pawn"


class Color(str, Enum):
    """Color de la pieza."""

    WHITE = "white"
    BLACK = "black"


#: Identificador de pieza en la notación braille española (R/D/A/C/T/P).
PIECE_TO_LETTER: Mapping[PieceType, str] = MappingProxyType(
    {
        PieceType.KING: "R",
        PieceType.QUEEN: "D",
        PieceType.BISHOP: "A",
        PieceType.KNIGHT: "C",
        PieceType.ROOK: "T",
        PieceType.PAWN: "P",
    }
)

#: Mapa inverso letra -> tipo de pieza.
LETTER_TO_PIECE: Mapping[str, PieceType] = MappingProxyType(
    {v: k for k, v in PIECE_TO_LETTER.items()}
)

# --------------------------------------------------------------------------------------
# Elementos gráficos adicionales
# --------------------------------------------------------------------------------------


class HighlightColor(str, Enum):
    """Colores de casilla resaltada previstos por la especificación."""

    YELLOW = "yellow"
    RED = "red"


class ArrowDirection(str, Enum):
    """Dirección de una flecha entre casillas.

    La especificación usa dos símbolos según la dirección de la flecha.
    """

    FORWARD = "forward"  # ⠒⠕
    BACKWARD = "backward"  # ⠪⠒


#: Símbolos braille de flecha según la dirección.
ARROW_SYMBOL: Mapping[ArrowDirection, str] = MappingProxyType(
    {
        ArrowDirection.FORWARD: "\u2812\u2815",  # ⠒⠕
        ArrowDirection.BACKWARD: "\u282a\u2812",  # ⠪⠒
    }
)


class BoardOrientation(str, Enum):
    """Orientación del tablero. Debe determinarse explícitamente, nunca asumirse."""

    WHITE_AT_BOTTOM = "white-at-bottom"
    BLACK_AT_BOTTOM = "black-at-bottom"
    UNKNOWN = "unknown"


#: Etiqueta reservada para expresar incertidumbre sin inventar una pieza.
UNKNOWN_LABEL = "unknown"

#: Versión del formato de la transcripción / contratos.
FORMAT_VERSION = "1.0"
