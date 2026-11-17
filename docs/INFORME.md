# Informe - Proyecto 1: Agente de Rescate con Víctimas en Riesgo

> Completa este informe con los resultados obtenidos al ejecutar tus propios
> casos de prueba y prepárate para sustentar cada decisión de implementación.

## 1. Representación del estado

Un estado se representa por la tupla:

```text
(fila, columna, victimas_vivas, tick_actual)
```

- `fila, columna`: posición actual del agente.
- `victimas_vivas`: conjunto inmutable de identificadores de víctimas que no
  han sido rescatadas ni han fallecido.
- `tick_actual`: número de movimientos efectuados.

La clase `Estado` es inmutable y hasheable. Por eso puede usarse como clave de
diccionarios y en conjuntos de visitados. El historial de rescates y muertes se
conserva en los nodos de búsqueda para poder reconstruir la ruta y las métricas.

## 2. Espacio de búsqueda

Las acciones son Norte, Sur, Este y Oeste. Una acción es válida únicamente si
el destino está dentro de la cuadrícula y no es una pared. Cada movimiento
cuesta un tick; no existe una acción de espera.

Al finalizar el movimiento, el tick aumenta en uno. Si el agente llegó a una
víctima y `tick_actual <= ticks_supervivencia`, la víctima se rescata. Cualquier
víctima viva para la cual `tick_actual > ticks_supervivencia` fallece. El
objetivo es encontrar una ruta terminal con el mayor número de rescates; en
empates se prefiere la de menos ticks.

## 3. Algoritmos

- **BFS:** usa una cola FIFO y explora por niveles de profundidad.
- **UCS:** usa una cola de prioridad ordenada por el costo acumulado. Como cada
  movimiento cuesta uno, su costo coincide con los ticks.
- **IDDFS:** ejecuta búsquedas en profundidad con límites crecientes. El límite
  máximo relevante es el mayor tiempo de supervivencia más un tick.
- **A\*:** usa `f(n) = g(n) + h(n)`, donde `g(n)` cuenta fallecimientos ya
  ocurridos y `h(n)` estima fallecimientos inevitables.

## 4. Heurística de A* y admisibilidad

Para cada víctima viva se calcula la distancia Manhattan desde el agente. Una
víctima está condenada si:

```text
distancia_manhattan(agente, víctima) > ticks_supervivencia - tick_actual
```

La heurística es el número de víctimas condenadas. La distancia Manhattan
ignora paredes, por lo que nunca es mayor que la cantidad real de movimientos
necesarios. Por tanto, si incluso esa distancia mínima supera el tiempo
restante, la víctima necesariamente morirá. Cada víctima contada representa un
fallecimiento inevitable; en consecuencia, `h(n)` no sobreestima los
fallecimientos futuros y es admisible.

## 5. Pruebas y resultados

Describe aquí cada mapa utilizado, su número de víctimas y los resultados de
la tabla que muestra la aplicación. Incluye al menos casos con paredes,
víctimas que expiran, rutas alternativas y situaciones donde no sea posible
rescatar a todas las víctimas.

| Caso | Algoritmo | Nodos explorados | Tiempo | Rescatadas | Fallecidas | Ticks |
|---|---:|---:|---:|---:|---:|---:|
| Completar | | | | | | |

## 6. Análisis comparativo

Explica las diferencias observadas en nodos explorados y tiempo de ejecución.
Relaciona los resultados de A* con el uso de la heurística y los de IDDFS con
la repetición de exploraciones en cada límite de profundidad.
