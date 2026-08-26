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
        self.root.geometry("920x650")
        self.sistema = SistemaSimulado(ruta_resultados())
        self.codigo_entrada = tk.StringVar()
        self.codigo_salida = tk.StringVar()
        self.placa = tk.StringVar(value="LAB-001")
        self.minutos = tk.IntVar(value=95)
        self.promocion = tk.StringVar()
        self.rfid = tk.StringVar(value="9900001")

        ttk.Label(root, text="SIMULACIÓN SEGURA — SIN GPIO NI IMPRESORAS",
                  font=("Arial", 15, "bold")).pack(pady=8)
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=10)
        self._entrada()
        self._tpv()
        self._salida()
        self._pensionados()
        self.log = tk.Text(root, height=8, state="disabled")
        self.log.pack(fill="x", padx=10, pady=8)

    def registrar(self, texto):
        self.log.configure(state="normal")
        self.log.insert("end", f"[{datetime.now():%H:%M:%S}] {texto}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def campo(self, marco, etiqueta, variable, fila, ancho=55):
        ttk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="e", padx=6, pady=6)
        ttk.Entry(marco, textvariable=variable, width=ancho).grid(row=fila, column=1, sticky="w", padx=6, pady=6)

    def _entrada(self):
        f = ttk.Frame(self.tabs, padding=20)
        self.tabs.add(f, text="Entrada")
        self.campo(f, "Placa:", self.placa, 0, 25)
        self.campo(f, "Minutos de estancia simulada:", self.minutos, 1, 10)
        ttk.Button(f, text="Expedir boleto", command=self.expedir).grid(row=2, column=1, sticky="w", pady=12)
        self.campo(f, "QR generado:", self.codigo_entrada, 3)

    def _tpv(self):
        f = ttk.Frame(self.tabs, padding=20)
        self.tabs.add(f, text="TPV")
        self.campo(f, "QR de entrada:", self.codigo_entrada, 0)
        self.campo(f, "QR promoción (opcional):", self.promocion, 1)
        ttk.Button(f, text="Usar promoción Bodega Aurrera",
                   command=lambda: self.promocion.set(PROMOCION_BA)).grid(row=2, column=1, sticky="w")
        ttk.Button(f, text="Cobrar boleto", command=self.cobrar).grid(row=3, column=1, sticky="w", pady=12)
        self.campo(f, "QR de salida:", self.codigo_salida, 4)

    def _salida(self):
        f = ttk.Frame(self.tabs, padding=20)
        self.tabs.add(f, text="Salida")
        self.campo(f, "QR de salida:", self.codigo_salida, 0)
        ttk.Button(f, text="Validar y abrir barrera", command=self.salir).grid(row=1, column=1, sticky="w", pady=12)
        ttk.Label(f, text="La segunda lectura del mismo QR debe ser rechazada.").grid(row=2, column=1, sticky="w")

    def _pensionados(self):
        f = ttk.Frame(self.tabs, padding=20)
        self.tabs.add(f, text="Pensionados RFID")
        self.campo(f, "Número de tarjeta:", self.rfid, 0, 25)
        ttk.Button(f, text="Preparar tarjeta de prueba", command=self.preparar_rfid).grid(row=1, column=1, sticky="w", pady=8)
        ttk.Button(f, text="Registrar entrada", command=self.entrada_rfid).grid(row=2, column=1, sticky="w", pady=8)
        ttk.Button(f, text="Registrar salida", command=self.salida_rfid).grid(row=3, column=1, sticky="w", pady=8)
        ttk.Label(f, text="Los datos de prueba sólo se permiten en una base terminada en _prueba.").grid(row=4, column=1, sticky="w")

    def ejecutar(self, accion):
        try:
            accion()
        except (ErrorSimulacion, ValueError) as error:
            self.registrar(f"RECHAZADO: {error}")
            messagebox.showwarning("Operación rechazada", str(error))
        except Exception as error:
            self.registrar(f"ERROR TÉCNICO: {error}")
            messagebox.showerror("Error técnico", str(error))

    def expedir(self):
        def accion():
            fecha = datetime.now().replace(microsecond=0) - timedelta(minutes=int(self.minutos.get()))
            r = self.sistema.expedir(self.placa.get(), fecha)
            self.codigo_entrada.set(r.codigo)
            self.promocion.set("")
            self.codigo_salida.set("")
            self.registrar(f"Entrada: folio {r.folio}; boleto {r.boleto}")
            messagebox.showinfo("Entrada autorizada", f"Folio {r.folio}\nQR: {r.qr}")
        self.ejecutar(accion)

    def cobrar(self):
        def accion():
            r = self.sistema.cobrar(self.codigo_entrada.get(), self.promocion.get())
            self.codigo_salida.set(r.codigo_salida)
            self.registrar(f"TPV: folio {r.folio}; {r.tarifa}; ${r.importe}.00")
            messagebox.showinfo("Cobro correcto", f"Importe: ${r.importe}.00\nQR salida: {r.qr}")
        self.ejecutar(accion)

    def salir(self):
        def accion():
            r = self.sistema.salir(self.codigo_salida.get())
            self.registrar(f"Salida folio {r.folio}: {r.mensaje}")
            if r.autorizado:
                messagebox.showinfo("Salida autorizada", r.mensaje)
            else:
                messagebox.showwarning("Salida rechazada", r.mensaje)
        self.ejecutar(accion)

    def entrada_rfid(self):
        self.ejecutar(lambda: self._mostrar_rfid(
            self.sistema.db.entrada_pensionado(int(self.rfid.get()), datetime.now())
        ))

    def preparar_rfid(self):
        self.ejecutar(lambda: self._mostrar_rfid(
            self.sistema.db.preparar_pensionado_prueba(int(self.rfid.get()))
        ))

    def salida_rfid(self):
        self.ejecutar(lambda: self._mostrar_rfid(
            self.sistema.db.salida_pensionado(int(self.rfid.get()), datetime.now())
        ))

    def _mostrar_rfid(self, mensaje):
        self.registrar(mensaje)
        messagebox.showinfo("Pensionado", mensaje)


if __name__ == "__main__":
    ventana = tk.Tk()
    SimuladorGUI(ventana)
    ventana.mainloop()
