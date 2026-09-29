# ROADMAP.md — Roadmap de desarrollo

> ## Estado de implementación (actualizado)
>
> Leyenda: ✅ hecho · 🟡 parcial/scaffold · ⬜ pendiente
>
> | Fase | Estado | Notas |
> |---|---|---|
> | Fase 0 — Descubrimiento y especificación | ✅ | Contratos v1 (Pydantic) + spec braille/coordenadas congelados en `packages/contracts`. |
> | Fase 1 — Fundaciones técnicas | ✅ | Monorepo, API FastAPI con ciclo de vida, persistencia intercambiable, Docker/compose, CI, frontend base. |
> | Fase 2 — Pipeline de visión MVP | 🟡 | Pipeline híbrido y recognizer **intercambiable** implementados; recognizer real de IA pendiente de dataset (usa `StubRecognizer` determinista). |
> | Fase 3 — Transcripción y accesibilidad | ✅ | Motor de transcripción determinista con tests; frontend accesible (lectura lineal, ARIA, teclado). |
> | Fase 4 — Corrección e historial | ✅ | Corrección/confirmación sin sobreescribir la predicción original; historial; feedback diferido. |
> | Fase 5 — Evaluación y endurecimiento | ⬜ | Requiere dataset y modelo entrenado para medir métricas reales. |
> | Fase 6 — Funciones avanzadas | 🟡 | Contratos de resaltados y flechas ya modelados; detección en imagen pendiente. |
>
> **Verificación:** 85 pruebas de backend en verde (dominio, visión, API); frontend con
> `typecheck` y `build` correctos. Detalle en la sección 16.
>
> El reconocimiento real de piezas por IA (Fase 2.3), las métricas de la Fase 5 y la
> detección visual de la Fase 6 dependen de un dataset anotado que aún no existe, tal como
> el propio roadmap advierte ("las métricas no deben inventarse antes de medir el baseline").

## 1. Visión del producto

Construir una primera versión funcional que convierta una imagen de un tablero de ajedrez en una transcripción accesible y posteriormente evolucionarla hacia un sistema robusto capaz de interpretar distintos estilos de tablero y aprovechar feedback humano de forma controlada.

## 2. Roadmap general

```text
FASE 0  Descubrimiento y especificación
   ↓
FASE 1  Fundaciones técnicas
   ↓
FASE 2  Pipeline de visión MVP
   ↓
FASE 3  Transcripción + accesibilidad
   ↓
FASE 4  Corrección + historial
   ↓
FASE 5  Evaluación y endurecimiento
   ↓
FASE 6  Elementos avanzados y aprendizaje
```

## 3. Fase 0 — Descubrimiento y especificación ✅

### Objetivos

- [x] Congelar el formato de `BoardState`. → `packages/contracts/.../models.py`
- [x] Definir sintaxis de transcripción. → `transcription.py`
- [x] Definir reglas de coordenadas y orientación. → `coordinates.py`, enum `BoardOrientation`
- [x] Definir criterios de accesibilidad. → aplicados en `apps/web`
- [x] Preparar el esquema de datos. → contratos v1 + export JSON Schema (`json_schemas.py`)
- [🟡] Definir dataset inicial. → estructura `data/` lista; imágenes reales pendientes

### Entregables

- Especificación funcional.
- Contrato de datos v1.
- Primer conjunto de imágenes.
- Especificación de transcripción.
- Criterios de aceptación.

### Riesgo crítico

La especificación de orientación debe ser inequívoca. Una imagen puede mostrar el tablero desde una perspectiva distinta y el sistema no debe asumir una orientación incorrecta.

## 4. Fase 1 — Fundaciones técnicas ✅

### Objetivos

Construir el esqueleto del sistema antes de integrar IA.

### Trabajo

- [x] Repositorio. → monorepo (`packages/`, `services/`, `apps/`, `infra/`)
- [x] CI. → `.github/workflows/ci.yml` (backend + frontend)
- [x] Docker. → `infra/api.Dockerfile`, `infra/web.Dockerfile`, `docker-compose.yml`
- [x] API FastAPI. → `apps/api` con endpoints v1
- [x] Frontend React. → `apps/web` (Vite + TS)
- [🟡] PostgreSQL. → interfaz `Repository` lista; MVP usa memoria, servicio y perfil `postgres` preparados
- [🟡] Object Storage. → `image_ref` modelado; almacén S3 pendiente (MVP referencia en memoria)
- [x] Contratos Pydantic/JSON Schema. → `packages/contracts`
- [x] Logging. → `logging` en servicio/app
- [x] Entorno de desarrollo. → `.env.example`, instalación editable, `pytest.ini`

