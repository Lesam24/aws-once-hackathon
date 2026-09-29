# Aplicación de accesibilidad para adaptar el ajedrez a personas ciegas

Enfoques: Innovacion, Accesibilidad, Impactocto social y viabilidad

Objetivo: Crear unaa aplicacion/software a través del cual los ciegos puedan interpretar un tablero de ajedrez, transcribiendolo a texto, usando combinaciones de braile y fichas, junto
con el sistema de coordenadas del ajedrez convencional.

La notación no distingue entre la posición de las piezas blancas y la de las
negras a la hora de anotar las jugadas. Por tanto, las casillas se denominan y
numeran igual para ambos jugadores.
El tablero está leído como un eje de coordenadas.
• Las columnas se representan por las ocho primeras letras del alfabeto. Según
esto, de izquierda a derecha, tendremos: a, b, c, d, e, f, g y h.
• Las filas se representan en braille por un número en posición baja, del 1 al 8,
comenzando desde la posición de las blancas.
Equivalencias de símbolos para los números en posición baja:
1 ⠂
2 ⠆
3 ⠒
4 ⠲
5 ⠢
6 ⠖
7 ⠶
8 ⠦
Las piezas de ajedrez:
R Rey
D Dama
A Alfil
C Caballo
T Torre
P Peón
En determinadas representaciones de tableros, algunas casillas aparecen
resaltadas, en rojo o en amarillo, para distinguirlas. Estas se escribirán por
separado indicando en cada caso su color.
Asimismo, en los diagramas de los tableros, en ocasiones se muestran flechas
que unen casillas. En la transcripción se indicarán las casillas que estén
afectadas unidas mediante la flecha ⠒⠕ o ⠪⠒ dependiendo de la dirección de
la misma.
Ej.
Re⠂
Rey, columna e, fila 1

## Necesidades tecnicas básicas

- Entrada: Imagen del tablero de ajedrez
- Salida esperada: Transcipción de texto del tablero

La transcripción deberá ser realizada a través de una IA que lea imagenes, analice la fotografía y empiece a realizar la transcipción. Deberá de haber 2 opciones, una para ciegos y otra para videntes,
en el caso de ciegos, la transcipción se realizará sin capacidad de edición. En caso de videntes, previo a la salida, habrá una opción para editar y corregir la transcipción, en caso de corrección
se deberá promptear al usuario corrector que se usará para aprender, cualquier error por su parte podrá empeorará futuras transcripciones. En caso de error, la IA recibirá el feedback y aprenderá de la misma.

La IA debe de ser capaz de analizar e interpretar diferentes estilos de tablero.

-- Flujo: Imagen de tablero -> Selección de modo -> Transcipción -> (Vidente) Opción a correccion -> Entrega de la transcipción

### Añadidos:
- Guardado de transcripciones (entrada y salida)
- Opción para entrar al historial, para videntes y confirmarle a la IA que su resultado fue correcto, para poder actualizar el algoritmo.

