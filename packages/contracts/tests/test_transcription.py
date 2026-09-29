from chess_contracts import (
    Arrow,
    ArrowDirection,
    BoardOrientation,
    BoardState,
    Color,
    Highlight,
    HighlightColor,
    Piece,
    PieceType,
    TranscriptionOptions,
    transcribe,
)
from chess_contracts.fixtures import DIAGRAM_1, DIAGRAM_2, DIAGRAM_23


def _king_board():
    return BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[
            Piece(color=Color.WHITE, type=PieceType.KING, square="e1"),
            Piece(color=Color.BLACK, type=PieceType.KING, square="e8"),
        ],
    )


def test_transcribe_basic_king_tokens():
    t = transcribe(_king_board())
    assert t.white_lines[0].text == "Re\u2802"  # Re1
    assert t.black_lines[0].text == "Re\u2826"  # Re8


def test_transcription_is_deterministic():
    board = DIAGRAM_1
    a = transcribe(board)
    b = transcribe(board)
    assert a.model_dump() == b.model_dump()


def test_transcription_separates_colors():
    t = transcribe(DIAGRAM_1)
    assert len(t.white_lines) == 13
    assert len(t.black_lines) == 14
    # king first in ordering
    assert t.white_lines[0].readable.startswith("Rey")


def test_pawns_without_letter_option():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[Piece(color=Color.WHITE, type=PieceType.PAWN, square="a2")],
    )
    default = transcribe(board)
    assert default.white_lines[0].text == "Pa\u2806"
    variant = transcribe(board, TranscriptionOptions(pawns_without_letter=True))
    assert variant.white_lines[0].text == "a\u2806"


def test_highlight_and_arrow_rendering():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[],
        highlights=[Highlight(square="g3", color=HighlightColor.YELLOW)],
        arrows=[Arrow(from_square="d4", to_square="d1", direction=ArrowDirection.FORWARD)],
    )
    t = transcribe(board)
    assert "amarillo" in t.highlights[0]
    # flecha forward usa ⠒⠕
    assert "\u2812\u2815" in t.arrows[0]


def test_unknown_orientation_produces_warning():
    board = BoardState(orientation=BoardOrientation.UNKNOWN, pieces=[])
    t = transcribe(board)
    assert any("Orientación" in w for w in t.warnings)


def test_low_confidence_warning():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[Piece(color=Color.WHITE, type=PieceType.QUEEN, square="d1", confidence=0.3)],
    )
    t = transcribe(board)
    assert any("incierta" in w for w in t.warnings)


def test_as_text_roundtrips_labels():
    text = transcribe(DIAGRAM_2).as_text()
    assert "Blancas:" in text
    assert "Negras:" in text


def test_all_diagrams_transcribe_without_error():
    for board in (DIAGRAM_1, DIAGRAM_2, DIAGRAM_23):
        t = transcribe(board)
        assert t.white_lines and t.black_lines


# ---------------------------------------------------------------------------
# Narrativa en prosa (para voz / braille)
# ---------------------------------------------------------------------------


def test_narrative_is_present_and_nonempty():
    t = transcribe(DIAGRAM_1)
    assert t.narrative
    assert isinstance(t.narrative, str)


def test_narrative_has_sentence_structure():
    t = transcribe(_king_board())
    n = t.narrative
    # puntuación de prosa: puntos y comas
    assert "." in n
    # encabezado con recuento
    assert "2 piezas en total" in n
    assert "1 blanca" in n and "1 negra" in n


def test_narrative_describes_pieces_readably():
    t = transcribe(_king_board())
    n = t.narrative
    assert "Piezas blancas: rey en e 1." in n
    assert "Piezas negras: rey en e 8." in n


def test_narrative_orientation_phrase():
    assert "blancas en la parte inferior" in transcribe(DIAGRAM_1).narrative
    unknown = BoardState(orientation=BoardOrientation.UNKNOWN, pieces=[])
    assert "orientación no determinada" in transcribe(unknown).narrative


def test_narrative_natural_join_uses_commas_and_conjunction():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[
            Piece(color=Color.WHITE, type=PieceType.KING, square="e1"),
            Piece(color=Color.WHITE, type=PieceType.ROOK, square="a1"),
            Piece(color=Color.WHITE, type=PieceType.ROOK, square="h1"),
        ],
    )
    n = transcribe(board).narrative
    # tres piezas -> "..., ... y ..."
    assert ", " in n
    assert " y " in n


def test_narrative_includes_highlights_and_arrows():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[],
        highlights=[Highlight(square="g3", color=HighlightColor.YELLOW)],
        arrows=[Arrow(from_square="d4", to_square="d1", direction=ArrowDirection.FORWARD)],
    )
    n = transcribe(board).narrative
    assert "resaltadas" in n.lower()
    assert "amarillo" in n
    assert "Flechas:" in n
    assert "de d 4 a d 1" in n


def test_narrative_includes_warnings():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[Piece(color=Color.WHITE, type=PieceType.QUEEN, square="d1", confidence=0.3)],
    )
    n = transcribe(board).narrative
    assert "Avisos:" in n
    assert "incierta" in n


def test_narrative_is_deterministic():
    assert transcribe(DIAGRAM_23).narrative == transcribe(DIAGRAM_23).narrative


def test_narrative_singular_plural_agreement():
    one = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[Piece(color=Color.WHITE, type=PieceType.KING, square="e1")],
    )
    n = transcribe(one).narrative
    assert "1 pieza en total" in n
    assert "Sin piezas negras." in n


# ---------------------------------------------------------------------------
# Bloque braille en formato ONCE (tokens en línea)
# ---------------------------------------------------------------------------


def test_braille_block_inline_format():
    t = transcribe(_king_board())
    lines = t.braille_block.split("\n")
    assert lines[0] == "Blancas: Re\u2802"
    assert lines[1] == "Negras: Re\u2826"


def test_braille_block_tokens_space_separated():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[
            Piece(color=Color.WHITE, type=PieceType.KING, square="e1"),
            Piece(color=Color.WHITE, type=PieceType.QUEEN, square="d1"),
            Piece(color=Color.WHITE, type=PieceType.ROOK, square="a1"),
        ],
    )
    block = transcribe(board).braille_block
    # Rey, Dama, Torre en una sola línea separados por espacios.
    assert block.startswith("Blancas: Re\u2802 Dd\u2802 Ta\u2802")


def test_braille_block_highlights_described_apart():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[Piece(color=Color.WHITE, type=PieceType.KING, square="e1")],
        highlights=[
            Highlight(square="g3", color=HighlightColor.YELLOW),
            Highlight(square="h4", color=HighlightColor.YELLOW),
        ],
    )
    block = transcribe(board).braille_block
    assert "Resaltadas en amarillo las casillas g\u2812 y h\u2832" in block


def test_braille_block_single_highlight_singular():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[],
        highlights=[Highlight(square="g3", color=HighlightColor.YELLOW)],
    )
    block = transcribe(board).braille_block
    assert "Resaltadas en amarillo la casilla g\u2812" in block


def test_braille_block_arrow_described():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[],
        arrows=[Arrow(from_square="d4", to_square="d1", direction=ArrowDirection.FORWARD)],
    )
    block = transcribe(board).braille_block
    assert "Flecha: d\u2832\u2812\u2815d\u2802" in block


def test_braille_block_is_deterministic():
    assert transcribe(DIAGRAM_1).braille_block == transcribe(DIAGRAM_1).braille_block
