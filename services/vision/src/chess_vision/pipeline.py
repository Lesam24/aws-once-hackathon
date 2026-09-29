"""Orquestador del pipeline de visión: bytes de imagen -> VisionResult -> BoardState."""

from __future__ import annotations

from dataclasses import dataclass

from chess_contracts.models import (
    BoardDetection,
    BoardState,
    Piece,
    SquarePrediction,
    VisionResult,
)
from chess_contracts.spec import BoardOrientation

from .labels import label_to_piece
from .recognizers import PieceRecognizer, StubRecognizer
from .stages import (
    BoardGeometry,
    ImageError,
    decode_image,
    detect_and_rectify,
    preprocess,
    segment,
)

PIPELINE_VERSION = "vision-pipeline@0.1.0"

__all__ = ["VisionPipeline", "ImageError", "PIPELINE_VERSION"]


@dataclass
class VisionPipeline:
    """Pipeline híbrido con recognizer de piezas intercambiable."""

    recognizer: PieceRecognizer = None  # type: ignore[assignment]
    pipeline_version: str = PIPELINE_VERSION

    def __post_init__(self) -> None:
        if self.recognizer is None:
            self.recognizer = StubRecognizer()

    def run(
        self,
        image_bytes: bytes,
        *,
        orientation: BoardOrientation = BoardOrientation.WHITE_AT_BOTTOM,
    ) -> VisionResult:
        """Ejecuta el pipeline completo y devuelve un ``VisionResult``.

        :raises ImageError: si la imagen es inválida o no se detecta un tablero.
        """
        image = decode_image(image_bytes)
        pre = preprocess(image)
        geometry: BoardGeometry = detect_and_rectify(pre)
        if not geometry.detected:
            raise ImageError(
                "No se ha podido identificar un tablero de ajedrez en la imagen."
            )

        square_images = segment(geometry, orientation)
        labels = self.recognizer.recognize(square_images)

        predictions = [
            SquarePrediction(square=lbl.square, label=lbl.label, confidence=lbl.confidence)
            for lbl in labels
        ]

        detection = BoardDetection(
            board_bbox=(0.0, 0.0, 0.0, 0.0),
            corners=geometry.corners,
            confidence=geometry.confidence,
        )
        return VisionResult(
            detection=detection,
            orientation=orientation,
            squares=predictions,
            model_version=getattr(self.recognizer, "version", None),
            pipeline_version=self.pipeline_version,
        )

    def to_board_state(self, vision: VisionResult) -> BoardState:
        """Normaliza un ``VisionResult`` a un ``BoardState`` canónico.

        Las casillas ``empty`` se omiten. Las ``unknown`` no producen pieza (no se inventa
        nada); su incertidumbre queda registrada en el ``VisionResult`` original.
        """
        pieces: list[Piece] = []
        for pred in vision.squares:
            mapped = label_to_piece(pred.label)
            if mapped is None:
                continue  # empty o unknown
            color, ptype = mapped
            pieces.append(
                Piece(
                    color=color,
                    type=ptype,
                    square=pred.square,
                    confidence=pred.confidence,
                )
            )
        return BoardState(
            orientation=vision.orientation,
            pieces=pieces,
            model_version=vision.model_version,
            pipeline_version=vision.pipeline_version,
        )
