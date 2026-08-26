#!/usr/bin/env python3
"""Interfaz gráfica para probar el flujo completo sin hardware."""

import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

from nucleo import ErrorSimulacion, PROMOCION_BA, SistemaSimulado, ruta_resultados


class SimuladorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Laboratorio del estacionamiento")
        self.root.geometry("1100x760")
        self.sistema = SistemaSimulado(ruta_resultados())

        # Cada punto tiene su propia captura. Así un boleto nuevo no reemplaza
        # el que el operador estaba procesando en TPV o en Salida.
        self.entrada_codigo_generado = tk.StringVar()
        self.tpv_codigo_entrada = tk.StringVar()
        self.tpv_ultimo_codigo_salida = tk.StringVar()
        self.salida_codigo = tk.StringVar()
        self.placa = tk.StringVar(value="LAB-001")
        self.minutos = tk.IntVar(value=95)
        self.promocion = tk.StringVar()
        self.rfid = tk.StringVar(value="9900001")
        self.codigos_cobro = {}
        self.codigos_salida = {}

        ttk.Label(
            root, text="SIMULACIÓN SEGURA — SIN GPIO NI IMPRESORAS",
            font=("Arial", 15, "bold"),
        ).pack(pady=8)
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=10)
        self._entrada()
        self._tpv()
        self._salida()
        self._pensionados()
        self.log = tk.Text(root, height=8, state="disabled")
        self.log.pack(fill="x", padx=10, pady=8)
        self.root.after(100, self.refrescar_listas)

    def registrar(self, texto):
        self.log.configure(state="normal")
        self.log.insert("end", f"[{datetime.now():%H:%M:%S}] {texto}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def campo(self, marco, etiqueta, variable, fila, ancho=55, solo_lectura=False):
        ttk.Label(marco, text=etiqueta).grid(
            row=fila, column=0, sticky="e", padx=6, pady=6
        )
        entrada = ttk.Entry(
            marco, textvariable=variable, width=ancho,
            state="readonly" if solo_lectura else "normal",
        )
        entrada.grid(row=fila, column=1, sticky="ew", padx=6, pady=6)
        return entrada

    def _entrada(self):
        f = ttk.Frame(self.tabs, padding=20)
        f.columnconfigure(1, weight=1)
        self.tabs.add(f, text="Entrada")
        self.campo(f, "Placa:", self.placa, 0, 25)
        self.campo(f, "Minutos de estancia simulada:", self.minutos, 1, 10)
        ttk.Button(f, text="Expedir boleto", command=self.expedir).grid(
            row=2, column=1, sticky="w", pady=12
        )
        self.campo(
            f, "Último QR generado:", self.entrada_codigo_generado, 3,
            solo_lectura=True,
        )
        ttk.Label(
            f,
            text=("Cada expedición se conserva en MariaDB y aparecerá en la lista "
                  "de pendientes de la TPV."),
        ).grid(row=4, column=1, sticky="w", pady=8)

    def _tpv(self):
        f = ttk.Frame(self.tabs, padding=14)
        f.columnconfigure(1, weight=1)
        f.rowconfigure(7, weight=1)
        self.tabs.add(f, text="TPV")
        self.campo_tpv = self.campo(f, "QR de entrada:", self.tpv_codigo_entrada, 0)
        self.campo(f, "QR promoción (opcional):", self.promocion, 1)
        ttk.Button(
            f, text="Usar promoción Bodega Aurrera",
            command=lambda: self.promocion.set(PROMOCION_BA),
        ).grid(row=2, column=1, sticky="w")
        ttk.Button(f, text="Cobrar boleto", command=self.cobrar).grid(
            row=3, column=1, sticky="w", pady=10
        )
        self.campo(
            f, "Último QR de salida:", self.tpv_ultimo_codigo_salida, 4,
            solo_lectura=True,
        )
        botones = ttk.Frame(f)
        botones.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(8, 3))
        ttk.Label(botones, text="Boletos pendientes de cobro").pack(side="left")
        ttk.Button(
            botones, text="Actualizar", command=self.refrescar_listas
        ).pack(side="right")
        ttk.Button(
            botones, text="Cargar seleccionado", command=self.cargar_cobro
        ).pack(side="right", padx=8)
        self.tabla_cobro = ttk.Treeview(
            f, columns=("folio", "entrada", "placa"), show="headings", height=9
        )
        for columna, titulo, ancho in (
            ("folio", "Folio", 90), ("entrada", "Entrada", 190),
            ("placa", "Placa", 180),
        ):
            self.tabla_cobro.heading(columna, text=titulo)
            self.tabla_cobro.column(columna, width=ancho, anchor="center")
        self.tabla_cobro.grid(row=7, column=0, columnspan=2, sticky="nsew")
        self.tabla_cobro.bind("<Double-1>", lambda _evento: self.cargar_cobro())

    def _salida(self):
        f = ttk.Frame(self.tabs, padding=14)
        f.columnconfigure(1, weight=1)
        f.rowconfigure(4, weight=1)
        self.tabs.add(f, text="Salida")
        self.campo_salida = self.campo(f, "QR de salida:", self.salida_codigo, 0)
        ttk.Button(f, text="Validar y abrir barrera", command=self.salir).grid(
            row=1, column=1, sticky="w", pady=10
        )
        botones = ttk.Frame(f)
        botones.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 3))
        ttk.Label(botones, text="Boletos pagados pendientes de salida").pack(side="left")
        ttk.Button(
            botones, text="Actualizar", command=self.refrescar_listas
        ).pack(side="right")
        ttk.Button(
            botones, text="Cargar seleccionado", command=self.cargar_salida
        ).pack(side="right", padx=8)
        self.tabla_salida = ttk.Treeview(
            f, columns=("folio", "pago", "tolerancia", "placa"),
            show="headings", height=11,
        )
        for columna, titulo, ancho in (
            ("folio", "Folio", 80), ("pago", "Hora de pago", 180),
            ("tolerancia", "Tolerancia", 110), ("placa", "Placa", 160),
        ):
            self.tabla_salida.heading(columna, text=titulo)
            self.tabla_salida.column(columna, width=ancho, anchor="center")
        self.tabla_salida.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.tabla_salida.bind("<Double-1>", lambda _evento: self.cargar_salida())

    def _pensionados(self):
        f = ttk.Frame(self.tabs, padding=14)
        f.columnconfigure(1, weight=1)
        f.rowconfigure(6, weight=1)
        self.tabs.add(f, text="Pensionados RFID")
        self.campo_rfid = self.campo(f, "Número de tarjeta:", self.rfid, 0, 25)
        ttk.Button(
            f, text="Preparar tarjeta de prueba", command=self.preparar_rfid
        ).grid(row=1, column=1, sticky="w", pady=5)
        ttk.Button(f, text="Registrar entrada", command=self.entrada_rfid).grid(
            row=2, column=1, sticky="w", pady=5
        )
        ttk.Button(f, text="Registrar salida", command=self.salida_rfid).grid(
            row=3, column=1, sticky="w", pady=5
        )
        ttk.Label(
            f, text="Seleccione cualquier tarjeta; cada estado se conserva en MariaDB."
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=7)
        self.tabla_pensionados = ttk.Treeview(
            f, columns=("tarjeta", "nombre", "estado", "vigencia"),
            show="headings", height=9,
        )
        for columna, titulo, ancho in (
            ("tarjeta", "Tarjeta", 120), ("nombre", "Nombre", 230),
            ("estado", "Estado", 110), ("vigencia", "Vigencia", 180),
        ):
            self.tabla_pensionados.heading(columna, text=titulo)
            self.tabla_pensionados.column(columna, width=ancho, anchor="center")
        self.tabla_pensionados.grid(row=6, column=0, columnspan=2, sticky="nsew")
        self.tabla_pensionados.bind(
            "<Double-1>", lambda _evento: self.cargar_pensionado()
        )

    def ejecutar(self, accion):
        try:
            accion()
        except (ErrorSimulacion, ValueError) as error:
            self.registrar(f"RECHAZADO: {error}")
            messagebox.showwarning("Operación rechazada", str(error))
        except Exception as error:
            self.registrar(f"ERROR TÉCNICO: {error}")
            messagebox.showerror("Error técnico", str(error))

    def refrescar_listas(self):
        self.ejecutar(self._refrescar_listas)

    def _refrescar_listas(self):
        self.codigos_cobro.clear()
        self.tabla_cobro.delete(*self.tabla_cobro.get_children())
        for fila in self.sistema.db.listar_pendientes_cobro():
            folio = int(fila["id"])
            self.codigos_cobro[str(folio)] = fila["codigo_entrada"]
            self.tabla_cobro.insert(
                "", "end", iid=f"cobro-{folio}",
                values=(folio, fila["Entrada"].strftime("%Y-%m-%d %H:%M:%S"), fila["Placas"]),
            )

        self.codigos_salida.clear()
        self.tabla_salida.delete(*self.tabla_salida.get_children())
        for fila in self.sistema.db.listar_pendientes_salida():
            folio = int(fila["id"])
            self.codigos_salida[str(folio)] = fila["codigo_salida"]
            self.tabla_salida.insert(
                "", "end", iid=f"salida-{folio}",
                values=(folio, fila["Salida"].strftime("%Y-%m-%d %H:%M:%S"),
                        fila["estado_tolerancia"], fila["Placas"]),
            )

        self.tabla_pensionados.delete(*self.tabla_pensionados.get_children())
        for fila in self.sistema.db.listar_pensionados():
            tarjeta = int(fila["Num_tarjeta"])
            vigencia = fila["Fecha_vigencia"]
            vigencia_texto = vigencia.strftime("%Y-%m-%d %H:%M:%S") if vigencia else ""
            self.tabla_pensionados.insert(
                "", "end", iid=f"rfid-{tarjeta}",
                values=(tarjeta, fila["Nom_cliente"], fila["Estatus"], vigencia_texto),
            )

    @staticmethod
    def _folio_seleccionado(tabla, prefijo):
        seleccion = tabla.selection()
        if not seleccion:
            raise ErrorSimulacion("Seleccione primero un registro de la lista.")
        return seleccion[0].removeprefix(prefijo)

    def cargar_cobro(self):
        def accion():
            folio = self._folio_seleccionado(self.tabla_cobro, "cobro-")
            self.tpv_codigo_entrada.set(self.codigos_cobro[folio])
            self.campo_tpv.focus_set()
        self.ejecutar(accion)

    def cargar_salida(self):
        def accion():
            folio = self._folio_seleccionado(self.tabla_salida, "salida-")
            self.salida_codigo.set(self.codigos_salida[folio])
            self.campo_salida.focus_set()
        self.ejecutar(accion)

    def cargar_pensionado(self):
        def accion():
            tarjeta = self._folio_seleccionado(self.tabla_pensionados, "rfid-")
            self.rfid.set(tarjeta)
            self.campo_rfid.focus_set()
        self.ejecutar(accion)

    def expedir(self):
        def accion():
            fecha = datetime.now().replace(microsecond=0) - timedelta(
                minutes=int(self.minutos.get())
            )
            r = self.sistema.expedir(self.placa.get(), fecha)
            self.entrada_codigo_generado.set(r.codigo)
            self.registrar(
                f"Entrada folio {r.folio}: ABRE BARRERA (simulada) durante 3 segundos; "
                f"boleto {r.boleto}"
            )
            self._refrescar_listas()
            messagebox.showinfo(
                "Entrada autorizada",
                f"Folio {r.folio}\nABRE BARRERA (simulada) 3 segundos\nQR: {r.qr}",
            )
        self.ejecutar(accion)

    def cobrar(self):
        def accion():
            try:
                r = self.sistema.cobrar(
                    self.tpv_codigo_entrada.get(), self.promocion.get()
                )
                self.tpv_ultimo_codigo_salida.set(r.codigo_salida)
                self.salida_codigo.set(r.codigo_salida)
                self.registrar(f"TPV folio {r.folio}: {r.tarifa}; ${r.importe}.00")
                self._refrescar_listas()
                messagebox.showinfo(
                    "Cobro correcto", f"Importe: ${r.importe}.00\nQR salida: {r.qr}"
                )
            finally:
                self.tpv_codigo_entrada.set("")
                self.promocion.set("")
                self.root.after_idle(self.campo_tpv.focus_set)
        self.ejecutar(accion)

    def salir(self):
        def accion():
            try:
                r = self.sistema.salir(self.salida_codigo.get())
                self.registrar(f"Salida folio {r.folio}: {r.mensaje}")
                self._refrescar_listas()
                if r.autorizado:
                    messagebox.showinfo("Salida autorizada", r.mensaje)
                else:
                    messagebox.showwarning("Salida rechazada", r.mensaje)
            finally:
                self.salida_codigo.set("")
                self.root.after_idle(self.campo_salida.focus_set)
        self.ejecutar(accion)

    def entrada_rfid(self):
        self._operacion_rfid("entrada")

    def preparar_rfid(self):
        self._operacion_rfid("preparar")

    def salida_rfid(self):
        self._operacion_rfid("salida")

    def _operacion_rfid(self, tipo):
        def accion():
            try:
                tarjeta = int(self.rfid.get())
                if tipo == "preparar":
                    mensaje = self.sistema.db.preparar_pensionado_prueba(tarjeta)
                elif tipo == "entrada":
                    mensaje = self.sistema.db.entrada_pensionado(tarjeta, datetime.now())
                else:
                    mensaje = self.sistema.db.salida_pensionado(tarjeta, datetime.now())
                self._mostrar_rfid(mensaje)
                self._refrescar_listas()
            finally:
                if tipo != "preparar":
                    self.rfid.set("")
                    self.root.after_idle(self.campo_rfid.focus_set)
        self.ejecutar(accion)

    def _mostrar_rfid(self, mensaje):
        self.registrar(mensaje)
        messagebox.showinfo("Pensionado", mensaje)


if __name__ == "__main__":
    ventana = tk.Tk()
    SimuladorGUI(ventana)
    ventana.mainloop()
