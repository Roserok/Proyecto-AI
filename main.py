"""Inicio del programa."""

import tkinter as tk

from src.interfaz import AplicacionRescate


def main():
    """Inicia la aplicacion."""
    raiz = tk.Tk()
    AplicacionRescate(raiz)
    raiz.minsize(950, 560)
    raiz.mainloop()


if __name__ == "__main__":
    main()
