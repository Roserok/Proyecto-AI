"""Lectura y validación de los archivos de entrada del proyecto."""

from __future__ import annotations

from pathlib import Path

from src.modelo import InstanciaRescate, Mapa, Posicion, Victima


class ErrorDeFormato(ValueError):
    """Indica que un archivo de entrada no cumple el formato requerido."""


def cargar_instancia(ruta_mapa: str | Path, ruta_victimas: str | Path) -> InstanciaRescate:
    """Carga ambos archivos y valida que representen una instancia coherente."""
    mapa = cargar_mapa(ruta_mapa)
    victimas = cargar_victimas(ruta_victimas)
    validar_victimas_en_mapa(mapa, victimas)
    return InstanciaRescate(mapa=mapa, victimas=tuple(victimas))


def cargar_mapa(ruta: str | Path) -> Mapa:
    """Lee una cuadrícula rectangular con una única posición inicial ``S``.

    Cada fila puede escribirse carácter por carácter (por ejemplo, ``#S..#``)
    o como celdas separadas por espacios (por ejemplo, ``# S . V1 #``). Las
    etiquetas ``V1``, ``V2``, etc. son opcionales si las posiciones se
    proporcionan exclusivamente en ``victimas.txt``.
    """
    lineas = _lineas_con_contenido(ruta)
    if not lineas:
        raise ErrorDeFormato("El archivo del mapa está vacío.")

    celdas = tuple(_separar_fila(linea) for linea in lineas)
    columnas = len(celdas[0])
    if columnas == 0 or any(len(fila) != columnas for fila in celdas):
        raise ErrorDeFormato("El mapa debe ser una cuadrícula rectangular no vacía.")

    posiciones_inicio: list[Posicion] = []
    paredes: set[Posicion] = set()
    simbolos_permitidos = {"#", ".", "S"}
    etiquetas_victimas: dict[str, Posicion] = {}
    for fila, contenido in enumerate(celdas):
        for columna, celda in enumerate(contenido):
            es_etiqueta_victima = celda.startswith("V") and len(celda) > 1
            if celda not in simbolos_permitidos and not es_etiqueta_victima:
                raise ErrorDeFormato(
                    f"Símbolo no permitido en ({fila}, {columna}): {celda!r}."
                )
            if celda == "S":
                posiciones_inicio.append((fila, columna))
            elif celda == "#":
                paredes.add((fila, columna))
            elif es_etiqueta_victima:
                if celda in etiquetas_victimas:
                    raise ErrorDeFormato(f"La etiqueta de víctima {celda!r} aparece más de una vez.")
                etiquetas_victimas[celda] = (fila, columna)

    if len(posiciones_inicio) != 1:
        raise ErrorDeFormato("El mapa debe contener exactamente una posición inicial 'S'.")

    return Mapa(
        celdas=celdas,
        posicion_inicial=posiciones_inicio[0],
        paredes=frozenset(paredes),
        etiquetas_victimas=tuple(etiquetas_victimas.items()),
    )


def cargar_victimas(ruta: str | Path) -> list[Victima]:
    """Lee víctimas con el formato ``id,fila,columna,ticks_supervivencia``."""
    lineas = _lineas_con_contenido(ruta)
    if not lineas:
        raise ErrorDeFormato("El archivo de víctimas está vacío.")

    encabezado = lineas[0].replace(" ", "").lower()
    esperado = "id,fila,columna,ticks_supervivencia"
    if encabezado != esperado:
        raise ErrorDeFormato(f"Encabezado inválido. Se esperaba: {esperado}.")

    victimas: list[Victima] = []
    identificadores: set[str] = set()
    for numero_linea, linea in enumerate(lineas[1:], start=2):
        partes = [parte.strip() for parte in linea.split(",")]
        if len(partes) != 4 or not all(partes):
            raise ErrorDeFormato(f"Línea {numero_linea}: se esperaban 4 valores separados por coma.")

        identificador, texto_fila, texto_columna, texto_ticks = partes
        if identificador in identificadores:
            raise ErrorDeFormato(f"Línea {numero_linea}: id de víctima repetido: {identificador!r}.")
        try:
            fila, columna, ticks = int(texto_fila), int(texto_columna), int(texto_ticks)
        except ValueError as error:
            raise ErrorDeFormato(
                f"Línea {numero_linea}: fila, columna y ticks deben ser enteros."
            ) from error
        if fila < 0 or columna < 0 or ticks < 0:
            raise ErrorDeFormato(f"Línea {numero_linea}: fila, columna y ticks no pueden ser negativos.")

        identificadores.add(identificador)
        victimas.append(Victima(identificador, fila, columna, ticks))

    if not victimas:
        raise ErrorDeFormato("Debe registrarse al menos una víctima.")
    return victimas


def validar_victimas_en_mapa(mapa: Mapa, victimas: list[Victima]) -> None:
    """Comprueba que cada víctima ocupe una celda libre y una posición única."""
    posiciones: set[Posicion] = set()
    etiquetas = dict(mapa.etiquetas_victimas)
    for victima in victimas:
        if not mapa.esta_dentro(victima.posicion):
            raise ErrorDeFormato(
                f"La víctima {victima.identificador!r} está fuera del mapa: {victima.posicion}."
            )
        if not mapa.es_transitable(victima.posicion):
            raise ErrorDeFormato(
                f"La víctima {victima.identificador!r} está sobre una pared: {victima.posicion}."
            )
        if victima.posicion == mapa.posicion_inicial:
            raise ErrorDeFormato(
                f"La víctima {victima.identificador!r} no puede ocupar la posición inicial S."
            )
        if victima.posicion in posiciones:
            raise ErrorDeFormato(f"Hay más de una víctima en la posición {victima.posicion}.")
        if etiquetas and etiquetas.get(victima.identificador) != victima.posicion:
            raise ErrorDeFormato(
                f"La posición de {victima.identificador!r} no coincide con su etiqueta en el mapa."
            )
        posiciones.add(victima.posicion)

    if etiquetas and set(etiquetas) != {victima.identificador for victima in victimas}:
        raise ErrorDeFormato("Las etiquetas de víctimas del mapa y victimas.txt deben coincidir.")


def _lineas_con_contenido(ruta: str | Path) -> list[str]:
    """Obtiene líneas no vacías y elimina espacios exteriores."""
    try:
        with Path(ruta).open(encoding="utf-8") as archivo:
            return [linea.strip() for linea in archivo if linea.strip()]
    except OSError as error:
        raise ErrorDeFormato(f"No se pudo leer {ruta!s}: {error}") from error


def _separar_fila(linea: str) -> tuple[str, ...]:
    """Acepta filas compactas o celdas separadas por espacios."""
    return tuple(linea.split()) if any(caracter.isspace() for caracter in linea) else tuple(linea)
