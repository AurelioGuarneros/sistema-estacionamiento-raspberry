"""Configuracion visual y operativa de la TPV.

El archivo se guarda junto al programa para que la pantalla de configuracion
pueda cambiar tarifas e impresora sin editar codigo ni archivos del sistema.
"""

import json
import os
import shutil
from copy import deepcopy
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb
from tkinter import ttk

from PIL import Image, ImageTk


AZUL = "#17365d"
AZUL_CLARO = "#d9eaf7"
FONDO = "#f4f6f8"
TEXTO = "#17202a"
ROJO = "#b3261e"
VERDE = "#2e7d32"

RUTA_CONFIG = Path(__file__).with_name("configuracion_tpv.json")
RUTA_RECURSOS = Path(__file__).with_name("recursos_configuracion")


def _tarifa_actual():
    """Replica como valores iniciales la tarifa que ya usa la TPV."""
    tabla = {}
    for hora in range(25):
        exacta = 10 if hora == 0 else min(hora, 24) * 10
        siguiente = min(max(hora + 1, 1), 24) * 10
        tabla[str(hora)] = {
            "hora": exacta,
            "1": siguiente,
            "2": siguiente,
            "3": siguiente,
        }
    return tabla


CONFIG_PREDETERMINADA = {
    "general": {
        "nombre_estacionamiento": "Hidalgo 401",
        "correo": "",
        "cantidad_cajones": 0,
        "nombre_punto": "TPV",
        "pantalla_completa": True,
        "mostrar_reloj": False,
        "placa_obligatoria": False,
    },
    "empresa": {
        "nombre": "", "rfc": "", "calle_numero": "", "colonia": "",
        "codigo_postal": "", "alcaldia_municipio": "", "estado": "",
    },
    "sucursal": {
        "calle_numero": "", "colonia": "", "codigo_postal": "", "estado": "",
    },
    "facturacion": {"correo": "", "telefono": ""},
    "imagenes": {"logo": "", "vehiculo": ""},
    "interface": {
        "tema": "Azul",
        "tamano_texto": "Normal",
    },
    "impresora": {
        "modelo": "Epson USB",
        "modo": "usb",
        "dispositivo": "/dev/usb/lp0",
        "vendor_id": "04b8",
        "product_id": "0e15",
    },
    "tarifa": {
        "tipo": "avanzada",
        "boleto_perdido": 250,
        "simple": {
            "inicio_cobro_fraccion": 1,
            "primer_cuarto": 10,
            "segundo_cuarto": 10,
            "tercer_cuarto": 10,
            "hora": 10,
        },
        "personalizada": _tarifa_actual(),
    },
    "funcionamiento": {
        "enviar_cortes": True,
        "confirmar_cierre": True,
    },
}


def _combinar(base, guardada):
    resultado = deepcopy(base)
    for clave, valor in guardada.items():
        if isinstance(valor, dict) and isinstance(resultado.get(clave), dict):
            resultado[clave] = _combinar(resultado[clave], valor)
        else:
            resultado[clave] = valor
    return resultado


def cargar_configuracion():
    try:
        with RUTA_CONFIG.open("r", encoding="utf-8") as archivo:
            return _combinar(CONFIG_PREDETERMINADA, json.load(archivo))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        configuracion = deepcopy(CONFIG_PREDETERMINADA)
        modo = os.environ.get("ESTACIONAMIENTO_PRINTER_MODE", "usb").lower()
        configuracion["impresora"].update({
            "modelo": "POS80 0416:5011" if modo == "lp" else "Epson USB",
            "modo": modo,
            "dispositivo": os.environ.get(
                "ESTACIONAMIENTO_PRINTER_DEVICE", "/dev/usb/lp0"
            ),
            "vendor_id": os.environ.get(
                "ESTACIONAMIENTO_PRINTER_VENDOR_ID", "04b8"
            ),
            "product_id": os.environ.get(
                "ESTACIONAMIENTO_PRINTER_PRODUCT_ID", "0e15"
            ),
        })
        return configuracion


def guardar_configuracion(configuracion):
    temporal = RUTA_CONFIG.with_suffix(".json.tmp")
    with temporal.open("w", encoding="utf-8") as archivo:
        json.dump(configuracion, archivo, ensure_ascii=False, indent=2)
        archivo.flush()
        os.fsync(archivo.fileno())
    temporal.replace(RUTA_CONFIG)


