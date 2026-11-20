"""Punto de entrada de la aplicación."""

import tkinter as tk

from src.interfaz import AplicacionRescate


def main():
    """Inicializa la ventana principal e inicia el ciclo de eventos."""
    raiz = tk.Tk()
    AplicacionRescate(raiz)
    raiz.minsize(950, 560)
    raiz.mainloop()


if __name__ == "__main__":
    main()
