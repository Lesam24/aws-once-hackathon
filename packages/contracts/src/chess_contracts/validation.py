"""Validadores de coherencia del ``BoardState``.

Filosofía (docs/ARCHITECTURE.md §6): una posición que falle una regla NO se "arregla"
automáticamente inventando datos; se marca como inconsistente para revisión.
"""

from __future__ import annotations

from collections import Counter

from .coordinates import is_valid_square
from .models import (
    BoardState,
    Severity,
    ValidationIssue,
    ValidationResult,
)
from .spec import BoardOrientation, Color, PieceType

__all__ = ["validate_board"]


def validate_board(board: BoardState) -> ValidationResult:
    """Valida coherencia geométrica y ajedrecística básica del ``BoardState``."""
    issues: list[ValidationIssue] = []

    # --- Coordenadas válidas ---
    for piece in board.pieces:
        if not is_valid_square(piece.square):
            issues.append(
                ValidationIssue(
                    code="invalid_square",
                    message=f"Casilla inválida: {piece.square!r}",
                    severity=Severity.ERROR,
                    square=piece.square,
                )
            )

    # --- Máximo una pieza por casilla ---
    counts = Counter(p.square for p in board.pieces)
    for square, n in counts.items():
        if n > 1:
            issues.append(
                ValidationIssue(
                    code="square_occupied_multiple",
                    message=f"{n} piezas en la casilla {square}",
                    severity=Severity.ERROR,
                    square=square,
                )
            )

    # --- Orientación explícita ---
    if board.orientation is BoardOrientation.UNKNOWN:
        issues.append(
            ValidationIssue(
                code="orientation_unknown",
                message="La orientación del tablero no está determinada.",
                severity=Severity.WARNING,
            )
        )

    # --- Comprobaciones ajedrecísticas (opcionales, no bloqueantes) ---
    for color in (Color.WHITE, Color.BLACK):
        kings = [
            p for p in board.pieces if p.color is color and p.type is PieceType.KING
        ]
        if len(kings) == 0:
            issues.append(
                ValidationIssue(
                    code="missing_king",
                    message=f"No se ha detectado el rey {color.value}.",
                    severity=Severity.WARNING,
                )
            )
        elif len(kings) > 1:
            issues.append(
                ValidationIssue(
                    code="multiple_kings",
                    message=f"Se han detectado {len(kings)} reyes {color.value}.",
                    severity=Severity.WARNING,
                )
            )

    # Peones en filas 1 u 8 son físicamente imposibles.
    for piece in board.pieces:
        if piece.type is PieceType.PAWN and piece.square[1] in ("1", "8"):
            issues.append(
                ValidationIssue(
                    code="pawn_on_back_rank",
                    message=f"Peón en fila de coronación: {piece.square}",
                    severity=Severity.WARNING,
                    square=piece.square,
                )
            )

    ok = not any(i.severity is Severity.ERROR for i in issues)
    return ValidationResult(ok=ok, issues=issues)
