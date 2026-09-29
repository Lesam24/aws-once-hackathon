# ARCHITECTURE.md — Propuesta de arquitectura

## 1. Objetivo arquitectónico

Diseñar una plataforma capaz de transformar una imagen de un tablero de ajedrez en una representación accesible y estructurada, manteniendo separadas las responsabilidades de:

- interfaz y accesibilidad;
- ingestión de imágenes;
- visión artificial;
- representación de la posición;
- validación;
- transcripción;
- persistencia;
- feedback y mejora del modelo.

El objetivo principal de esta separación es poder mejorar el reconocimiento sin tener que reescribir la lógica de transcripción o la interfaz accesible.

## 2. Decisiones arquitectónicas principales

### DA-01 — Arquitectura modular con backend central

Se propone una arquitectura modular de tipo monolito modular para el MVP, con posibilidad de extraer servicios posteriormente.

**Motivo:** un sistema distribuido completo desde el primer día introduciría complejidad operacional sin aportar un beneficio proporcional para un MVP.

```text
                    ┌──────────────────────┐
                    │      Frontend        │
                    │ React + TypeScript   │
                    └──────────┬───────────┘
                               │ HTTPS/REST
                    ┌──────────▼───────────┐
                    │      FastAPI         │
                    │ API + Auth + Domain  │
                    └───────┬────┬─────────┘
                            │    │
              ┌─────────────┘    └──────────────┐
              ▼                                 ▼
     ┌─────────────────┐                ┌─────────────────┐
     │ Vision Pipeline │                │ PostgreSQL      │
     │ OpenCV + Model  │                │ metadata/FB     │
     └────────┬────────┘                └─────────────────┘
              │
              ▼
     ┌─────────────────┐
     │ Position Domain │
     │ + Validation    │
     └────────┬────────┘
              ▼
     ┌─────────────────┐
     │ Transcription   │
     │ Braille + Coord │
     └────────┬────────┘
              ▼
     ┌─────────────────┐
     │ Object Storage  │
     │ original images │
     └─────────────────┘
```

### DA-02 — Representación intermedia `BoardState`

La IA no debe generar directamente el texto final. Debe producir una estructura canónica:

```text
Image
  ↓
VisionResult
  ↓
BoardState
  ↓
ValidationResult
  ↓
Transcription
```

La `BoardState` actúa como contrato entre reconocimiento y presentación.

### DA-03 — Pipeline híbrido de visión

Se propone una estrategia híbrida:

```text
Preprocesado clásico
      ↓
Detección geométrica
      ↓
Rectificación
      ↓
Localización de casillas
      ↓
Modelo de IA para piezas
      ↓
Reglas / validación
      ↓
Resultado estructurado
```

Esto evita delegar a un único modelo problemas que pueden resolverse de forma determinista.

### DA-04 — Feedback diferido

Las correcciones humanas se registran como datos etiquetados. No deben modificar automáticamente el modelo de producción.

```text
Feedback humano
      ↓
Almacenamiento
      ↓
Curación
      ↓
Dataset versionado
      ↓
Entrenamiento
      ↓
Evaluación
      ↓
Aprobación
      ↓
Despliegue
```

## 3. Componentes

### 3.1 Frontend

Responsabilidades:

- seleccionar modo de uso;
- capturar/subir imagen;
- mostrar estado del procesamiento;
- mostrar transcripción;
- permitir correcciones en modo vidente;
- consultar historial;
- comunicar errores de forma accesible.

Requisitos de diseño:

- HTML semántico.
- Controles con nombres accesibles.
- Foco visible y gestión correcta del foco.
- Navegación por teclado.
- Mensajes de estado anunciables por lector de pantalla.
- No depender exclusivamente de color.
- Vista de resultado lineal para lectura asistida.

### 3.2 API Backend

Responsabilidades:

- autenticación/autorización, si se incorpora cuenta de usuario;
- validación de peticiones;
- creación de trabajos de análisis;
- exposición de resultados;
- persistencia;
- gestión del historial;
- recepción de feedback;
- control de versiones de pipeline/modelo.

Endpoints iniciales sugeridos:

```text
POST   /api/v1/analyses
GET    /api/v1/analyses/{id}
GET    /api/v1/analyses/{id}/transcription
POST   /api/v1/analyses/{id}/correction
POST   /api/v1/analyses/{id}/feedback/confirm
GET    /api/v1/history
GET    /api/v1/health
```

### 3.3 Servicio de ingestión

Valida:

