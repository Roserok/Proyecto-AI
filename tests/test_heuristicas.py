"""Pruebas de las cotas usadas por A*."""

import unittest

from src.heuristicas import distancia_manhattan, victimas_condenadas
from src.modelo import Estado, InstanciaRescate, Mapa, Victima


class PruebasDeHeuristicas(unittest.TestCase):
    """Comprueba la detección de víctimas ya imposibles de rescatar."""

    def test_cuenta_una_victima_condenada(self) -> None:
        instancia = InstanciaRescate(
            mapa=Mapa(celdas=(("S", ".", "."),), posicion_inicial=(0, 0), paredes=frozenset()),
            victimas=(Victima("V1", 0, 2, 1),),
        )
        estado = Estado(0, 0, frozenset({"V1"}), 0)

        self.assertEqual(distancia_manhattan((0, 0), (0, 2)), 2)
        self.assertEqual(victimas_condenadas(instancia, estado), 1)
