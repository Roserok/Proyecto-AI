"""Implementaciones desde cero de los algoritmos de búsqueda requeridos."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import heapq
from itertools import count
from time import perf_counter

from src.modelo import Estado, InstanciaRescate
from src.heuristicas import victimas_condenadas
from src.simulacion import Transicion, movimientos_posibles


@dataclass(frozen=True, slots=True)
class NodoBusqueda:
    """Información de una ruta parcial mientras se explora el espacio."""

    estado: Estado
    transiciones: tuple[Transicion, ...]
    rescatadas: frozenset[str]
    fallecidas: frozenset[str]

    @property
    def cantidad_rescatadas(self) -> int:
        """Cantidad acumulada de víctimas rescatadas en esta ruta."""
        return len(self.rescatadas)


@dataclass(frozen=True, slots=True)
class ResultadoBusqueda:
    """Resultado completo de ejecutar un algoritmo sobre una instancia."""

    algoritmo: str
    transiciones: tuple[Transicion, ...]
    rescatadas: tuple[str, ...]
    fallecidas: tuple[str, ...]
    ticks_totales: int
    nodos_explorados: int
    tiempo_segundos: float

    @property
    def acciones(self) -> tuple[str, ...]:
        """Ruta compacta expresada como acciones cardinales."""
        return tuple(transicion.accion for transicion in self.transiciones)


def busqueda_amplitud(instancia: InstanciaRescate) -> ResultadoBusqueda:
    """Explora el espacio por niveles y conserva la mejor solución terminal.

    La búsqueda no se detiene al encontrar la primera solución: la meta es
    maximizar rescates, por lo que se evalúan todas las rutas relevantes hasta
    que no quede ninguna víctima viva. Entre soluciones con los mismos
    rescates, se conserva la de menor cantidad de ticks.
    """
    inicio_tiempo = perf_counter()
    estado_inicial = instancia.estado_inicial()
    nodo_inicial = NodoBusqueda(
        estado=estado_inicial,
        transiciones=(),
        rescatadas=frozenset(),
        fallecidas=frozenset(),
    )
    frontera: deque[NodoBusqueda] = deque([nodo_inicial])
    mejor_rescates_por_estado: dict[Estado, int] = {estado_inicial: 0}
    mejor_solucion: NodoBusqueda | None = None
    nodos_explorados = 0

    while frontera:
        nodo = frontera.popleft()
        nodos_explorados += 1

        if not nodo.estado.victimas_vivas:
            if _es_mejor_solucion(nodo, mejor_solucion):
                mejor_solucion = nodo
            continue

        for transicion in movimientos_posibles(instancia, nodo.estado):
            siguiente = NodoBusqueda(
                estado=transicion.estado,
                transiciones=nodo.transiciones + (transicion,),
                rescatadas=nodo.rescatadas | frozenset(transicion.rescatadas),
                fallecidas=nodo.fallecidas | frozenset(transicion.fallecidas),
            )
            rescates_previos = mejor_rescates_por_estado.get(siguiente.estado, -1)
            if siguiente.cantidad_rescatadas <= rescates_previos:
                continue
            mejor_rescates_por_estado[siguiente.estado] = siguiente.cantidad_rescatadas
            frontera.append(siguiente)

    if mejor_solucion is None:
        # Con una cantidad finita de ticks toda víctima termina rescatada o
        # fallecida; esta protección evita devolver un resultado incompleto.
        raise RuntimeError("No se encontró un estado terminal para la instancia.")

    return _crear_resultado("BFS", mejor_solucion, nodos_explorados, inicio_tiempo)


def busqueda_costo_uniforme(instancia: InstanciaRescate) -> ResultadoBusqueda:
    """Explora las rutas por costo acumulado mediante una cola de prioridad.

    Como cada acción cuesta un tick, el costo de una ruta coincide con su
    cantidad de movimientos. Aun así, la implementación usa explícitamente
    una cola de prioridad, como corresponde a UCS.
    """
    inicio_tiempo = perf_counter()
    estado_inicial = instancia.estado_inicial()
    nodo_inicial = NodoBusqueda(
        estado=estado_inicial,
        transiciones=(),
        rescatadas=frozenset(),
        fallecidas=frozenset(),
    )
    consecutivo = count()
    frontera: list[tuple[int, int, NodoBusqueda]] = [(0, next(consecutivo), nodo_inicial)]
    mejor_rescates_por_estado: dict[Estado, int] = {estado_inicial: 0}
    mejor_solucion: NodoBusqueda | None = None
    nodos_explorados = 0

    while frontera:
        costo, _, nodo = heapq.heappop(frontera)
        nodos_explorados += 1

        if not nodo.estado.victimas_vivas:
            if _es_mejor_solucion(nodo, mejor_solucion):
                mejor_solucion = nodo
            continue

        for transicion in movimientos_posibles(instancia, nodo.estado):
            siguiente = NodoBusqueda(
                estado=transicion.estado,
                transiciones=nodo.transiciones + (transicion,),
                rescatadas=nodo.rescatadas | frozenset(transicion.rescatadas),
                fallecidas=nodo.fallecidas | frozenset(transicion.fallecidas),
            )
            rescates_previos = mejor_rescates_por_estado.get(siguiente.estado, -1)
            if siguiente.cantidad_rescatadas <= rescates_previos:
                continue
            mejor_rescates_por_estado[siguiente.estado] = siguiente.cantidad_rescatadas
            heapq.heappush(frontera, (costo + 1, next(consecutivo), siguiente))

    if mejor_solucion is None:
        raise RuntimeError("No se encontró un estado terminal para la instancia.")
    return _crear_resultado("UCS", mejor_solucion, nodos_explorados, inicio_tiempo)


def busqueda_profundidad_iterativa(instancia: InstanciaRescate) -> ResultadoBusqueda:
    """Ejecuta búsquedas con límite creciente de profundidad (IDDFS).

    Se revisan todos los límites hasta que haya transcurrido un tick después
    del mayor plazo de supervivencia. En ese momento toda víctima que no fue
    rescatada necesariamente habrá fallecido, por lo cual el espacio relevante
    quedó cubierto.
    """
    inicio_tiempo = perf_counter()
    estado_inicial = instancia.estado_inicial()
    nodo_inicial = NodoBusqueda(
        estado=estado_inicial,
        transiciones=(),
        rescatadas=frozenset(),
        fallecidas=frozenset(),
    )
    profundidad_maxima = max(v.ticks_supervivencia for v in instancia.victimas) + 1
    mejor_solucion: NodoBusqueda | None = None
    nodos_explorados = 0

    for limite in range(profundidad_maxima + 1):
        mejor_rescates_por_estado: dict[Estado, int] = {estado_inicial: 0}

        def explorar(nodo: NodoBusqueda, restante: int) -> None:
            nonlocal mejor_solucion, nodos_explorados
            nodos_explorados += 1
            if not nodo.estado.victimas_vivas:
                if _es_mejor_solucion(nodo, mejor_solucion):
                    mejor_solucion = nodo
                return
            if restante == 0:
                return

            for transicion in movimientos_posibles(instancia, nodo.estado):
                siguiente = NodoBusqueda(
                    estado=transicion.estado,
                    transiciones=nodo.transiciones + (transicion,),
                    rescatadas=nodo.rescatadas | frozenset(transicion.rescatadas),
                    fallecidas=nodo.fallecidas | frozenset(transicion.fallecidas),
                )
                rescates_previos = mejor_rescates_por_estado.get(siguiente.estado, -1)
                if siguiente.cantidad_rescatadas <= rescates_previos:
                    continue
                mejor_rescates_por_estado[siguiente.estado] = siguiente.cantidad_rescatadas
                explorar(siguiente, restante - 1)

        explorar(nodo_inicial, limite)

    if mejor_solucion is None:
        raise RuntimeError("No se encontró un estado terminal para la instancia.")
    return _crear_resultado("IDDFS", mejor_solucion, nodos_explorados, inicio_tiempo)


def busqueda_a_estrella(instancia: InstanciaRescate) -> ResultadoBusqueda:
    """Busca rutas que minimizan fallecimientos con A* y una heurística admisible.

    ``g(n)`` es el número de víctimas que ya fallecieron y ``h(n)`` estima
    cuántas más necesariamente fallecerán. Minimizar ``g + h`` equivale a
    maximizar el número de rescates.
    """
    inicio_tiempo = perf_counter()
    estado_inicial = instancia.estado_inicial()
    nodo_inicial = NodoBusqueda(
        estado=estado_inicial,
        transiciones=(),
        rescatadas=frozenset(),
        fallecidas=frozenset(),
    )
    consecutivo = count()
    prioridad_inicial = victimas_condenadas(instancia, estado_inicial)
    frontera: list[tuple[int, int, int, NodoBusqueda]] = [
        (prioridad_inicial, 0, next(consecutivo), nodo_inicial)
    ]
    mejores_fallecimientos_por_estado: dict[Estado, int] = {estado_inicial: 0}
    mejor_solucion: NodoBusqueda | None = None
    nodos_explorados = 0

    while frontera:
        _, _, _, nodo = heapq.heappop(frontera)
        fallecimientos = len(nodo.fallecidas)
        if fallecimientos > mejores_fallecimientos_por_estado.get(nodo.estado, fallecimientos):
            continue
        nodos_explorados += 1

        if not nodo.estado.victimas_vivas:
            if _es_mejor_solucion(nodo, mejor_solucion):
                mejor_solucion = nodo
            continue

        for transicion in movimientos_posibles(instancia, nodo.estado):
            siguiente = NodoBusqueda(
                estado=transicion.estado,
                transiciones=nodo.transiciones + (transicion,),
                rescatadas=nodo.rescatadas | frozenset(transicion.rescatadas),
                fallecidas=nodo.fallecidas | frozenset(transicion.fallecidas),
            )
            siguientes_fallecimientos = len(siguiente.fallecidas)
            anterior = mejores_fallecimientos_por_estado.get(siguiente.estado)
            if anterior is not None and siguientes_fallecimientos >= anterior:
                continue
            mejores_fallecimientos_por_estado[siguiente.estado] = siguientes_fallecimientos
            heuristica = victimas_condenadas(instancia, siguiente.estado)
            prioridad = siguientes_fallecimientos + heuristica
            heapq.heappush(
                frontera,
                (prioridad, siguiente.estado.tick_actual, next(consecutivo), siguiente),
            )

    if mejor_solucion is None:
        raise RuntimeError("No se encontró un estado terminal para la instancia.")
    return _crear_resultado("A*", mejor_solucion, nodos_explorados, inicio_tiempo)


def comparar_algoritmos(instancia: InstanciaRescate) -> tuple[ResultadoBusqueda, ...]:
    """Ejecuta los cuatro algoritmos y devuelve resultados comparables."""
    return (
        busqueda_amplitud(instancia),
        busqueda_costo_uniforme(instancia),
        busqueda_profundidad_iterativa(instancia),
        busqueda_a_estrella(instancia),
    )


def _es_mejor_solucion(candidata: NodoBusqueda, actual: NodoBusqueda | None) -> bool:
    """Ordena soluciones por rescates máximos y, en empate, menos ticks."""
    if actual is None:
        return True
    return (candidata.cantidad_rescatadas, -candidata.estado.tick_actual) > (
        actual.cantidad_rescatadas,
        -actual.estado.tick_actual,
    )


def _crear_resultado(
    algoritmo: str,
    solucion: NodoBusqueda,
    nodos_explorados: int,
    inicio_tiempo: float,
) -> ResultadoBusqueda:
    """Convierte una solución interna en el formato público de resultados."""
    return ResultadoBusqueda(
        algoritmo=algoritmo,
        transiciones=solucion.transiciones,
        rescatadas=tuple(sorted(solucion.rescatadas)),
        fallecidas=tuple(sorted(solucion.fallecidas)),
        ticks_totales=solucion.estado.tick_actual,
        nodos_explorados=nodos_explorados,
        tiempo_segundos=perf_counter() - inicio_tiempo,
    )