- formato de imagen;
- tamaño máximo;
- dimensiones mínimas;
- contenido no vacío/corrupto;
- metadatos que deban eliminarse por privacidad.

Debe registrar un `analysis_id` desde el principio.

### 3.4 Pipeline de visión

#### Paso A — Preprocesado

Operaciones posibles:

- normalización de tamaño;
- reducción de ruido;
- corrección de iluminación;
- conversión de espacio de color;
- detección de bordes.

#### Paso B — Detección del tablero

El sistema busca la región correspondiente al tablero.

Salida:

```json
{
  "board_bbox": [x, y, width, height],
  "corners": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]],
  "confidence": 0.97
}
```

#### Paso C — Rectificación

Con las esquinas detectadas se realiza una transformación de perspectiva para obtener una vista normalizada de 8×8.

#### Paso D — Segmentación

La imagen rectificada se divide en 64 casillas.

Cada casilla queda asociada inequívocamente con una coordenada.

```text
8  a8 b8 c8 d8 e8 f8 g8 h8
7  a7 b7 c7 d7 e7 f7 g7 h7
...
1  a1 b1 c1 d1 e1 f1 g1 h1
   a  b  c  d  e  f  g  h
```

La orientación debe determinarse de forma explícita. El sistema no debe asumirla sin una señal fiable.

#### Paso E — Reconocimiento de piezas

Cada casilla se clasifica como:

```text
empty
white_pawn
white_knight
white_bishop
white_rook
white_queen
white_king
black_pawn
black_knight
black_bishop
black_rook
black_queen
black_king
unknown
```

La etiqueta `unknown` es importante: permite expresar incertidumbre sin inventar una pieza.

#### Paso F — Detección de elementos adicionales

Fase posterior al MVP:

```text
highlight:
  square + color

arrow:
  from_square
  to_square
  direction_symbol
```

## 4. Dominio de ajedrez

El dominio no debe depender de OpenCV ni del modelo de IA.

Entidades principales:

```text
BoardState
├── orientation
├── pieces[]
├── highlights[]
├── arrows[]
└── metadata
```

Una pieza:

```text
Piece
├── color
├── type
├── square
└── confidence
```

### Coordenadas

El dominio debe mantener una única fuente de verdad para la conversión de índices `(fila, columna)` a casillas `a1`–`h8`.

### Braille

Debe existir un módulo de dominio con el mapa:

```text
1 → ⠂
2 → ⠆
3 → ⠒
4 → ⠲
5 → ⠢
6 → ⠖
7 → ⠶
8 → ⠦
```

La conversión debe ser determinista y tener tests unitarios completos.

## 5. Motor de transcripción

Entrada:

```text
BoardState
```

Salida:

```text
Transcription
├── lines[]
├── highlights[]
├── arrows[]
├── warnings[]
└── format_version
```

Ejemplo conceptual:

```text
Re⠂
Dc⠒
Pg⠢
```

El motor no debe decidir qué pieza había en una casilla. Esa responsabilidad pertenece a visión/validación.

## 6. Validación y confianza

El sistema debe conservar la confianza de los modelos.

Una estrategia básica:

```text
confidence >= threshold
    ↓
resultado aceptable

confidence < threshold
    ↓
marcar como incierto
    ↓
revisión en modo vidente
```

En modo para personas ciegas, el sistema no debe mostrar una corrección visual inexistente. Debe poder expresar incertidumbre en una forma compatible con el canal de salida.

### Validaciones recomendadas

- 64 casillas identificadas.
- Coordenadas válidas.
- Máximo una pieza por casilla.
- Tipos y colores válidos.
- Coherencia de orientación.
- Comprobaciones ajedrecísticas opcionales.

Una posición que falle una regla no debe ser “arreglada” automáticamente inventando datos; debe marcarse como inconsistente.

## 7. Persistencia

### PostgreSQL

Tablas sugeridas:

```text
users
analyses
analysis_images
board_states
transcriptions
corrections
feedback_events
model_versions
pipeline_versions
```

### Object Storage

Guardar:

- imagen original;
- imagen normalizada opcional;
- derivados necesarios para debugging, con política de retención.

Los binarios no deberían almacenarse directamente en PostgreSQL salvo casos muy concretos.

## 8. Modelo de datos de feedback

Cada feedback debería registrar como mínimo:

```text
feedback_id
analysis_id
user_id / anonymous_session_id
original_prediction
corrected_prediction
feedback_type
created_at
model_version
pipeline_version
review_status
```

