import pytest

from chess_contracts import transcribe, validate_board
from chess_contracts.spec import BoardOrientation
from chess_vision import (
    ImageError,
    StubRecognizer,
    UncertainRecognizer,
    VisionPipeline,
)

# PNG mínimo válido (firma + IHDR) suficiente para la validación sin OpenCV.
PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000080000000808020000004b6d29dc"
)


def test_run_produces_64_squares():
    pipeline = VisionPipeline(recognizer=StubRecognizer())
    result = pipeline.run(PNG_BYTES)
    assert len(result.squares) == 64
    assert result.pipeline_version.startswith("vision-pipeline@")
    assert result.model_version == "stub@1"


def test_stub_end_to_end_initial_position():
    pipeline = VisionPipeline(recognizer=StubRecognizer())
    result = pipeline.run(PNG_BYTES)
    board = pipeline.to_board_state(result)
    # posición inicial: 32 piezas
    assert len(board.pieces) == 32
    validation = validate_board(board)
    assert validation.ok
    transcription = transcribe(board)
    assert len(transcription.white_lines) == 16
    assert len(transcription.black_lines) == 16


def test_empty_image_raises():
    pipeline = VisionPipeline(recognizer=StubRecognizer())
    with pytest.raises(ImageError):
        pipeline.run(b"")


def test_unrecognized_format_raises():
    pipeline = VisionPipeline(recognizer=StubRecognizer())
    with pytest.raises(ImageError):
        pipeline.run(b"not-an-image")


def test_uncertain_recognizer_produces_no_pieces():
    pipeline = VisionPipeline(recognizer=UncertainRecognizer())
    result = pipeline.run(PNG_BYTES)
    board = pipeline.to_board_state(result)
    # unknown no inventa piezas
    assert board.pieces == []
    # pero la incertidumbre queda en el VisionResult
    assert all(s.label == "unknown" for s in result.squares)


def test_orientation_black_at_bottom_maps_squares():
    pipeline = VisionPipeline(recognizer=StubRecognizer())
    result = pipeline.run(PNG_BYTES, orientation=BoardOrientation.BLACK_AT_BOTTOM)
    assert result.orientation is BoardOrientation.BLACK_AT_BOTTOM
    squares = {s.square for s in result.squares}
    assert len(squares) == 64  # sigue cubriendo todas las casillas


def test_recognizer_is_swappable_without_changing_contract():
    for rec in (StubRecognizer(), UncertainRecognizer()):
        pipeline = VisionPipeline(recognizer=rec)
        result = pipeline.run(PNG_BYTES)
        board = pipeline.to_board_state(result)
        # el contrato de salida es siempre BoardState
        assert hasattr(board, "pieces")
