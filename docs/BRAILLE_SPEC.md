# Especificación extraída del PDF — Reto Ajedrez ONCE

## Fuente

**RETO AJEDREZ de la ONCE — Adaptación a Braille**.

La signografía indicada se basa en el Documento técnico B8, Documentos técnicos relacionados con el Braille, de la Comisión Braille Española, ajustada a la representación utilizada por el libro original.

## Reglas de representación

La notación no distingue entre la posición de las piezas blancas y la de las negras al anotar las jugadas. Las casillas se denominan y numeran igual para ambos jugadores.

El tablero se interpreta como un eje de coordenadas:

- Columnas, de izquierda a derecha: `a b c d e f g h`.
- Filas: números en posición baja en braille, del 1 al 8, comenzando desde la posición de las blancas.

### Números en posición baja

| Número | Braille |
|---|---|
| 1 | `⠂` |
| 2 | `⠆` |
| 3 | `⠒` |
| 4 | `⠲` |
| 5 | `⠢` |
| 6 | `⠖` |
| 7 | `⠶` |
| 8 | `⠦` |

### Piezas

| Símbolo | Pieza |
|---|---|
| `R` | Rey |
| `D` | Dama |
| `A` | Alfil |
| `C` | Caballo |
| `T` | Torre |
| `P` | Peón |

Ejemplo del documento: `Re⠂` = rey, columna e, fila 1.

## Elementos adicionales

### Casillas resaltadas

Cuando una casilla está resaltada, se escribe por separado indicando su color. El documento muestra ejemplos de resaltado en **amarillo** y **rojo**.

### Flechas

Las flechas que unen casillas se representan indicando las casillas afectadas y utilizando `⠒⠕` o `⠪⠒` según la dirección de la flecha.

## Ejemplos de tableros extraídos

### Tablero 1 — Adaptación 1

**Blancas:** `Re⠂ Dd⠂ Ta⠂ Th⠂ Cc⠒ Cf⠒ Ac⠲ Ag⠒ Pa⠆ Pb⠆ Pc⠆ Pd⠒ Pe⠲ Pf⠆ Pg⠆ Ph⠆`

**Negras:** `Re⠦ Dd⠦ Ta⠦ Th⠦ Cc⠖ Cf⠖ Ac⠢ Ac⠦ Pa⠶ Pb⠶ Pc⠶ Pd⠖ Pe⠢ Pf⠶ Pg⠢ Ph⠖`

**Resaltadas:** amarillo en `g⠒` y `h⠲`.

También aparece una adaptación alternativa en la que los peones se expresan mediante coordenadas sin prefijo de pieza:

**Blancas:** `Re⠂ Dd⠂ Ta⠂ Th⠂ Cc⠒ Cf⠒ Ac⠲ Ag⠒ a⠆ b⠆ c⠆ d⠒ e⠲ f⠆ g⠆ h⠆`

**Negras:** `Re⠦ Dd⠦ Ta⠦ Th⠦ Cc⠖ Cf⠖ Ac⠢ Ac⠦ a⠶ b⠶ c⠖ e⠢ f⠶ g⠢ h⠖`

**Resaltadas:** amarillo en `g⠒` y `h⠲`.

### Tablero 2 — Adaptación 2

**Blancas:** `Re⠂ Dd⠂ Ta⠂ Th⠂ Cc⠒ Af⠂ Af⠲ a⠆ b⠆ c⠆ e⠲ f⠆ g⠆ h⠆`

**Negras:** `Re⠦ Dd⠦ Ta⠦ Th⠦ Cg⠲ Ac⠦ Af⠦ a⠶ b⠶ d⠖ e⠢ f⠶ g⠶ h⠶`

**Resaltadas:** amarillo en `d⠂` y `d⠲`.

**Flecha:** desde `d⠲` hacia `d⠂`: `d⠲¬⠒⠕¬d⠂`.

### Tablero 3 — Adaptación 3

**Blancas:** `Re⠂ Dd⠂ Ta⠂ Th⠂ Cb⠂ Cf⠒ Af⠂ Ag⠢ a⠆ b⠆ c⠲ d⠲ e⠆ f⠆ g⠆ h⠆`

**Negras:** `Re⠦ Dd⠦ Ta⠦ Th⠦ Cb⠦ Cf⠖ Ac⠦ Af⠦ a⠶ b⠶ c⠶ d⠶ e⠖ f⠢ g⠶ h⠖`

**Resaltadas:** amarillo en `h⠶` y `h⠖`, con flecha `h⠶¬⠒⠕¬h⠖`.

### Tablero 4 — Adaptación 4

**Blancas:** `Rh⠂ a⠲ b⠒ c⠆ f⠒ g⠲ h⠒`

**Negras:** `Ra⠦ a⠶ b⠖ f⠲ g⠢ h⠲`

