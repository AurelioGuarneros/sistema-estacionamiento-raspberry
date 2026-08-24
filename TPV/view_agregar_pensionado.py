import qrcode
from escpos.printer import Usb, USBNotFoundError

from tkinter import messagebox as mb
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
from datetime import datetime
from queries import Pensionados
import traceback

class View_agregar_pensionados:
    """Clase de la vista para agregar pensionados."""
    def __init__(self, nombre_estacionamiento:str):
        """Inicializa una instancia de la clase ViewAgregarPensionados y crea la ventana principal de la interfaz."""
        self.nombre_estacionamiento = nombre_estacionamiento
        self.query = Pensionados()

        # Crea la ventana principal
        self.panel_crud = tk.Toplevel()

        # Se elimina la funcionalidad del botón de cerrar
        self.panel_crud.protocol("WM_DELETE_WINDOW", lambda: self.desconectar())

        self.panel_crud.title(f'Agregar pensionado - {self.nombre_estacionamiento}')

        # Configura la columna principal del panel para que use todo el espacio disponible
        self.panel_crud.columnconfigure(0, weight=1)

        # Crea las variables para los datos del pensionado
        self.variable_numero_tarjeta = StringVar()
        self.variable_nombre = StringVar()
        self.variable_apellido_1 = StringVar()
        self.variable_apellido_2 = StringVar()
        self.variable_fecha_alta = StringVar()
        self.variable_telefono_1 = StringVar()
        self.variable_telefono_2 = StringVar()
        self.variable_ciudad = StringVar()
        self.variable_colonia = StringVar()
        self.variable_cp = StringVar()
        self.variable_numero_calle = StringVar()

        self.variable_placas = StringVar()
        self.variable_auto_modelo = StringVar()
        self.variable_auto_color = StringVar()

        self.variable_monto = StringVar()
        self.variable_cortesia = StringVar()
        self.variable_tolerancia = StringVar()
        self.variable_tolerancia.set("5")

        self.__variable_es_reposicion = StringVar()

        self.registros = None

        # Llama a la función interface() que configura la interfaz gráfica
        self.interface()

        self.panel_crud.resizable(False, False)

        # Inicia el loop principal de la ventana
        self.panel_crud.mainloop()

    def interface(self):
        """Define la interfaz gráfica para agregar pensionados."""
        # Se crea un Label Frame principal para la sección superior
        seccion_superior = tk.LabelFrame(self.panel_crud, text='')
        seccion_superior.columnconfigure(1, weight=1)
        seccion_superior.propagate(True)
        seccion_superior.grid(row=0, column=0, sticky=tk.NSEW)

        # Se crea un Label Frame para la sección de la conexión
        etiqueta_user = tk.Label(seccion_superior, text=f'Bienvenido/a')
        etiqueta_user.grid(row=0, column=0, padx=5, pady=5)


        seccion_tarjeta_reposicon = tk.Frame(seccion_superior)
        seccion_tarjeta_reposicon.grid(row=1, column=0)


        etiqueta_reposicion_info = ttk.Label(seccion_tarjeta_reposicon, text='¿La tarjeta a registrar es de reposición?: ')
        etiqueta_reposicion_info.grid(row=0, column=0, padx=5, pady=5)

        campo_reposicion = ttk.Combobox(seccion_tarjeta_reposicon, width=5, state="readonly", textvariable=self.__variable_es_reposicion)
        campo_reposicion["values"] = ["Si", "No"]
        campo_reposicion.current(1)
        campo_reposicion.grid(row=0, column=1, padx=5, pady=5)



        seccion_datos_pensionado = ttk.LabelFrame(seccion_superior, text="\t\t\tIngresa los datos del pensionado a registrar")
        seccion_datos_pensionado.grid(row=2, column=0,padx=5, pady=5, sticky=tk.NW)



        seccion_datos_personales_pensionado = tk.LabelFrame(seccion_datos_pensionado, text="Datos personales del pensionado")
        seccion_datos_personales_pensionado.grid(row=2, column=0,padx=5, pady=5, sticky=tk.NW)


        etiqueta_numero_tarjeta = ttk.Label(seccion_datos_personales_pensionado, text='Número de tarjeta: ')
        etiqueta_numero_tarjeta.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NW)
        self.campo_numero_tarjeta = ttk.Entry(seccion_datos_personales_pensionado, textvariable=self.variable_numero_tarjeta)
        self.campo_numero_tarjeta.grid(row=0, column=1, padx=5, pady=5)

        etiqueta_nombre_pensionado = ttk.Label(seccion_datos_personales_pensionado, text='Nombre: ')
        etiqueta_nombre_pensionado.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_nombre_pensinado = ttk.Entry(seccion_datos_personales_pensionado, textvariable=self.variable_nombre)
        campo_nombre_pensinado.grid(row=1, column=1, padx=5, pady=5)

        etiqueta_apellido_1_pensionado = ttk.Label(seccion_datos_personales_pensionado, text='Primer apellido: ')
        etiqueta_apellido_1_pensionado.grid(row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_apellido_1_pensionado = ttk.Entry(seccion_datos_personales_pensionado, textvariable=self.variable_apellido_1)
        campo_apellido_1_pensionado.grid(row=2, column=1, padx=5, pady=5)

        etiqueta_apellido_2_pensionado = ttk.Label(seccion_datos_personales_pensionado, text='Segundo apellido: ')
        etiqueta_apellido_2_pensionado.grid(row=3, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_apellido_2_pensionado = ttk.Entry(seccion_datos_personales_pensionado, textvariable=self.variable_apellido_2)
        campo_apellido_2_pensionado.grid(row=3, column=1, padx=5, pady=5)

        etiqueta_telefono_1_pensionado = ttk.Label(seccion_datos_personales_pensionado, text='Telefono 1: ')
        etiqueta_telefono_1_pensionado.grid(row=4, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_telefono_1_pensionado = ttk.Entry(seccion_datos_personales_pensionado, textvariable=self.variable_telefono_1)
        campo_telefono_1_pensionado.grid(row=4, column=1, padx=5, pady=5)

        etiqueta_telefono_2_pensionado = ttk.Label(seccion_datos_personales_pensionado, text='Telefono 2: ')
        etiqueta_telefono_2_pensionado.grid(row=5, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_telefono_2_pensionado = ttk.Entry(seccion_datos_personales_pensionado, textvariable=self.variable_telefono_2)
        campo_telefono_2_pensionado.grid(row=5, column=1, padx=5, pady=5)

        etiqueta_ciudad_pensionado = ttk.Label(seccion_datos_personales_pensionado, text='Ciudad: ')
        etiqueta_ciudad_pensionado.grid(row=7, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_ciudad_pensionado = ttk.Entry(seccion_datos_personales_pensionado, textvariable=self.variable_ciudad)
        campo_ciudad_pensionado.grid(row=7, column=1, padx=5, pady=5)

        etiqueta_colonia_pensionado = ttk.Label(seccion_datos_personales_pensionado, text='Colonia: ')
        etiqueta_colonia_pensionado.grid(row=8, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_colonia_pensionado = ttk.Entry(seccion_datos_personales_pensionado, textvariable=self.variable_colonia)
        campo_colonia_pensionado.grid(row=8, column=1, padx=5, pady=5)

        etiqueta_CP_pensionado = ttk.Label(seccion_datos_personales_pensionado, text='CP: ')
        etiqueta_CP_pensionado.grid(row=9, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_CP_pensionado = ttk.Entry(seccion_datos_personales_pensionado, textvariable=self.variable_cp)
        campo_CP_pensionado.grid(row=9, column=1, padx=5, pady=5)

        etiqueta_numero_calle_pensionado = ttk.Label(seccion_datos_personales_pensionado, text='Numero de calle: ')
        etiqueta_numero_calle_pensionado.grid(row=10, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_numero_calle_pensionado = ttk.Entry(seccion_datos_personales_pensionado, textvariable=self.variable_numero_calle)
        campo_numero_calle_pensionado.grid(row=10, column=1, padx=5, pady=5)




        seccion_derecha = ttk.Frame(seccion_datos_pensionado)
        seccion_derecha.grid(row=2, column=1,padx=5, pady=5, sticky=tk.NW)

        seccion_datos_auto_pensionado = tk.LabelFrame(seccion_derecha, text="Datos del auto del pensionado")
        seccion_datos_auto_pensionado.grid(row=0, column=0,padx=5, pady=5, sticky=tk.NW)


        etiqueta_placa_auto_pensionado = ttk.Label(seccion_datos_auto_pensionado, text='Placa: ')
        etiqueta_placa_auto_pensionado.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_placa_auto_pensionado = ttk.Entry(seccion_datos_auto_pensionado, textvariable=self.variable_placas)
        campo_placa_auto_pensionado.grid(row=0, column=1, padx=5, pady=5)

        etiqueta_modelo_auto_pensionado = ttk.Label(seccion_datos_auto_pensionado, text='Modelo: ')
        etiqueta_modelo_auto_pensionado.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_placa_modelo_pensionado = ttk.Entry(seccion_datos_auto_pensionado, textvariable=self.variable_auto_modelo)
        campo_placa_modelo_pensionado.grid(row=1, column=1, padx=5, pady=5)

        etiqueta_color_auto_pensionado = ttk.Label(seccion_datos_auto_pensionado, text='Color: ')
        etiqueta_color_auto_pensionado.grid(row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_color_auto_pensionado = ttk.Entry(seccion_datos_auto_pensionado, textvariable=self.variable_auto_color)
        campo_color_auto_pensionado.grid(row=2, column=1, padx=5, pady=5)



        seccion_datos_pension = tk.LabelFrame(seccion_derecha, text="Datos de la pension")
        seccion_datos_pension.grid(row=1, column=0,padx=5, pady=5, sticky=tk.NW)

        etiqueta_monto_dato_pension = ttk.Label(seccion_datos_pension, text='Monto X Mes: ')
        etiqueta_monto_dato_pension.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NW)
        self.campo_monto_dato_pension = ttk.Entry(seccion_datos_pension, textvariable=self.variable_monto)
        self.campo_monto_dato_pension.grid(row=0, column=1, padx=5, pady=5)

        etiqueta_cortesia_dato_pension = ttk.Label(seccion_datos_pension, text='Cortesia: ')
        etiqueta_cortesia_dato_pension.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)

        campo_cortesia_dato_pension = ttk.Combobox(seccion_datos_pension, width=5, state="readonly", textvariable=self.variable_cortesia)
        campo_cortesia_dato_pension["values"] = ["Si", "No"]
        campo_cortesia_dato_pension.current(1)
        campo_cortesia_dato_pension.grid(row=1, column=1, padx=1, pady=1, sticky=tk.NW)

        etiqueta_color_auto_pensionado = ttk.Label(seccion_datos_pension, text='Tolerancia: ')
        etiqueta_color_auto_pensionado.grid(row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_color_auto_pensionado = ttk.Entry(seccion_datos_pension, textvariable=self.variable_tolerancia)
        campo_color_auto_pensionado.grid(row=2, column=1, padx=5, pady=5)

        # Crea un botón y lo empaqueta en la seccion_botones_consulta
        boton_agregar_pensionado = tk.Button(self.panel_crud,  text='Agregar usuario', command=self.agregar_pensionado, width=20, font=("Arial", 12), background="red")
        boton_agregar_pensionado.grid(row=5, column=0, padx=5, pady=5)

        self.campo_numero_tarjeta.focus()

    def agregar_pensionado(self):
        """Agrega un nuevo pensionado con los datos ingresados."""
        try:
            pensionado_fecha_alta =  datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            variable_numero_tarjeta = self.variable_numero_tarjeta.get()
            variable_nombre = self.variable_nombre.get()
            variable_apellido_1 = self.variable_apellido_1.get()
            variable_apellido_2 = self.variable_apellido_2.get()
            variable_fecha_alta = pensionado_fecha_alta
            variable_telefono_1 = self.variable_telefono_1.get()
            variable_telefono_2 = self.variable_telefono_2.get()
            variable_ciudad = self.variable_ciudad.get()
            variable_colonia = self.variable_colonia.get()
            variable_cp = self.variable_cp.get()
            variable_numero_calle = self.variable_numero_calle.get()

            variable_placas = self.variable_placas.get()
            variable_auto_modelo = self.variable_auto_modelo.get()
            variable_auto_color = self.variable_auto_color.get()

            variable_monto = self.variable_monto.get()
            variable_cortesia = self.variable_cortesia.get()
            variable_tolerancia = 5
            variable_estatus = "Inactiva"

            try:
                variable_numero_tarjeta = int(variable_numero_tarjeta)

            except Exception as e:
                traceback.print_exc()
                mb.showerror("Error", "Ingresa un numero de tarjeta valido")
                self.campo_numero_tarjeta.focus()
                return

            try:
                variable_monto = int(variable_monto)

            except Exception as e:
                traceback.print_exc()
                mb.showerror("Error", "Ingresa un monto valido")
                self.campo_monto_dato_pension.focus()
                return


            if self.__variable_es_reposicion.get() == "Si":
                respuesta = mb.askyesno("Advertencia", "¿Estas seguro de que la tarjeta registrada es de reposición? De ser asi no olvides desactivar la antigua tarjeta")
                variable_estatus = "Reposicion"
                if respuesta is False:return


            if len(variable_nombre) == 0 or len(variable_apellido_1) == 0 or len(variable_apellido_2) == 0 or len(variable_fecha_alta) == 0 or len(variable_telefono_1) == 0 or len(variable_telefono_2) == 0 or len(variable_ciudad) == 0 or len(variable_colonia) == 0 or len(variable_cp) == 0 or len(variable_numero_calle) == 0 or len(variable_placas) == 0 or len(variable_auto_modelo) == 0 or len(variable_auto_color) == 0 or len(variable_cortesia) == 0 or len(str(variable_tolerancia)) == 0:
                raise IndexError("No dejar campos en blanco")

            if variable_cortesia == "No" and variable_monto == 0:
                raise TypeError("Ingrese el monto a pagar")
            if variable_cortesia == "Si": variable_monto = 0


            datos_pensionado = (variable_numero_tarjeta, variable_nombre, variable_apellido_1, variable_apellido_2, variable_fecha_alta, variable_telefono_1, variable_telefono_2, variable_ciudad, variable_colonia, variable_cp, variable_numero_calle, variable_placas, variable_auto_modelo, variable_auto_color, variable_monto, variable_cortesia, variable_tolerancia, variable_estatus)

            resultado = self.query.consultar_pensionado(variable_numero_tarjeta)

            if len(resultado) == 0:
                self.query.agregar_pensionados(datos_pensionado)
                mb.showinfo("Información", "El pensionado fue añadido correctamente, realice su pago de pensión para activar la tarjeta")
                self.desconectar()
            else:
                self.variable_numero_tarjeta.set('')
                self.campo_numero_tarjeta.focus()
                mb.showerror("Error", "Ya existe un pensionado registrado con ese numero de tarjeta")
                return

        except ValueError as e:
            traceback.print_exc()
            mb.showerror("Error", e)
        except TypeError as e:
            traceback.print_exc()
            mb.showerror("Error", e)
        except IndexError as e:
            traceback.print_exc()
            mb.showerror("Error", e)
        except Exception as e:
            traceback.print_exc()
            mb.showerror("Error", e)

    def desconectar(self):
        """Cierra la ventana principal y detiene el hilo en el que se ejecuta."""
        self.panel_crud.quit()
        self.panel_crud.destroy()

# View_agregar_pensionados()
