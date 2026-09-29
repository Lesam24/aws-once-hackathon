"""Motor de transcripción determinista: ``BoardState`` -> ``Transcription``.

Reglas (de docs/BRAILLE_SPEC.md y docs/PROMPT.md):

- Las piezas se transcriben como ``<letra pieza><columna><fila braille>`` (ej. ``Re⠂``).
- La columna se escribe con su letra latina; solo la fila usa braille (número bajo).
- Las casillas resaltadas se escriben por separado indicando su color.
- Las flechas se representan uniendo casillas con ``⠒⠕`` (forward) o ``⠪⠒`` (backward).
- Los peones admiten una variante sin letra ``P`` (solo coordenada). Es una opción de
  formato, no el comportamiento por defecto.

El motor NO decide qué pieza había en una casilla: solo transforma un ``BoardState`` ya
resuelto. La incertidumbre (piezas ``unknown``) se refleja como avisos, nunca inventando
una pieza.
"""

from __future__ import annotations

from .braille import piece_token, square_to_braille
from .coordinates import file_of, rank_of
from .models import (
    Arrow,
    BoardState,
    Highlight,
    Piece,
    Transcription,
    TranscriptionLine,
)
from .spec import (
    ARROW_SYMBOL,
    PIECE_TO_LETTER,
    Color,
    PieceType,
)

__all__ = ["transcribe", "TranscriptionOptions"]

#: Descripción legible de cada tipo de pieza (para lectores de pantalla).
_PIECE_READABLE = {
    PieceType.KING: "Rey",
    PieceType.QUEEN: "Dama",
    PieceType.BISHOP: "Alfil",
    PieceType.KNIGHT: "Caballo",
    PieceType.ROOK: "Torre",
    PieceType.PAWN: "Peón",
}

_COLOR_READABLE = {Color.WHITE: "blanca", Color.BLACK: "negra"}

#: Orden de importancia para ordenar la salida de forma estable y natural.
_PIECE_ORDER = {
    PieceType.KING: 0,
    PieceType.QUEEN: 1,
    PieceType.ROOK: 2,
    PieceType.BISHOP: 3,
    PieceType.KNIGHT: 4,
    PieceType.PAWN: 5,
}


class TranscriptionOptions:
    """Opciones de formato de la transcripción."""

    def __init__(self, *, pawns_without_letter: bool = False) -> None:
        #: Si True, los peones se escriben solo como coordenada (variante de formato).
        self.pawns_without_letter = pawns_without_letter


def _piece_sort_key(piece: Piece) -> tuple[int, int, int]:
    """Orden estable: por tipo de pieza, luego columna, luego fila."""
    return (
        _PIECE_ORDER[piece.type],
        file_of(piece.square),  # type: ignore[return-value]
        rank_of(piece.square),
    )


def _sort_pieces(pieces: list[Piece]) -> list[Piece]:
    return sorted(pieces, key=lambda p: (_PIECE_ORDER[p.type], p.square))


def _line_for_piece(piece: Piece, options: TranscriptionOptions) -> TranscriptionLine:
    with_letter = not (piece.type is PieceType.PAWN and options.pawns_without_letter)
    text = piece_token(piece.type, piece.square, with_piece_letter=with_letter)
    readable = (
        f"{_PIECE_READABLE[piece.type]} {_COLOR_READABLE[piece.color]} en "
        f"{piece.square}"
    )
    return TranscriptionLine(text=text, square=piece.square, readable=readable)


def _highlight_repr(h: Highlight) -> str:
    color = "amarillo" if h.color.value == "yellow" else "rojo"
    return f"{square_to_braille(h.square)} ({color})"


def _arrow_repr(a: Arrow) -> str:
    symbol = ARROW_SYMBOL[a.direction]
    return f"{square_to_braille(a.from_square)}{symbol}{square_to_braille(a.to_square)}"


def transcribe(
    board: BoardState, options: TranscriptionOptions | None = None
) -> Transcription:
    """Transforma un ``BoardState`` en una ``Transcription`` determinista.

    La misma entrada produce siempre la misma salida (requisito de reproducibilidad).
    """
    opts = options or TranscriptionOptions()

    white = [p for p in board.pieces if p.color is Color.WHITE]
    black = [p for p in board.pieces if p.color is Color.BLACK]

    white_lines = [_line_for_piece(p, opts) for p in _sort_pieces(white)]
    black_lines = [_line_for_piece(p, opts) for p in _sort_pieces(black)]

    highlights = [_highlight_repr(h) for h in board.highlights]
    arrows = [_arrow_repr(a) for a in board.arrows]

    warnings: list[str] = []
    if board.orientation.value == "unknown":
        warnings.append(
            "Orientación del tablero no determinada; la lectura puede no ser fiable."
        )
    low_conf = [p for p in board.pieces if p.confidence < 0.5]
    for p in low_conf:
        warnings.append(
            f"Pieza incierta en {p.square} (confianza {p.confidence:.2f})."
        )

    return Transcription(
        white_lines=white_lines,
        black_lines=black_lines,
        highlights=highlights,
        arrows=arrows,
        warnings=warnings,
    )
