from tkinter import filedialog
import qrcode

from tkinter import messagebox as mb
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar

from datetime import datetime

from queries import Pensionados
import traceback
from escpos.printer import Usb, USBNotFoundError


class View_modificar_pensionados():
    """Clase para mostrar la ventana de modificación de datos de un pensionado."""

    def __init__(self, datos_pensionado, nombre_estacionamiento):
        """
        Constructor de la clase. Inicializa la ventana y los atributos.

        Args:
            datos_pensionado (tuple): Tupla con los datos del pensionado a modificar.
        """
        self.nombre_estacionamiento = nombre_estacionamiento
        self.query = Pensionados()
        self.datos_pensionado = datos_pensionado

        # Crear la ventana principal
        self.panel_crud = tk.Toplevel()

        # Se elimina la funcionalidad del botón de cerrar
        self.panel_crud.protocol("WM_DELETE_WINDOW", lambda: self.desconectar())

        self.panel_crud.title(f'Modificar pensionado . {self.nombre_estacionamiento}')

        # Configura la columna principal del panel para que use todo el espacio disponible
        self.panel_crud.columnconfigure(0, weight=1)

        # Variables para almacenar los datos del pensionado
        self.variable_numero_tarjeta = StringVar()
        self.variable_numero_tarjeta.set(datos_pensionado[0][0])

        self.variable_nombre = StringVar()
        self.variable_nombre.set(datos_pensionado[0][1])

        self.variable_apellido_1 = StringVar()
        self.variable_apellido_1.set(datos_pensionado[0][2])

        self.variable_apellido_2 = StringVar()
        self.variable_apellido_2.set(datos_pensionado[0][3])


        self.variable_telefono_1 = StringVar()
        self.variable_telefono_1.set(datos_pensionado[0][4])

        self.variable_telefono_2 = StringVar()
        self.variable_telefono_2.set(datos_pensionado[0][5])

        self.variable_ciudad = StringVar()
        self.variable_ciudad.set(datos_pensionado[0][6])

        self.variable_colonia = StringVar()
        self.variable_colonia.set(datos_pensionado[0][7])

        self.variable_cp = StringVar()
        self.variable_cp.set(datos_pensionado[0][8])

        self.variable_numero_calle = StringVar()
        self.variable_numero_calle.set(datos_pensionado[0][9])

        self.variable_placas = StringVar()
        self.variable_placas.set(datos_pensionado[0][10])

        self.variable_auto_modelo = StringVar()
        self.variable_auto_modelo.set(datos_pensionado[0][11])

        self.variable_auto_color = StringVar()
        self.variable_auto_color.set(datos_pensionado[0][12])

        self.variable_monto = StringVar()
        self.variable_monto.set(datos_pensionado[0][13])

        self.variable_cortesia = StringVar()
        self.variable_cortesia.set(datos_pensionado[0][14])

        self.variable_tolerancia = StringVar()
        self.variable_tolerancia.set("5")

        self.variable_vigencia = StringVar()
        self.variable_vigencia.set(datos_pensionado[0][16])

        self.variable_estatus = StringVar()
        self.variable_estatus.set(datos_pensionado[0][17])

        self.registros = None

        # Llama a la función interface() que configura la interfaz gráfica
        self.interface()

        self.panel_crud.resizable(False, False)

        # Inicia el loop principal de la ventana
        self.panel_crud.mainloop()

    def interface(self):
        """ Crea la interfaz gráfica de la ventana de modificación."""

        # Crear un Label Frame principal para la sección superior
        seccion_superior = tk.LabelFrame(self.panel_crud, text='')
        seccion_superior.columnconfigure(1, weight=1)
        seccion_superior.propagate(True)
        seccion_superior.grid(row=0, column=0, sticky=tk.NSEW)

        # Se crea un Label Frame para la sección de la conexión
        etiqueta_user = tk.Label(seccion_superior, text=f'Bienvenido/a')
        etiqueta_user.grid(row=0, column=0, padx=5, pady=5)

        seccion_datos_pensionado = ttk.LabelFrame(seccion_superior, text="\t\t\tIngresa los datos del pensionado a modificar")
        seccion_datos_pensionado.grid(row=1, column=0,padx=5, pady=5, sticky=tk.NW)


        seccion_datos_personales_pensionado = tk.LabelFrame(seccion_datos_pensionado, text="Datos personales del pensionado")
        seccion_datos_personales_pensionado.grid(row=2, column=0,padx=5, pady=5, sticky=tk.NW)


        etiqueta_numero_tarjeta = ttk.Label(seccion_datos_personales_pensionado, text='Número de tarjeta: ')
        etiqueta_numero_tarjeta.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NW)
        self.campo_numero_tarjeta = ttk.Entry(seccion_datos_personales_pensionado, textvariable=self.variable_numero_tarjeta, state="disabled")
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
        campo_monto_dato_pension = ttk.Entry(seccion_datos_pension, textvariable=self.variable_monto)
        campo_monto_dato_pension.grid(row=0, column=1, padx=5, pady=5)

        etiqueta_cortesia_dato_pension = ttk.Label(seccion_datos_pension, text='Cortesia: ')
        etiqueta_cortesia_dato_pension.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)

        campo_cortesia_dato_pension = ttk.Combobox(seccion_datos_pension, width=5, state="readonly", textvariable=self.variable_cortesia)
        campo_cortesia_dato_pension["values"] = ["Si", "No"]

        campo_cortesia_dato_pension.grid(row=1, column=1, padx=1, pady=1, sticky=tk.NW)

        etiqueta_tolerancia = ttk.Label(seccion_datos_pension, text='Tolerancia: ')
        etiqueta_tolerancia.grid(row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        self.campo_tolerancia = ttk.Entry(seccion_datos_pension, textvariable=self.variable_tolerancia)
        self.campo_tolerancia.grid(row=2, column=1, padx=5, pady=5)


        seccion_inferior = tk.LabelFrame(self.panel_crud, text='')
        seccion_inferior.grid(row=1, column=0)


        # Crea un botón y lo empaqueta en la seccion_botones_consulta
        boton_modificar_pensionado = tk.Button(seccion_inferior, text='Desactivar tarjeta', command=self.desactivar_tarjeta, width=20, font=("Arial", 12), background="red")
        boton_modificar_pensionado.grid(row=0, column=0, padx=5, pady=5)

        # Crea un botón y lo empaqueta en la seccion_botones_consulta
        boton_modificar_pensionado = tk.Button(seccion_inferior, text='Guardar Cambios', command=self.modificar_pensionado, width=20, font=("Arial", 12), background="red")
        boton_modificar_pensionado.grid(row=0, column=1, padx=5, pady=5)

    def desactivar_tarjeta(self):
        """ Desactiva temporal o permanentemente la tarjeta del pensionado."""
        mensaje = ""
        respuesta = mb.askyesno("Advertencia", "¿Estas seguro de querer desactivar esta tarjeta?")
        if respuesta:pass
        else:
            self.campo_tolerancia.focus()
            return

        vigencia = self.variable_vigencia.get()
        if vigencia == 'None':vigencia = None

        if vigencia == None:
            mb.showinfo("Alerta", "La tarjeta ya esta desactivada, para reactivar la tarjeta es necesario realizar un pago de la pensión para asignar nueva fecha de vigencia")
            self.campo_tolerancia.focus()
            return

        respuesta = mb.askyesno("Advertencia", "¿La desactivación es temporal?")

        if respuesta:
            self.variable_estatus.set("InactivaTemp")
            mensaje = "temporalmente"

        else:
            self.variable_estatus.set("InactivaPerm")
            mensaje = "permanentemente"

        if vigencia:
            self.variable_vigencia.set(None)
            mb.showinfo("Alerta", f"Se ha desactivado {mensaje} la tarjeta")
            self.modificar_pensionado()


    def modificar_pensionado(self):
        """ Modifica los datos del pensionado en la base de datos."""
        try:
            # Obtener los datos del formulario
            variable_numero_tarjeta = self.variable_numero_tarjeta.get()
            variable_nombre = self.variable_nombre.get()
            variable_apellido_1 = self.variable_apellido_1.get()
            variable_apellido_2 = self.variable_apellido_2.get()

            variable_telefono_1 = self.variable_telefono_1.get()
            variable_telefono_2 = self.variable_telefono_2.get()
            variable_ciudad = self.variable_ciudad.get()
            variable_colonia = self.variable_colonia.get()
            variable_cp = self.variable_cp.get()
            variable_numero_calle = self.variable_numero_calle.get()

            variable_placas = self.variable_placas.get()
            variable_auto_modelo = self.variable_auto_modelo.get()
            variable_auto_color = self.variable_auto_color.get()

            variable_monto = int(self.variable_monto.get())
            variable_cortesia = self.variable_cortesia.get()
            variable_tolerancia = self.variable_tolerancia.get()
            fecha_modificación_pensionado = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            vigencia = self.variable_vigencia.get()
            if vigencia == "None":vigencia = None
            estatus = self.variable_estatus.get()


            if len(variable_numero_tarjeta) == 0 or len(variable_nombre) == 0 or len(variable_apellido_1) == 0 or len(variable_apellido_2) == 0 or len(variable_telefono_1) == 0 or len(variable_telefono_2) == 0 or len(variable_ciudad) == 0 or len(variable_colonia) == 0 or len(variable_cp) == 0 or len(variable_numero_calle) == 0 or len(variable_placas) == 0 or len(variable_auto_modelo) == 0 or len(variable_auto_color) == 0 or len(str(variable_monto)) == 0 or len(variable_cortesia) == 0 or variable_tolerancia == 0:raise IndexError("No dejar campos en blanco")

            if variable_cortesia == "No" and variable_monto == 0:raise IndexError("Ingrese el monto a pagar")
            if variable_cortesia == "Si":variable_monto = 0

            datos_pensionado = (variable_numero_tarjeta, variable_nombre, variable_apellido_1, variable_apellido_2, variable_telefono_1, variable_telefono_2, variable_ciudad, variable_colonia, variable_cp, variable_numero_calle, variable_placas, variable_auto_modelo, variable_auto_color, variable_monto, variable_cortesia, variable_tolerancia, fecha_modificación_pensionado, vigencia, estatus)

            self.query.actualizar_pensionado(datos_pensionado=datos_pensionado, Num_tarjeta = variable_numero_tarjeta)
            mb.showinfo("Información", "El pensionado fue modificado correctamente")
            self.desconectar()

        except IndexError as e:
            traceback.print_exc()
            mb.showerror("Error", e)
        except ValueError as e:
            traceback.print_exc()
            mb.showerror("Error", e)
        except Exception as e:
            traceback.print_exc()
            mb.showerror("Error", e)

    def desconectar(self):
        """ Cierra la ventana principal y detiene el hilo en el que se ejecuta. """
        self.panel_crud.quit()
        self.panel_crud.destroy()