### Criterio de salida

Una imagen puede registrarse como `analysis` y existir un flujo de estado:

```text
created → processing → completed / failed
```

## 5. Fase 2 — Pipeline de visión MVP 🟡

### Objetivos

Reconocer el tablero y sus piezas.

Implementado en `services/vision`: pipeline híbrido con etapas separadas y **recognizer
de piezas intercambiable** (interfaz `PieceRecognizer`). OpenCV/numpy son opcionales, de
modo que el flujo end-to-end funciona con `StubRecognizer` mientras no exista el modelo.

### Iteración 2.1 — Detección del tablero 🟡

- [x] localizar región del tablero; → `stages.detect_and_rectify` (con OpenCV)
- [x] detectar esquinas; → contorno + `approxPolyDP`
- [x] rectificar perspectiva; → `warpPerspective`
- [⬜] probar condiciones de iluminación. → requiere dataset real

### Iteración 2.2 — Segmentación ✅

- [x] generar 64 casillas; → `stages.segment`
- [x] validar coordenadas; → vía `coordinates` (fuente de verdad)
- [x] resolver orientación. → `BoardOrientation` explícita, sin asumir

### Iteración 2.3 — Reconocimiento de piezas 🟡

- [⬜] crear dataset anotado; → pendiente
- [⬜] entrenar baseline; → pendiente (interfaz lista para enchufar el modelo)
- [⬜] evaluar tipo/color; → pendiente de baseline
- [x] incorporar clase `unknown`. → `labels.UNKNOWN` + `UncertainRecognizer`; no inventa piezas

### Criterio de salida

Se genera un `BoardState` reproducible para el conjunto de prueba.

Las métricas exactas de aceptación deben fijarse después de disponer del dataset inicial; no deben inventarse antes de medir el baseline.

## 6. Fase 3 — Transcripción y accesibilidad ✅

### Objetivos

Transformar el `BoardState` en una salida realmente utilizable.

### Trabajo

- [x] motor de coordenadas; → `coordinates.py` (tests completos)
- [x] mapa de Braille; → `braille.py` + `spec.RANK_TO_BRAILLE` (fuente de verdad)
- [x] motor de transcripción; → `transcription.py`, determinista y con tests
- [x] vista accesible; → `apps/web` (HTML semántico, foco visible)
- [x] navegación lineal; → `TranscriptionView` (listas ordenadas + descripción legible)
- [x] anuncios de estados mediante lector de pantalla; → `StatusAnnouncer` (ARIA live)
- [x] tratamiento de incertidumbres. → avisos de orientación/confianza en la transcripción

### Pruebas

- lector de pantalla;
- teclado sin ratón;
- zoom;
- foco;
- contraste;
- contenido no basado exclusivamente en color.

### Criterio de salida

Una persona puede recorrer la transcripción sin depender de información exclusivamente visual.

## 7. Fase 4 — Corrección e historial ✅

### Objetivos

Incorporar el segundo camino del producto: revisión humana.

### Funcionalidad

```text
Predicción
   ↓
Revisión
   ├── Confirmar
   └── Corregir
          ↓
     FeedbackEvent
```

### Trabajo

- [x] editor en modo vidente; → `CorrectionEditor` (tabla editable, accesible)
- [🟡] comparación imagen/resultado; → resultado revisable; miniatura de imagen pendiente
- [x] confirmación explícita; → `POST /feedback/confirm`
- [x] historial; → `GET /history` + `HistoryView`
- [x] auditoría; → `FeedbackEvent` con `review_status`, versiones de modelo/pipeline
- [x] almacenamiento de versión original y corregida. → `original_board_state` + `corrected_board_state`

### Criterio de salida

Una corrección nunca elimina la predicción original y puede reconstruirse el estado anterior.
✅ Verificado: `test_correction_preserves_original` comprueba que la predicción original
(32 piezas) se conserva intacta junto a la corrección.

