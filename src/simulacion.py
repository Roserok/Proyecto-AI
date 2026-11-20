"""Reglas de simulacion."""

from dataclasses import dataclass

from src.modelo import Estado


# Direcciones disponibles.
DIRECCIONES = (
    ("N", -1, 0),
    ("S", 1, 0),
    ("E", 0, 1),
    ("O", 0, -1),
)


@dataclass(frozen=True)
class Transicion:
    """Resultado de un movimiento."""

    accion: str
    estado: Estado
    rescatadas: tuple
    fallecidas: tuple


def movimientos_posibles(instancia, estado):
    """Genera los movimientos posibles."""
    transiciones = []
    for accion, cambio_fila, cambio_columna in DIRECCIONES:
        destino = (estado.fila + cambio_fila, estado.columna + cambio_columna)
        if instancia.mapa.es_transitable(destino):
            transiciones.append(aplicar_movimiento(instancia, estado, accion))
    return tuple(transiciones)


def aplicar_movimiento(instancia, estado, accion):
    """Aplica un movimiento."""
    cambios = {nombre: (fila, columna) for nombre, fila, columna in DIRECCIONES}
    if accion not in cambios:
        raise ValueError(f"Acción no válida: {accion!r}.")

    cambio_fila, cambio_columna = cambios[accion]
    destino = (estado.fila + cambio_fila, estado.columna + cambio_columna)
    if not instancia.mapa.es_transitable(destino):
        raise ValueError(f"La acción {accion!r} lleva a una celda no transitable: {destino}.")

    siguiente_tick = estado.tick_actual + 1
    victimas_por_id = instancia.victimas_por_id
    rescatadas = []
    fallecidas = []
    siguen_vivas = set()

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
