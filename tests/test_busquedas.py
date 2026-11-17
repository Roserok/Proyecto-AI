"""Pruebas para los algoritmos de búsqueda."""

import unittest

from src.busquedas import (
    busqueda_a_estrella,
    busqueda_amplitud,
    comparar_algoritmos,
    busqueda_costo_uniforme,
    busqueda_profundidad_iterativa,
)
from src.modelo import InstanciaRescate, Mapa, Victima


class PruebasDeBusquedaAmplitud(unittest.TestCase):
    """Verifica la búsqueda por amplitud sobre una ruta simple."""

    def test_encuentra_la_ruta_que_rescata_a_todas_las_victimas(self) -> None:
        instancia = InstanciaRescate(
            mapa=Mapa(
                celdas=(
                    ("#", "#", "#", "#", "#"),
                    ("#", "S", ".", ".", "#"),
                    ("#", "#", "#", "#", "#"),
                ),
                posicion_inicial=(1, 1),
                paredes=frozenset({(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 4), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)}),
            ),
            victimas=(Victima("V1", 1, 2, 1), Victima("V2", 1, 3, 2)),
        )

        resultado = busqueda_amplitud(instancia)

        self.assertEqual(resultado.acciones, ("E", "E"))
        self.assertEqual(resultado.rescatadas, ("V1", "V2"))
        self.assertEqual(resultado.fallecidas, ())
        self.assertEqual(resultado.ticks_totales, 2)

    def test_ucs_encuentra_la_misma_solucion_optima_en_el_caso_simple(self) -> None:
        resultado = busqueda_costo_uniforme(self._instancia_de_corredor())

        self.assertEqual(resultado.algoritmo, "UCS")
        self.assertEqual(resultado.acciones, ("E", "E"))
        self.assertEqual(resultado.rescatadas, ("V1", "V2"))

    def test_iddfs_encuentra_la_misma_solucion_optima_en_el_caso_simple(self) -> None:
        resultado = busqueda_profundidad_iterativa(self._instancia_de_corredor())

        self.assertEqual(resultado.algoritmo, "IDDFS")
        self.assertEqual(resultado.acciones, ("E", "E"))
        self.assertEqual(resultado.rescatadas, ("V1", "V2"))

    def test_a_estrella_encuentra_la_misma_solucion_optima_en_el_caso_simple(self) -> None:
        resultado = busqueda_a_estrella(self._instancia_de_corredor())

        self.assertEqual(resultado.algoritmo, "A*")
        self.assertEqual(resultado.acciones, ("E", "E"))
        self.assertEqual(resultado.rescatadas, ("V1", "V2"))

    def test_comparacion_ejecuta_los_cuatro_algoritmos(self) -> None:
        resultados = comparar_algoritmos(self._instancia_de_corredor())

        self.assertEqual(tuple(resultado.algoritmo for resultado in resultados), ("BFS", "UCS", "IDDFS", "A*"))

    def _instancia_de_corredor(self) -> InstanciaRescate:
        return InstanciaRescate(
            mapa=Mapa(
                celdas=(
                    ("#", "#", "#", "#", "#"),
                    ("#", "S", ".", ".", "#"),
                    ("#", "#", "#", "#", "#"),
                ),
                posicion_inicial=(1, 1),
                paredes=frozenset({(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 4), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4)}),
            ),
            victimas=(Victima("V1", 1, 2, 1), Victima("V2", 1, 3, 2)),
        )
