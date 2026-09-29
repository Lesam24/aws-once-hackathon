# chess-contracts

Contratos de datos versionados y **dominio determinista** del proyecto Chess Accessibility.

Este paquete es la única fuente de verdad para:

- La especificación braille de la ONCE (`spec.py`): números en posición baja, letras de pieza.
- La conversión `(fila, columna) <-> casilla a1..h8` (`coordinates.py`).
- El mapa `fila -> braille` (`braille.py`).
- Los modelos de contrato v1 (`models.py`): `BoardState`, `VisionResult`, `Transcription`,
  `FeedbackEvent`, `Correction`, etc.
- El motor de transcripción `BoardState -> Transcription` (`transcription.py`).
- Los validadores de coherencia (`validation.py`).

Todo lo de este paquete es **puro** (sin dependencias de OpenCV, IA ni base de datos) y
está cubierto por pruebas unitarias que usan los diagramas reales de la especificación.
