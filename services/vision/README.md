# chess-vision

Pipeline de visión híbrido (docs/ARCHITECTURE.md §3.4). Etapas deterministas de OpenCV +
un **recognizer de piezas intercambiable**.

```text
preprocess -> detect_board -> rectify -> segment(8x8) -> recognize -> VisionResult
```

## Diseño clave

- El recognizer de piezas implementa la interfaz `PieceRecognizer`. Se puede sustituir el
  modelo (baseline, CNN, VLM...) **sin tocar** el contrato `BoardState` ni la transcripción.
- OpenCV/numpy son **opcionales**. Sin ellos, el pipeline funciona end-to-end con
  `StubRecognizer`, un recognizer determinista que devuelve una posición conocida. Esto
  permite construir y probar el flujo completo (API, frontend, transcripción) antes de
  disponer de un modelo entrenado.
- Cada casilla puede etiquetarse como `unknown` para expresar incertidumbre sin inventar
  una pieza.
- La orientación se resuelve de forma explícita; nunca se asume.

## Uso

```python
from chess_vision import VisionPipeline
from chess_vision.recognizers import StubRecognizer

pipeline = VisionPipeline(recognizer=StubRecognizer())
vision_result = pipeline.run(image_bytes)          # -> VisionResult
board_state = pipeline.to_board_state(vision_result)  # -> BoardState
```

## Sustituir el modelo

Implementa `PieceRecognizer.recognize(squares)` y pásalo al pipeline. El resto del sistema
no cambia.
