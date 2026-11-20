"""Entidades inmutables que describen una instancia del rescate."""

from dataclasses import dataclass


Posicion = tuple


@dataclass(frozen=True)
class Victima:
    """Víctima ubicada en una celda con un límite de supervivencia."""

    identificador: str
    fila: int
    columna: int
    ticks_supervivencia: int

    @property
    def posicion(self):
        """Devuelve la posición de la víctima como ``(fila, columna)``."""
        return (self.fila, self.columna)


@dataclass(frozen=True)
class Estado:
    """Nodo del espacio de búsqueda.

    ``victimas_vivas`` contiene únicamente las víctimas que aún no han muerto
    ni han sido rescatadas. Al ser inmutable, el estado puede usarse con
    seguridad en conjuntos de visitados y como clave de diccionarios.
    """

    fila: int
    columna: int
    victimas_vivas: frozenset
    tick_actual: int

    @property
    def posicion(self):
        """Devuelve la posición actual del agente."""
        return (self.fila, self.columna)


@dataclass(frozen=True)
class Mapa:
    """Cuadrícula y datos estáticos del entorno de rescate."""

    celdas: tuple
    posicion_inicial: Posicion
    paredes: frozenset
    etiquetas_victimas: tuple = ()

    @property
    def filas(self):
        """Número de filas de la cuadrícula."""
        return len(self.celdas)

    @property
    def columnas(self):
        """Número de columnas de la cuadrícula."""
        return len(self.celdas[0])

    def esta_dentro(self, posicion):
        """Indica si una posición pertenece a la cuadrícula."""
        fila, columna = posicion
        return 0 <= fila < self.filas and 0 <= columna < self.columnas

    def es_transitable(self, posicion):
        """Indica si el agente puede ocupar la posición."""
        return self.esta_dentro(posicion) and posicion not in self.paredes


@dataclass(frozen=True)
class InstanciaRescate:
    """Datos completos de una ejecución: mapa y víctimas registradas."""

    mapa: Mapa
    victimas: tuple

    @property
    def victimas_por_id(self):
        """Crea un índice para consultar una víctima por su identificador."""
        return {victima.identificador: victima for victima in self.victimas}

    def estado_inicial(self):
        """Construye el estado inicial indicado en la especificación."""
        return Estado(
            fila=self.mapa.posicion_inicial[0],
            columna=self.mapa.posicion_inicial[1],
            victimas_vivas=frozenset(v.identificador for v in self.victimas),
            tick_actual=0,
        )
