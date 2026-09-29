import pytest
from pydantic import ValidationError

from chess_contracts import (
    Arrow,
    BoardState,
    Color,
    Piece,
    PieceType,
    Transcription,
    VisionResult,
)
from chess_contracts.json_schemas import SCHEMA_MODELS


def test_piece_rejects_invalid_square():
    with pytest.raises(ValidationError):
        Piece(color=Color.WHITE, type=PieceType.KING, square="z9")


def test_piece_confidence_bounds():
    with pytest.raises(ValidationError):
        Piece(color=Color.WHITE, type=PieceType.KING, square="e1", confidence=1.5)


def test_arrow_validates_both_squares():
    with pytest.raises(ValidationError):
        Arrow(from_square="e1", to_square="zz")


def test_boardstate_defaults():
    b = BoardState()
    assert b.pieces == []
    assert b.contract_version == "1.0"


def test_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        Piece(color=Color.WHITE, type=PieceType.KING, square="e1", bogus=1)


def test_roundtrip_serialization():
    b = BoardState(pieces=[Piece(color=Color.WHITE, type=PieceType.KING, square="e1")])
    data = b.model_dump()
    restored = BoardState.model_validate(data)
    assert restored == b


def test_transcription_json_schema_generates():
    schema = Transcription.model_json_schema()
    assert "properties" in schema


@pytest.mark.parametrize("name,model", SCHEMA_MODELS.items())
def test_all_schemas_generate(name, model):
    schema = model.model_json_schema()
    assert schema.get("type") == "object"
