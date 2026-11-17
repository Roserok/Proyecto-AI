"""Reglas de transición y utilidades para la simulación del rescate."""

from __future__ import annotations

from dataclasses import dataclass

from src.modelo import Estado, InstanciaRescate, Posicion


# La fila aumenta hacia el sur y la columna aumenta hacia el este.
DIRECCIONES: tuple[tuple[str, int, int], ...] = (
    ("N", -1, 0),
    ("S", 1, 0),
    ("E", 0, 1),
    ("O", 0, -1),
)


@dataclass(frozen=True, slots=True)
class Transicion:
    """Resultado de efectuar un movimiento válido del agente.

    Los identificadores de ``rescatadas`` y ``fallecidas`` corresponden solo
    al tick que acaba de transcurrir. El historial completo se conservará en
    la ruta que produzcan los algoritmos de búsqueda.
    """

    accion: str
    estado: Estado
    rescatadas: tuple[str, ...]
    fallecidas: tuple[str, ...]


def movimientos_posibles(instancia: InstanciaRescate, estado: Estado) -> tuple[Transicion, ...]:
    """Genera todas las transiciones permitidas desde un estado.

    No se incluye una acción de espera porque la guía exige que el agente se
    mueva en cada turno.
    """
    transiciones: list[Transicion] = []
    for accion, cambio_fila, cambio_columna in DIRECCIONES:
        destino = (estado.fila + cambio_fila, estado.columna + cambio_columna)
        if instancia.mapa.es_transitable(destino):
            transiciones.append(aplicar_movimiento(instancia, estado, accion))
    return tuple(transiciones)


def aplicar_movimiento(
    instancia: InstanciaRescate, estado: Estado, accion: str
) -> Transicion:
    """Aplica una acción cardinal y resuelve rescates y muertes del nuevo tick.

    Una víctima se rescata al llegar si ``tick_actual <= ticks_supervivencia``.
    Si no se rescata y el tick ya es mayor que su límite, fallece.
    """
    cambios = {nombre: (fila, columna) for nombre, fila, columna in DIRECCIONES}
    if accion not in cambios:
        raise ValueError(f"Acción no válida: {accion!r}.")

    cambio_fila, cambio_columna = cambios[accion]
    destino: Posicion = (estado.fila + cambio_fila, estado.columna + cambio_columna)
    if not instancia.mapa.es_transitable(destino):
        raise ValueError(f"La acción {accion!r} lleva a una celda no transitable: {destino}.")

    siguiente_tick = estado.tick_actual + 1
    victimas_por_id = instancia.victimas_por_id
    rescatadas: list[str] = []
    fallecidas: list[str] = []
    siguen_vivas: set[str] = set()

    for identificador in estado.victimas_vivas:
        victima = victimas_por_id[identificador]
        if victima.posicion == destino and siguiente_tick <= victima.ticks_supervivencia:
            rescatadas.append(identificador)
        elif siguiente_tick > victima.ticks_supervivencia:
            fallecidas.append(identificador)
        else:
            siguen_vivas.add(identificador)

    estado_siguiente = Estado(
        fila=destino[0],
        columna=destino[1],
        victimas_vivas=frozenset(siguen_vivas),
        tick_actual=siguiente_tick,
    )
    return Transicion(
        accion=accion,
        estado=estado_siguiente,
        rescatadas=tuple(sorted(rescatadas)),
        fallecidas=tuple(sorted(fallecidas)),
    )
