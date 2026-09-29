"""Exportación de los contratos a JSON Schema.

Permite compartir los contratos v1 con el frontend u otros servicios. Ejecutar como
módulo escribe los esquemas en un directorio:

    python -m chess_contracts.json_schemas packages/contracts/schemas
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .models import (
    BoardState,
    FeedbackEvent,
    Transcription,
    ValidationResult,
    VisionResult,
)

SCHEMA_MODELS = {
    "BoardState.v1": BoardState,
    "VisionResult.v1": VisionResult,
    "Transcription.v1": Transcription,
    "ValidationResult.v1": ValidationResult,
    "FeedbackEvent.v1": FeedbackEvent,
}


def export(out_dir: str | Path) -> list[Path]:
    """Escribe un archivo ``<name>.schema.json`` por contrato. Devuelve las rutas."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, model in SCHEMA_MODELS.items():
        path = out / f"{name}.schema.json"
        path.write_text(
            json.dumps(model.model_json_schema(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        written.append(path)
    return written


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "schemas"
    for p in export(target):
        print(f"wrote {p}")
