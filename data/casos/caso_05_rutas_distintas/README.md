# Caso 05 - Rutas distintas

Este caso permite comprobar que los algoritmos no tienen por qué animar la
misma ruta, incluso cuando logran el mismo resultado óptimo.

Resultados comprobados con la implementación actual:

| Algoritmo | Ruta | Rescatadas | Fallecidas | Ticks |
|---|---|---:|---:|---:|
| BFS | S, N, E, E, E, S, E, E, S | 2 | 1 | 9 |
| UCS | S, N, E, E, E, S, E, E, S | 2 | 1 | 9 |
| IDDFS | S, N, E, E, E, S, E, E, S | 2 | 1 | 9 |
| A* | S, E, N, E, E, S, E, E, S | 2 | 1 | 9 |

La víctima `V1` no puede ser rescatada a tiempo. Los cuatro algoritmos
rescatan `V2` y `V3`; A* elige un desvío diferente porque su prioridad usa la
heurística de víctimas condenadas.
