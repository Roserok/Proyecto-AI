"""Funciones para A*."""

from collections import deque

def distancia_manhattan(origen, destino):
    """Calcula distancia Manhattan."""
    return abs(origen[0] - destino[0]) + abs(origen[1] - destino[1])


def distancia_mas_corta(mapa, origen, destino):
    """Busca la distancia mas corta."""
    if not mapa.es_transitable(origen) or not mapa.es_transitable(destino):
        return None

    frontera = deque([(origen, 0)])
    visitadas = {origen}
    direcciones = ((-1, 0), (1, 0), (0, 1), (0, -1))

    while frontera:
        posicion, distancia = frontera.popleft()
        if posicion == destino:
            return distancia
        for cambio_fila, cambio_columna in direcciones:
            vecina = (posicion[0] + cambio_fila, posicion[1] + cambio_columna)
            if vecina not in visitadas and mapa.es_transitable(vecina):
                visitadas.add(vecina)
                frontera.append((vecina, distancia + 1))
    return None


def victimas_condenadas(instancia, estado):
    """Cuenta victimas sin tiempo."""
    victimas_por_id = instancia.victimas_por_id
    condenadas = 0
    for identificador in estado.victimas_vivas:
        victima = victimas_por_id[identificador]
        distancia = distancia_mas_corta(instancia.mapa, estado.posicion, victima.posicion)
        ticks_restantes = victima.ticks_supervivencia - estado.tick_actual
        if distancia is None or distancia > ticks_restantes:
            condenadas += 1
    return condenadas