def configuracion_impresora():
    """Devuelve la seleccion de pantalla o, si no existe, la del entorno."""
    if RUTA_CONFIG.exists():
        return cargar_configuracion()["impresora"]
    modo = os.environ.get("ESTACIONAMIENTO_PRINTER_MODE", "usb").lower()
    return {
        "modelo": "POS80 0416:5011" if modo == "lp" else "Epson USB",
        "modo": modo,
        "dispositivo": os.environ.get(
            "ESTACIONAMIENTO_PRINTER_DEVICE", "/dev/usb/lp0"
        ),
        "vendor_id": os.environ.get("ESTACIONAMIENTO_PRINTER_VENDOR_ID", "04b8"),
        "product_id": os.environ.get("ESTACIONAMIENTO_PRINTER_PRODUCT_ID", "0e15"),
    }


class VentanaConfiguracion(tk.Toplevel):
    """Panel moderno que conserva las secciones del sistema anterior."""

    def __init__(self, master, al_guardar=None):
        super().__init__(master)
        self.al_guardar = al_guardar
        self.configuracion = cargar_configuracion()
        self.title("Panel de configuracion")
        self.configure(bg=FONDO)
        self.geometry("1180x760")
        self.minsize(960, 650)
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._crear_variables()
        self._construir()

    def _crear_variables(self):
        general = self.configuracion["general"]
        impresora = self.configuracion["impresora"]
        tarifa = self.configuracion["tarifa"]
        funcionamiento = self.configuracion["funcionamiento"]
        self.nombre = tk.StringVar(value=general["nombre_estacionamiento"])
        self.correo = tk.StringVar(value=general.get("correo", ""))
        self.cantidad_cajones = tk.StringVar(value=str(general.get("cantidad_cajones", 0)))
        self.nombre_punto = tk.StringVar(value=general.get("nombre_punto", "TPV"))
        self.pantalla_completa = tk.BooleanVar(value=general["pantalla_completa"])
        self.mostrar_reloj = tk.BooleanVar(value=general["mostrar_reloj"])
        self.placa_obligatoria = tk.BooleanVar(value=general["placa_obligatoria"])
        self.modelo_impresora = tk.StringVar(value=impresora["modelo"])
        self.vendor_id = tk.StringVar(value=impresora["vendor_id"])
        self.product_id = tk.StringVar(value=impresora["product_id"])
        self.dispositivo = tk.StringVar(value=impresora["dispositivo"])
        self.tipo_tarifa = tk.StringVar(value=tarifa["tipo"])
        self.boleto_perdido = tk.StringVar(value=str(tarifa["boleto_perdido"]))
        self.enviar_cortes = tk.BooleanVar(value=funcionamiento["enviar_cortes"])
        self.confirmar_cierre = tk.BooleanVar(value=funcionamiento["confirmar_cierre"])
        empresa = self.configuracion["empresa"]
        sucursal = self.configuracion["sucursal"]
        facturacion = self.configuracion["facturacion"]
        imagenes = self.configuracion["imagenes"]
        self.empresa_vars = {clave: tk.StringVar(value=valor) for clave, valor in empresa.items()}
        self.sucursal_vars = {clave: tk.StringVar(value=valor) for clave, valor in sucursal.items()}
        self.facturacion_vars = {clave: tk.StringVar(value=valor) for clave, valor in facturacion.items()}
        self.logo = tk.StringVar(value=imagenes.get("logo", ""))
        self.vehiculo = tk.StringVar(value=imagenes.get("vehiculo", ""))
        self._imagenes_tk = {}
        self.valores_tarifa = {}

    def _construir(self):
        encabezado = tk.Frame(self, bg=AZUL, padx=24, pady=16)
        encabezado.pack(fill="x")
        tk.Label(
            encabezado, text="PANEL DE CONFIGURACION", bg=AZUL, fg="white",
            font=("Arial", 24, "bold")
        ).pack(side="left")
        tk.Label(
            encabezado, text=self.nombre.get(), bg=AZUL, fg=AZUL_CLARO,
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=18, pady=(7, 0))
        tk.Button(
            encabezado, text="CERRAR", command=self.destroy, bg=ROJO, fg="white",
            activebackground="#8c1d18", activeforeground="white",
            font=("Arial", 12, "bold"), padx=18, pady=7, relief="flat"
        ).pack(side="right")

        estilo = ttk.Style(self)
        estilo.configure("TPV.TNotebook.Tab", font=("Arial", 13, "bold"), padding=(20, 10))
        cuaderno = ttk.Notebook(self, style="TPV.TNotebook")
        cuaderno.pack(fill="both", expand=True, padx=18, pady=16)

        self._pestana_general(cuaderno)
        self._pestana_empresa(cuaderno)
        self._pestana_imagenes(cuaderno)
        self._pestana_interface(cuaderno)
        self._pestana_tarifas(cuaderno)
        self._pestana_funcionamiento(cuaderno)

        pie = tk.Frame(self, bg="#e8edf2", padx=18, pady=12)
        pie.pack(fill="x")
        tk.Button(
            pie, text="Cancelar", command=self.destroy, bg="#6c757d", fg="white",
            font=("Arial", 12, "bold"), padx=20, pady=8, relief="flat"
        ).pack(side="right", padx=(10, 0))
        tk.Button(
            pie, text="GUARDAR CONFIGURACION", command=self._guardar,
            bg=VERDE, fg="white", font=("Arial", 12, "bold"),
            padx=20, pady=8, relief="flat"
        ).pack(side="right")

    def _marco(self, cuaderno, titulo):
        marco = tk.Frame(cuaderno, bg=FONDO, padx=24, pady=20)
        cuaderno.add(marco, text=titulo)
        return marco

    def _fila(self, padre, texto, variable, fila, ancho=28):
        tk.Label(padre, text=texto, bg="white", fg=TEXTO, font=("Arial", 12, "bold")).grid(
            row=fila, column=0, sticky="w", padx=14, pady=10
        )
        entrada = tk.Entry(padre, textvariable=variable, width=ancho, font=("Arial", 12))
        entrada.grid(row=fila, column=1, sticky="w", padx=14, pady=10)
        return entrada

    def _pestana_general(self, cuaderno):
        marco = self._marco(cuaderno, "General")
        tarjeta = tk.LabelFrame(
            marco, text=" Informacion del estacionamiento ", bg="white",
            fg=AZUL, font=("Arial", 14, "bold"), padx=12, pady=12
        )
        tarjeta.pack(fill="x")
        self._fila(tarjeta, "Nombre", self.nombre, 0, 36)
        self._fila(tarjeta, "Correo para reportes", self.correo, 1, 36)
        self._fila(tarjeta, "Cantidad de cajones", self.cantidad_cajones, 2, 12)
        self._fila(tarjeta, "Nombre del punto en el boleto", self.nombre_punto, 3, 24)
        clave_correo = bool(os.environ.get("ESTACIONAMIENTO_SMTP_PASSWORD", ""))
        tk.Label(
            tarjeta,
            text="Contraseña de correo: " + ("CONFIGURADA EN ARCHIVO PRIVADO" if clave_correo else "NO CONFIGURADA"),
            bg="white", fg=VERDE if clave_correo else ROJO, font=("Arial", 11, "bold")
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=14, pady=8)
        tk.Checkbutton(
            tarjeta, text="Iniciar en pantalla completa", variable=self.pantalla_completa,
            bg="white", font=("Arial", 12), activebackground="white"
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=14, pady=8)
        tk.Checkbutton(
            tarjeta, text="Solicitar placa obligatoriamente", variable=self.placa_obligatoria,
            bg="white", font=("Arial", 12), activebackground="white"
        ).grid(row=6, column=0, columnspan=2, sticky="w", padx=14, pady=8)

    def _grupo_datos(self, padre, titulo, variables, campos):
        tarjeta = tk.LabelFrame(
            padre, text=f" {titulo} ", bg="white", fg=AZUL,
            font=("Arial", 13, "bold"), padx=10, pady=10
        )
        for fila, (clave, etiqueta) in enumerate(campos):
            self._fila(tarjeta, etiqueta, variables[clave], fila, 28)
        return tarjeta

    def _pestana_empresa(self, cuaderno):
        marco = self._marco(cuaderno, "Empresa y sucursal")
        columnas = tk.Frame(marco, bg=FONDO)
        columnas.pack(fill="both", expand=True)
        empresa = self._grupo_datos(columnas, "Datos de la empresa", self.empresa_vars, (
            ("nombre", "Nombre o razon social"), ("rfc", "RFC"),
            ("calle_numero", "Calle y numero"), ("colonia", "Colonia"),
            ("codigo_postal", "Codigo postal"), ("alcaldia_municipio", "Alcaldia o municipio"),
            ("estado", "Entidad estatal"),
        ))
        empresa.pack(side="left", fill="both", expand=True, padx=(0, 8))
        derecha = tk.Frame(columnas, bg=FONDO)
        derecha.pack(side="left", fill="both", expand=True, padx=(8, 0))
        sucursal = self._grupo_datos(derecha, "Datos de la sucursal", self.sucursal_vars, (
            ("calle_numero", "Calle y numero"), ("colonia", "Colonia"),
            ("codigo_postal", "Codigo postal"), ("estado", "Entidad estatal"),
        ))
        sucursal.pack(fill="x", pady=(0, 14))
        facturacion = self._grupo_datos(derecha, "Datos para facturacion", self.facturacion_vars, (
            ("correo", "Correo"), ("telefono", "Numero telefonico"),
        ))
        facturacion.pack(fill="x")

    def _pestana_imagenes(self, cuaderno):
        marco = self._marco(cuaderno, "Imagenes y boleto")
        tk.Label(
            marco, text="Las imagenes se copiaran a una carpeta estable de la TPV.",
            bg=FONDO, fg="#5d6d7e", font=("Arial", 11)
        ).pack(anchor="w", pady=(0, 12))
        contenedor = tk.Frame(marco, bg=FONDO)
        contenedor.pack(fill="both", expand=True)
        for columna, (tipo, titulo, variable) in enumerate((
            ("logo", "Logo de la empresa", self.logo),
            ("vehiculo", "Imagen de marcas o vehiculo", self.vehiculo),
        )):
            tarjeta = tk.LabelFrame(
                contenedor, text=f" {titulo} ", bg="white", fg=AZUL,
                font=("Arial", 14, "bold"), padx=16, pady=16
            )
            tarjeta.grid(row=0, column=columna, sticky="nsew", padx=8)
            contenedor.grid_columnconfigure(columna, weight=1)
            vista = tk.Label(tarjeta, text="Sin imagen seleccionada", bg="#eef2f5",
                             fg="#5d6d7e", width=42, height=15)
            vista.pack(fill="both", expand=True, pady=(0, 12))
            setattr(self, f"vista_{tipo}", vista)
            tk.Button(
                tarjeta, text="SELECCIONAR IMAGEN",
                command=lambda t=tipo: self._seleccionar_imagen(t),
                bg=AZUL, fg="white", font=("Arial", 11, "bold"),
                padx=14, pady=8, relief="flat"
            ).pack()
            if variable.get():
                self._mostrar_imagen(tipo, variable.get())

    def _seleccionar_imagen(self, tipo):
        ruta = filedialog.askopenfilename(
            parent=self, title="Seleccionar imagen",
            filetypes=(("Imagenes", "*.png *.jpg *.jpeg *.bmp"), ("Todos", "*.*"))
        )
        if not ruta:
            return
        (self.logo if tipo == "logo" else self.vehiculo).set(ruta)
        self._mostrar_imagen(tipo, ruta)

    def _mostrar_imagen(self, tipo, ruta):
        vista = getattr(self, f"vista_{tipo}")
        try:
            imagen = Image.open(ruta)
            imagen.thumbnail((390, 260), Image.Resampling.LANCZOS)
            foto = ImageTk.PhotoImage(imagen)
            self._imagenes_tk[tipo] = foto
            vista.configure(image=foto, text="")
        except (OSError, ValueError):
            vista.configure(image="", text="No se pudo abrir la imagen")

    @staticmethod
    def _guardar_imagen(origen, nombre):
        if not origen:
            return ""
        ruta = Path(origen)
        if not ruta.is_file():
            raise ValueError(f"No se encontro la imagen: {ruta}")
        RUTA_RECURSOS.mkdir(parents=True, exist_ok=True)
        destino = RUTA_RECURSOS / f"{nombre}{ruta.suffix.lower()}"
        if ruta.resolve() != destino.resolve():
            shutil.copy2(ruta, destino)
        return str(destino)

    def _pestana_interface(self, cuaderno):
        marco = self._marco(cuaderno, "Interface")
        tarjeta = tk.LabelFrame(
            marco, text=" Apariencia de la TPV ", bg="white", fg=AZUL,
            font=("Arial", 14, "bold"), padx=16, pady=16
        )
        tarjeta.pack(fill="x", pady=(0, 16))
        tk.Checkbutton(
            tarjeta, text="Mostrar reloj adicional", variable=self.mostrar_reloj,
            bg="white", font=("Arial", 12), activebackground="white"
        ).pack(anchor="w", pady=6)

        impresora = tk.LabelFrame(
            marco, text=" Impresora de comprobantes ", bg="white", fg=AZUL,
            font=("Arial", 14, "bold"), padx=12, pady=12
        )
        impresora.pack(fill="x")
        tk.Label(impresora, text="Modelo", bg="white", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=10
        )
        selector = ttk.Combobox(
            impresora, textvariable=self.modelo_impresora, state="readonly", width=28,
            values=("Epson USB", "POS80 0416:5011"), font=("Arial", 12)
        )
        selector.grid(row=0, column=1, sticky="w", padx=14, pady=10)
        selector.bind("<<ComboboxSelected>>", self._cambiar_impresora)
        self._fila(impresora, "Vendor ID", self.vendor_id, 1, 12)
        self._fila(impresora, "Product ID", self.product_id, 2, 12)
        self._fila(impresora, "Dispositivo Linux", self.dispositivo, 3, 22)

    def _pestana_tarifas(self, cuaderno):
        marco = self._marco(cuaderno, "Tarifas")
        superior = tk.Frame(marco, bg="white", padx=14, pady=12)
        superior.pack(fill="x", pady=(0, 12))
        tk.Label(superior, text="Tipo de tarifa", bg="white", fg=AZUL,
                 font=("Arial", 13, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            superior, textvariable=self.tipo_tarifa, state="readonly", width=16,
            values=("simple", "avanzada"), font=("Arial", 12)
        ).grid(row=0, column=1, padx=12)
        tk.Label(superior, text="Boleto perdido $", bg="white",
                 font=("Arial", 12, "bold")).grid(row=0, column=2, padx=(30, 8))
        tk.Entry(superior, textvariable=self.boleto_perdido, width=10,
                 font=("Arial", 12), justify="right").grid(row=0, column=3)

        contenedor = tk.Frame(marco, bg="white")
        contenedor.pack(fill="both", expand=True)
        lienzo = tk.Canvas(contenedor, bg="white", highlightthickness=0)
        barra = ttk.Scrollbar(contenedor, orient="vertical", command=lienzo.yview)
        tabla = tk.Frame(lienzo, bg="white")
        tabla.bind("<Configure>", lambda _e: lienzo.configure(scrollregion=lienzo.bbox("all")))
        ventana = lienzo.create_window((0, 0), window=tabla, anchor="nw")
        lienzo.bind("<Configure>", lambda e: lienzo.itemconfigure(ventana, width=e.width))
        lienzo.configure(yscrollcommand=barra.set)
        lienzo.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        titulos = ("Hora", "Hora completa", "Primer cuarto", "Segundo cuarto", "Tercer cuarto")
        for columna, titulo in enumerate(titulos):
            tk.Label(tabla, text=titulo, bg=AZUL, fg="white", font=("Arial", 11, "bold"),
                     padx=8, pady=8).grid(row=0, column=columna, sticky="ew", padx=1, pady=1)
            tabla.grid_columnconfigure(columna, weight=1)
        datos = self.configuracion["tarifa"]["personalizada"]
        for hora in range(25):
            tk.Label(tabla, text=str(hora), bg="#e8edf2", fg=TEXTO,
                     font=("Arial", 11, "bold"), pady=5).grid(
                row=hora + 1, column=0, sticky="ew", padx=1, pady=1
            )
            for columna, clave in enumerate(("hora", "1", "2", "3"), start=1):
                variable = tk.StringVar(value=str(datos[str(hora)][clave]))
                self.valores_tarifa[(str(hora), clave)] = variable
                tk.Entry(tabla, textvariable=variable, justify="center", width=12,
                         font=("Arial", 11)).grid(row=hora + 1, column=columna,
                                                  sticky="ew", padx=2, pady=2)

    def _pestana_funcionamiento(self, cuaderno):
        marco = self._marco(cuaderno, "Funcionamiento interno")
        tarjeta = tk.LabelFrame(
            marco, text=" Comportamiento seguro ", bg="white", fg=AZUL,
            font=("Arial", 14, "bold"), padx=16, pady=16
        )
        tarjeta.pack(fill="x")
        tk.Checkbutton(
            tarjeta, text="Enviar informacion de cortes al cerrar",
            variable=self.enviar_cortes, bg="white", font=("Arial", 12),
            activebackground="white"
        ).pack(anchor="w", pady=7)
        tk.Checkbutton(
            tarjeta, text="Pedir confirmacion antes de cerrar la TPV",
            variable=self.confirmar_cierre, bg="white", font=("Arial", 12),
            activebackground="white"
        ).pack(anchor="w", pady=7)
        tk.Label(
            tarjeta,
            text="Los datos de conexion y contraseñas permanecen protegidos fuera de esta pantalla.",
            bg="white", fg="#5d6d7e", font=("Arial", 11)
        ).pack(anchor="w", pady=(18, 4))

    def _cambiar_impresora(self, _event=None):
        if self.modelo_impresora.get() == "POS80 0416:5011":
            self.vendor_id.set("0416")
            self.product_id.set("5011")
            self.dispositivo.set("/dev/usb/lp0")
        else:
            self.vendor_id.set("04b8")
            self.product_id.set("0e15")

    @staticmethod
    def _numero(valor, nombre):
        try:
            numero = float(valor)
        except ValueError as error:
            raise ValueError(f"{nombre} debe ser un numero") from error
        if numero < 0:
            raise ValueError(f"{nombre} no puede ser negativo")
        return int(numero) if numero.is_integer() else numero

    def _guardar(self):
        try:
            if not self.nombre.get().strip():
                raise ValueError("El nombre del estacionamiento es obligatorio")
            self.configuracion["general"].update({
                "nombre_estacionamiento": self.nombre.get().strip(),
                "correo": self.correo.get().strip(),
                "cantidad_cajones": int(self._numero(self.cantidad_cajones.get(), "Cantidad de cajones")),
                "nombre_punto": self.nombre_punto.get().strip(),
                "pantalla_completa": self.pantalla_completa.get(),
                "mostrar_reloj": self.mostrar_reloj.get(),
                "placa_obligatoria": self.placa_obligatoria.get(),
            })
            self.configuracion["empresa"] = {
                clave: variable.get().strip() for clave, variable in self.empresa_vars.items()
            }
            self.configuracion["sucursal"] = {
                clave: variable.get().strip() for clave, variable in self.sucursal_vars.items()
            }
            self.configuracion["facturacion"] = {
                clave: variable.get().strip() for clave, variable in self.facturacion_vars.items()
            }
            self.configuracion["imagenes"] = {
                "logo": self._guardar_imagen(self.logo.get(), "logo_empresa"),
                "vehiculo": self._guardar_imagen(self.vehiculo.get(), "imagen_vehiculo"),
            }
            modelo = self.modelo_impresora.get()
            self.configuracion["impresora"].update({
                "modelo": modelo,
                "modo": "lp" if modelo == "POS80 0416:5011" else "usb",
                "vendor_id": self.vendor_id.get().strip().lower(),
                "product_id": self.product_id.get().strip().lower(),
                "dispositivo": self.dispositivo.get().strip(),
            })
            self.configuracion["tarifa"]["tipo"] = self.tipo_tarifa.get()
            self.configuracion["tarifa"]["boleto_perdido"] = self._numero(
                self.boleto_perdido.get(), "Boleto perdido"
            )
            for (hora, fraccion), variable in self.valores_tarifa.items():
                self.configuracion["tarifa"]["personalizada"][hora][fraccion] = self._numero(
                    variable.get(), f"Tarifa de hora {hora}"
                )
            self.configuracion["funcionamiento"].update({
                "enviar_cortes": self.enviar_cortes.get(),
                "confirmar_cierre": self.confirmar_cierre.get(),
            })
            guardar_configuracion(self.configuracion)
        except (ValueError, OSError) as error:
            mb.showerror("No se pudo guardar", str(error), parent=self)
            return
        if self.al_guardar:
            self.al_guardar(self.configuracion)
        mb.showinfo("Configuracion", "Los cambios se guardaron correctamente.", parent=self)
        self.destroy()

