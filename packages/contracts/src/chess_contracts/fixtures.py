"""Fixtures de posiciones reales extraídas de docs/BRAILLE_SPEC.md.

Se usan como material de pruebas unitarias y de evaluación. Los diagramas de audio dan
colocaciones explícitas de piezas; se codifican aquí como ``BoardState`` canónicos.

Nota de fidelidad: el Diagrama 5 de la fuente contiene una inconsistencia (A6 aparece
como caballo negro y como peón negro). Se conserva tal cual en ``DIAGRAM_5_RAW`` para
usarlo como caso de validación, no como ground truth.
"""

from __future__ import annotations

from .models import BoardState, Piece
from .spec import BoardOrientation, Color, PieceType

K, Q, B, N, R, P = (
    PieceType.KING,
    PieceType.QUEEN,
    PieceType.BISHOP,
    PieceType.KNIGHT,
    PieceType.ROOK,
    PieceType.PAWN,
)
W, BL = Color.WHITE, Color.BLACK


def _p(color: Color, ptype: PieceType, square: str) -> Piece:
    return Piece(color=color, type=ptype, square=square)


# Diagrama 1 — pág. 15
DIAGRAM_1 = BoardState(
    orientation=BoardOrientation.WHITE_AT_BOTTOM,
    pieces=[
        _p(W, K, "e2"), _p(W, Q, "a4"), _p(W, R, "c1"), _p(W, R, "h1"),
        _p(W, B, "b5"), _p(W, N, "c3"), _p(W, N, "f3"),
        _p(W, P, "a2"), _p(W, P, "b2"), _p(W, P, "d2"),
        _p(W, P, "f2"), _p(W, P, "g2"), _p(W, P, "h2"),
        _p(BL, K, "e8"), _p(BL, Q, "d7"), _p(BL, R, "a8"), _p(BL, R, "h8"),
        _p(BL, B, "f8"), _p(BL, B, "g4"), _p(BL, N, "c6"),
        _p(BL, P, "a7"), _p(BL, P, "b7"), _p(BL, P, "c5"),
        _p(BL, P, "e7"), _p(BL, P, "f7"), _p(BL, P, "g7"), _p(BL, P, "h7"),
    ],
)

# Diagrama 2 — pág. 17
DIAGRAM_2 = BoardState(
    orientation=BoardOrientation.WHITE_AT_BOTTOM,
    pieces=[
        _p(W, K, "d2"), _p(W, B, "h6"), _p(W, N, "e1"),
        _p(W, P, "a3"), _p(W, P, "b2"), _p(W, P, "g2"), _p(W, P, "h3"),
        _p(BL, K, "e6"), _p(BL, B, "c4"), _p(BL, N, "c6"),
        _p(BL, P, "b7"), _p(BL, P, "b6"), _p(BL, P, "d5"),
        _p(BL, P, "g6"), _p(BL, P, "h7"),
    ],
)

# Diagrama 23 — pág. 44
DIAGRAM_23 = BoardState(
    orientation=BoardOrientation.WHITE_AT_BOTTOM,
    pieces=[
        _p(W, K, "h3"), _p(W, Q, "f5"), _p(W, R, "f1"), _p(W, N, "e2"),
        _p(W, P, "a6"), _p(W, P, "c4"), _p(W, P, "d5"),
        _p(W, P, "g3"), _p(W, P, "g4"),
        _p(BL, K, "h7"), _p(BL, Q, "g6"), _p(BL, R, "e7"), _p(BL, B, "e3"),
        _p(BL, P, "a7"), _p(BL, P, "c5"), _p(BL, P, "e4"),
        _p(BL, P, "g5"), _p(BL, P, "h6"),
    ],
)

ALL_VALID_DIAGRAMS = {
    "diagram_1": DIAGRAM_1,
    "diagram_2": DIAGRAM_2,
    "diagram_23": DIAGRAM_23,
}
