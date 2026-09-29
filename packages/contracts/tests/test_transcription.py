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