### Tablero 5 — Adaptación 5

**Blancas:** `Rg⠂ Dd⠒ Tc⠂ Cd⠆ Ch⠢ Ac⠒ c⠲ d⠢ e⠲ g⠆ h⠒`

**Negras:** `Rg⠦ Db⠦ Ta⠆ Tb⠖ Ad⠖ Ad⠶ c⠢ e⠢ f⠖ f⠶ h⠖`

**Resaltadas:** amarillo en `g⠒` y `h⠢`; rojo en `f⠖`.

**Flechas:**
- `c⠂¬⠒⠕¬f⠂`
- `d⠒¬⠒⠕¬g⠒`
- `h⠢¬⠒⠕¬f⠖`

### Tablero 6 — Adaptación 6

**Blancas:** `Rg⠂ Dd⠂ Ta⠂ Te⠂ Cd⠆ Cf⠒ Ac⠂ Ac⠆ b⠲ c⠒ d⠢ e⠲ f⠆ g⠆ h⠒`

**Negras:** `Rg⠦ Dc⠶ Tb⠦ Tf⠦ Cb⠶ Cf⠖ Ac⠦ Ae⠶ b⠢ c⠢ d⠖ e⠢ f⠶ g⠶ h⠶`

**Resaltadas:** amarillo en `b⠶` y `d⠦`; rojo en `c⠂`.

**Flechas:** desde `d⠆`, ocupada por el caballo, hacia `b⠂`, `b⠒` y `f⠂`.

## Ejemplos de adaptación a audio incluidos en el PDF

### Diagrama 1 — pág. 15

**Blancas:** Rey en E2, Dama en A4, Torres en C1 y H1, Alfil en B5, Caballos en C3 y F3, Peones en A2, B2, D2, F2, G2 y H2.

**Negras:** Rey en E8, Dama en D7, Torres en A8 y H8, Alfiles en F8 y G4, Caballo en C6, Peones en A7, B7, C5, E7, F7, G7 y H7.

### Diagrama 2 — pág. 17

**Blancas:** Rey en D2, Alfil en H6, Caballo en E1, Peones en A3, B2, G2 y H3.

**Negras:** Rey en E6, Alfil en C4, Caballo en C6, Peones en B7, B6, D5, G6 y H7.

### Diagrama 5 — pág. 24

**Blancas:** Rey en G1, Dama en D1, Torres en A1 y E1, Alfiles en B3 y C1, Caballos en B1 y F3, Peones en A2, B2, C3, D4, E4, F2, G2 y H2.

**Negras:** Rey en G8, Dama en D8, Torres en A8 y F8, Alfiles en E7 y C4, Caballos en A6 y F6, Peones en A6, B5, C7, D6, E5, F7, G7 y H7.

### Diagrama 23 — pág. 44

**Blancas:** Rey en H3, Dama en F5, Torre en F1, Caballo en E2, Peones en A6, C4, D5, G3 y G4.

**Negras:** Rey en H7, Dama en G6, Torre en E7, Alfil en E3, Peones en A7, C5, E4, G5 y H6.

## Información necesaria para el proyecto de software

El PDF aporta requisitos y casos de prueba que deben incorporarse al sistema:

1. **Contrato de coordenadas:** columnas `a-h` y filas 1-8 representadas mediante los ocho números braille indicados.
2. **Independencia del color en la coordenada:** una casilla tiene la misma denominación para blancas y negras.
3. **Reconocimiento de piezas:** el sistema debe poder producir, como mínimo, Rey, Dama, Alfil, Caballo, Torre y Peón mediante `R/D/A/C/T/P` cuando el formato de la adaptación use el identificador de pieza.
4. **Representación alternativa de peones:** los ejemplos muestran adaptaciones en las que los peones pueden aparecer como coordenadas sin letra `P`; esto debe tratarse como una variante de formato y no descartarse durante el diseño.
5. **Elementos gráficos adicionales:** resaltados por color y flechas entre casillas deben modelarse como entidades independientes del estado de las piezas.
6. **Flechas dirigidas:** el modelo de datos deberá guardar origen, destino y dirección para poder producir `⠒⠕` o `⠪⠒`.
7. **Casos de prueba reales:** los seis tableros de adaptación braille y los cuatro diagramas de audio son material candidato para pruebas unitarias, integración y evaluación visual.
8. **Compatibilidad de salida:** conviene conservar tanto una representación semántica interna del tablero como una salida textual/braille generada a partir de esa representación.

## Observaciones de fidelidad de la fuente

Este documento conserva el contenido tal como aparece en la extracción proporcionada del PDF. No se han corregido aparentes inconsistencias de la fuente. En particular, el Diagrama 5 contiene una referencia a A6 tanto para un Caballo negro como para un Peón negro; debe mantenerse como dato de validación o revisarse contra la página visual original antes de usarlo como ground truth.

