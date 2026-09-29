"""Etapas deterministas del pipeline de visión.

Cada etapa está aislada para poder mejorarse de forma independiente. Cuando OpenCV/numpy
no están instalados, las etapas geométricas degradan a un comportamiento neutro que
permite ejecutar el flujo completo (útil para probar API/transcripción con el
``StubRecognizer``).
"""

from __future__ import annotations

from dataclasses import dataclass

from chess_contracts.coordinates import square_from_indices
from chess_contracts.spec import BoardOrientation

from .recognizers import SquareImage

try:  # OpenCV es opcional
    import cv2  # type: ignore
    import numpy as np  # type: ignore

    _HAS_CV = True
except Exception:  # pragma: no cover - depende del entorno
    _HAS_CV = False


@dataclass
class BoardGeometry:
    """Resultado de la detección + rectificación del tablero."""

    detected: bool
    corners: list[tuple[float, float]]
    confidence: float
    rectified: object | None = None  # imagen 8x8 normalizada (numpy) si hay OpenCV


class ImageError(ValueError):
    """La entrada no es una imagen válida o no contiene un tablero reconocible."""


def decode_image(data: bytes) -> object:
    """Decodifica bytes a una imagen. Sin OpenCV, valida mínimamente y devuelve los bytes."""
    if not data:
        raise ImageError("La imagen está vacía.")
    if not _HAS_CV:
        # Validación mínima de firmas de formato comunes (PNG/JPEG/GIF/WEBP/BMP).
        signatures = (b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"RIFF", b"BM")
        if not any(data.startswith(sig) for sig in signatures):
            raise ImageError("Formato de imagen no reconocido.")
        return data
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ImageError("No se ha podido decodificar la imagen.")
    return img


def preprocess(image: object) -> object:
    """Normalización de tamaño, reducción de ruido y escala de grises (si hay OpenCV)."""
    if not _HAS_CV:
        return image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # type: ignore
    gray = cv2.GaussianBlur(gray, (5, 5), 0)  # type: ignore
    return gray


def detect_and_rectify(
    image: object, *, expected_size: int = 512
) -> BoardGeometry:
    """Detecta el contorno del tablero y rectifica la perspectiva a una vista cuadrada.

    Sin OpenCV se asume que la imagen ya es un tablero encuadrado (confianza reducida),
    de modo que el flujo end-to-end sigue siendo posible con el recognizer stub.
    """
    if not _HAS_CV:
        return BoardGeometry(detected=True, corners=[], confidence=0.5, rectified=image)

    edges = cv2.Canny(image, 50, 150)  # type: ignore
    contours, _ = cv2.findContours(  # type: ignore
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return BoardGeometry(detected=False, corners=[], confidence=0.0)

    largest = max(contours, key=cv2.contourArea)  # type: ignore
    peri = cv2.arcLength(largest, True)  # type: ignore
    approx = cv2.approxPolyDP(largest, 0.02 * peri, True)  # type: ignore
    if len(approx) != 4:
        # No es un cuadrilátero claro; devolvemos la imagen sin rectificar.
        return BoardGeometry(detected=True, corners=[], confidence=0.4, rectified=image)

    pts = approx.reshape(4, 2).astype("float32")
    ordered = _order_corners(pts)
    dst = np.array(  # type: ignore
        [[0, 0], [expected_size - 1, 0],
         [expected_size - 1, expected_size - 1], [0, expected_size - 1]],
        dtype="float32",
    )
    matrix = cv2.getPerspectiveTransform(ordered, dst)  # type: ignore
    warped = cv2.warpPerspective(image, matrix, (expected_size, expected_size))  # type: ignore
    corners = [(float(x), float(y)) for x, y in ordered]
    return BoardGeometry(detected=True, corners=corners, confidence=0.9, rectified=warped)


def _order_corners(pts):  # pragma: no cover - requiere OpenCV/numpy
    rect = np.zeros((4, 2), dtype="float32")  # type: ignore
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # type: ignore
    rect[2] = pts[np.argmax(s)]  # type: ignore
    diff = np.diff(pts, axis=1)  # type: ignore
    rect[1] = pts[np.argmin(diff)]  # type: ignore
    rect[3] = pts[np.argmax(diff)]  # type: ignore
    return rect


def segment(
    geometry: BoardGeometry, orientation: BoardOrientation
) -> list[SquareImage]:
    """Divide la vista rectificada en 64 casillas, asociando cada una a su coordenada.

    La orientación determina el mapeo (fila,columna) de imagen -> casilla. Debe venir
    resuelta explícitamente; este módulo no la adivina.
    """
    squares: list[SquareImage] = []
    rectified = geometry.rectified
    tile = None
    if _HAS_CV and rectified is not None and hasattr(rectified, "shape"):
        h, w = rectified.shape[:2]
        tile_h, tile_w = h // 8, w // 8

    # row_img: 0 arriba en la imagen. Mapeamos a fila de ajedrez según orientación.
    for row_img in range(8):
        for col_img in range(8):
            file_index, rank = _map_to_coordinate(row_img, col_img, orientation)
            square = square_from_indices(file_index, rank)
            pixels = None
            if _HAS_CV and rectified is not None and hasattr(rectified, "shape"):
                y0, x0 = row_img * tile_h, col_img * tile_w
                pixels = rectified[y0 : y0 + tile_h, x0 : x0 + tile_w]
            squares.append(SquareImage(square=square, pixels=pixels))
    return squares


def _map_to_coordinate(
    row_img: int, col_img: int, orientation: BoardOrientation
) -> tuple[int, int]:
    """Mapea la fila/columna de imagen (0=arriba/izquierda) a (file_index, rank)."""
    if orientation is BoardOrientation.BLACK_AT_BOTTOM:
        # negras abajo: arriba-izquierda de la imagen es h1
        file_index = 7 - col_img
        rank = row_img + 1
    else:
        # white-at-bottom (por defecto / unknown): arriba-izquierda es a8
        file_index = col_img
        rank = 8 - row_img
    return file_index, rank
