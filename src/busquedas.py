"""Implementaciones desde cero de los algoritmos de búsqueda requeridos."""

from collections import deque
from dataclasses import dataclass
import heapq
from time import perf_counter

from src.modelo import Estado
from src.heuristicas import victimas_condenadas
from src.simulacion import movimientos_posibles


@dataclass(frozen=True)
class NodoBusqueda:
    """Información de una ruta parcial mientras se explora el espacio."""

    estado: Estado
    transiciones: tuple
    rescatadas: frozenset
    fallecidas: frozenset

    @property
    def cantidad_rescatadas(self):
        """Cantidad acumulada de víctimas rescatadas en esta ruta."""
        return len(self.rescatadas)


@dataclass(frozen=True)
class ResultadoBusqueda:
    """Resultado completo de ejecutar un algoritmo sobre una instancia."""

    algoritmo: str
    transiciones: tuple
    rescatadas: tuple
    fallecidas: tuple
    ticks_totales: int
    nodos_explorados: int
    tiempo_segundos: float

    @property
    def acciones(self):
        """Ruta compacta expresada como acciones cardinales."""
        return tuple(transicion.accion for transicion in self.transiciones)


def busqueda_amplitud(instancia):
    """Busca por niveles."""
    inicio_tiempo = perf_counter()
    estado_inicial = instancia.estado_inicial()
    nodo_inicial = NodoBusqueda(
        estado=estado_inicial,
        transiciones=(),
        rescatadas=frozenset(),
        fallecidas=frozenset(),
    )
    frontera = deque([nodo_inicial])
    mejor_rescates_por_estado = {estado_inicial: 0}
    mejor_solucion = None
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
        # Evita devolver un resultado incompleto.
        raise RuntimeError("No se encontró un estado terminal para la instancia.")

    return _crear_resultado("BFS", mejor_solucion, nodos_explorados, inicio_tiempo)


def busqueda_costo_uniforme(instancia):
    """Busca por costo acumulado."""
    inicio_tiempo = perf_counter()
    estado_inicial = instancia.estado_inicial()
    nodo_inicial = NodoBusqueda(
        estado=estado_inicial,
        transiciones=(),
        rescatadas=frozenset(),
        fallecidas=frozenset(),
    )
    consecutivo = 0
    frontera = [(0, consecutivo, nodo_inicial)]
    mejor_rescates_por_estado = {estado_inicial: 0}
    mejor_solucion = None
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
            consecutivo += 1
            heapq.heappush(frontera, (costo + 1, consecutivo, siguiente))

    if mejor_solucion is None:
        raise RuntimeError("No se encontró un estado terminal para la instancia.")
    return _crear_resultado("UCS", mejor_solucion, nodos_explorados, inicio_tiempo)


def busqueda_profundidad_iterativa(instancia):
    """Busca con profundidad iterativa."""
    inicio_tiempo = perf_counter()
    estado_inicial = instancia.estado_inicial()
    nodo_inicial = NodoBusqueda(
        estado=estado_inicial,
        transiciones=(),
        rescatadas=frozenset(),
        fallecidas=frozenset(),
    )
    profundidad_maxima = max(v.ticks_supervivencia for v in instancia.victimas) + 1
    mejor_solucion = None
    nodos_explorados = 0

    for limite in range(profundidad_maxima + 1):
        mejor_rescates_por_estado = {estado_inicial: 0}

        def explorar(nodo, restante):
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


def busqueda_a_estrella(instancia):
    """Busca rutas con A*."""
    inicio_tiempo = perf_counter()
    estado_inicial = instancia.estado_inicial()
    nodo_inicial = NodoBusqueda(
        estado=estado_inicial,
        transiciones=(),
        rescatadas=frozenset(),
        fallecidas=frozenset(),
    )
    consecutivo = 0
    prioridad_inicial = victimas_condenadas(instancia, estado_inicial)
    frontera = [(prioridad_inicial, 0, consecutivo, nodo_inicial)]
    mejores_fallecimientos_por_estado = {estado_inicial: 0}
    mejor_solucion = None
    nodos_explorados = 0

    while frontera:
        prioridad, _, _, nodo = heapq.heappop(frontera)
        fallecimientos = len(nodo.fallecidas)
        if fallecimientos > mejores_fallecimientos_por_estado.get(nodo.estado, fallecimientos):
            continue

        # Descarta rutas que no pueden mejorar la mejor solución.
        if mejor_solucion is not None:
            fallecimientos_mejor = len(mejor_solucion.fallecidas)
            ticks_mejor = mejor_solucion.estado.tick_actual
            if prioridad > fallecimientos_mejor or (
                prioridad == fallecimientos_mejor
                and nodo.estado.tick_actual >= ticks_mejor
            ):
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
            if mejor_solucion is not None:
                fallecimientos_mejor = len(mejor_solucion.fallecidas)
                ticks_mejor = mejor_solucion.estado.tick_actual
                if prioridad > fallecimientos_mejor or (
                    prioridad == fallecimientos_mejor
                    and siguiente.estado.tick_actual >= ticks_mejor
                ):
                    continue
            heapq.heappush(
                frontera,
                (prioridad, siguiente.estado.tick_actual, consecutivo + 1, siguiente),
            )
            consecutivo += 1

    if mejor_solucion is None:
        raise RuntimeError("No se encontró un estado terminal para la instancia.")
    return _crear_resultado("A*", mejor_solucion, nodos_explorados, inicio_tiempo)


def comparar_algoritmos(instancia):
    """Ejecuta los cuatro algoritmos y devuelve resultados comparables."""
    return (
        busqueda_amplitud(instancia),
        busqueda_costo_uniforme(instancia),
        busqueda_profundidad_iterativa(instancia),
        busqueda_a_estrella(instancia),
    )


def _es_mejor_solucion(candidata, actual):
    """Ordena soluciones por rescates máximos y, en empate, menos ticks."""
    if actual is None:
        return True
    return (candidata.cantidad_rescatadas, -candidata.estado.tick_actual) > (
        actual.cantidad_rescatadas,
        -actual.estado.tick_actual,
    )


def _crear_resultado(algoritmo, solucion, nodos_explorados, inicio_tiempo):
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
