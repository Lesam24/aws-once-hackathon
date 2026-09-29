# chess-api

Backend FastAPI del proyecto. Orquesta el ciclo de vida del análisis y expone los
contratos v1.

## Endpoints (v1)

| Método | Ruta | Descripción |
|---|---|---|
| GET  | `/api/v1/health` | Estado del servicio. |
| POST | `/api/v1/analyses` | Sube una imagen y crea un análisis (`created→processing→completed/failed`). |
| GET  | `/api/v1/analyses/{id}` | Devuelve el análisis completo. |
| GET  | `/api/v1/analyses/{id}/transcription` | Devuelve solo la transcripción. |
| POST | `/api/v1/analyses/{id}/correction` | (modo vidente) Envía una corrección del `BoardState`. |
| POST | `/api/v1/analyses/{id}/feedback/confirm` | (modo vidente) Confirma que el resultado es correcto. |
| GET  | `/api/v1/history` | Historial de análisis. |

## Principios respetados

- **La corrección nunca sobreescribe la predicción original.** Se guarda como
  `FeedbackEvent` con `original_board_state` y `corrected_board_state`.
- **Feedback diferido.** El feedback entra con `review_status = pending`; no reentrena nada.
- **Trazabilidad.** Cada análisis y evento registra `model_version` y `pipeline_version`.
- **Persistencia intercambiable.** El repositorio es una interfaz; el MVP usa memoria y
  deja lista la ruta a PostgreSQL.

## Arranque

```bash
uvicorn chess_api.main:app --reload --app-dir apps/api/src
```
