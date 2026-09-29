# Chess Accessibility

Aplicación de accesibilidad que analiza imágenes de tableros de ajedrez y las convierte
en una transcripción estructurada en **braille + coordenadas**, accesible para personas
ciegas y revisable por personas videntes.

La documentación de producto, arquitectura y hoja de ruta vive en [`docs/`](./docs).

## Estructura del repositorio

```text
.
├── packages/
│   └── contracts/        # Contratos de datos versionados (Pydantic v1) + dominio
│       └── chess_contracts/
│           ├── spec.py           # Constantes de la especificación braille/ONCE
│           ├── coordinates.py    # (fila,col) <-> casilla a1..h8  (fuente de verdad)
│           ├── braille.py        # mapa fila -> braille  (fuente de verdad)
│           ├── models.py         # BoardState, VisionResult, Transcription, Feedback...
│           ├── transcription.py  # BoardState -> Transcription (determinista)
│           └── validation.py     # validadores de coherencia
├── services/
│   └── vision/           # Pipeline de visión híbrido + recognizer intercambiable
├── apps/
│   ├── api/              # Backend FastAPI (ciclo de vida de análisis, feedback, historial)
│   └── web/             # Frontend React + TypeScript accesible
├── data/                 # raw / annotations / curated (datasets)
├── tests/                # Pruebas unitarias e integración (backend)
├── infra/                # Docker / compose / CI
└── docs/                 # Especificación, arquitectura y roadmap
```

## Puesta en marcha (desarrollo)

### Backend + dominio

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e packages/contracts -e services/vision -e apps/api
pytest
```

Arrancar la API:

```bash
uvicorn chess_api.main:app --reload --app-dir apps/api/src
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

### Docker Compose

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up --build
```

## Principios

1. **Accesibilidad desde el diseño.** El modo ciego no es un añadido posterior.
2. **Visión desacoplada de la transcripción.** El `BoardState` es el contrato entre ambos.
3. **Feedback trazable.** Una corrección nunca sobreescribe la predicción original ni
   modifica el modelo en producción.
4. **Determinismo.** Coordenadas, braille y transcripción son reproducibles y tienen tests.
5. **Modelo intercambiable.** El recognizer de piezas se puede sustituir sin tocar el
   contrato ni el motor de transcripción.

Ver [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) y [docs/ROADMAP.md](./docs/ROADMAP.md).
