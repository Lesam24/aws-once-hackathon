from chess_contracts import (
    BoardOrientation,
    BoardState,
    Color,
    Piece,
    PieceType,
    Severity,
    validate_board,
)
from chess_contracts.fixtures import DIAGRAM_1, DIAGRAM_2, DIAGRAM_23


def test_valid_diagrams_pass():
    for board in (DIAGRAM_1, DIAGRAM_2, DIAGRAM_23):
        result = validate_board(board)
        assert result.ok, [i.message for i in result.issues]


def test_duplicate_square_is_error():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[
            Piece(color=Color.WHITE, type=PieceType.KING, square="e1"),
            Piece(color=Color.WHITE, type=PieceType.QUEEN, square="e1"),
            Piece(color=Color.BLACK, type=PieceType.KING, square="e8"),
        ],
    )
    result = validate_board(board)
    assert not result.ok
    assert any(i.code == "square_occupied_multiple" for i in result.issues)


def test_missing_king_warns():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[Piece(color=Color.WHITE, type=PieceType.QUEEN, square="d1")],
    )
    result = validate_board(board)
    codes = {i.code for i in result.issues}
    assert "missing_king" in codes
    # missing king is a warning, not an error -> still ok
    assert result.ok


def test_unknown_orientation_warns():
    board = BoardState(orientation=BoardOrientation.UNKNOWN, pieces=[])
    result = validate_board(board)
    assert any(i.code == "orientation_unknown" for i in result.issues)


def test_pawn_on_back_rank_warns():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[
            Piece(color=Color.WHITE, type=PieceType.KING, square="e1"),
            Piece(color=Color.BLACK, type=PieceType.KING, square="e8"),
            Piece(color=Color.WHITE, type=PieceType.PAWN, square="a1"),
        ],
    )
    result = validate_board(board)
    assert any(i.code == "pawn_on_back_rank" for i in result.issues)


def test_multiple_kings_warns():
    board = BoardState(
        orientation=BoardOrientation.WHITE_AT_BOTTOM,
        pieces=[
            Piece(color=Color.WHITE, type=PieceType.KING, square="e1"),
            Piece(color=Color.WHITE, type=PieceType.KING, square="d1"),
            Piece(color=Color.BLACK, type=PieceType.KING, square="e8"),
        ],
    )
    result = validate_board(board)
    assert any(i.code == "multiple_kings" for i in result.issues)


def test_severity_enum_used():
    board = BoardState(orientation=BoardOrientation.UNKNOWN, pieces=[])
    result = validate_board(board)
    assert all(isinstance(i.severity, Severity) for i in result.issues)