`review_status` puede ser:

```text
pending
accepted
rejected
used_for_training
```

Esto permite distinguir “corrección enviada” de “dato considerado válido para entrenamiento”.

## 9. Estrategia de IA

### Primera aproximación

Para el MVP, el sistema debería entrenarse con datos representativos de:

- piezas y sets gráficos diferentes;
- tableros con diferentes colores;
- diferentes escalas;
- fotografías con perspectiva;
- diferentes condiciones de iluminación;
- capturas de pantalla de aplicaciones o sitios de ajedrez;
- posiciones densas y posiciones con pocas piezas.

### Arquitectura del reconocimiento

Se puede empezar con detector de piezas + clasificación de tipo/color o con un detector multicategoría.

La decisión final debe evaluarse sobre un dataset propio del proyecto.

### Segundo nivel opcional

Un modelo multimodal puede utilizarse para casos difíciles o como mecanismo adicional de verificación, pero el resultado final debe pasar por la representación estructurada y los validadores del sistema.

## 10. Entrenamiento y MLOps

Estructura:

```text
data/raw
   ↓
annotation
   ↓
data/curated/vN
   ↓
train
   ↓
validation
   ↓
model registry
   ↓
staging
   ↓
production
```

Cada modelo debe estar asociado con:

- versión del dataset;
- configuración de entrenamiento;
- métricas;
- commit del código;
- fecha;
- conjunto de pruebas.

## 11. Estrategia de errores

### Error de imagen

Ejemplo:

```text
No se ha podido identificar un tablero de ajedrez en la imagen.
```

### Tablero detectado, pieza incierta

El sistema conserva:

```text
square = e4
prediction = unknown
confidence = 0.42
```

### Posición parcialmente reconocida

La salida debe indicar que hay elementos no determinados. No debe convertir incertidumbre en certeza.

## 12. Seguridad y privacidad

Medidas propuestas:

- HTTPS.
- Autorización por recurso.
- URLs temporales para objetos cuando sea necesario.
- Cifrado en reposo según infraestructura disponible.
- Eliminación configurable de imágenes.
- Minimización de datos personales.
- Registro de auditoría de correcciones y cambios de modelo.

## 13. Observabilidad

Métricas técnicas:

```text
request_latency
vision_latency
transcription_latency
queue_depth
error_rate
storage_usage
```

Métricas de IA:

```text
piece_accuracy
square_accuracy
board_exact_match
unknown_rate
false_positive_rate
```

Métricas de producto:

```text
human_correction_rate
confirmation_rate
time_to_result
successful_analysis_rate
```

## 14. Escalabilidad

### MVP

Monolito modular + worker opcional.

### Crecimiento

Extraer únicamente los componentes que presenten necesidades reales de escalabilidad:

```text
API
 ├── Analysis Service
 ├── Vision Worker(s)
 ├── Feedback Service
 └── Notification/History
```

El almacenamiento de imágenes y las inferencias son candidatos naturales para escalar independientemente.

## 15. Contratos entre componentes

Se recomienda definir esquemas versionados:

```text
AnalysisRequest v1
VisionResult v1
BoardState v1
Transcription v1
FeedbackEvent v1
```

Preferentemente con JSON Schema / Pydantic.

## 16. Pruebas

### Unitarias

- conversión fila/columna → coordenada;
- coordenada → Braille;
- generación de transcripción;
- validadores;
- serialización de contratos.

### Integración

- upload → análisis → resultado;
- corrección → historial;
- feedback → dataset pendiente.

### IA

Los conjuntos de entrenamiento, validación y prueba deben estar separados.

Especial atención a que imágenes muy similares de un mismo tablero no terminen repartidas entre train y test, porque eso puede inflar artificialmente las métricas.

## 17. Criterios de aceptación arquitectónicos del MVP

El MVP se considera técnicamente listo cuando:

1. Una imagen válida puede procesarse end-to-end.
2. La salida queda representada en un contrato estructurado.
3. El motor de transcripción es reproducible para la misma entrada.
4. El modo accesible puede utilizarse sin depender de interacción visual.
5. El modo vidente permite revisar y corregir.
6. Las correcciones quedan auditadas.
7. Las versiones de modelo y pipeline quedan registradas.
8. Hay pruebas automatizadas para la lógica determinista.
9. Se pueden medir errores sin sobrescribir el dato original.
10. El sistema puede sustituir el modelo de visión sin cambiar el contrato de transcripción.
