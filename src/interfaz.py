"""Interfaz gráfica de escritorio desarrollada exclusivamente con Tkinter."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.busquedas import ResultadoBusqueda, comparar_algoritmos
from src.modelo import Estado, InstanciaRescate
from src.parser import ErrorDeFormato, cargar_instancia


COLORES = {
    "pared": "#374151",
    "libre": "#f8fafc",
    "agente": "#2563eb",
    "viva": "#f59e0b",
    "rescatada": "#16a34a",
    "fallecida": "#dc2626",
    "borde": "#94a3b8",
}


class AplicacionRescate(ttk.Frame):
    """Ventana que permite cargar, resolver y animar una instancia."""

    def __init__(self, raiz: tk.Tk) -> None:
        super().__init__(raiz, padding=12)
        self.raiz = raiz
        self.raiz.title("Agente de Rescate con Víctimas en Riesgo")
        self.grid(sticky="nsew")
        raiz.columnconfigure(0, weight=1)
        raiz.rowconfigure(0, weight=1)

        self.ruta_mapa = tk.StringVar()
        self.ruta_victimas = tk.StringVar()
        self.algoritmo = tk.StringVar(value="BFS")
        self.velocidad_ms = tk.IntVar(value=500)
        self.mensaje = tk.StringVar(value="Carga un mapa y un archivo de víctimas.")
        self.instancia: InstanciaRescate | None = None
        self.resultado_seleccionado: ResultadoBusqueda | None = None
        self.indice_paso = 0
        self.estado_actual: Estado | None = None
        self.rescatadas: set[str] = set()
        self.fallecidas: set[str] = set()

        self._crear_controles()

    def _crear_controles(self) -> None:
        """Construye los paneles de carga, configuración, mapa y resultados."""
        carga = ttk.LabelFrame(self, text="1. Carga de archivos", padding=8)
        carga.grid(row=0, column=0, sticky="ew")
        carga.columnconfigure(1, weight=1)
        ttk.Button(carga, text="Examinar mapa", command=self._elegir_mapa).grid(row=0, column=0, padx=(0, 8), pady=3)
        ttk.Label(carga, textvariable=self.ruta_mapa).grid(row=0, column=1, sticky="w")
        ttk.Button(carga, text="Examinar víctimas", command=self._elegir_victimas).grid(row=1, column=0, padx=(0, 8), pady=3)
        ttk.Label(carga, textvariable=self.ruta_victimas).grid(row=1, column=1, sticky="w")

        configuracion = ttk.LabelFrame(self, text="2. Configuración", padding=8)
        configuracion.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(configuracion, text="Algoritmo para animar:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            configuracion,
            textvariable=self.algoritmo,
            values=("BFS", "UCS", "IDDFS", "A*"),
            state="readonly",
            width=10,
        ).grid(row=0, column=1, padx=8)
        ttk.Label(configuracion, text="Velocidad (ms):").grid(row=0, column=2, padx=(20, 0))
        ttk.Spinbox(configuracion, from_=100, to=2000, increment=100, textvariable=self.velocidad_ms, width=7).grid(row=0, column=3, padx=8)
        ttk.Button(configuracion, text="Iniciar Rescate", command=self.iniciar_rescate).grid(row=0, column=4, padx=(20, 0))

        contenido = ttk.Frame(self)
        contenido.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        contenido.columnconfigure(0, weight=1)
        contenido.columnconfigure(1, weight=1)
        contenido.rowconfigure(0, weight=1)

        mapa_panel = ttk.LabelFrame(contenido, text="3. Simulación", padding=8)
        mapa_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        mapa_panel.rowconfigure(0, weight=1)
        mapa_panel.columnconfigure(0, weight=1)
        self.lienzo = tk.Canvas(mapa_panel, width=460, height=420, background="white", highlightthickness=0)
        self.lienzo.grid(row=0, column=0, sticky="nsew")
        self.lienzo.bind("<Configure>", lambda _evento: self._dibujar_mapa())

        resultados = ttk.LabelFrame(contenido, text="4. Resultados y comparación", padding=8)
        resultados.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        resultados.columnconfigure(0, weight=1)
        self.resumen = tk.StringVar(value="Aún no hay simulación ejecutada.")
        ttk.Label(resultados, textvariable=self.resumen, justify="left").grid(row=0, column=0, sticky="w")
        columnas = ("algoritmo", "nodos", "tiempo", "rescatadas", "fallecidas")
        self.tabla = ttk.Treeview(resultados, columns=columnas, show="headings", height=7)
        encabezados = {
            "algoritmo": "Algoritmo",
            "nodos": "Nodos",
            "tiempo": "Tiempo (s)",
            "rescatadas": "Rescatadas",
            "fallecidas": "Fallecidas",
        }
        for columna in columnas:
            self.tabla.heading(columna, text=encabezados[columna])
            self.tabla.column(columna, anchor="center", width=95)
        self.tabla.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        ttk.Label(self, textvariable=self.mensaje).grid(row=3, column=0, sticky="w", pady=(8, 0))

    def _elegir_mapa(self) -> None:
        ruta = filedialog.askopenfilename(title="Selecciona mapa.txt", filetypes=(("Texto", "*.txt"), ("Todos", "*.*")))
        if ruta:
            self.ruta_mapa.set(ruta)
            self._cargar_si_es_posible()

    def _elegir_victimas(self) -> None:
        ruta = filedialog.askopenfilename(title="Selecciona victimas.txt", filetypes=(("Texto", "*.txt"), ("Todos", "*.*")))
        if ruta:
            self.ruta_victimas.set(ruta)
            self._cargar_si_es_posible()

    def _cargar_si_es_posible(self) -> None:
        if not self.ruta_mapa.get() or not self.ruta_victimas.get():
            return
        try:
            self.instancia = cargar_instancia(self.ruta_mapa.get(), self.ruta_victimas.get())
        except ErrorDeFormato as error:
            self.instancia = None
            self.mensaje.set("Error de lectura: revisa los archivos seleccionados.")
            messagebox.showerror("Archivo inválido", str(error), parent=self.raiz)
            return
        self.mensaje.set("Archivos leídos correctamente. Selecciona un algoritmo e inicia el rescate.")
        self._reiniciar_animacion()
        self._dibujar_mapa()

    def iniciar_rescate(self) -> None:
        """Ejecuta la comparación y prepara la animación del algoritmo elegido."""
        if self.instancia is None:
            self._cargar_si_es_posible()
        if self.instancia is None:
            messagebox.showwarning("Faltan archivos", "Selecciona un mapa y un archivo de víctimas válidos.", parent=self.raiz)
            return
        try:
            resultados = comparar_algoritmos(self.instancia)
        except (RuntimeError, ValueError) as error:
            messagebox.showerror("No fue posible resolver", str(error), parent=self.raiz)
            return

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for resultado in resultados:
            self.tabla.insert(
                "",
                "end",
                values=(
                    resultado.algoritmo,
                    resultado.nodos_explorados,
                    f"{resultado.tiempo_segundos:.5f}",
                    len(resultado.rescatadas),
                    len(resultado.fallecidas),
                ),
            )
        self.resultado_seleccionado = next(resultado for resultado in resultados if resultado.algoritmo == self.algoritmo.get())
        self._reiniciar_animacion()
        self.mensaje.set(f"Simulando la ruta calculada por {self.algoritmo.get()}.")
        self._animar_siguiente()

    def _reiniciar_animacion(self) -> None:
        if self.instancia is None:
            return
        self.indice_paso = 0
        self.estado_actual = self.instancia.estado_inicial()
        self.rescatadas = set()
        self.fallecidas = set()
        self.resumen.set("Simulación preparada. Tick actual: 0")

    def _animar_siguiente(self) -> None:
        if self.instancia is None or self.resultado_seleccionado is None or self.estado_actual is None:
            return
        self._dibujar_mapa()
        if self.indice_paso >= len(self.resultado_seleccionado.transiciones):
            self.resumen.set(
                "RESULTADO DE LA SIMULACIÓN\n"
                f"Víctimas totales: {len(self.instancia.victimas)}\n"
                f"Víctimas rescatadas: {len(self.rescatadas)}\n"
                f"Víctimas fallecidas: {len(self.fallecidas)}\n"
                f"Ticks totales: {self.estado_actual.tick_actual}"
            )
            self.mensaje.set("Simulación finalizada.")
            return

        transicion = self.resultado_seleccionado.transiciones[self.indice_paso]
        self.rescatadas.update(transicion.rescatadas)
        self.fallecidas.update(transicion.fallecidas)
        self.estado_actual = transicion.estado
        self.indice_paso += 1
        self.resumen.set(
            f"Tick actual: {self.estado_actual.tick_actual}\n"
            f"Rescatadas: {len(self.rescatadas)} | Fallecidas: {len(self.fallecidas)}"
        )
        self.raiz.after(max(100, self.velocidad_ms.get()), self._animar_siguiente)

    def _dibujar_mapa(self) -> None:
        if self.instancia is None or self.estado_actual is None:
            return
        mapa = self.instancia.mapa
        ancho = max(1, int(self.lienzo.winfo_width() / mapa.columnas))
        alto = max(1, int(self.lienzo.winfo_height() / mapa.filas))
        self.lienzo.delete("all")
        victimas = self.instancia.victimas_por_id
        for fila in range(mapa.filas):
            for columna in range(mapa.columnas):
                posicion = (fila, columna)
                x1, y1 = columna * ancho, fila * alto
                x2, y2 = x1 + ancho, y1 + alto
                color = COLORES["pared"] if posicion in mapa.paredes else COLORES["libre"]
                self.lienzo.create_rectangle(x1, y1, x2, y2, fill=color, outline=COLORES["borde"])

        for identificador, victima in victimas.items():
            fila, columna = victima.posicion
            x1, y1 = columna * ancho + 4, fila * alto + 4
            x2, y2 = (columna + 1) * ancho - 4, (fila + 1) * alto - 4
            if identificador in self.rescatadas:
                color, texto = COLORES["rescatada"], f"{identificador}\nOK"
            elif identificador in self.fallecidas:
                color, texto = COLORES["fallecida"], f"{identificador}\nX"
            else:
                restantes = max(0, victima.ticks_supervivencia - self.estado_actual.tick_actual)
                color, texto = COLORES["viva"], f"{identificador}\n{restantes}"
            self.lienzo.create_oval(x1, y1, x2, y2, fill=color, outline="")
            self.lienzo.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=texto, fill="white", font=("Segoe UI", 9, "bold"))

        fila, columna = self.estado_actual.posicion
        x1, y1 = columna * ancho + ancho * 0.27, fila * alto + alto * 0.27
        x2, y2 = columna * ancho + ancho * 0.73, fila * alto + alto * 0.73
        self.lienzo.create_oval(x1, y1, x2, y2, fill=COLORES["agente"], outline="white", width=2)
        self.lienzo.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="A", fill="white", font=("Segoe UI", 9, "bold"))