## 8. Fase 5 — Evaluación y endurecimiento ⬜

### Objetivos

Medir la calidad real del sistema y preparar una versión demostrable.

> Pendiente: depende de disponer de un dataset de test congelado y un modelo entrenado.
> Las métricas de esta fase deben obtenerse midiendo, no fijarse de antemano.

### Trabajo

- dataset de test congelado;
- benchmark reproducible;
- pruebas con estilos distintos;
- análisis de falsos positivos/negativos;
- mejora de UX;
- pruebas de carga;
- seguridad;
- retención de datos;
- documentación.

### Métricas

Separar tres familias:

**Visión**

- exactitud de pieza;
- exactitud de casilla;
- exactitud de color;
- exactitud de posición completa;
- tasa de elementos `unknown`.

**Producto**

- porcentaje de análisis completados;
- porcentaje de correcciones;
- tiempo hasta resultado.

**Accesibilidad**

- tareas completadas con lector de pantalla;
- errores de navegación;
- comprensión de la salida en pruebas con usuarios.

Las métricas deberán obtenerse de pruebas reales; no se deben presentar objetivos como resultados alcanzados.

## 9. Fase 6 — Funciones avanzadas 🟡

> El **modelo de datos** de resaltados y flechas ya está implementado en los contratos
> (`Highlight`, `Arrow`, `ArrowDirection`) y el motor de transcripción ya los renderiza
> (`⠒⠕` / `⠪⠒`). Falta la **detección visual** de estos elementos en la imagen (requiere
> dataset) y el aprendizaje por feedback curado.

### 6.1 Casillas resaltadas

Detectar:

```text
square
color
confidence
```

### 6.2 Flechas

Detectar:

```text
from_square
to_square
direction
confidence
```

y convertirlas al símbolo establecido por la especificación.

### 6.3 Estilos de tablero

Ampliar el dataset con nuevos estilos y crear pruebas por familia de estilo.

### 6.4 Aprendizaje mediante feedback

Proceso:

```text
feedback
   ↓
curación
   ↓
dataset versionado
   ↓
experimento
   ↓
validación
   ↓
comparación contra modelo actual
   ↓
despliegue controlado
```

El feedback no debe considerarse correcto solo porque haya sido introducido por un usuario; debe existir una estrategia de validación.

## 10. MVP de 8 semanas

| Semana | Objetivo | Entregable | Estado |
|---|---|---|---|
| 1 | Especificación | contratos, coordenadas, transcripción | ✅ |
| 2 | Base técnica | repositorio, CI, API, frontend, BD | ✅ |
| 3 | Detección tablero | tablero + perspectiva | 🟡 (código listo; falta prueba con imágenes reales) |
| 4 | Casillas/piezas | baseline de reconocimiento | 🟡 (segmentación ✅; baseline de IA pendiente de dataset) |
| 5 | Transcripción | `BoardState` → texto | ✅ |
| 6 | Accesibilidad | modo ciego + lector de pantalla | ✅ |
| 7 | Corrección/historial | revisión + feedback | ✅ |
| 8 | Evaluación | benchmark, bugs, demo y documentación | ⬜ (requiere dataset/modelo) |

## 11. Backlog priorizado

### P0 — imprescindible para MVP

- [x] Carga de imagen. → `POST /api/v1/analyses` + ingestión validada
- [x] Detección de tablero. → `stages.detect_and_rectify` (con OpenCV)
- [x] Rectificación. → `warpPerspective`
- [x] División 8×8. → `stages.segment`
- [🟡] Reconocimiento de piezas. → interfaz + stub; modelo de IA pendiente de dataset
- [x] Coordenadas. → `coordinates.py`
- [x] Transcripción. → `transcription.py`
- [x] Modo accesible. → frontend modo ciego, ARIA, teclado
- [x] Modo vidente. → editor de corrección
- [x] Corrección. → `POST /correction` (preserva original)
- [x] Historial. → `GET /history`
- [x] Trazabilidad. → `model_version` + `pipeline_version` en análisis y feedback

### P1 — siguiente iteración

- Resaltados.
- Flechas.
- Más estilos.
- Captura desde cámara.
- Mejoras del modelo.
- Dataset curado de feedback.

### P2 — evolución

