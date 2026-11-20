"""Clases del problema."""

from dataclasses import dataclass


Posicion = tuple


@dataclass(frozen=True)
class Victima:
    """Datos de una victima."""

    identificador: str
    fila: int
    columna: int
    ticks_supervivencia: int

    @property
    def posicion(self):
        """Retorna la posicion."""
        return (self.fila, self.columna)


@dataclass(frozen=True)
class Estado:
    """Estado actual."""

    fila: int
    columna: int
    victimas_vivas: frozenset
    tick_actual: int

    @property
    def posicion(self):
        """Retorna la posicion."""
        return (self.fila, self.columna)


@dataclass(frozen=True)
class Mapa:
    """Datos del mapa."""

    celdas: tuple
    posicion_inicial: Posicion
    paredes: frozenset
    etiquetas_victimas: tuple = ()

    @property
    def filas(self):
        """Cantidad de filas."""
        return len(self.celdas)

    @property
    def columnas(self):
        """Cantidad de columnas."""
        return len(self.celdas[0])

    def esta_dentro(self, posicion):
        """Revisa limites del mapa."""
        fila, columna = posicion
        return 0 <= fila < self.filas and 0 <= columna < self.columnas

    def es_transitable(self, posicion):
        """Revisa si una celda es libre."""
        return self.esta_dentro(posicion) and posicion not in self.paredes


@dataclass(frozen=True)
class InstanciaRescate:
    """Mapa y victimas."""

    mapa: Mapa
    victimas: tuple

    @property
    def victimas_por_id(self):
        """Busca victimas por id."""
        return {victima.identificador: victima for victima in self.victimas}

    def estado_inicial(self):
        """Crea el estado inicial."""
        return Estado(
            fila=self.mapa.posicion_inicial[0],
            columna=self.mapa.posicion_inicial[1],
            victimas_vivas=frozenset(v.identificador for v in self.victimas),
            tick_actual=0,
        )
