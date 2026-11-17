"""Pruebas de las reglas que se ejecutan en cada tick."""

import unittest

from src.modelo import InstanciaRescate, Mapa, Victima
from src.simulacion import aplicar_movimiento, movimientos_posibles


class PruebasDeSimulacion(unittest.TestCase):
    """Verifica movimientos, rescates y fallecimientos."""

    def setUp(self) -> None:
        self.instancia = InstanciaRescate(
            mapa=Mapa(
                celdas=(
                    ("#", "#", "#", "#"),
                    ("#", "S", ".", "#"),
                    ("#", ".", ".", "#"),
                    ("#", "#", "#", "#"),
                ),
                posicion_inicial=(1, 1),
                paredes=frozenset({(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 3), (2, 0), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)}),
            ),
            victimas=(
                Victima("V1", 1, 2, 1),
                Victima("V2", 2, 2, 0),
            ),
        )

    def test_llegar_a_tiempo_rescata_y_las_otras_victimas_expiran(self) -> None:
        transicion = aplicar_movimiento(self.instancia, self.instancia.estado_inicial(), "E")

        self.assertEqual(transicion.estado.tick_actual, 1)
        self.assertEqual(transicion.estado.posicion, (1, 2))
        self.assertEqual(transicion.rescatadas, ("V1",))
        self.assertEqual(transicion.fallecidas, ("V2",))
        self.assertEqual(transicion.estado.victimas_vivas, frozenset())

    def test_solo_ofrece_celdas_transitables(self) -> None:
        acciones = {transicion.accion for transicion in movimientos_posibles(self.instancia, self.instancia.estado_inicial())}

        self.assertEqual(acciones, {"S", "E"})