- Vídeo/captura continua.
- FEN/PGN.
- Integración con plataformas externas.
- Análisis temporal de partidas.
- Modelos especializados por familia de estilos.

## 12. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Perspectiva extrema | Alto | rectificación + dataset variado |
| Piezas visualmente similares | Alto | datos específicos + clase `unknown` |
| Estilos no vistos | Alto | entrenamiento diverso + pruebas por estilo |
| Mala iluminación | Medio | augmentations + preprocesado |
| Orientación ambigua | Alto | detectar orientación explícitamente |
| Corrección humana errónea | Alto | feedback diferido + curación |
| Dependencia de un modelo | Medio | contrato `BoardState` desacoplado |
| Exceso de latencia | Medio | worker asíncrono + optimización |
| Falta de accesibilidad real | Alto | pruebas con lector de pantalla |
| Pérdida de trazabilidad | Alto | versionado de modelo/pipeline |

## 13. Criterios para pasar de MVP a producción

Antes de una expansión de usuarios, el equipo debería disponer de:

- dataset de evaluación estable;
- métricas reproducibles;
- control de versiones de modelos;
- monitorización de errores;
- política de retención de imágenes;
- registro de feedback;
- pruebas de accesibilidad;
- procedimiento de rollback del modelo;
- documentación de limitaciones.

## 14. Hitos

### H1 — Demo técnica 🟡

Entrada de imagen → posición estructurada.
Flujo completo implementado con `StubRecognizer`; con imágenes reales requiere el modelo de IA.

### H2 — Demo funcional ✅

Entrada de imagen → transcripción accesible.
Funciona end-to-end: `POST /analyses` devuelve la transcripción braille.

### H3 — MVP 🟡

Modos ciego/vidente + corrección + historial. ✅ implementados.
Pendiente el reconocimiento real de piezas para cerrar el hito con imágenes arbitrarias.

### H4 — Beta ⬜

Dataset ampliado + benchmark + pruebas de usuarios.

### H5 — V1 ⬜

Pipeline estable + aprendizaje controlado + soporte de funciones avanzadas.

## 15. Definición de hecho (Definition of Done) para una funcionalidad

Una funcionalidad se considera terminada cuando:

1. Tiene criterios de aceptación.
2. Tiene tests adecuados.
3. Está integrada en el contrato de datos correspondiente.
4. Es compatible con accesibilidad cuando afecta a UI.
5. Tiene logging suficiente para diagnosticar errores.
6. Está documentada.
7. No rompe las versiones soportadas de los contratos.
8. Se puede reproducir el comportamiento relevante con una entrada de prueba.

## 16. Estado de verificación

Resultado de la última ejecución tras implementar las fases 0, 1, 3 y 4 (y el scaffold de la 2):

**Backend — 85 pruebas en verde**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e "packages/contracts[dev]" -e "services/vision[dev]" -e "apps/api[dev]"
pytest -q          # 85 passed
```

- `packages/contracts/tests` — coordenadas, braille, transcripción, validación, modelos y esquemas.
- `services/vision/tests` — pipeline end-to-end, recognizer intercambiable, clase `unknown`, orientación.
- `apps/api/tests` — ciclo de vida del análisis, transcripción, corrección (preserva original), confirmación e historial.

**Frontend — typecheck y build correctos**

```bash
cd apps/web && npm install
npm run typecheck   # sin errores
npm run build       # build de producción correcto
```

**Comprobación de fidelidad de la especificación**

- `Re1` (rey, columna e, fila 1) → `Re⠂`, exactamente como el ejemplo del PDF.
- Tabla de filas 1–8 → `⠂ ⠆ ⠒ ⠲ ⠢ ⠖ ⠶ ⠦`, verificada en `test_braille.py`.
- Diagramas 1, 2 y 23 de la especificación cargados como fixtures y validados.

**Qué queda fuera y por qué**

El reconocimiento real de piezas por IA (Fase 2.3), las métricas de la Fase 5 y la
detección visual de resaltados/flechas (Fase 6) dependen de un dataset anotado que aún no
existe. La arquitectura los deja preparados: el recognizer es intercambiable sin tocar el
contrato `BoardState` ni el motor de transcripción, tal como exige el criterio 10 de
`ARCHITECTURE.md`.
