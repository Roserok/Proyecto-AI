"""Pruebas de lectura y validación de los archivos de entrada."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.parser import ErrorDeFormato, cargar_instancia


class PruebasDelParser(unittest.TestCase):
    """Verifica casos representativos de los dos archivos de entrada."""

    def test_carga_una_instancia_valida(self) -> None:
        with TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            (ruta / "mapa.txt").write_text("#####\n#S..#\n#...#\n#####\n", encoding="utf-8")
            (ruta / "victimas.txt").write_text(
                "id,fila,columna,ticks_supervivencia\nV1,1,3,4\n",
                encoding="utf-8",
            )

            instancia = cargar_instancia(ruta / "mapa.txt", ruta / "victimas.txt")

        self.assertEqual(instancia.mapa.posicion_inicial, (1, 1))
        self.assertEqual(instancia.estado_inicial().victimas_vivas, frozenset({"V1"}))

    def test_rechaza_victima_sobre_una_pared(self) -> None:
        with TemporaryDirectory() as directorio:
            ruta = Path(directorio)
            (ruta / "mapa.txt").write_text("#####\n#S..#\n#####\n", encoding="utf-8")
            (ruta / "victimas.txt").write_text(
                "id,fila,columna,ticks_supervivencia\nV1,0,0,4\n",
                encoding="utf-8",
            )

            with self.assertRaises(ErrorDeFormato):
                cargar_instancia(ruta / "mapa.txt", ruta / "victimas.txt")
