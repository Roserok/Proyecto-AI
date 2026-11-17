"""Heurísticas admisibles utilizadas por A*."""

from __future__ import annotations

from src.modelo import Estado, InstanciaRescate, Posicion


def distancia_manhattan(origen: Posicion, destino: Posicion) -> int:
    """Calcula una cota inferior de movimientos entre dos celdas."""
    return abs(origen[0] - destino[0]) + abs(origen[1] - destino[1])


def victimas_condenadas(instancia: InstanciaRescate, estado: Estado) -> int:
    """Cuenta víctimas que no pueden alcanzarse antes de su vencimiento.

    La distancia Manhattan ignora paredes y, por tanto, nunca es mayor que la
    distancia real que debería recorrer el agente. Si esa cota ya supera los
    ticks restantes de una víctima, su fallecimiento es inevitable. Por ello
    este valor es una cota inferior del número de fallecimientos futuros y es
    admisible para A*.
    """
    victimas_por_id = instancia.victimas_por_id
    return sum(
        distancia_manhattan(estado.posicion, victimas_por_id[identificador].posicion)
        > victimas_por_id[identificador].ticks_supervivencia - estado.tick_actual
        for identificador in estado.victimas_vivas
    )
