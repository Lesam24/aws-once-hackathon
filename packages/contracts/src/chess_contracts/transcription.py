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

__all__ = [
    "transcribe",
    "TranscriptionOptions",
    "build_narrative",
    "build_braille_block",
]

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


def _square_braille(square: str) -> str:
    """Casilla en braille: columna latina + fila braille. Ej.: 'g3' -> 'g⠒'."""
    return square_to_braille(square)


def build_braille_block(
    white_lines: list[TranscriptionLine],
    black_lines: list[TranscriptionLine],
    board: BoardState,
) -> str:
    """Genera la transcripción braille en el formato oficial de la ONCE.

    Tokens en línea separados por espacios, precedidos por 'Blancas:' y 'Negras:'.
    Las casillas resaltadas y las flechas se describen aparte, como indica la
    especificación. Determinista: misma entrada, misma salida.

    Ejemplo:
        Blancas: Re⠂ Dd⠂ Ta⠂ Th⠂ ...
        Negras: Re⠦ Dd⠦ Ta⠦ Th⠦ ...
        Resaltadas en amarillo las casillas g⠒ y h⠲
    """
    parts: list[str] = []

    if white_lines:
        parts.append("Blancas: " + " ".join(line.text for line in white_lines))
    if black_lines:
        parts.append("Negras: " + " ".join(line.text for line in black_lines))

    # Casillas resaltadas, agrupadas por color, descritas por separado.
    for color_value, color_word in (("yellow", "amarillo"), ("red", "rojo")):
        squares = [
            _square_braille(h.square)
            for h in board.highlights
            if h.color.value == color_value
        ]
        if squares:
            noun = "la casilla" if len(squares) == 1 else "las casillas"
            parts.append(
                f"Resaltadas en {color_word} {noun} {_join_natural(squares)}"
            )

    # Flechas entre casillas, con su símbolo direccional.
    for a in board.arrows:
        parts.append(
            f"Flecha: {_square_braille(a.from_square)}"
            f"{ARROW_SYMBOL[a.direction]}{_square_braille(a.to_square)}"
        )

    return "\n".join(parts)


#: Descripción legible de la casilla, deletreada para voz ("e uno" en lugar de "e1").
def _square_readable(square: str) -> str:
    return f"{file_of(square)} {rank_of(square)}"


def _piece_phrase(piece: Piece) -> str:
    """Frase de una pieza: 'rey en e1'. El color se agrupa aparte."""
    name = _PIECE_READABLE[piece.type].lower()
    return f"{name} en {_square_readable(piece.square)}"


def _join_natural(items: list[str]) -> str:
    """Une elementos con comas y una conjunción final ('a, b y c')."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])} y {items[-1]}"


def _color_section(color_word: str, pieces: list[Piece]) -> str:
    """Construye la frase de un color: 'Piezas blancas: rey en e1, dama en d1.'"""
    if not pieces:
        return f"Sin piezas {color_word}."
    phrases = [_piece_phrase(p) for p in pieces]
    return f"Piezas {color_word}: {_join_natural(phrases)}."


def build_narrative(
    board: BoardState,
    white: list[Piece],
    black: list[Piece],
    warnings: list[str],
) -> str:
    """Genera la descripción en prosa continua para voz o braille.

    Determinista: la misma entrada produce siempre el mismo texto. Usa las mismas piezas
    ya ordenadas que las líneas braille para mantener coherencia con el resto de la salida.
    """
    total = len(white) + len(black)
    parts: list[str] = []

    # Encabezado con orientación y recuento.
    orientation_word = {
        "white-at-bottom": "con las blancas en la parte inferior",
        "black-at-bottom": "con las negras en la parte inferior",
        "unknown": "con orientación no determinada",
    }.get(board.orientation.value, "con orientación no determinada")
    parts.append(
        f"Tablero {orientation_word}. "
        f"{total} {'pieza' if total == 1 else 'piezas'} en total: "
        f"{len(white)} {'blanca' if len(white) == 1 else 'blancas'} "
        f"y {len(black)} {'negra' if len(black) == 1 else 'negras'}."
    )

    parts.append(_color_section("blancas", white))
    parts.append(_color_section("negras", black))

    # Casillas resaltadas.
    if board.highlights:
        hl = [
            f"{_square_readable(h.square)} en "
            f"{'amarillo' if h.color.value == 'yellow' else 'rojo'}"
            for h in board.highlights
        ]
        parts.append(f"Casillas resaltadas: {_join_natural(hl)}.")

    # Flechas.
    if board.arrows:
        ar = [
            f"de {_square_readable(a.from_square)} a {_square_readable(a.to_square)}"
            for a in board.arrows
        ]
        parts.append(f"Flechas: {_join_natural(ar)}.")

    # Avisos de fiabilidad.
    if warnings:
        parts.append(f"Avisos: {' '.join(warnings)}")

    return " ".join(parts)


def transcribe(
    board: BoardState, options: TranscriptionOptions | None = None
) -> Transcription:
    """Transforma un ``BoardState`` en una ``Transcription`` determinista.

    La misma entrada produce siempre la misma salida (requisito de reproducibilidad).
    """
    opts = options or TranscriptionOptions()

    white_sorted = _sort_pieces([p for p in board.pieces if p.color is Color.WHITE])
    black_sorted = _sort_pieces([p for p in board.pieces if p.color is Color.BLACK])

    white_lines = [_line_for_piece(p, opts) for p in white_sorted]
    black_lines = [_line_for_piece(p, opts) for p in black_sorted]

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

    narrative = build_narrative(board, white_sorted, black_sorted, warnings)
    braille_block = build_braille_block(white_lines, black_lines, board)

    return Transcription(
        white_lines=white_lines,
        black_lines=black_lines,
        highlights=highlights,
        arrows=arrows,
        warnings=warnings,
        narrative=narrative,
        braille_block=braille_block,
    )
