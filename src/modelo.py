"""Entidades inmutables que describen una instancia del rescate."""

from __future__ import annotations

from dataclasses import dataclass


Posicion = tuple[int, int]


@dataclass(frozen=True, slots=True)
class Victima:
    """Víctima ubicada en una celda con un límite de supervivencia."""

    identificador: str
    fila: int
    columna: int
    ticks_supervivencia: int

    @property
    def posicion(self) -> Posicion:
        """Devuelve la posición de la víctima como ``(fila, columna)``."""
        return (self.fila, self.columna)


@dataclass(frozen=True, slots=True)
class Estado:
    """Nodo del espacio de búsqueda.

    ``victimas_vivas`` contiene únicamente las víctimas que aún no han muerto
    ni han sido rescatadas. Al ser inmutable, el estado puede usarse con
    seguridad en conjuntos de visitados y como clave de diccionarios.
    """

    fila: int
    columna: int
    victimas_vivas: frozenset[str]
    tick_actual: int

    @property
    def posicion(self) -> Posicion:
        """Devuelve la posición actual del agente."""
        return (self.fila, self.columna)


@dataclass(frozen=True, slots=True)
class Mapa:
    """Cuadrícula y datos estáticos del entorno de rescate."""

    celdas: tuple[tuple[str, ...], ...]
    posicion_inicial: Posicion
    paredes: frozenset[Posicion]
    etiquetas_victimas: tuple[tuple[str, Posicion], ...] = ()

    @property
    def filas(self) -> int:
        """Número de filas de la cuadrícula."""
        return len(self.celdas)

    @property
    def columnas(self) -> int:
        """Número de columnas de la cuadrícula."""
        return len(self.celdas[0])

    def esta_dentro(self, posicion: Posicion) -> bool:
        """Indica si una posición pertenece a la cuadrícula."""
        fila, columna = posicion
        return 0 <= fila < self.filas and 0 <= columna < self.columnas

    def es_transitable(self, posicion: Posicion) -> bool:
        """Indica si el agente puede ocupar la posición."""
        return self.esta_dentro(posicion) and posicion not in self.paredes


@dataclass(frozen=True, slots=True)
class InstanciaRescate:
    """Datos completos de una ejecución: mapa y víctimas registradas."""

    mapa: Mapa
    victimas: tuple[Victima, ...]

    @property
    def victimas_por_id(self) -> dict[str, Victima]:
        """Crea un índice para consultar una víctima por su identificador."""
        return {victima.identificador: victima for victima in self.victimas}

    def estado_inicial(self) -> Estado:
        """Construye el estado inicial indicado en la especificación."""
        return Estado(
            fila=self.mapa.posicion_inicial[0],
            columna=self.mapa.posicion_inicial[1],
            victimas_vivas=frozenset(v.identificador for v in self.victimas),
            tick_actual=0,
        )
