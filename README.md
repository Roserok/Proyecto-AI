# Proyecto 1 - Agente de Rescate

Aplicación de escritorio en Python con Tkinter para simular un agente de
rescate en una cuadrícula y comparar BFS, UCS, IDDFS y A*.

## Ejecutar

Desde la carpeta del proyecto, ejecuta:

```powershell
python main.py
```

No se requieren dependencias externas: se usa únicamente Python, Tkinter y la
biblioteca estándar.

## Archivos de entrada

Selecciona ambos archivos desde la interfaz:

- Un mapa rectangular con `#` (pared), `.` (libre) y una sola `S` (inicio).
- Un archivo de víctimas con encabezado
  `id,fila,columna,ticks_supervivencia`.

Las posiciones se numeran desde cero. También se admiten filas separadas por
espacios y etiquetas como `V1` en el mapa, siempre que coincidan con el archivo
de víctimas.

Ejemplo de `victimas.txt`:

```text
id,fila,columna,ticks_supervivencia
V1,1,4,5
V2,3,7,12
```

## Estructura

- `main.py`: inicio de la aplicación.
- `src/modelo.py`: entidades inmutables del problema.
- `src/parser.py`: lectura y validación de los archivos.
- `src/simulacion.py`: movimientos, ticks, rescates y fallecimientos.
- `src/busquedas.py`: BFS, UCS, IDDFS, A* y comparación.
- `src/heuristicas.py`: distancia Manhattan y heurística para A*.
- `src/interfaz.py`: interfaz Tkinter y animación.
- `data/`: ejemplos de entrada.
- `tests/`: pruebas automatizadas.
- `docs/`: guía base del informe.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```
