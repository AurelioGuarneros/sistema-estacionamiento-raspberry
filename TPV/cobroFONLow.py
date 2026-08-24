import os
from datetime import datetime, date, timedelta
from tkinter import messagebox as mb

from escpos.printer import Usb, USBNotFoundError

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import scrolledtext as st

from tkinter import *
from tkinter import simpledialog

from operacion_tpv import Operacion
import xlsxwriter
penalizacion_con_importe = False
from dateutil.relativedelta import relativedelta
from view_login import View_Login
from queries import Pensionados
from view_agregar_pensionado import View_agregar_pensionados
from view_modificar_pensionado import View_modificar_pensionados
import traceback
import math

from atexit import register
from reloj import RelojAnalogico
from time import sleep
from controller_email import main, send_other_corte

from threading import Thread
from os import path, listdir, makedirs
from controller_email import ToolsEmail
tools = ToolsEmail()

###--###
data_rinter = (0x04b8, 0x0e28, 0)

contraseña_pensionados = os.environ.get("ESTACIONAMIENTO_PASSWORD_PENSIONADOS", "")

valor_tarjeta = 116
valor_reposiion_tarjeta = 232
penalizacion_diaria_pension = 0

logo_1 = "LOGO1.jpg"
AutoA = "AutoA.png"

qr_imagen = "reducida.png"
PROMOCIONES = ("Promo1", "BA BODEGA AURRERA")
nombre_estacionamiento = 'Hidalgo 401'

estilo = ('Arial', 12)
font_entrada = ('Arial', 20)
font_entrada_negritas = ('Arial', 20, 'bold')
font_mensaje = ('Arial', 40)
font_reloj = ('Arial', 65)
font_cancel = ('Arial', 15)

button_color = "#062546"#"#39acec""#6264d4"
button_letters_color = "white" 

from controller_email import main

show_clock = False
send_data = True
pantalla_completa = True
required_plate = False

class FormularioOperacion:
    def __init__(self):
        if send_data:
            register(main)

        self.controlador_crud_pensionados = Pensionados()
        self.folio_auxiliar = None

        self.DB=Operacion()
        self.root=tk.Tk()
        self.root.title(f"{nombre_estacionamiento} COBRO")

        if pantalla_completa:
            # Obtener el ancho y alto de la pantalla
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # Configura la ventana para que ocupe toda la pantalla
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Colocar el LabelFrame en las coordenadas calculadas
        principal = tk.LabelFrame(self.root)
        principal.pack(expand=True, padx=5, pady=5, anchor='n')

        self.cuaderno1 = ttk.Notebook(principal)
        # Asociar el evento <<NotebookTabChanged>> a la función on_tab_changed
        self.cuaderno1.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.cuaderno1.config(cursor="")         # Tipo de cursor
        self.ExpedirRfid()
        self.check_inputs()
        self.consulta_por_folio()
        self.listado_completo()
        self.interface_pensionados()
        self.cuaderno1.grid(column=0, row=0, padx=2, pady=5)
        if show_clock:
            self.reloj = RelojAnalogico()

        self.root.mainloop()


    def ExpedirRfid(self):
        seccion_entrada = tk.Frame(self.cuaderno1)
        self.cuaderno1.add(seccion_entrada, text="Expedir Boleto")

        seccion_entrada = tk.Frame(seccion_entrada)

        seccion_entrada.grid(column=0, row=0, padx=2, pady=2, sticky=tk.NSEW)

        frame_bienvenida = tk.Frame(seccion_entrada)
        frame_bienvenida.grid(column=0, row=0, padx=2, pady=2)

        frame_mensaje_bienvenida = tk.Frame(frame_bienvenida)
        frame_mensaje_bienvenida.grid(column=0, row=0, padx=2, pady=2)

        # Asegura que la fila y la columna del frame se expandan con el contenedor
        frame_mensaje_bienvenida.grid_rowconfigure(0, weight=1)
        frame_mensaje_bienvenida.grid_columnconfigure(0, weight=1)

        label_entrada = tk.Label(frame_mensaje_bienvenida, text=f"Bienvenido(a) al estacionamiento {nombre_estacionamiento}", font=('Arial', 25), justify='center')
        label_entrada.grid(row=0, column=0)



        frame_datos_entrada = tk.Frame(seccion_entrada)
        frame_datos_entrada.grid(column=0, row=1, padx=2, pady=2)

        frame_info_cliente=tk.Frame(frame_datos_entrada)
        frame_info_cliente.grid(column=0, row=0, padx=2, pady=2)

        frame_info_placa=tk.Frame(frame_info_cliente)
        frame_info_placa.grid(column=0, row=0, padx=2, pady=2)

        label_placa=tk.Label(frame_info_placa, text="Ingrese Placa", font=('Arial', 25))
        label_placa.grid(column=0, row=0, padx=2, pady=2)

        self.Placa=tk.StringVar()
        self.entry_placa=tk.Entry(frame_info_placa, width=20, textvariable=self.Placa, font=('Arial', 35, 'bold'), justify='center')
        self.entry_placa.grid(column=0, row=1, padx=2, pady=2)



        frame_boton=tk.Frame(frame_datos_entrada)
        frame_boton.grid(column=2, row=0, padx=2, pady=2)

        frame_folio = tk.Frame(frame_boton)
        frame_folio.grid(column=0, row=0, padx=2, pady=2)

        label_folio=tk.Label(frame_folio, text="Folio:", font=font_entrada)
        label_folio.grid(column=0, row=0, padx=2, pady=2, sticky="nsew")
        self.MaxId=tk.StringVar()
        entryMaxId=ttk.Entry(frame_folio, width=12, textvariable=self.MaxId, state="readonly", font=font_entrada)
        entryMaxId.grid(column=1, row=0, padx=2, pady=2, sticky=tk.NW)

        boton_entrada=tk.Button(frame_boton, text="Generar Entrada", width=15, height=3, anchor="center", background=button_color, fg=button_letters_color, font=font_entrada_negritas, command=self.agregarRegistroRFID)
        boton_entrada.grid(column=0, row=1, padx=2, pady=2)
        

        frame_info = tk.LabelFrame(seccion_entrada)#, background = '#CCC')
        frame_info.grid(column=0, row=2, padx=2, pady=2)

        self.label_informacion = tk.Label(frame_info, text="... ", width=25, font=font_mensaje, justify='center')
        self.label_informacion.grid(column=0, row=0, padx=2, pady=2)



        frame_reloj = tk.Frame(seccion_entrada)
        frame_reloj.grid(column=0, row=3, padx=2, pady=2)

        self.Reloj = tk.Label(frame_reloj, text="Reloj", background="white", font=font_reloj, justify='center')
        self.Reloj.grid(column=0, row=0, padx=2, pady=2)
        self.entry_placa.focus()

    def check_inputs(self):
        fecha_hora =datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        self.Reloj.config(text=fecha_hora)            
        self.root.after(60, self.check_inputs)

    def agregarRegistroRFID(self):
        placa=self.Placa.get()
        if not placa and required_plate:
            self.label_informacion.config(text=f"Error: Ingrese una placa")
            return

        MaxFolio=self.DB.MaxfolioEntrada()
        folio_boleto = int(MaxFolio) + 1
        self.MaxId.set(folio_boleto)

        folio_cifrado = self.DB.cifrar_folio(folio = folio_boleto)
        # print(f"QR entrada: {folio_cifrado}")

        #Generar QR
        self.DB.generar_QR(folio_cifrado)

        fechaEntro = datetime.today()

        horaentrada = str(fechaEntro)
        horaentrada=horaentrada[:19]
        # self.labelhr.configure(text=(horaentrada[:-3], "Entro"))
        corteNum = 0
        datos=(fechaEntro, corteNum, placa)

        printer = Usb(0x04b8, 0x0e28, 0)

        printer.image(logo_1)
        printer.text("--------------------------------------\n")
        printer.set(align="center")
        printer.text("BOLETO DE ENTRADA\n")
        printer.text('Entro: '+horaentrada[:-3]+'\n')
        printer.text('Placas '+placa+'\n')
        printer.text(f'Folio 000{folio_boleto}\n')

        printer.set(align = "center")
        printer.image(qr_imagen)

        printer.text("--------------------------------------\n")
        printer.cut()

        printer.close()

        self.DB.altaRegistroRFID(datos)
        self.Placa.set('')
        self.label_informacion.config(text="Se genera boleto")

    #########################fin de pagina1 inicio pagina2#########################
    def consulta_por_folio(self):
        self.pagina2 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina2, text=" Modulo de Cobro")
        #en el frame
        self.FOLIO_QR=tk.LabelFrame(self.pagina2, text="FOLIO_QR")
        self.FOLIO_QR.grid(column=0, row=0, padx=2, pady=10, sticky=tk.NW)

        self.labelframe2=tk.LabelFrame(self.FOLIO_QR, text="Autos")
        self.labelframe2.grid(column=0, row=0, padx=2, pady=10, sticky=tk.NW)
        self.label1=tk.Label(self.labelframe2, text="Lector QR")
        self.label1.grid(column=0, row=0, padx=4, pady=4)
        self.label3=tk.Label(self.labelframe2, text="Entro:")
        self.label3.grid(column=0, row=1, padx=4, pady=4)
        self.label4=tk.Label(self.labelframe2, text="Salio:")
        self.label4.grid(column=0, row=2, padx=4, pady=4)


        self.labelpromo=tk.LabelFrame(self.FOLIO_QR, text="Leer el QR de Promocion")
        self.labelpromo.grid(column=0, row=1, padx=2, pady=10, sticky=tk.NW)
        self.promolbl1=tk.Label(self.labelpromo, text="Codigo QR")
        self.promolbl1.grid(column=0, row=0, padx=4, pady=4)
        self.promolbl2=tk.Label(self.labelpromo, text="Tipo Prom")
        self.promolbl2.grid(column=0, row=1, padx=4, pady=4)

        #creamos un objeto para obtener la lectura de la PROMOCION
        self.promo=tk.StringVar()
        self.entrypromo=tk.Entry(self.labelpromo, textvariable=self.promo, justify='center')
        self.entrypromo.bind('<Return>',self.CalculaPromocion)#con esto se lee automatico
        self.entrypromo.grid(column=1, row=0, padx=4, pady=4)           
        #este es donde pongo el tipo de PROMOCION
        self.PrTi=tk.StringVar()
        self.entryPrTi=tk.Entry(self.labelpromo, width=20, textvariable=self.PrTi, state= "readonly", justify='center')
        self.entryPrTi.grid(column=1, row=1)
        #botones


        self.labelcuantopagas=tk.LabelFrame(self.FOLIO_QR, text='cual es el pago')
        self.labelcuantopagas.grid(column=0,row=2, padx=2, pady=10, sticky=tk.NW)
        self.cuantopagas=tk.Label(self.labelcuantopagas, text="la cantidad entregada")
        self.cuantopagas.grid(column=0, row=0, padx=4, pady=4)
        self.importees=tk.Label(self.labelcuantopagas, text="el importe es")
        self.importees.grid(column=0, row=1, padx=4, pady=4)
        self.cambio=tk.Label(self.labelcuantopagas, text="el cambio es")
        self.cambio.grid(column=0, row=2, padx=4, pady=4)
        self.cuantopagasen=tk.StringVar()
        self.cuantopagasen.set(100)
        self.entrycuantopagasen=tk.Entry(self.labelcuantopagas, width=15, textvariable=self.cuantopagasen, justify='center')
        #self.entrycuantopagasen.bind('<Return>',self.calcular_cambio)
        self.entrycuantopagasen.grid(column=1, row=0)
        self.elimportees=tk.StringVar()
        self.entryelimportees=tk.Entry(self.labelcuantopagas, width=15, textvariable=self.elimportees, state="readonly", justify='center')
        self.entryelimportees.grid(column=1, row=1)
        self.elcambioes=tk.StringVar()
        self.entryelcambioes=tk.Entry(self.labelcuantopagas, width=15, textvariable=self.elcambioes, state="readonly", justify='center')
        self.entryelcambioes.grid(column=1, row=2)


        #en otro frame
        self.labelframe3_principal=tk.LabelFrame(self.pagina2, text="Datos del COBRO")
        self.labelframe3_principal.grid(column=1, row=0, pady=10, sticky=tk.NW)

        self.labelframe3=tk.LabelFrame(self.labelframe3_principal, text="Tiempo y Salida")
        self.labelframe3.grid(column=0, row=0, padx=2, pady=10, sticky=tk.NW)
        self.lbl1=tk.Label(self.labelframe3, text="Hr Salida")
        self.lbl1.grid(column=0, row=1, padx=4, pady=4)
        self.lbl2=tk.Label(self.labelframe3, text="TiempoTotal")
        self.lbl2.grid(column=0, row=2, padx=4, pady=4)
        self.lbl3=tk.Label(self.labelframe3, text="Importe")
        self.lbl3.grid(column=0, row=3, padx=4, pady=4)


        self.IImporte = tk.Label(self.labelframe3, text="") #Creacion del Label
        self.IImporte.config(width =4)
        self.IImporte.config(background="white") #Cambiar color de fondo
        self.IImporte.config(font=('Arial', 48)) #Cambiar tipo y tamaño de fuente
        self.IImporte.grid(column=1, row=4, padx=0, pady=0)   


        #se crea objeto para MOSTRAR LA HORA DEL CALCULO
        self.copia_fecha_salida = tk.StringVar()
        self.entry_copia_fecha_salida=tk.Entry(self.labelframe3, width=15, textvariable=self.copia_fecha_salida, state = "readonly")
        self.entry_copia_fecha_salida.grid(column=1, row=1)

        #SE CREA UN OBJETO caja de texto IGUAL A LOS DEMAS Y MUESTRA EL TOTAL DEL TIEMPO
        self.TiempoTotal=tk.StringVar()
        self.TiempoTotal_auxiliar=tk.StringVar()
        self.entryTiempoTotal=tk.Entry(self.labelframe3, width=15, textvariable=self.TiempoTotal_auxiliar, state= "readonly")
        self.entryTiempoTotal.grid(column=1, row=2)
        #SE CREA UN OBJETO caja de texto IGUAL A LOS DEMAS para mostrar el importe y llevarlo a guardar en BD
        self.importe=tk.StringVar()
        self.entryimporte=tk.Entry(self.labelframe3, width=15, textvariable=self.importe, state= "readonly")
        self.entryimporte.grid(column=1, row=3)

        self.scrol_datos_boleto_cobrado=st.ScrolledText(self.labelframe3_principal, width=28, height=7)
        self.scrol_datos_boleto_cobrado.grid(column=0,row=2, padx=1, pady=1)

        self.label15=tk.Label(self.labelframe3_principal, text="Viabilidad de COBRO")
        self.label15.grid(column=0, row=3, padx=0, pady=0)

        self.labelPerdido_principal=tk.LabelFrame(self.pagina2, text="")
        self.labelPerdido_principal.grid(column=2,row=0, pady=10, sticky=tk.NW)

        self.labelPerdido=tk.LabelFrame(self.labelPerdido_principal, text="Boleto Perdido/Dañado")
        self.labelPerdido.grid(column=0,row=0,padx=2, pady=10, sticky=tk.NW)


        self.label_frame_folio=tk.LabelFrame(self.labelPerdido, text="FOLIO")
        self.label_frame_folio.grid(column=0,row=0,padx=2, pady=10, sticky=tk.NW)


        self.lblFOLIO=tk.Label(self.label_frame_folio, text="INGRESE FOLIO", font=("Arial", 11))
        self.lblFOLIO.grid(column=0, row=0, sticky=tk.NW,padx=2, pady=5)

        self.PonerFOLIO=tk.StringVar()
        self.entryPonerFOLIO=tk.Entry(self.label_frame_folio, width=15, textvariable=self.PonerFOLIO, font=("Arial", 11), justify='center')
        self.entryPonerFOLIO.grid(column=1, row=0, sticky=tk.NW,padx=2, pady=5)


        self.label_botones_boletos_perdido=tk.LabelFrame(self.labelPerdido, text="BOLETO DAÑADO/PERDIDO")
        self.label_botones_boletos_perdido.grid(column=0,row=1,padx=2, pady=10, sticky=tk.NW)

        self.boton_boleto_dañado=tk.Button(self.label_botones_boletos_perdido, text="Boleto\nDañado", background=button_color, fg=button_letters_color, command=self.BoletoDañado, width=10, height=3, anchor="center", font=("Arial", 10))
        self.boton_boleto_dañado.grid(column=0, row=1, sticky=tk.NE, padx=10, pady=5)

        self.boton3=tk.Button(self.label_botones_boletos_perdido, text="Boleto Perdido\nCON FOLIO", background=button_color, fg=button_letters_color, command=self.BoletoPerdido_conFolio, width=10, height=3, anchor="center", font=("Arial", 10))
        self.boton3.grid(column=1, row=1, sticky=tk.NE, padx=10, pady=5)

        self.boton3=tk.Button(self.label_botones_boletos_perdido, text="Boleto Perdido\nSIN FOLIO", background=button_color, fg=button_letters_color, command=self.BoletoPerdido_sinFolio, width=10, height=3, anchor="center", font=("Arial", 10))
        self.boton3.grid(column=2, row=1, sticky=tk.NE, padx=10, pady=5)


        self.labelPerdido2=tk.LabelFrame(self.labelPerdido_principal, text="Boletos sin cobro")
        self.labelPerdido2.grid(column=0,row=1,padx=2, pady=10, sticky=tk.NW)

        self.boton2=tk.Button(self.labelPerdido2, text="B./SIN cobro", command=self.BoletoDentro, width=10, height=2, anchor="center", background=button_color, fg=button_letters_color)
        self.boton2.grid(column=0, row=0)

        self.scrolledtxt=st.ScrolledText(self.labelPerdido2, width=28, height=7)
        self.scrolledtxt.grid(column=1,row=0, padx=10, pady=10)




        #se crea objeto para ver pedir el folio la etiqueta con texto
        self.folio=tk.StringVar()
        self.entryfolio=tk.Entry(self.labelframe2, textvariable=self.folio, justify='center')
        self.entryfolio.bind('<Return>',self.consultar)#con esto se lee automatico y se va a consultar
        self.entryfolio.grid(column=1, row=0, padx=4, pady=4)
        #se crea objeto para mostrar el dato de la  Entrada solo lectura
        self.fecha_entrada=tk.StringVar()
        self.entry_fecha_entrada=ttk.Entry(self.labelframe2, textvariable=self.fecha_entrada, state="readonly",  width=15)
        self.entry_fecha_entrada.grid(column=1, row=1, padx=4, pady=4, sticky=tk.NW)

        #se crea objeto para mostrar el dato la Salida solo lectura
        self.fecha_salida=tk.StringVar()
        self.entry_fecha_salida=ttk.Entry(self.labelframe2, textvariable=self.fecha_salida, state="readonly",  width=15)
        self.entry_fecha_salida.grid(column=1, row=2, padx=4, pady=4, sticky=tk.NW)

        #creamos un objeto para obtener la lectura de la PROMOCION
        self.promo=tk.StringVar()
        self.promo_auxiliar=tk.StringVar()
        self.entrypromo=tk.Entry(self.labelpromo, textvariable=self.promo, justify='center')
        self.entrypromo.bind('<Return>',self.CalculaPromocion)#con esto se lee automatico
        self.entrypromo.grid(column=1, row=0, padx=4, pady=4)           
        #este es donde pongo el tipo de PROMOCION
        self.TarifaPreferente=tk.StringVar()
        self.entryTarifaPreferente=tk.Entry(self.labelpromo, width=20, textvariable=self.TarifaPreferente, state= "readonly", justify='center')
        self.entryTarifaPreferente.grid(column=1, row=1)
        #botones


        self.bcambio=tk.Button(self.labelcuantopagas, text="Cobro", command=self.calcular_cambio, width=10, height=2, anchor="center", background=button_color, fg=button_letters_color)
        self.bcambio.grid(column=0, row=4)

        self.BoletoDentro()

    def BoletoDentro(self):
        respuesta=self.DB.Autos_dentro()
        self.scrolledtxt.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtxt.insert(tk.END, "Folio num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\nPlacas: "+str(fila[2])+"\n\n")

    def BoletoPerdido_conFolio(self):
        """
        Esta funcion se encarga de manejar el cobro de un boleto perdido con folio.

        Verifica si se ha ingresado un número de folio para el boleto perdido y realiza las operaciones correspondientes.
        Calcula la permanencia del vehículo y el importe a cobrar.
        Establece el concepto del boleto como "Per" de perdido.

        :param self: Objeto de la clase que contiene los atributos y métodos necesarios.

        :return: None
        """

        datos = self.PonerFOLIO.get()

        if len(datos) == 0:
            mb.showerror("Error", "Ingrese un folio")
            return

        self.folio.set(datos)
        datos = self.folio.get()
        self.folio_auxiliar = datos
        importe = 0

        # Consultar los datos correspondientes al folio
        respuesta = self.DB.consulta(datos)
        if len(respuesta) > 0:
            # Establecer la descripcion y precio basados en la respuesta
            self.fecha_entrada.set(respuesta[0][0])
            self.fecha_salida.set(respuesta[0][1])
            self.Placa.set(respuesta[0][6])

            # Calcular la permanencia
            self.CalculaPermanencia()

            if penalizacion_con_importe:

                # Calcular el importe basado en las horas y días de permanencia
                if self.horas_dentro <= 24:
                    importe = 200
                elif self.horas_dentro > 24 or self.dias_dentro >= 1:
                    importe = 200 + ((self.dias_dentro) * 720 + (self.horas_dentro * 30))

            else:
                importe = 200

            # Establecer el importe y mostrarlo
            self.mostrar_importe(importe)

            # Realizar otras operaciones y configuraciones
            self.TarifaPreferente.set("Per")
            self.promo.set("")
            self.PonerFOLIO.set("")

            if show_clock:
                self.reloj.update_data(self.TarifaPreferente.get(), importe)

        else:
            # Limpiar campos y mostrar mensaje de error
            self.limpiar_campos()
            mb.showinfo("Informacion", "No existe un auto con dicho codigo")

    def BoletoPerdido_sinFolio(self):
        """
        Esta funcion se encarga de imprimir un boleto perdido sin un número de folio especificado.

        Verifica si se ha confirmado la impresion del boleto perdido.
        Genera un boleto nuevo para poder cobrar boletos que han sido extraviados.
        Agrega el registro del pago a la base de datos.

        :return: None
        """
        Boleto_perdido = mb.askokcancel("Advertencia", f"¿Esta seguro de imprimir un boleto perdido?")

        if Boleto_perdido == False:
            return

        MaxFolio = self.DB.MaxfolioEntrada()
        folio_boleto = MaxFolio + 1
        self.MaxId.set(folio_boleto)

        fechaEntro = datetime.today()
        horaentrada = str(fechaEntro)
        horaentrada=horaentrada[:19]
        corteNum = 0
        placa="BoletoPerdido"
        datos=(fechaEntro, corteNum, placa)

        #aqui lo imprimimos
        printer = Usb(0x04b8, 0x0e28, 0)

        printer.image(logo_1)
        printer.text("--------------------------------------\n")
        printer.set(align = "center")
        printer.text("B O L E T O  P E R D I D O\n")
        printer.set(align="center")
        printer.text("BOLETO DE ENTRADA\n")
        printer.text('Entro: '+horaentrada[:-3]+'\n')
        printer.text('Placas '+placa+'\n')
        printer.text(f'Folio 000{folio_boleto}\n')
        printer.set(align = "center")
        printer.text("B O L E T O  P E R D I D O\n")
        printer.text("--------------------------------------\n")

        printer.cut()
        printer.close()

        #Agregar registro del pago a la base de datos
        self.DB.altaRegistroRFID(datos)
        self.Placa.set('')

        self.BoletoDentro()

    def consultar(self, event):
        # Vaciar campo de importe
        self.IImporte.config(text="")

        # Obtener folio
        datos=str(self.folio.get())

        # Si la caja de texto esta vacia limpia la informacion en pantalla
        if len(datos) == 0:
            self.limpiar_campos()
            self.entryfolio.focus()
            return

        #Verificar si lee el folio o la promocion
        if len(datos) > 20:

            mb.showinfo("Promocion", "leer primero el folio")
            self.limpiar_campos()
            self.entryfolio.focus()
            return

        # folio = datos[26:]
        folio = self.DB.descifrar_folio(folio_cifrado = datos)
        self.folio.set(folio)
        folio = self.folio.get()
        self.folio_auxiliar = folio
        print(f"\nFolio descifrado: {folio}")

        respuesta=self.DB.consulta(folio)
        if len(respuesta) == 0:
            mb.showinfo("Informacion", "No existe un auto con dicho codigo")
            self.limpiar_campos()
            return

        self.fecha_entrada.set(respuesta[0][0])
        self.fecha_salida.set(respuesta[0][1])
        self.Placa.set(respuesta[0][6])
        self.CalculaPermanencia()#nos vamos a la funcion de calcular permanencia

    def calcular_tarifa_hidalgo401(self, dias, horas, minutos, tarifa):
        """
        Calcula la tarifa del estacionamiento Hidalgo 401 usando
        exclusivamente los importes del desglose proporcionado.

        Tarifas del desglose:
            Bodega Aurrera: 0-2 h = $5; 3-24 h según tabla.
            Público general: 1-24 h según tabla.

        Nota:
            El documento no especifica una regla para minutos entre
            horas completas. Para no inventar importes intermedios,
            esta implementación redondea hacia la siguiente hora
            cuando existen minutos adicionales.

        Retorna None si el tiempo supera 24 horas.
        """

        try:
            dias = int(dias)
            horas = int(horas)
            minutos = int(minutos)
        except (TypeError, ValueError):
            return None

        # Tiempo total real en minutos, incluyendo los días.
        minutos_totales = (dias * 24 * 60) + (horas * 60) + minutos

        # Boleto sellado Bodega Aurrera.
        # El desglose indica 0 a 2 horas = $5.
        if tarifa in ("BA", "BA BODEGA AURRERA", "BA Aurrera 2H"):
            if minutos_totales <= 120:
                return 5

        if minutos_totales <= 10:
            return 10

        # El desglose proporcionado termina en 24 horas.
        if minutos_totales > 24 * 60:
            return None

        # Cualquier minuto adicional hace que se tome la siguiente
        # hora completa de la tabla.
        horas_cobradas = (minutos_totales + 59) // 60

        # Boleto sellado Bodega Aurrera: 3 a 24 horas.
        if tarifa in ("BA", "BA BODEGA AURRERA", "BA Aurrera 2H"):

            tarifas_ba = {
                3: 15,
                4: 25,
                5: 35,
                6: 45,
                7: 55,
                8: 65,
                9: 75,
                10: 85,
                11: 95,
                12: 105,
                13: 115,
                14: 125,
                15: 135,
                16: 145,
                17: 155,
                18: 165,
                19: 175,
                20: 185,
                21: 195,
                22: 205,
                23: 215,
                24: 225,
            }
            return tarifas_ba.get(horas_cobradas)

        # Público en general.
        tarifas_normal = {
            1: 10,
            2: 20,
            3: 30,
            4: 40,
            5: 50,
            6: 60,
            7: 70,
            8: 80,
            9: 90,
            10: 100,
            11: 110,
            12: 120,
            13: 130,
            14: 140,
            15: 150,
            16: 160,
            17: 170,
            18: 180,
            19: 190,
            20: 200,
            21: 210,
            22: 220,
            23: 230,
            24: 240,
        }
        return tarifas_normal.get(horas_cobradas)


    def CalculaPermanencia(self):
        """
        Esta funcion calcula la permanencia del folio seleccionado.

        Realiza diferentes cálculos basados en la informacion del boleto y actualiza los valores correspondientes.

        :param self: Objeto de la clase que contiene los atributos y métodos necesarios.

        :return: None
        """
        # Borra el valor actual del importe
        self.IImporte.config(text="")

        # Obtiene el valor de salida
        salida = self.fecha_salida.get()

        if len(salida) > 5:
            # Si el valor de salida tiene más de 5 caracteres, significa que ya ha sido cobrado
            self.label15.configure(text=("Este Boleto ya Tiene cobro"))

            # Realiza una consulta con el folio seleccionado para obtener informacion adicional del boleto
            respuesta = self.DB.consulta({self.folio.get()})

            # Imprime en una caja de texto la informacion del boleto cuando ya ha sido cobrado
            self.scrol_datos_boleto_cobrado.delete("1.0", tk.END)
            for fila in respuesta:
                self.scrol_datos_boleto_cobrado.insert(
                    tk.END,
                    f"Folio: {fila[2]}\nEntro: {str(fila[0])[:-3]}\nSalio: {str(fila[1])[:-3]}\nTiempo: {str(fila[3])[:-3]}\nTarifa: {fila[4]}\nImporte: {fila[5]}"
                )

            pregunta = mb.askyesno("Advertencia", "Este boleto ya tiene cobro ¿Desea reimprimir el comprobante de pago?")

            if pregunta:

                Entrada = respuesta[0][0]
                Salida = respuesta[0][1]

                folio = respuesta[0][2]
                TiempoTotal = str(respuesta[0][3])
                TarifaPreferente = respuesta[0][4]
                Importe = respuesta[0][5]
                Placas = respuesta[0][6]

                self.Placa.set(Placas)
                self.folio.set(folio)
                self.TarifaPreferente.set(TarifaPreferente)
                self.importe.set(Importe)
                self.fecha_entrada.set(Entrada)
                self.copia_fecha_salida.set(Salida)
                self.TiempoTotal.set(TiempoTotal)

                # La reimpresion tambien debe incluir el QR que se presenta
                # en la salida del estacionamiento.
                self.Comprobante(titulo='REIMPRESION', QR_salida=True)

            # Reinicia los valores de varios atributos
            self.limpiar_campos()
            return

        # Si el valor de salida tiene menos de 5 caracteres, significa que no ha sido cobrado
        self.scrol_datos_boleto_cobrado.delete("1.0", tk.END)
        self.TarifaPreferente.set("Normal")
        self.label15.configure(text="Lo puedes COBRAR")

        # Obtiene la fecha actual
        Salida = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        Salida = datetime.strptime(Salida, '%Y-%m-%d %H:%M:%S')

        self.copia_fecha_salida.set(Salida)


        # Obtiene la fecha del boleto seleccionado y realiza las conversiones necesarias
        Entrada = self.fecha_entrada.get()
        Entrada = datetime.strptime(Entrada, '%Y-%m-%d %H:%M:%S')

        TiempoTotal = Salida - Entrada

        # Calcula la diferencia en días, horas y minutos
        self.dias_dentro = TiempoTotal.days
        segundos_vividos = TiempoTotal.seconds

        self.horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
        self.minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)

        self.TiempoTotal.set(TiempoTotal)
        self.TiempoTotal_auxiliar.set(self.TiempoTotal.get()[:-3])

        # Calcula el importe de acuerdo con el desglose de tarifas
        # proporcionado para Hidalgo 401.
        #
        # El desglose solamente contempla tarifas hasta 24 horas.
        # Los minutos que exceden una hora completa se consideran
        # como la siguiente hora de la tabla. Esta regla es una
        # decisión de implementación porque el desglose no especifica
        # expresamente cómo cobrar minutos intermedios.
        importe = self.calcular_tarifa_hidalgo401(
            dias=self.dias_dentro,
            horas=self.horas_dentro,
            minutos=self.minutos_dentro,
            tarifa=self.TarifaPreferente.get()
        )

        if importe is None:
            mb.showwarning(
                "Tiempo excedido",
                "El desglose de tarifas proporcionado contempla\n"
                "hasta 24 horas. No se puede calcular automáticamente\n"
                "un importe para una permanencia mayor a 24 horas."
            )
            self.importe.set("")
            self.IImporte.config(text="")
            self.entrypromo.focus()
            return

        # Establecer el importe y mostrarlo
        self.mostrar_importe(importe)

        # Coloca el foco en el campo entrypromo
        self.entrypromo.focus()

        if show_clock:
            self.reloj.set_time(
                entrada=str(Entrada),
                salida=str(Salida),
                days = self.dias_dentro,
                hour= self.horas_dentro,
                minute= self.minutos_dentro,
                seconds= segundos_vividos,
                importe=importe)

            # Espera un segundo para que de tiempo a cargar la animacion
            sleep(0.5)

    def calcular_cambio(self):
        folio = self.folio.get()
        if len(folio) == 0:
            mb.showerror("Error", "Error vuelva a escanear el QR del boleto")

            # Reinicia los valores de varios atributos
            self.limpiar_campos()
            return

        if self.folio_auxiliar != folio:
            mb.showerror("Error", "Error vuelva a escanear el QR del boleto")

            # Reinicia los valores de varios atributos
            self.limpiar_campos()
            return

        elimporte=str(self.importe.get(), )
        self.elimportees.set(elimporte)
        valorescrito=str(self.cuantopagasen.get(),)
        elimporte=float(elimporte)
        valorescrito=int(valorescrito)

        cambio=valorescrito-elimporte
        cambio=str(cambio)

        self.elcambioes.set(cambio)

        self.GuardarCobro()

        self.Comprobante()
        self.Comprobante(titulo='CONTRA', imagen_logo=False, QR_salida = True)

        self.limpiar_campos()


    def Comprobante(self, titulo: str = 'Comprobante de pago', imagen_logo: bool = True, QR_salida: bool = False) -> None:
        """Genera un comprobante de pago o un boleto cancelado.

        Args:
            titulo (str, optional): El título del comprobante. Por defecto es 'Comprobante de pago'.
            imagen_logo (bool, optional): Indica si se debe imprimir una imagen de logo en el comprobante. Por defecto es True.
            QR_salida (bool, optional): Indica si se debe imprimir un codigo QR de salida en el comprobante. Por defecto es False.
        """

        # Obtiene los valores de diferentes variables desde las variables de control
        Placa = self.Placa.get()
        Folio = self.folio.get()
        TarifaPreferente = self.TarifaPreferente.get()
        Importe = self.importe.get()
        Entrada = self.fecha_entrada.get()[:-3]
        Salida = self.copia_fecha_salida.get()[:-3]
        TiempoTotal = self.TiempoTotal.get()[:-3]

        valor = 'N/A'
        # Configuracion de la impresora
        printer = Usb(0x04b8, 0x0e28, 0)
        printer.set(align="center")
        printer.text(f"{titulo}\n")

        if titulo == "Boleto Cancelado":
            # Seccion de comprobante para boletos cancelados
            printer.set(align="left")

            printer.text(f'Folio boleto cancelado: {Folio}\n')
            printer.text(f'El auto entro: {Entrada}\n')
            printer.text(f'El auto salio: {Salida}\n')
            printer.text(f'Motivo: {self.motive_cancel.get()}\n')
        else:
            # Seccion de comprobante para pagos normales o boletos perdidos

            if Placa == "BoletoPerdido":
                # Si es un boleto perdido, muestra un mensaje especial
                printer.text("BOLETO PERDIDO\n")
                Entrada = valor
                Salida = valor
                TiempoTotal = valor

            if imagen_logo:
                # Imprimir el logo si está habilitado
                printer.image(logo_1)
                print("Imprime logo")

            printer.set(align="left")
            printer.text("El importe es: $" + Importe + "\n")
            printer.text('El auto entro: ' + Entrada + '\n')
            printer.text('El auto salio: ' + Salida + '\n')
            printer.text('El auto permanecio: ' + TiempoTotal + '\n')
            printer.text('El folio del boleto es: ' + Folio + '\n')
            printer.text('TIPO DE COBRO: ' + TarifaPreferente + '\n')

            if QR_salida:
                # SalidaFONLow.py separa los primeros 19 caracteres como
                # fecha/hora y toma el resto como numero de folio.
                entrada_qr = str(self.fecha_entrada.get())[:19]
                qr = entrada_qr + Folio
                # print(qr)
                self.DB.generar_QR(qr)
                # Imprimir el codigo QR de salida si está habilitado
                printer.set(align="center")
                printer.image(qr_imagen)
                print("Imprime QR salida")

        printer.cut()
        printer.close()

    def GuardarCobro(self, motive:str=None):
        """Guarda la informacion de un cobro realizado en la base de datos."""

        # Obtener el valor del codigo QR de promocion (si está presente, de lo contrario, será None)
        QRPromo = self.promo_auxiliar.get()
        if QRPromo == '': QRPromo = None

        # Obtener el valor del folio del boleto
        folio = self.folio.get()

        # Realiza una consulta con el folio seleccionado para obtener informacion adicional del boleto
        respuesta = self.DB.consulta(folio)

        if len(respuesta) == 0:
            # Si no se encuentra el boleto con el folio proporcionado, muestra un mensaje de error y sale de la funcion
            mb.showerror("Error", f"Ha ocurrido un error al realizar el cobro, escanee nuevamente el QR")
            return

        # Obtener valores adicionales del boleto
        Entrada = self.fecha_entrada.get()
        Salida = self.copia_fecha_salida.get()
        TiempoTotal = self.TiempoTotal.get()
        TarifaPreferente = self.TarifaPreferente.get()
        importe = self.importe.get()

        self.label15.configure(text=(Salida, "SI se debe modificar"))

        # Valor para verificar el cobro (valor de ejemplo)
        vobo = "lmf"

        # Crear una tupla con los datos del cobro
        datos = (motive, vobo, importe, TiempoTotal, Entrada, Salida, TarifaPreferente, QRPromo, folio)

        # Guardar el cobro en la base de datos
        self.DB.guardacobro(datos)

    def CalculaPromocion(self, event):
        """
        Esta funcion se encarga de aplicar una promocion al boleto seleccionado.

        :param event: Evento que activa la funcion.

        :return: None
        """

        # Valida si el boleto está cobrado como perdido
        TarifaPreferente = self.TarifaPreferente.get()
        if TarifaPreferente == "Per":
            mb.showerror("Error", "A los boletos cobrados como perdidos no se pueden aplicar promociones")
            self.promo.set('')
            self.promo_auxiliar.set('')
            self.entrypromo.focus()
            return

        # Valida que solo se pueda aplicar una promocion por boleto
        if TarifaPreferente not in ["Normal", "Danado"]:
            mb.showerror("Error", "Solo se puede aplicar una promocion por boleto")
            self.promo.set('')
            self.entrypromo.focus()
            return

        # Obtiene y normaliza el texto entregado por el lector QR.
        # Esto permite reconocer BA BODEGA AURRERA aunque el lector agregue espacios
        # al inicio/final o entregue letras minusculas.
        QRPromoOriginal = self.promo.get().strip()
        QRPromoNormalizado = " ".join(QRPromoOriginal.upper().split())

        partes_promo = QRPromoNormalizado.rsplit(" ", 1)
        if (
            len(partes_promo) == 2
            and partes_promo[0] == "BA BODEGA AURRERA"
            and partes_promo[1].isdigit()
            and len(partes_promo[1]) == 6
        ):
            TipoPromo = "BA BODEGA AURRERA"
        elif QRPromoOriginal == "Promo1":
            # Conserva la promocion que ya existia anteriormente.
            TipoPromo = "Promo1"
        else:
            TipoPromo = None

        # Verifica si la promocion es conocida.
        if TipoPromo not in PROMOCIONES:
            mb.showwarning("IMPORTANTE", "Promocion desconocida, escanee nuevamente el QR de promocion")
            self.promo.set('')
            self.promo_auxiliar.set('')
            self.entrypromo.focus()
            return

        # Promo1 conserva su validacion historica de codigo unico.
        # Tanto Promo1 como BA BODEGA AURRERA llevan un codigo unico.
        # La consulta evita que el mismo QR se utilice en dos boletos.
        if TipoPromo in ("Promo1", "BA BODEGA AURRERA"):
            codigo_a_validar = QRPromoNormalizado if TipoPromo == "BA BODEGA AURRERA" else QRPromoOriginal
            respuesta = self.DB.ValidaPromo(codigo_a_validar)

            if len(respuesta) > 0:
                mb.showwarning("IMPORTANTE", "LA PROMOCION YA FUE APLICADA")
                self.promo.set('')
                self.promo_auxiliar.set('')
                self.entrypromo.focus()
                return

        self.promo_auxiliar.set(QRPromoNormalizado if TipoPromo == "BA BODEGA AURRERA" else QRPromoOriginal)
        # Obtiene el importe actual
        importe = int(self.importe.get())

        # Aplica diferentes descuentos según el tipo de promocion
        if TipoPromo == "Promo1":
            importe = 0
            text_promo = "Promo1"

        elif TipoPromo == "BA BODEGA AURRERA":
            # Bodega Aurrera utiliza directamente la tabla
            # "BOLETO SELLADO BODEGA AURRERA" del desglose.
            # NO se restan 2 horas al tiempo real.
            importe = self.calcular_tarifa_hidalgo401(
                dias=self.dias_dentro,
                horas=self.horas_dentro,
                minutos=self.minutos_dentro,
                tarifa="BA"
            )

            if importe is None:
                mb.showwarning(
                    "Tiempo excedido",
                    "El desglose de Bodega Aurrera contempla hasta 24 horas.\n"
                    "No se puede calcular automáticamente un importe para\n"
                    "una permanencia mayor a 24 horas."
                )
                self.promo.set("")
                self.promo_auxiliar.set("")
                self.entrypromo.focus()
                return

            text_promo = "BA BODEGA AURRERA"

        # Añade "Danado" a la descripcion de la promocion si el boleto está marcado como "Danado"
        if TarifaPreferente == "Danado":
            text_promo = text_promo + TarifaPreferente

        # Establece el tipo de promocion y muestra el importe actualizado
        self.TarifaPreferente.set(text_promo)
        self.promo.set("")
        self.mostrar_importe(importe)

        if show_clock:
            self.reloj.update_data(text_promo, importe)



    ###################### Fin de Pagina2 Inicio Pagina3 ###############################
    def listado_completo(self):
        self.motive_cancel=tk.StringVar()

        self.modulo_corte = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.modulo_corte, text="Modulo de Corte")
        self.labelframe1=tk.LabelFrame(self.modulo_corte, text="Autos")
        self.labelframe1.grid(column=0, row=0, padx=1, pady=1)
        self.labelframe2=tk.LabelFrame(self.modulo_corte, text="Generar Corte")
        self.labelframe2.grid(column=1, row=0, padx=0, pady=0)


        self.labelframe4=tk.LabelFrame(self.modulo_corte, text="Cuadro Comparativo")
        self.labelframe4.grid(column=1, row=1, padx=0, pady=0)
        self.labelframe5=tk.LabelFrame(self.modulo_corte, text="Reporte de Cortes")
        self.labelframe5.grid(column=1, row=2, padx=1, pady=1)       
        self.lblSal=tk.Label(self.labelframe4, text="Salida de Autos")
        self.lblSal.grid(column=3, row=1, padx=1, pady=1)
        self.lblS=tk.Label(self.labelframe4, text="Entrada de Autos")
        self.lblS.grid(column=3, row=2, padx=1, pady=1)
        self.lblAnterior=tk.Label(self.labelframe4, text="Autos del Turno anterior")
        self.lblAnterior.grid(column=3, row=3, padx=1, pady=1)
        self.lblEnEstac=tk.Label(self.labelframe4, text="Autos en Estacionamiento")
        self.lblEnEstac.grid(column=3, row=4, padx=1, pady=1)
        self.lblC=tk.Label(self.labelframe4, text="Boletos Cobrados:")
        self.lblC.grid(column=0, row=1, padx=1, pady=1)
        self.lblE=tk.Label(self.labelframe4, text="Boletos Expedidos:")
        self.lblE.grid(column=0, row=2, padx=1, pady=1)
        self.lblA=tk.Label(self.labelframe4, text="Boletos Turno Anterior:")
        self.lblA.grid(column=0, row=3, padx=1, pady=1)
        self.lblT=tk.Label(self.labelframe4, text="Boletos Por Cobrar:")
        self.lblT.grid(column=0, row=4, padx=1, pady=1)
        self.BoletosCobrados=tk.StringVar()
        self.entryBoletosCobrados=tk.Entry(self.labelframe4, width=5, textvariable=self.BoletosCobrados, state= "readonly")
        self.entryBoletosCobrados.grid(column=1, row=1)
        self.BEDespuesCorte=tk.StringVar()
        self.entryBEDespuesCorte=tk.Entry(self.labelframe4, width=5, textvariable=self.BEDespuesCorte, state= "readonly")
        self.entryBEDespuesCorte.grid(column=1, row=2)
        self.BAnteriores=tk.StringVar()
        self.entryBAnteriores=tk.Entry(self.labelframe4, width=5, textvariable=self.BAnteriores, state= "readonly")
        self.entryBAnteriores.grid(column=1, row=3)
        self.BDentro=tk.StringVar()
        self.entryBDentro=tk.Entry(self.labelframe4, width=5, textvariable=self.BDentro, state= "readonly")
        self.entryBDentro.grid(column=1, row=4)
        self.SalidaAutos=tk.StringVar()
        self.entrySalidaAutos=tk.Entry(self.labelframe4, width=5, textvariable=self.SalidaAutos, state= "readonly")
        self.entrySalidaAutos.grid(column=2, row=1)
        self.SensorEntrada=tk.StringVar()
        self.entrySensorEntrada=tk.Entry(self.labelframe4, width=5, textvariable=self.SensorEntrada, state= "readonly", borderwidth=5)
        self.entrySensorEntrada.grid(column=2, row=2)
        self.Autos_Anteriores=tk.StringVar()
        self.entryAutos_Anteriores=tk.Entry(self.labelframe4, width=5, textvariable=self.Autos_Anteriores, state= "readonly")
        self.entryAutos_Anteriores.grid(column=2, row=3)
        self.AutosEnEstacionamiento=tk.StringVar()
        self.entryAutosEnEstacionamiento=tk.Entry(self.labelframe4, width=5, textvariable=self.AutosEnEstacionamiento, state= "readonly", borderwidth=5)
        self.entryAutosEnEstacionamiento.grid(column=2, row=4)
        self.boton6=tk.Button(self.labelframe4, text="Consulta Bol-Sensor", command=self.Puertoycontar, width=15, height=1, anchor="center", background=button_color, fg=button_letters_color)
        self.boton6.grid(column=1, row=0, padx=1, pady=1)

        self.FrmCancelado=tk.LabelFrame(self.modulo_corte, text="Boleto Cancelado")
        self.FrmCancelado.grid(column=0, row=2, padx=0, pady=0)
        self.labelCorte=tk.Label(self.labelframe2, text="El Total del CORTE es:")
        self.labelCorte.grid(column=0, row=1, padx=0, pady=0)
        self.label2=tk.Label(self.labelframe2, text="La Fecha de CORTE es:")
        self.label2.grid(column=0, row=2, padx=1, pady=1)
        self.label3=tk.Label(self.labelframe2, text="El CORTE Inicia ")
        self.label3.grid(column=0, row=3, padx=1, pady=1)
        self.label4=tk.Label(self.labelframe2, text="El Numero de CORTE es:")
        self.label4.grid(column=0, row=4, padx=1, pady=1)



        label_frame_corte_anterior = tk.LabelFrame(self.modulo_corte, text="Consulta Cortes Anteriores")
        label_frame_corte_anterior.grid(column=0, row=1, padx=0, pady=0)

        label_etiquetas_corte = tk.Frame(label_frame_corte_anterior)
        label_etiquetas_corte.grid(column=0, row=0, padx=0, pady=0)

        etiqueta_corte=tk.Label(label_etiquetas_corte, text="CORTE a Consultar: ")
        etiqueta_corte.grid(column=0, row=0, padx=1, pady=1)

        self.corte_anterior=tk.StringVar()
        self.entry_cortes_anteriores=tk.Entry(label_etiquetas_corte, width=20, textvariable=self.corte_anterior, justify='center')
        self.entry_cortes_anteriores.grid(column=1, row=0)

        boton_corte = tk.Button(label_frame_corte_anterior, text="Imprimir Corte", background=button_color, fg=button_letters_color, command=self.reimprimir_corte, width=15, height=3, anchor="center")
        boton_corte.grid(column=0, row=1, padx=4, pady=4)



        frame_folio_cancelado = tk.Frame(self.FrmCancelado)
        frame_folio_cancelado.grid(column=1, row=1, padx=4, pady=4)

        self.btnCancelado=tk.Button(frame_folio_cancelado, text="Cancelar Boleto ",command=self.BoletoCancelado,width=12, height=2, anchor="center", background=button_color, fg=button_letters_color)
        self.btnCancelado.grid(column=1, row=0)


        self.ImporteCorte=tk.StringVar()
        self.entryImporteCorte=tk.Entry(self.labelframe2, width=20, textvariable=self.ImporteCorte, state= "readonly", borderwidth=5, justify='center')
        self.entryImporteCorte.grid(column=1, row=1)
        self.FechaCorte=tk.StringVar()
        self.entryFechaCorte=tk.Entry(self.labelframe2, width=20, textvariable=self.FechaCorte, state= "readonly")
        self.entryFechaCorte.grid(column=1, row=2)
        self.FechUCORTE=tk.StringVar()
        self.entryFechUCORTE=tk.Entry(self.labelframe2, width=20, textvariable=self.FechUCORTE, state= "readonly")
        self.entryFechUCORTE.grid(column=1, row=3)



        frame_botones_entrada = Frame(self.labelframe1)
        frame_botones_entrada.grid(column=0, row=0, padx=4, pady=4)

        self.boton1=ttk.Button(frame_botones_entrada, text="Todas las Entradas", command=self.listar)
        self.boton1.grid(column=0, row=0, padx=4, pady=4)
        self.boton2=ttk.Button(frame_botones_entrada, text="Entradas sin corte", command=self.listar1)
        self.boton2.grid(column=1, row=0, padx=4, pady=4)

        self.boton3=tk.Button(self.labelframe2, text="Calcular Corte", command=self.Calcular_Corte, width=15, height=1, background=button_color, fg=button_letters_color)
        self.boton3.grid(column=2, row=1, padx=4, pady=4)
        self.boton4=tk.Button(self.labelframe2, text="Generar Corte", command=self.Guardar_Corte, width=15, height=1, anchor="center", background=button_color, fg=button_letters_color)
        self.boton4.grid(column=2, row=3, padx=4, pady=4)


        self.scrolledtext1=st.ScrolledText(self.labelframe1, width=28, height=4)
        self.scrolledtext1.grid(column=0,row=1, padx=1, pady=1)

        self.label7=tk.Label(self.labelframe5, text="Mes :")
        self.label7.grid(column=0, row=0, padx=1, pady=1)
        self.label8=tk.Label(self.labelframe5, text="Ano :")
        self.label8.grid(column=0, row=2, padx=1, pady=1)
        self.comboMesCorte = ttk.Combobox(self.labelframe5, width=6, justify=tk.RIGHT, state="readonly")
        self.comboMesCorte["values"] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        self.comboMesCorte.current(0)
        self.comboMesCorte.grid(column=1, row=0, padx=1, pady=1)
        self.AnoCorte=tk.IntVar()
        Ano= datetime.now().date().year
        self.AnoCorte.set(Ano)
        self.entryAnoCorte=tk.Entry(self.labelframe5, width=7, textvariable=self.AnoCorte, justify=tk.RIGHT)
        self.entryAnoCorte.grid(column=1, row=2)
        self.boton6=tk.Button(self.labelframe5, text="Reporte de Corte", command=self.Reporte_Corte, width=15, height=1, anchor="center", background=button_color, fg=button_letters_color)
        self.boton6.grid(column=3, row=2, padx=4, pady=4)       


        self.seccion_boton_usuario = tk.LabelFrame(self.labelframe5, text='Administrar usuarios')
        self.seccion_boton_usuario.grid(column=3, row=3, padx=4, pady=4, sticky='NESW') 

        self.boton_usuarios=tk.Button(self.seccion_boton_usuario, text="Entrar",	 
        command=lambda:{
                self.desactivar(),
                View_Login(),
                self.activar()
                },
        width=15, height=1, anchor="center", background=button_color, fg=button_letters_color)
        self.boton_usuarios.grid(column=0, row=0, padx=4, pady=4)

    def reimprimir_corte(self):
        numero_corte = self.entry_cortes_anteriores.get()
        if not numero_corte:
            mb.showinfo("Error", "Ingrese el numero de corte a consultar")
            self.entry_cortes_anteriores.focus()
            self.corte_anterior.set("")
            return

        corte_info = self.DB.consultar_corte(numero_corte)

        if len(corte_info) == 0:
            mb.showinfo("Error", "No hay información que corresponda al corte solicitado")
            self.entry_cortes_anteriores.focus()
            self.corte_anterior.set("")
            return

        numero_corte = int(numero_corte)
        for info in corte_info:
            inicio_corte_fecha = self.DB.consultar_corte(numero_corte-1)[0][1]
            final_corte_fecha = info[1]
            importe_corte = info[2]
            BAnterioresImpr = info[3]
            folio_final = info[4]
        
        folio_inicio = self.DB.consultar_corte(numero_corte-1)[0][4]
        
        corte_info = self.DB.consultar_información_corte(numero_corte)
        for info in corte_info:
            nombre_cajero = info[0]
            turno_cajero = info[1]



        printer = Usb(0x04b8, 0x0e28, 0)

        list_corte = []

        printer.set(align="center")
        txt = f"REIMPRESION DEL CORTE {numero_corte}\n"
        printer.text(txt)
        list_corte.append(txt)
        printer.set(align="left")

        txt = f"Cajero que lo consulta: {self.DB.CajeroenTurno()[0][1]}\n"
        printer.text(txt)
        list_corte.append(txt)

        txt = f"Hora de consulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        printer.text(txt)
        list_corte.append(txt)

        txt = f"Est {nombre_estacionamiento} CORTE Num {numero_corte}\n"
        printer.text(txt)
        list_corte.append(txt)

        txt = f'IMPORTE: ${importe_corte}\n\n'
        printer.text(txt)
        list_corte.append(txt)

        nombre_dia_inicio = self.get_day_name(inicio_corte_fecha.weekday())
        inicio_corte_fecha = datetime.strftime(inicio_corte_fecha, '%d-%b-%Y a las %H:%M:%S')
        txt = f'Inicio: {nombre_dia_inicio} {inicio_corte_fecha}\n'
        printer.text(txt)
        list_corte.append(txt)

        nombre_dia_fin = self.get_day_name(final_corte_fecha.weekday())
        final_corte_fecha = datetime.strftime(final_corte_fecha, "%d-%b-%Y a las %H:%M:%S")
        txt = f'Final: {nombre_dia_fin} {final_corte_fecha}\n\n'
        printer.text(txt)
        list_corte.append(txt)


        txt = f"Folio {folio_inicio} al inicio del turno\n"
        printer.text(txt)
        list_corte.append(txt)

        txt = f"Folio {folio_final} al final del turno\n\n"
        printer.text(txt)
        list_corte.append(txt)

        txt = f"Cajero en Turno: {nombre_cajero}\n"
        printer.text(txt)
        list_corte.append(txt)

        txt = f"Turno: {turno_cajero}\n"
        printer.text(txt)
        list_corte.append(txt)

        BolCobrImpresion = self.DB.Cuantos_Boletos_Cobro_Reimpresion(numero_corte)

        txt = f"Boletos Cobrados: {BolCobrImpresion}\n"
        printer.text(txt)
        list_corte.append(txt)

        BEDespuesCorteImpre = self.DB.boletos_expedidos_reimpresion(numero_corte)
        txt = f'Boletos Expedidos: {BEDespuesCorteImpre}\n'
        printer.text(txt)
        list_corte.append(txt)

        BAnterioresImpr = self.DB.consultar_corte(numero_corte-1)[0][3]
        txt = f"Boletos Turno Anterior: {BAnterioresImpr}\n"
        printer.text(txt)
        list_corte.append(txt)

        BDentroImp = (int(BAnterioresImpr) + int(BEDespuesCorteImpre))-(int(BolCobrImpresion))
        txt = f'Boletos dejados: {BDentroImp}\n'
        printer.text(txt)
        list_corte.append(txt)

        txt = "----------------------------------\n\n"
        printer.text(txt)
        list_corte.append(txt)

        respuesta=self.DB.desglose_cobrados(numero_corte)

        printer.set(align="center")
        txt = "Cantidad e Importes\n\n"
        printer.text(txt)
        list_corte.append(txt)
        printer.set(align="left")

        txt = "Cantidad - Tarifa - valor C/U - Total\n\n"
        printer.text(txt)
        list_corte.append(txt)

        for fila in respuesta:
            txt = f"  {str(fila[0])}  -  {str(fila[1])}  -  ${str(fila[2])}   -  ${str(fila[3])}\n"
            printer.text(txt)
            list_corte.append(txt)

        else:
            txt = f"\n{BolCobrImpresion} Boletos        Suma total ${importe_corte}\n"
            printer.text(txt)
            list_corte.append(txt)

        txt = "----------------------------------\n\n"
        printer.text(txt)
        list_corte.append(txt)

        desgloce_cancelados = self.DB.desgloce_cancelados(numero_corte)
        if len(desgloce_cancelados) > 0:
            printer.set(align="center")
            txt = "Boletos cancelados\n\n"
            printer.text(txt)
            list_corte.append(txt)
            printer.set(align="left")

            for boleto in desgloce_cancelados:
                txt = f"Folio:{boleto[0]} - Motivo: {boleto[1]}\n"
                printer.text(txt)
                list_corte.append(txt)

            txt = "----------------------------------\n\n"
            printer.text(txt)
            list_corte.append(txt)

        Quedados_Pensionados = self.controlador_crud_pensionados.get_Anteriores_Pensionados(numero_corte)
        Entradas_Totales_Pensionados = self.controlador_crud_pensionados.get_Entradas_Totales_Pensionados(numero_corte)
        Salidas_Pensionados = self.controlador_crud_pensionados.get_Salidas_Pensionados(numero_corte)
        Anteriores_Pensionados = self.controlador_crud_pensionados.get_Anteriores_Pensionados(numero_corte-1)
        
        quedados_totales = Quedados_Pensionados - Anteriores_Pensionados

        Quedados = 0 if quedados_totales < 0 else quedados_totales

        if Entradas_Totales_Pensionados > 0 or Salidas_Pensionados > 0 or Quedados_Pensionados > 0:

            printer.set(align="center")
            txt = "Entradas de pensionados\n\n"
            printer.text(txt)
            list_corte.append(txt)
            printer.set(align="left")

            txt = f"Anteriores: {Anteriores_Pensionados}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Entradas: {Entradas_Totales_Pensionados}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Salidas: {Salidas_Pensionados}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Quedados: {Quedados}\n"
            printer.text(txt)
            list_corte.append(txt)

            # Imprime separador
            txt = "----------------------------------\n\n"
            printer.text(txt)
            list_corte.append(txt)

        # Obtiene la cantidad e importes de las pensiones para el corte actual
        respuesta = self.DB.total_pensionados_corte(numero_corte)

        # Si hay pensionados en el corte, se procede a imprimir la seccion correspondiente
        if len(respuesta) > 0:
            printer.set(align="center")
            txt = "Cantidad e Importes Pensiones\n\n"
            printer.text(txt)
            list_corte.append(txt)

            printer.set(align="left")
            txt = "Cuantos - Concepto - ImporteTotal \n"
            printer.text(txt)
            list_corte.append(txt)

            for fila in respuesta:
                txt = f"   {str(fila[0])}   -  {str(fila[1])}   -   ${str(fila[2])}\n"
                printer.text(txt)
                list_corte.append(txt)

            else:
                txt = f"----------------------------------\n"
                printer.text(txt)
                list_corte.append(txt)

        # Imprime ultimo separador
        txt = "----------------------------------\n"
        printer.text(txt)
        list_corte.append(txt)

        # Corta el papel
        printer.cut()
        printer.close()

        # La carpeta puede no existir en una instalación nueva.
        makedirs("Reimpresion_Cortes", exist_ok=True)
        txt_file_corte = f"Reimpresion_Cortes/Reimpresion_{nombre_estacionamiento.replace(' ', '_')}_Corte_N°_{numero_corte}.txt"

        with open(file=txt_file_corte, mode="w") as file:
            file.writelines(list_corte)
            file.close()

        thread = Thread(target=send_other_corte)
        thread.start()

        self.entry_cortes_anteriores.focus()
        self.corte_anterior.set("")



    def BoletoCancelado(self):
        self.desactivar()
        # Crear la ventana principal
        self.cancel_window = tk.Toplevel()
        self.cancel_window.title("Cancelar Boleto")

        # Se elimina la funcionalidad del boton de cerrar
        self.cancel_window.protocol("WM_DELETE_WINDOW", lambda: {self.activar(),self.cancel_window.destroy()})

        # Elevar la ventana secundaria al frente de todas las otras ventanas
        self.cancel_window.lift()

        # Colocar el LabelFrame en las coordenadas calculadas
        principal_frame_cancel = tk.LabelFrame(self.cancel_window)
        principal_frame_cancel.pack(expand=True, padx=5, pady=5, anchor='n')

        labelframe_cancelar_boleto=tk.LabelFrame(principal_frame_cancel, text="Cancelar Boleto")
        labelframe_cancelar_boleto.grid(column=0, row=0, padx=5, pady=5)

        labelframe_cancelar_boleto_folio=tk.Frame(labelframe_cancelar_boleto)
        labelframe_cancelar_boleto_folio.grid(column=0, row=0, padx=5, pady=5)

        etiqueta = tk.Label(labelframe_cancelar_boleto_folio, text="Ingresa el Folio a cancelar: ", font=font_cancel)
        etiqueta.grid(column=0, row=0, padx=2, pady=2)

        self.FolioCancelado=tk.StringVar()
        self.entry_folio_cancelado=tk.Entry(labelframe_cancelar_boleto_folio, width=10, textvariable=self.FolioCancelado, justify='center', font=font_cancel)
        self.entry_folio_cancelado.grid(column=1, row=0, padx=2, pady=2)
        self.entry_folio_cancelado.focus()


        # Crear una etiqueta
        etiqueta = tk.Label(labelframe_cancelar_boleto, text="Ingresa el motivo de la cancelación del boleto", font=font_cancel)
        etiqueta.grid(column=0, row=1, padx=2, pady=5)

        self.EntryMotive_Cancel = tk.Entry(labelframe_cancelar_boleto, font=font_cancel, width=30, textvariable=self.motive_cancel, justify='center')
        self.EntryMotive_Cancel.grid(column=0, row=2, padx=2, pady=2)

        # Crear un botón para obtener el texto
        boton = tk.Button(labelframe_cancelar_boleto, text="Cancelar Boleto", command=lambda:cancelar_boleto(), background=button_color, fg=button_letters_color, width=15, height=2, font=font_cancel)
        boton.grid(column=0, row=3, padx=2, pady=2)

        labelframe_lista_boletos=tk.LabelFrame(principal_frame_cancel, text="Lista de boletos")
        labelframe_lista_boletos.grid(column=1, row=0, padx=5, pady=5)

        self.boton7=tk.Button(labelframe_lista_boletos, text="Actualizar", command=lambda:boletos_dentro(), width=12, height=1, background=button_color, fg=button_letters_color, font=font_cancel)
        self.boton7.grid(column=0, row=0, padx=1, pady=1)

        scroller_boletos_dentro=st.ScrolledText(labelframe_lista_boletos, width=25, height=8)
        scroller_boletos_dentro.grid(column=0,row=1, padx=2, pady=2)

        def boletos_dentro():
            respuesta=self.DB.Autos_dentro()
            scroller_boletos_dentro.delete("1.0", tk.END)
            for fila in respuesta:
                scroller_boletos_dentro.insert(tk.END, "Folio num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\nPlacas: "+str(fila[2])+"\n\n")

        boletos_dentro()

        def cancelar_boleto():
            folio = self.FolioCancelado.get()
            if not folio:
                mb.showerror("Error", "Ingrese un folio a cancelar")
                self.entry_folio_cancelado.focus()
                return

            motive_cancel = self.motive_cancel.get()
            if not motive_cancel:
                mb.showerror("Error", "Ingresa el motivo por el cual se esta cancelando el boleto")
                self.EntryMotive_Cancel.focus()
                return 

            cancelar = mb.askokcancel("Advertencia", f"¿Estas seguro de querer cancelar el boleto con folio: {self.FolioCancelado.get()}?")
            if cancelar == False:
                self.FolioCancelado.set("")
                self.entry_folio_cancelado.focus()
                return

            self.folio.set(folio)

            folio = self.folio.get()
            respuesta = self.DB.consulta(folio)

            if len(respuesta) == 0:
                self.fecha_entrada.set('')
                self.fecha_salida.set('')
                self.motive_cancel.set("")
                self.FolioCancelado.set("")
                self.folio.set("")
                mb.showinfo("Informacion", "No existe un auto con dicho codigo")
                self.entry_folio_cancelado.focus()
                return


            Salida = respuesta[0][1]
            Placas = respuesta[0][6]

            if Salida is not None:
                self.motive_cancel.set("")
                self.FolioCancelado.set("")
                self.folio.set("")
                mb.showerror("Error", "No se puede cancelar un boleto ya cobrado")
                self.entry_folio_cancelado.focus()
                return

            if Placas == "BoletoPerdido":
                mb.showerror("Error", "El folio ingresado corresponde a una reposicion de un boleto perdido, no se puede cancelar.")
                self.motive_cancel.set("")
                self.FolioCancelado.set("")
                self.folio.set("")
                return

            Entrada = str(respuesta[0][0])
            self.fecha_entrada.set(Entrada)
            self.CalculaPermanencia()
            importe = 0

            # Establecer el importe y mostrarlo
            self.mostrar_importe(importe)
            self.TarifaPreferente.set("CDO")
            self.GuardarCobro(motive_cancel)
            self.Comprobante(titulo='Boleto Cancelado', imagen_logo=False)
            self.FolioCancelado.set("")
            self.limpiar_campos()
            self.cancel_window.destroy()
            self.activar()

    def listar(self):
        respuesta=self.DB.recuperar_todos()
        self.scrolledtext1.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtext1.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\nSalio: "+str(fila[2])[:-3]+"\n\n")

    def listar1(self):
        respuesta=self.DB.recuperar_sincobro()
        self.scrolledtext1.delete("1.0", tk.END)
        #respuesta=str(respuesta)
        for fila in respuesta:
            self.scrolledtext1.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])[:-3]+"\nSalio: "+str(fila[2])[:-3]+"\nImporte: "+str(fila[3])+"\n\n")

            printer = Usb(0x04b8, 0x0e28, 0)

            printer.text('Entrada Num :')
            printer.text(str(fila[0]))
            printer.text('\n')
            printer.text('Entro :')
            printer.text(str(fila[1])[:-3])
            printer.text('\n')
            printer.text('Salio :')
            printer.text(str(fila[2])[:-3])
            printer.text('\n')
            printer.text('importe :')
            printer.text(str(fila[3]))
            printer.text('\n')
        else:
            print("-")
            printer.cut()
            printer.close()

    def Calcular_Corte(self):
        self.ImporteCorte.set(self.DB.corte())

        ##obtengamo la fechaFin del ultimo corte
        self.FechUCORTE.set(self.DB.UltimoCorte())

        self.FechaCorte.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))#donde el label esta bloqueado


    def Guardar_Corte(self):
        self.Calcular_Corte()
        self.Puertoycontar()

        ######Obtenemos los datos del Cajero en Turno
        cajero=self.DB.CajeroenTurno()
        for fila in cajero:
            id_cajero = fila[0]
            nombre_cajero = fila[1]
            inicio_corte = self.FechUCORTE.get()
            turno_cajero = fila[3]

        fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datos=(fecha_hoy, id_cajero)
        self.DB.Cierreusuario(datos)

        self.DB.NoAplicausuario(id_cajero)

        ##la fecha final de este corte que es la actual
        fechaDECorte = self.FechaCorte.get()
     
        ######el importe se obtiene de la suma
        importe_corte = self.ImporteCorte.get()
        AEE = self.DB.CuantosAutosdentro()
        maxnumid = self.DB.MaxfolioEntrada()
        NumBolQued = self.BDentro.get()
        Quedados_Pensionados = self.controlador_crud_pensionados.get_Quedados_Pensionados()

        datos=(importe_corte, inicio_corte, fechaDECorte, AEE, maxnumid, NumBolQued, Quedados_Pensionados)
        self.DB.GuarCorte(datos)

        numero_corte = self.DB.Maxfolio_Cortes()
        #este es para que la instruccion no marque error
        ActEntradas = (numero_corte, "cor")
        self.label4.configure(text = f"Numero de corte {numero_corte}")


        printer = Usb(0x04b8, 0x0e28, 0)

        # printer.image(logo_1)

        list_corte = []

        txt = f"Est {nombre_estacionamiento} CORTE Num {numero_corte}\n"
        printer.text(txt)
        list_corte.append(txt)

        txt = f'IMPORTE: ${importe_corte}\n\n'
        printer.text(txt)
        list_corte.append(txt)

        inicio_corte_fecha= datetime.strptime(self.FechUCORTE.get(), '%Y-%m-%d %H:%M:%S')
        nombre_dia_inicio = self.get_day_name(inicio_corte_fecha.weekday())
        inicio_corte_fecha = datetime.strftime(inicio_corte_fecha, '%d-%b-%Y a las %H:%M:%S')
        txt = f'Inicio: {nombre_dia_inicio} {inicio_corte_fecha}\n'
        printer.text(txt)
        list_corte.append(txt)

        final_corte_fecha= datetime.strptime(self.FechaCorte.get(), '%Y-%m-%d %H:%M:%S')
        nombre_dia_fin = self.get_day_name(final_corte_fecha.weekday())
        final_corte_fecha = datetime.strftime(final_corte_fecha, "%d-%b-%Y a las %H:%M:%S")
        txt = f'Final: {nombre_dia_fin} {final_corte_fecha}\n\n'
        printer.text(txt)
        list_corte.append(txt)

        MaxFolio = self.DB.MaxfolioEntrada()
        BEDespuesCorteImpre = self.BEDespuesCorte.get()
        folio_inicio = int(MaxFolio)-int(BEDespuesCorteImpre)

        txt = f"Folio {folio_inicio} al inicio del turno\n"
        printer.text(txt)
        list_corte.append(txt)

        txt = f"Folio {MaxFolio} al final del turno\n\n"
        printer.text(txt)
        list_corte.append(txt)

        txt = f"Cajero en Turno: {nombre_cajero}\n"
        printer.text(txt)
        list_corte.append(txt)

        txt = f"Turno: {turno_cajero}\n"
        printer.text(txt)
        list_corte.append(txt)

        txt = '------------------------------\n'
        printer.text(txt)
        list_corte.append(txt)

        inicios = self.DB.IniciosdeTurno(inicio_corte)
        for fila in inicios:
            txt = "Sesion "+fila[1]+": "+str(fila[0])+"\n"
            printer.text(txt)
            list_corte.append(txt)
        else:
            txt = "----------------------------------\n\n"
            printer.text(txt)
            list_corte.append(txt)

        BolCobrImpresion = self.BoletosCobrados.get()
        txt = f"Boletos Cobrados: {BolCobrImpresion}\n"
        printer.text(txt)
        list_corte.append(txt)

        txt = f'Boletos Expedidos: {BEDespuesCorteImpre}\n'
        printer.text(txt)
        list_corte.append(txt)

        BAnterioresImpr = self.BAnteriores.get()
        txt = f"Boletos Turno Anterior: {BAnterioresImpr}\n"
        printer.text(txt)
        list_corte.append(txt)

        BDentroImp = (int(BAnterioresImpr) + int(BEDespuesCorteImpre))-(int(BolCobrImpresion))
        txt = f'Boletos dejados: {BDentroImp}\n'
        printer.text(txt)
        list_corte.append(txt)

        txt = '------------------------------\n\n'
        printer.text(txt)
        list_corte.append(txt)

        self.ImporteCorte.set("")
        self.DB.ActualizarEntradasConcorte(ActEntradas)
        self.controlador_crud_pensionados.Actualizar_Entradas_Pension(numero_corte)
        self.DB.NocobradosAnt('ant')

        self.corte_anterior.set(numero_corte)
        Numcorte = self.corte_anterior.get()
        respuesta=self.DB.desglose_cobrados(Numcorte)

        printer.set(align="center")
        txt = "Cantidad e Importes\n\n"
        printer.text(txt)
        list_corte.append(txt)
        printer.set(align="left")

        txt = "Cantidad - Tarifa - valor C/U - Total \n"
        printer.text(txt)
        list_corte.append(txt)

        for fila in respuesta:
            txt = f"  {str(fila[0])}  -  {str(fila[1])}  -  ${str(fila[2])}   -  ${str(fila[3])}\n"
            printer.text(txt)
            list_corte.append(txt)

        else:
            txt = f"{BolCobrImpresion} Boletos        Suma total ${importe_corte}\n\n"
            printer.text(txt)
            list_corte.append(txt)

        txt = "----------------------------------\n\n"
        printer.text(txt)
        list_corte.append(txt)

        desgloce_cancelados = self.DB.desgloce_cancelados(numero_corte)
        if len(desgloce_cancelados) > 0:
            txt = "Boletos cancelados\n\n"
            printer.text(txt)
            list_corte.append(txt)

            for boleto in desgloce_cancelados:
                txt = f"Folio:{boleto[0]} - Motivo: {boleto[1]}\n"
                printer.text(txt)
                list_corte.append(txt)

            txt = "----------------------------------\n\n"
            printer.text(txt)
            list_corte.append(txt)

        Entradas_Totales_Pensionados = self.controlador_crud_pensionados.get_Entradas_Totales_Pensionados(numero_corte)
        Salidas_Pensionados = self.controlador_crud_pensionados.get_Salidas_Pensionados(numero_corte)
        Anteriores_Pensionados = self.controlador_crud_pensionados.get_Anteriores_Pensionados(numero_corte-1)
        
        quedados_totales = Quedados_Pensionados - Anteriores_Pensionados
        Quedados = 0 if quedados_totales < 0 else quedados_totales
        if Entradas_Totales_Pensionados > 0 or Salidas_Pensionados > 0 or Quedados_Pensionados > 0:

            printer.set(align="center")
            txt = "Entradas de pensionados\n\n"
            printer.text(txt)
            list_corte.append(txt)
            printer.set(align="left")

            txt = f"Anteriores: {Anteriores_Pensionados}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Entradas: {Entradas_Totales_Pensionados}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Salidas: {Salidas_Pensionados}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Quedados: {Quedados}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = "----------------------------------\n\n"
            printer.text(txt)
            list_corte.append(txt)

        # Obtiene la cantidad de boletos perdidos generados
        Boletos_perdidos_generados = self.DB.Boletos_perdidos_generados()
        # Obtiene el desglose de los boletos perdidos generados
        Boletos_perdidos_generados_desglose = self.DB.Boletos_perdidos_generados_desglose()
        # Obtiene la cantidad de boletos perdidos cobrados
        Boletos_perdidos_cobrados = self.DB.Boletos_perdidos_cobrados(Numcorte)
        # Obtiene el desglose de los boletos perdidos cobrados
        Boletos_perdidos_cobrados_desglose = self.DB.Boletos_perdidos_cobrados_desglose(Numcorte)
        # Obtiene la cantidad de boletos perdidos no cobrados
        Boletos_perdidos_no_cobrados = self.DB.Boletos_perdidos_no_cobrados()

        # Si hay boletos perdidos generados, cobrados o no cobrados, se procede a imprimir el reporte
        if Boletos_perdidos_generados > 0 or Boletos_perdidos_cobrados > 0 or Boletos_perdidos_no_cobrados > 0:
            # Imprime el encabezado de la seccion de boletos perdidos

            printer.set(align="center")
            txt = "BOLETOS PERDIDOS"+'\n'
            printer.text(txt)
            list_corte.append(txt)
            printer.set(align="left")

            # Imprime la cantidad de boletos perdidos generados y su desglose
            txt = f"Boletos perdidos generados: {Boletos_perdidos_generados + Boletos_perdidos_cobrados}" + '\n'
            printer.text(txt)
            list_corte.append(txt)

            for boleto in Boletos_perdidos_cobrados_desglose:
                txt = f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\n"
                printer.text(txt)
                list_corte.append(txt)

            for boleto in Boletos_perdidos_generados_desglose:
                txt = f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\n"
                printer.text(txt)
                list_corte.append(txt)


            # Imprime separador
            txt = "**********************************\n"
            printer.text(txt)
            list_corte.append(txt)

            # Imprime la cantidad de boletos perdidos cobrados y su desglose
            txt = f"Boletos perdidos cobrados: {Boletos_perdidos_cobrados}" + '\n\n'
            printer.text(txt)
            list_corte.append(txt)

            for boleto in Boletos_perdidos_cobrados_desglose:
                txt = f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\nFecha salida:{boleto[2]}\n"
                printer.text(txt)
                list_corte.append(txt)

            txt = "**********************************\n"
            printer.text(txt)
            list_corte.append(txt)

            # Imprime la cantidad de boletos perdidos no cobrados y su desglose
            txt = f"Boletos perdidos quedados: {Boletos_perdidos_no_cobrados}\n"
            printer.text(txt)
            list_corte.append(txt)

            for boleto in Boletos_perdidos_generados_desglose:
                txt = f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\n"
                printer.text(txt)
                list_corte.append(txt)

            # Imprime separador
            txt = "----------------------------------\n\n"
            printer.text(txt)
            list_corte.append(txt)

        # Obtiene la cantidad e importes de las pensiones para el corte actual
        respuesta = self.DB.total_pensionados_corte(Numcorte)

        # Si hay pensionados en el corte, se procede a imprimir la seccion correspondiente
        if len(respuesta) > 0:
            printer.set(align="center")
            txt = "Cantidad e Importes Pensiones\n\n"
            printer.text(txt)
            list_corte.append(txt)
            printer.set(align="left")

            txt = "Cuantos - Concepto - ImporteTotal \n"
            printer.text(txt)
            list_corte.append(txt)

            for fila in respuesta:
                txt = f"   {str(fila[0])}   -  {str(fila[1])}   -   ${str(fila[2])}\n"
                printer.text(txt)
                list_corte.append(txt)

            else:
                txt = f"----------------------------------\n"
                printer.text(txt)
                list_corte.append(txt)


        dir_path = path.abspath("Reimpresion_Cortes/")
        makedirs(dir_path, exist_ok=True)
        files = listdir(dir_path)
        if len(files) > 1: 
            printer.set(align="center")
            txt = "Reimpresiones de corte\n\n"
            printer.text(txt)
            list_corte.append(txt)
            printer.set(align="left")

            for file in files:
                _, ext = path.splitext(file)
                if ext.lower() == ".txt":
                    file_path = path.join(dir_path, file)
                    txt = "-----------------\n"
                    printer.text(txt)
                    list_corte.append(txt)

                    # Abrir el archivo y leer las primeras tres líneas
                    with open(file_path, 'r', encoding='utf-8') as f:
                        primeras_lineas = [next(f) for _ in range(3)]
                        f.close()

                    # Imprimir el nombre del archivo y las primeras tres líneas
                    for linea in primeras_lineas:
                        txt = f"{linea}"
                        printer.text(txt)
                        list_corte.append(txt)
                    tools.remove_file(file_path)
            txt = "-----------------\n"
            printer.text(txt)
            list_corte.append(txt)

            # Imprime ultimo separador
            txt = "----------------------------------\n"
            printer.text(txt)
            list_corte.append(txt)

        # Imprime ultimo separador
        txt = "----------------------------------\n"
        printer.text(txt)
        list_corte.append(txt)

        # Corta el papel
        printer.cut()
        printer.close()

        makedirs("Cortes", exist_ok=True)
        txt_file_corte = f"Cortes/{nombre_estacionamiento.replace(' ', '_')}_Corte_N°_{numero_corte}.txt"

        with open(file=txt_file_corte, mode="w") as file:
            file.writelines(list_corte)
            file.close()

        # Cierra el programa al final del reporte
        self.Cerrar_Programa()

    def Cerrar_Programa(self):
        self.root.destroy()

    def Reporte_Corte(self):
            mes=self.comboMesCorte.get()
            Ano=int(self.entryAnoCorte.get(), )
            if Ano is None :
                mb.showwarning("IMPORTANTE", "Debe capturar el Ano del reporte")
                return False
            elif Ano <= 0 :
                mb.showwarning("IMPORTANTE", "Distribucion debe ser un numero positivo mayor a cero")
                return False
            else :
                Libro = './XlsCorte/Rpte Corte '+ str(mes)+'-'+str(Ano)+'  '+str(datetime.now().date())+'.xlsx'
                
                datos=(mes, Ano)
                #Obtenemos Fecha (Inicialy Final) del mes que solicita el reporte
                CorteMaxMin=self.DB.Cortes_MaxMin(datos)
                for fila in CorteMaxMin:
                    UltFecha=fila[0] 
                    IniFecha=fila[1] 

                #Obtenemos Primer y Ultimo Folio de Cortes del Mes que se solicita el reporte
                datos=(IniFecha)
                CorteIni=self.DB.Cortes_Folio(datos)
                datos=(UltFecha)
                #CorteFin=self.DB.Cortes_FolioFin(datos)
                CorteFin=self.DB.Cortes_Folio(datos)
                #Obtnemos los Registros entre estos dos Folios para el cuerpo del reporte       
                datos=(CorteIni, CorteFin)
                #datos=(IniFecha, UltFecha)
                Registros=self.DB.Registros_corte(datos)
                TotalesCorte=self.DB.Totales_corte(datos)
                ResumenPromo=self.DB.Resumen_promo(datos)
                workbook = xlsxwriter.Workbook(Libro)
                worksheet = workbook.add_worksheet('CORTE')
                #Definimos Encabezado Principal
                #Obtenemos imagen del Encabezado
                worksheet.insert_image('A3', 'LOGO_NEW.jpg') #,{'x_scale': 0.20, 'y_scale': 0.20} Insert de Logo (imagen.png)
                #Definimos Formatos de celda del encabezado
                cell_format0 = workbook.add_format()
                cell_format0 = workbook.add_format({'bold': True,'align':'right'})
                cell_format1 = workbook.add_format()
                cell_format1 = workbook.add_format({'bold': True,'align':'right','num_format':'$#,##0.00', 'bg_color':'#D9D9D9'})
                cell_format2 = workbook.add_format() #{'num_format': 'dd/mm/yy'}
                cell_format2.set_num_format('dd/mm/yy h:mm:ss')  # Format string.
                cell_format3 = workbook.add_format()
                cell_format3 = workbook.add_format({'bold': True, 'align':'center','size': 15})
                cell_format4 = workbook.add_format()
                cell_format4 = workbook.add_format({'bold': True, 'align':'center'})
                cell_format5 = workbook.add_format()
                cell_format5 = workbook.add_format({'align':'right','num_format':'$#,##0.00'})
                cell_format6 = workbook.add_format()
                cell_format6= workbook.add_format({'align':'right','num_format':'#,##0'})                        
                #Colocamos Resumen x Promoci[on en Encabezado
                worksheet.write('E2', 'PROM', cell_format4)
                worksheet.write('F2', 'CANT.', cell_format4)
                worksheet.write('G2', 'TOTAL X PROMCION', cell_format4)                        
                row=2
                col=4
                for fila in ResumenPromo:
                    #print(str(fila[0]))
                    worksheet.write(row, col,   fila[1]) #Nombre de la Promo A12
                    worksheet.write(row, col+1, fila[0],cell_format6) #Numero de Folios por Promocion B12
                    worksheet.write(row, col+2, fila[3],cell_format5) #Monto Total por Promocion C12
                    row += 1
                #Colocamos Totales del Encabezado
                row=row+1
                worksheet.write('C3', 'REPORTE DE CORTE', cell_format3) #Aqui debe ir el nombre de la sucursal pero de d[onde lo obtengo?
                worksheet.write('E'+str(row), 'TOTAL:',cell_format4)
                worksheet.write('F'+str(row+1), 'PERIODO',cell_format4)
                worksheet.write('F'+str(row+2), 'Inicio')#f5
                worksheet.write('F'+str(row+3), 'Fin')#f6
                worksheet.write('F'+str(row+4), 'Cortes')#f7
                worksheet.write('F'+str(row+5), 'Suma del Periodo:', cell_format0)#f8
                worksheet.write('G'+str(row+2), IniFecha, cell_format2)#g5
                worksheet.write('G'+str(row+3), UltFecha, cell_format2)#g6
                for fila in TotalesCorte:
                    #print(str(fila[3]))
                    worksheet.write('G'+str(row), fila[0], cell_format5)#Total de Cobros en resumen
                    worksheet.write('F'+str(row), fila[3], cell_format6)#Total de Folios en Resumen
                    worksheet.write('G'+str(row+5), fila[0], cell_format1)# Total de cobros Encabezado
                    worksheet.write('G'+str(row+4),str(fila[2]) +" al "+ str(fila[1]))
                #Definimos Formato y Ancho de Fila Encabezado del cuerpo del reporte      
                cell_format = workbook.add_format({'bold': True, 'align':'center', 'text_wrap':True, 'border':1, 'pattern':1, 'bg_color':'#D9D9D9'}) #808080      
                worksheet.set_row(row+7, 34)
                #worksheet.set_row(10, 34)
                #Definimos anchos de Columna del cuerpo del reporte
                worksheet.set_column(0, 0, 10)
                worksheet.set_column(1, 2, 30)
                worksheet.set_column(3, 4, 14)
                worksheet.set_column(5, 5, 13)
                worksheet.set_column(6, 6, 30)
                worksheet.set_column(7, 7, 10)
                #Definimos Nombres de columnas del cuerpo del reporte
                worksheet.write('A'+str(row+8), 'FOLIO', cell_format)
                worksheet.write('B'+str(row+8), 'FECHA Y HORA ENT', cell_format)
                worksheet.write('C'+str(row+8), 'FECHA Y HORA SAL', cell_format)
                worksheet.write('D'+str(row+8), 'TIEMPO', cell_format)
                worksheet.write('E'+str(row+8), 'PRECIO', cell_format)
                worksheet.write('F'+str(row+8), 'CORTES', cell_format)
                worksheet.write('G'+str(row+8), 'DESCRIPCION', cell_format)
                worksheet.write('H'+str(row+8), 'PROM', cell_format)
                #Definimos Formatos de celda para datos del cuerpo del reporte                        
                cell_format7 = workbook.add_format() #{'num_format': 'hh:mm:ss'}
                cell_format7 = workbook.add_format({'align':'right','num_format':'h:mm:ss'})
                row=row+8
                col=0
                for fila in Registros:
                    #MontoTt= fila[0]
                    worksheet.write(row, col,   fila[0]) #Folio A12
                    worksheet.write(row, col+1, fila[1],cell_format2) #Fecha Hora Entrada B12
                    worksheet.write(row, col+2, fila[2],cell_format2) #Fecha Hora Salida C12
                    worksheet.write(row, col+3, fila[3],cell_format7) #Tiempo D12
                    worksheet.write(row, col+4, fila[4],cell_format5) #Precio E12
                    worksheet.write(row, col+5, fila[5]) #Cortes F12
                    worksheet.write(row, col+6, fila[6]) #Descripcion G12
                    worksheet.write(row, col+7, fila[7]) #Promociones H12
                    row += 1
                workbook.close()       
                mb.showinfo("Reporte de Corte",'Reporte Guardado')     



    def Puertoycontar(self):

        self.BoletosCobrados.set(self.DB.CuantosBoletosCobro())

        MaxFolioCorte=self.DB.Maxfolio_Cortes()

        # self.BEDespuesCorte.set(self.DB.BEDCorte()) # revisión pendiente
        # self.BAnteriores.set(self.DB.BAnteriores()) # revisión pendiente

        self.BAnteriores.set(self.DB.Quedados_Sensor(MaxFolioCorte))

        maxNumidIni=self.DB.MaxnumId()
        maxFolioEntradas= self.DB.MaxfolioEntrada()
        BEDCorte = maxFolioEntradas - maxNumidIni
        self.BEDespuesCorte.set(BEDCorte)

        self.BDentro.set(self.DB.CuantosAutosdentro())

        self.Autos_Anteriores.set(self.DB.Quedados_Sensor(MaxFolioCorte))


    ###################### Fin de Pagina2 Inicio Pagina3 ###############################
    def interface_pensionados(self):
        self.registros = None
        self.tipo_pago_ = None

        self.pagina4 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina4, text="Modulo Pensionados")
        #enmarca los controles LabelFrame 
        labelframe_pensionados = tk.LabelFrame(self.pagina4, text="Pensionados")
        labelframe_pensionados.grid(column=0, row=0, padx=2, pady=5, sticky=tk.NW)

        label_frame_datos_pago = tk.Frame(labelframe_pensionados)
        label_frame_datos_pago.grid(column=0, row=0, padx=2, pady=5, sticky=tk.NW)

        ######Pago, Vigencia y Numero de tarjeta
        labelframe_pensionados_datos_pago=tk.LabelFrame(label_frame_datos_pago, text="Datos de pago")
        labelframe_pensionados_datos_pago.grid(column=0, row=0, padx=2, sticky=tk.NW)

        labelframe_pensionados_datos_pago__=tk.Frame(labelframe_pensionados_datos_pago)
        labelframe_pensionados_datos_pago__.grid(column=0, row=0)

        lbldatos20=tk.Label(labelframe_pensionados_datos_pago__, text="Num. Tarjeta:")
        lbldatos20.grid(column=0, row=0, padx=4, pady=4)
        self.variable_numero_tarjeta=tk.StringVar()
        self.caja_texto_numero_tarjeta=ttk.Entry(labelframe_pensionados_datos_pago__, width=15, textvariable=self.variable_numero_tarjeta, justify='center')
        self.caja_texto_numero_tarjeta.grid(column=1, row=0, padx=4, pady=4)

        boton_consultar_pensionado=tk.Button(labelframe_pensionados_datos_pago__, text="Consultar", command=self.ConsulPagoPen, width=12, height=1, anchor="center",  font=("Arial", 10), background=button_color, fg=button_letters_color)
        boton_consultar_pensionado.grid(column=4, row=0, padx=4, pady=4)     

        lbldatos16=tk.Label(labelframe_pensionados_datos_pago__, text="Monto Mensual:")#informativo
        lbldatos16.grid(column=0, row=1, padx=4, pady=4)
        self.Monto=tk.StringVar()
        entryMonto=ttk.Entry(labelframe_pensionados_datos_pago__, width=10, textvariable=self.Monto, state="readonly", justify='center')
        entryMonto.grid(column=1, row=1)

        etiqueta_vigencia=tk.Label(labelframe_pensionados_datos_pago__, text="Vigencia:")
        etiqueta_vigencia.grid(column=3, row=1, padx=4, pady=4)
        self.Vigencia=tk.StringVar()
        cata_texto_vigencia=ttk.Entry(labelframe_pensionados_datos_pago__, width=15, textvariable=self.Vigencia, state="readonly")
        cata_texto_vigencia.grid(column=4, row=1, padx=4, pady=4)

        lbldatos17=tk.Label(labelframe_pensionados_datos_pago__, text="Mensualidades a Pagar:")
        lbldatos17.grid(column=0, row=2, padx=4, pady=4)

        self.meses_pago = tk.StringVar()
        self.comboMensual = ttk.Combobox(labelframe_pensionados_datos_pago__, width=8, state="readonly", textvariable=self.meses_pago)
        self.comboMensual["values"] = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        self.comboMensual.current(0)
        self.comboMensual.grid(column=1, row=2, padx=4, pady=4)

        etiqueta_estatus=tk.Label(labelframe_pensionados_datos_pago__, text="Estatus:")
        etiqueta_estatus.grid(column=3, row=2, padx=4, pady=4)  
        self.Estatus=tk.StringVar()
        cata_texto_estatus=ttk.Entry(labelframe_pensionados_datos_pago__, width=15, textvariable=self.Estatus, state="readonly", justify='center')
        cata_texto_estatus.grid(column=4, row=2, padx=4, pady=4)

        label_frame_informacion = tk.Frame(labelframe_pensionados_datos_pago)
        label_frame_informacion.grid(column=0, row=2)

        self.etiqueta_informacion = tk.Label(label_frame_informacion, text="", font=("Arial", 11))
        self.etiqueta_informacion.grid(column=0, row=0)



        label_frame_tipo_pago = tk.LabelFrame(label_frame_datos_pago, text="Tipo de pago")
        label_frame_tipo_pago.grid(column=1, row=0, padx=6, pady=5, sticky=tk.NW)

        # Crear una variable de control para el estado del checkbox
        self.variable_tipo_pago_efectivo = tk.BooleanVar()
        # Crear un checkbox y asociarlo a la variable de control
        checkbox_efectivo = tk.Checkbutton(label_frame_tipo_pago, text="Efectivo", variable=self.variable_tipo_pago_efectivo, command=lambda:{self.cambiar_valor(self.variable_tipo_pago_transferencia)})

        # Ubicar el checkbox en la ventana principal
        checkbox_efectivo.grid(column=0, row=0, padx=0, pady=0, sticky=tk.NW)

        self.variable_tipo_pago_transferencia = tk.BooleanVar()

        checkbox_transferencia = tk.Checkbutton(label_frame_tipo_pago, text="Transferencia", variable=self.variable_tipo_pago_transferencia, command=lambda:{self.cambiar_valor(self.variable_tipo_pago_efectivo)})

        # Ubicar el checkbox en la ventana principal
        checkbox_transferencia.grid(column=0, row=1, padx=0, pady=0, sticky=tk.NW)


        boton2=tk.Button(label_frame_tipo_pago, text="Cobrar Pension", command=self.Cobro_Pensionado, width=12, height=1, anchor="center",  font=("Arial", 10), background=button_color, fg=button_letters_color)
        boton2.grid(column=0, row=3, padx=4, pady=4)

        self.etiqueta_informacion_pago = tk.Label(label_frame_tipo_pago, text="", font=("Arial", 11))
        self.etiqueta_informacion_pago.grid(column=0, row=4)    



        labelframe_pensionados_acciones = tk.LabelFrame(labelframe_pensionados, text="Acciones")
        labelframe_pensionados_acciones.grid(column=1, row=0, padx=2, pady=5, sticky=tk.NW)

        self.boton_agregar_pensionado=tk.Button(labelframe_pensionados_acciones, background=button_color, fg=button_letters_color, text="Agregar Pensionado", anchor="center", font=("Arial", 12), width=27, command=self.agregar_pensionado)
        self.boton_agregar_pensionado.grid(column=0, row=0, padx=2, pady=5, sticky=tk.NW)
     
        self.boton_modificar_pensionado=tk.Button(labelframe_pensionados_acciones, background=button_color, fg=button_letters_color, text="Modificar info Pensionado", anchor="center", command=self.modificar_pensionado, font=("Arial", 12), width=27)
        self.boton_modificar_pensionado.grid(column=0, row=1, padx=2, pady=5, sticky=tk.NW)

        labelframe_pensionados_acciones_contraseña = ttk.Frame(labelframe_pensionados_acciones)
        labelframe_pensionados_acciones_contraseña.grid(column=0, row=2)

        lbldatos21=tk.Label(labelframe_pensionados_acciones_contraseña, text="Contraseña", font=("Arial", 10))
        lbldatos21.grid(column=0, row=0, padx=4, pady=4)

        self.variable_contraseña_pensionados=tk.StringVar()
        self.campo_texto_contraseña_pensionados=ttk.Entry(labelframe_pensionados_acciones_contraseña, width=20, textvariable=self.variable_contraseña_pensionados, show="*", font=("Arial", 10), justify='center')
        self.campo_texto_contraseña_pensionados.grid(column=1, row=0, padx=4, pady=4)

       


        ######Muestra de Pensionados Adentro
        labelframe_pensionados_dentro = tk.LabelFrame(labelframe_pensionados, text="Pensionados Adentro")
        labelframe_pensionados_dentro.grid(column=1, row=1, padx=2, pady=5)

        self.lbldatosTotPen=tk.Label(labelframe_pensionados_dentro, text="")
        self.lbldatosTotPen.grid(column=0, row=0, padx=4, pady=4)        

        boton5=tk.Button(labelframe_pensionados_dentro, text="Actualizar", command=self.PenAdentro, width=28, height=1, anchor="center", font=("Arial", 10), background=button_color, fg=button_letters_color)
        boton5.grid(column=0, row=1, padx=4, pady=4)

        self.scroll_pensionados_dentro = st.ScrolledText(labelframe_pensionados_dentro, width=28, height=10)
        self.scroll_pensionados_dentro.grid(column=0,row=2, padx=10, pady=10)




        #Tabla de Pensionados
        labelframe_pensionados.columnconfigure(0, weight=1)
        labelframe_pensionados.rowconfigure(1, weight=1)

        labelframe_tabla_pensionados = tk.LabelFrame(labelframe_pensionados, text="Tabla pensionados")
        labelframe_tabla_pensionados.grid(column=0, row=1, padx=2, pady=5, sticky='NSEW')

        labelframe_tabla_pensionados.columnconfigure(0, weight=1)
        labelframe_tabla_pensionados.rowconfigure(0, weight=1)

        # Obtiene los nombres de las columnas de la tabla que se va a mostrar
        columnas = ['N° de tarjeta', 'Cortesia', 'Nombre', 'Estado', 'Vigencia', 'Tolerancia', 'ID', 'Estatus']

        # Crea un Treeview con una columna por cada campo de la tabla
        self.tabla = ttk.Treeview(labelframe_tabla_pensionados, columns=columnas)
        self.tabla.config(height=4)
        self.tabla.grid(row=0, column=0, sticky='NSEW', padx=2, pady=5)

        # Define los encabezados de columna
        i = 1
        for headd in columnas:
            self.tabla.heading(f'#{i}', text=headd)
            self.tabla.column(f'#{i}', stretch=True)
            i += 1

        self.tabla.column('#0', width=0, stretch=False)
        self.tabla.column('#1', width=85, stretch=False)
        self.tabla.column('#2', width=60, stretch=False)
        self.tabla.column('#3', width=70, stretch=False)
        self.tabla.column('#4', width=70, stretch=False)
        self.tabla.column('#5', width=120, stretch=False)
        self.tabla.column('#6', width=75, stretch=False)
        self.tabla.column('#7', width=0, stretch=False)
        self.tabla.column('#8', width=75, stretch=False)

        # Crea un Scrollbar vertical y lo asocia con el Treeview
        scrollbar_Y = ttk.Scrollbar(labelframe_tabla_pensionados, orient='vertical', command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar_Y.set)
        scrollbar_Y.grid(row=0, column=1, sticky='NS')

        # Crea un Scrollbar horizontal y lo asocia con el Treeview
        scrollbar_X = ttk.Scrollbar(labelframe_tabla_pensionados, orient='horizontal', command=self.tabla.xview)
        self.tabla.configure(xscroll=scrollbar_X.set)
        scrollbar_X.grid(row=1, column=0, sticky='EW')

        # Empaqueta el Treeview en el labelframe
        self.tabla.grid(row=0, column=0, sticky='NSEW', padx=2, pady=5)

        self.tarjetas_expiradas()
        self.ver_pensionados()
        self.PenAdentro()

    def ConsulPagoPen(self):
        """Consulta la informacion de un pensionado y muestra los detalles del pago.
        
        Obtiene la informacion del pensionado asociado al número de tarjeta ingresado,
        calcula el monto a pagar y muestra los detalles del pago en la interfaz gráfica.

        Returns:
            None
        """
        numtarjeta = self.variable_numero_tarjeta.get()

        if not numtarjeta:
            mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
            self.limpiar_datos_pago()
            return

        resultado = self.DB.ValidarRFID(numtarjeta)

        if not resultado:
            mb.showwarning("IMPORTANTE", "No existe Cliente para ese Num de Tarjeta")
            self.limpiar_datos_pago()
            return

        respuesta = self.DB.ConsultaPensionado(resultado)

        if not respuesta:
            mb.showwarning("IMPORTANTE", "No se encontro informacion para el cliente")
            return

        cliente = respuesta[0]
        VigAct = cliente[12]
        Estatus = cliente[14]
        monto = cliente[15]
        cortesia = cliente[16]
        Tolerancia = int(cliente[17])

        self.Monto.set(monto)
        self.Vigencia.set(VigAct)
        self.Estatus.set(Estatus)
        pago = 0
        nummes = int(self.meses_pago.get())

        self.etiqueta_informacion.configure(text="")
        if cortesia == "Si":
            self.etiqueta_informacion.configure(text="El Pensionado cuenta con Cortesía")

        # Logica para determinar el pago según el estatus del pensionado
        # y mostrar mensajes informativos
        if Estatus == "Inactiva":
            # Cálculo del pago con penalizacion para estatus Inactiva
            pago = self.calcular_pago_media_pension(monto)
            nummes = 1
            valor_tarjeta_pension = valor_tarjeta
            if cortesia == "Si":
                pago = 0
                valor_tarjeta_pension = 0
            total = pago + valor_tarjeta_pension
            self.etiqueta_informacion.configure(text="Tarjeta desactivada")
            mb.showwarning("IMPORTANTE", f"La tarjeta esta desactivada, por lo que el pensionado solo pagará los dias faltantes del mes junto al precio de la tarjeta, posteriormente solo pagará el valor registrado de la pension.\n\nPago pension: {pago}\nPago tarjeton:    {valor_tarjeta_pension}\nPago total:        {total}")
            pago = total

        elif Estatus == "InactivaPerm":
            # Cálculo del pago con penalizacion para estatus InactivaPerm
            valor_tarjeta_pension = valor_tarjeta
            pago_mensualidad = monto * nummes
            total = pago_mensualidad + valor_tarjeta_pension

            self.etiqueta_informacion.configure(text="Tarjeta desactivada de forma permanente")
            mb.showwarning("IMPORTANTE", f"La tarjeta esta desactivada de forma permanente, por lo que el pensionado pagará una penalizacion correspondiente al precio de la tarjeta ademas de su respectiva mensualidad.\n\nPago pension: {pago_mensualidad}\nPenalizacion:    {valor_tarjeta_pension}\nPago total:        {total}")
            pago = total

        elif Estatus == "InactivaTemp":
            pago_mensualidad = monto * nummes

            self.etiqueta_informacion.configure(text="Tarjeta desactivada de forma temporal")
            mb.showwarning("IMPORTANTE", f"La tarjeta esta desactivada de forma temporal, por lo que el pensionado solo pagará su respectiva mensualidad.")
            pago = pago_mensualidad

        elif Estatus == "Reposicion":
            self.etiqueta_informacion.configure(text="Tarjeta de reposicion")
            mb.showwarning("IMPORTANTE", "La tarjeta es de reposicion por lo que el pensionado solo pagará dicho valor")
            pago = valor_reposiion_tarjeta

        elif VigAct != None:

            # Obtener la fecha y hora actual en formato deseado
            VigAct = VigAct.strftime("%Y-%m-%d %H:%M:%S")
            # Convertir la cadena de caracteres en un objeto datetime
            VigAct = datetime.strptime(VigAct, "%Y-%m-%d %H:%M:%S")

            # Obtener la fecha y hora actual en formato deseado
            hoy = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            # Convertir la cadena de caracteres en un objeto datetime
            hoy = datetime.strptime(hoy, "%Y-%m-%d %H:%M:%S")

            limite = self.get_date_limit(VigAct, Tolerancia)
            print(f"limite: {limite}")

            penalizacion_pension = 0

            if hoy > limite:
                penalizacion_pension, dias_atrasados = self.calcular_penalizacion_diaria(
                    penalizacion_diaria=penalizacion_diaria_pension,
                    fecha_limite=limite)

                mb.showwarning("IMPORTANTE", f"Vigencia Vencida por {dias_atrasados} días, se aplicará una penalizacion de ${penalizacion_pension}.00 sumado a su pago de pension.")
                self.caja_texto_numero_tarjeta.focus()

            pago = (monto * nummes) + penalizacion_pension

        self.etiqueta_informacion_pago.configure(text=f"${pago}.00")

    def Cobro_Pensionado(self):
        """Realiza el cobro de la pension al pensionado y actualiza su informacion en la base de datos.

        Realiza el cobro correspondiente a la pension del pensionado según su estado,
        tipo de pension y forma de pago seleccionada. Actualiza la informacion del pensionado
        en la base de datos con los nuevos datos de vigencia y estatus. Además, imprime un comprobante
        de pago y muestra mensajes informativos.

        Raises:
            TypeError: Si no se ha seleccionado una forma de pago.
        """
        tarjeta = self.variable_numero_tarjeta.get()
        nummes = int(self.meses_pago.get())

        try:
            usuario = self.DB.nombre_usuario_activo()
            usuario = str(usuario[0][0])
            # usuario = "prueba"

            # Verificar que se ha seleccionado una forma de pago
            if not self.variable_tipo_pago_transferencia.get() and not self.variable_tipo_pago_efectivo.get():
                raise TypeError("Selecciona una forma de pago")

            if not tarjeta:
                mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
                self.caja_texto_numero_tarjeta.focus()
                return

            Existe = self.DB.ValidarRFID(tarjeta)

            if not Existe:
                mb.showwarning("IMPORTANTE", "No existe Cliente para ese Num de Tarjeta")
                self.caja_texto_numero_tarjeta.focus()
                return

            respuesta = self.DB.ConsultaPensionado(Existe)

            if not respuesta:
                mb.showwarning("IMPORTANTE", "No se encontro informacion para el cliente")
                return

            cliente = respuesta[0]
            Nom_cliente = cliente[0]
            Apell1_cliente = cliente[1]
            Apell2_cliente = cliente[2]
            VigAct = cliente[12]
            Estatus = cliente[14]
            monto = cliente[15]
            cortesia = cliente[16]
            Tolerancia = int(cliente[17])

            fechaPago = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            pago = 0
            if Estatus == "Inactiva":
                pago = self.calcular_pago_media_pension(monto)
                nummes = 1
                total = pago + valor_tarjeta
                pago = total
                if cortesia == "Si":
                    pago = 0

            elif Estatus == "InactivaPerm":
                if cortesia == "Si":
                    pago = 0
                pago = monto * nummes
                total = pago + valor_tarjeta
                pago = total

            elif Estatus == "InactivaTemp":
                if cortesia == "Si":
                    pago = 0
                pago_mensualidad = monto * nummes
                pago = pago_mensualidad

            elif Estatus == "Reposicion":pago = valor_reposiion_tarjeta

            elif VigAct != None:

                # Obtener la fecha y hora actual en formato deseado
                VigAct = VigAct.strftime("%Y-%m-%d %H:%M:%S")
                # Convertir la cadena de caracteres en un objeto datetime
                VigAct = datetime.strptime(VigAct, "%Y-%m-%d %H:%M:%S")

                # Obtener la fecha y hora actual en formato deseado
                hoy = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                # Convertir la cadena de caracteres en un objeto datetime
                hoy = datetime.strptime(hoy, "%Y-%m-%d %H:%M:%S")

                limite = self.get_date_limit(VigAct, Tolerancia)
                print(f"limite: {limite}")

                penalizacion_pension = 0

                if hoy > limite:
                    penalizacion_pension, dias_atrasados = self.calcular_penalizacion_diaria(
                        penalizacion_diaria=penalizacion_diaria_pension,
                        fecha_limite=limite)

                pago = (monto * nummes) + penalizacion_pension

            if cortesia == "Si":
                pago = 0
                NvaVigencia = self.nueva_vigencia(
                    fecha= VigAct,
                    cortesia="Si")
                
            else:NvaVigencia = self.nueva_vigencia(
                    fecha= VigAct,
                    meses=nummes)

            datos = (Existe, tarjeta, fechaPago, NvaVigencia, nummes, pago, self.tipo_pago_)
            datos1 = ("Activo", NvaVigencia, Existe)

            self.DB.CobrosPensionado(datos)
            self.DB.Upd_Pensionado(datos1)

            self.imprimir_comprobante_pago_pensionado(
                numero_tarjeta=tarjeta,
                Nom_cliente=Nom_cliente,
                Apell1_cliente=Apell1_cliente,
                Apell2_cliente=Apell2_cliente,
                fecha_pago=fechaPago,
                vigencia=NvaVigencia[:10],
                monto=pago,
                usuario=usuario,
                tipo_pago=self.tipo_pago_
            )

            mb.showinfo("IMPORTANTE", "PAGO realizado con éxito")
            self.limpiar_datos_pago()

        except TypeError as e:
            print(e)
            traceback.print_exc()
            mb.showwarning("Error", e)

        except Exception as e:
            print(e)
            traceback.print_exc()
            mb.showwarning("Error", e)

    def PenAdentro(self):
        """Muestra en la interfaz gráfica la lista de pensionados que están adentro.

        Obtiene la lista de pensionados que están dentro del lugar y muestra sus nombres
        y detalles en un ScrolledText en la interfaz gráfica.
        """
        self.scroll_pensionados_dentro.configure(state="normal")
        respuesta=self.DB.TreaPenAdentro()
        self.scroll_pensionados_dentro.delete("1.0", tk.END)
        cont=0
        for fila in respuesta:
            self.scroll_pensionados_dentro.insert(tk.END,
            f"{cont+1}) {fila[0]}: \n   {fila[1]} {fila[2]}\n   {fila[3]} - {fila[4]}\n\n")
            cont=cont+1
        self.lbldatosTotPen.configure(text="PENSIONADOS ADENTRO: "+str(cont))
        self.scroll_pensionados_dentro.configure(state="disabled")

    def imprimir_comprobante_pago_pensionado(self,
                                            numero_tarjeta: str,
                                            Nom_cliente: str,
                                            Apell1_cliente: str,
                                            Apell2_cliente: str,
                                            fecha_pago: str,
                                            vigencia: str,
                                            monto: float,
                                            usuario: str,
                                            tipo_pago: str) -> None:
        """Imprime un comprobante de pago de una pension.
        Args:
            numero_tarjeta (str): El número de tarjeta del pensionado.
            Nom_cliente (str): El nombre del pensionado.
            Apell1_cliente (str): El primer apellido del pensionado.
            Apell2_cliente (str): El segundo apellido del pensionado.
            fecha_pago (str): La fecha en que se hizo el pago.
            vigencia (str): La fecha de vigencia de la pension.
            monto (float): El monto que se pago.
            usuario (str): Nombre del usuario en turno.
            tipo_pago (str): Tipo de pago.
        Returns:
            None: Esta funcion no devuelve nada, simplemente imprime un comprobante.
        Raises:
            None
        """
        printer = Usb(0x04b8, 0x0e28, 0)
        # Establece la alineacion del texto al centro
        printer.set(align="center")

        printer.text("----------------------------------\n")
        # Agrega un encabezado al comprobante
        printer.text("Comprobante de pago\n\n")
        
        # Establece la alineacion del texto a la izquierda
        printer.set(align="left")

        # Agrega informacion sobre el pago al comprobante
        printer.image(logo_1)
        printer.text(f"Numero de tarjeta: {numero_tarjeta}\n")
        printer.text(f"Nombre: {Nom_cliente}\n")
        printer.text(f"Apellido 1: {Apell1_cliente}\n")
        printer.text(f"Apellido 2: {Apell2_cliente}\n")
        printer.text(f"Fecha de pago: {fecha_pago}\n")
        printer.text(f"Monto pagado: ${monto}\n")
        printer.text(f"Tipo de pago: {tipo_pago}\n")
        printer.text(f"Cobro: {usuario}\n\n")
        printer.text(f"Fecha de vigencia: {vigencia}\n")

        printer.text("----------------------------------\n")

        # Corta el papel para finalizar la impresion
        printer.cut()
        printer.close()

    def cambiar_valor(self, contrario):
        """Cambia el valor de la variable según las variables de tipo de pago seleccionadas.
        Args:
            contrario (BooleanVar): Una variable booleana que se utiliza para establecer un valor opuesto.
        Returns:
            None
        """
        try:
            # Establece la variable contrario como False
            contrario.set(False)

            # Si la variable de tipo de pago transferencia está seleccionada, establece tipo_pago_ como "Transferencia"
            if self.variable_tipo_pago_transferencia.get():
                self.tipo_pago_ = "Transferencia"

            # Si la variable de tipo de pago efectivo está seleccionada, establece tipo_pago_ como "Efectivo"
            elif self.variable_tipo_pago_efectivo.get():
                self.tipo_pago_ = "Efectivo"

            # Si ninguna de las variables de tipo de pago está seleccionada, establece tipo_pago_ como None
            else:
                self.tipo_pago_ = None

        except Exception as e:
            # Si ocurre un error, no hace nada
            pass

    def vaciar_tipo_pago(self):
        """Vacia las variables de tipo de pago.
        Returns:
            None
        """
        # Establece las variables de tipo de pago como False
        self.variable_tipo_pago_transferencia.set(False)
        self.variable_tipo_pago_efectivo.set(False)

    def nueva_vigencia(self, fecha, meses = 1, cortesia = None):
        """
        Obtiene la fecha del último día del mes siguiente a la fecha dada y la devuelve como una cadena de texto en el formato '%Y-%m-%d %H:%M:%S'.

        :param fecha (str or datetime): Fecha a partir de la cual se obtendrá la fecha del último día del mes siguiente.

        :raises: TypeError si la fecha no es una cadena de texto ni un objeto datetime.

        :return:
            - nueva_vigencia (str): Una cadena de texto en el formato '%Y-%m-%d %H:%M:%S' que representa la fecha del último día del mes siguiente a la fecha dada.
        """
        try:
            nueva_vigencia = ''
            if fecha == None:
                # Obtener la fecha y hora actual en formato deseado
                fecha = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

                # fecha = "2023-04-30 23:59:59"

                # Convertir la cadena de caracteres en un objeto datetime
                fecha = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")

                fecha = fecha - relativedelta(months=1)

            # Verificar que la fecha sea de tipo str o datetime
            elif not isinstance(fecha, (str, datetime)):
                raise TypeError("La fecha debe ser una cadena de texto o un objeto datetime.")

            # Convertir la fecha dada en un objeto datetime si es de tipo str
            elif isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d 23:59:59')

            if cortesia == "Si":
                nueva_vigencia = fecha + relativedelta(years=5)

            else:
                # Obtener la fecha del primer día del siguiente mes
                mes_siguiente = fecha + relativedelta(months=meses, day=1)
                
                # Obtener la fecha del último día del mes siguiente
                ultimo_dia_mes_siguiente = mes_siguiente + relativedelta(day=31)
                if ultimo_dia_mes_siguiente.month != mes_siguiente.month:
                    ultimo_dia_mes_siguiente -= relativedelta(days=1)

                nueva_vigencia = ultimo_dia_mes_siguiente

            # convertir la fecha en formato de cadena
            nueva_vigencia = nueva_vigencia.strftime('%Y-%m-%d 23:59:59')

            # Devolver el valor
            return nueva_vigencia
        
        except TypeError as e:
            print(e)
            traceback.print_exc()
            mb.showwarning("Error", f"{e}")
        except Exception as e:
            print(e)
            traceback.print_exc()
            mb.showwarning("Error", f"{e}")

    def BoletoDañado(self):
        """
        Esta funcion se encarga de manejar el cobro de un boleto dañado.

        Verifica si se ha ingresado un número de folio para el boleto dañado y realiza las operaciones correspondientes.
        Muestra informacion relevante del boleto dañado y establece el tipo de pago como "Danado".

        :param self: Objeto de la clase que contiene los atributos y métodos necesarios.

        :return: None
        """

        datos = self.PonerFOLIO.get()
        self.folio.set(str(datos))
        datos = self.folio.get()
        self.folio_auxiliar = datos

        if len(datos) == 0:
            mb.showinfo("Error", "Ingrese el folio del boleto dañado")
            self.limpiar_campos()
            self.entryPonerFOLIO.focus()
            return

        respuesta = self.DB.consulta(datos)
        if len(respuesta) == 0:
            self.limpiar_campos()
            mb.showinfo("Informacion", "No existe un auto con dicho codigo")
            self.entryPonerFOLIO.focus()
            return

        if respuesta[0][6] == "BoletoPerdido":
            mb.showerror("Error", "No se puede cobrar como Danado un boleto perdido")
            self.limpiar_campos()
            self.entryPonerFOLIO.focus()
            return

        self.fecha_entrada.set(respuesta[0][0])
        self.fecha_salida.set(respuesta[0][1])
        self.CalculaPermanencia()
        self.TarifaPreferente.set("Danado")
        self.PonerFOLIO.set('')

    def desactivar(self):
        """Desactiva los botones de la interface"""
        self.root.withdraw()  # oculta la ventana

    def activar(self):
        """ Activa los botones de la interface  """
        self.root.deiconify()

    def desactivar_botones(self):
        """Esta funcion deshabilita los botones que permiten agregar y modificar pensionados en la interfaz gráfica."""
        self.desactivar()
        self.boton_agregar_pensionado.configure(state='disabled')
        self.boton_modificar_pensionado.configure(state='disabled')

    def activar_botones(self):
        """Esta funcion habilita los botones que permiten agregar y modificar pensionados en la interfaz gráfica."""
        self.activar()
        self.boton_agregar_pensionado.configure(state='normal')
        self.boton_modificar_pensionado.configure(state='normal')

    def limpiar_campos(self):
        """Limpia los campos y reinicia los valores de los atributos relacionados con la interfaz gráfica.

        Esta funcion reinicia los valores de varios atributos de la interfaz gráfica a su estado inicial,
        lo que implica limpiar campos de entrada de texto y etiquetas, y establecer valores por defecto en algunos atributos.
        """
        # Reinicia los valores de varios atributos
        self.folio.set("")
        self.Placa.set("")
        self.fecha_entrada.set("")
        self.fecha_salida.set("")
        self.copia_fecha_salida.set("")
        self.importe.set("")
        self.TiempoTotal.set("")
        self.TiempoTotal_auxiliar.set("")
        self.promo.set("")
        self.promo_auxiliar.set('')
        self.PonerFOLIO.set("")
        self.label15.configure(text="")
        self.TarifaPreferente.set("")
        self.IImporte.config(text="")
        self.folio_auxiliar = None
        self.motive_cancel.set("")
        self.entryfolio.focus()
        self.BoletoDentro()

        if show_clock:
            self.reloj.clear_data()

    def vaciar_tabla(self):
        """Vacía la tabla de datos.

        Esta funcion elimina todas las filas de la tabla que muestra los datos de pensionados en la interfaz gráfica.
        """
        # Elimina todas las filas de la tabla
        self.tabla.delete(*self.tabla.get_children())

    def llenar_tabla(self, registros):
        """
        Llena la tabla con los registros que cumplen con los criterios de búsqueda.

        :param registros: (list) Una lista de tuplas que representan los registros obtenidos de la base de datos.

        :raises None:

        :return: None
        """
        # Limpia la tabla antes de llenarla con nuevos registros
        self.vaciar_tabla()

        if self.registros:
            for registro in registros:
                # Pasa los valores del registro como tupla
                self.tabla.insert('', 'end', values=registro)

    def ver_pensionados(self):
        """
        Obtiene y muestra todos los pensionados en la tabla.

        Esta funcion obtiene todos los registros de pensionados desde la base de datos y luego los muestra
        en la tabla de la interfaz gráfica.
        """
        self.registros = self.controlador_crud_pensionados.ver_pensionados()
        self.llenar_tabla(self.registros)

    def eliminar_pensionado(self):
        """Elimina el pensionado seleccionado."""
        pass

    def agregar_pensionado(self):
        """
        Abre la ventana para agregar un nuevo pensionado.

        Esta funcion desactiva los botones, verifica la contraseña, y luego abre la ventana para agregar un nuevo pensionado.
        """
        self.desactivar_botones()
        contraseña = self.variable_contraseña_pensionados.get()

        if len(contraseña) == 0:
            mb.showwarning("Error", "Ingrese la contraseña para agregar un pensionado")
            self.variable_contraseña_pensionados.set("")
            self.campo_texto_contraseña_pensionados.focus()
            self.activar_botones()
            return

        if contraseña != contraseña_pensionados:
            mb.showwarning("Error", "Contraseña incorrecta")
            self.variable_contraseña_pensionados.set("")
            self.campo_texto_contraseña_pensionados.focus()
            self.activar_botones()
            return

        self.variable_contraseña_pensionados.set("")
        self.variable_numero_tarjeta.set("")
        View_agregar_pensionados(nombre_estacionamiento)

        self.limpiar_datos_pago()
        self.ver_pensionados()
        self.activar_botones()

    def modificar_pensionado(self):
        """
        Abre la ventana para modificar los datos de un pensionado existente.

        Esta funcion desactiva los botones, verifica la contraseña y el número de tarjeta del pensionado,
        y luego abre la ventana para modificar los datos del pensionado existente.
        """
        self.desactivar_botones()
        contraseña = self.variable_contraseña_pensionados.get()
        numero_tarjeta = self.variable_numero_tarjeta.get()

        if len(numero_tarjeta) == 0:
            mb.showwarning("Error", "Ingrese el número de tarjeta del pensionado a modificar")
            self.variable_numero_tarjeta.set("")
            self.caja_texto_numero_tarjeta.focus()
            self.activar_botones()
            return

        if len(contraseña) == 0:
            mb.showwarning("Error", "Ingrese la contraseña para agregar un pensionado")
            self.variable_contraseña_pensionados.set("")
            self.campo_texto_contraseña_pensionados.focus()
            self.activar_botones()
            return

        if contraseña != contraseña_pensionados:
            mb.showwarning("Error", "Contraseña incorrecta")
            self.variable_contraseña_pensionados.set("")
            self.campo_texto_contraseña_pensionados.focus()
            self.activar_botones()
            return

        resultado = self.controlador_crud_pensionados.consultar_pensionado(numero_tarjeta)

        if len(resultado) == 0:
            mb.showerror("Error", "No está registrado un pensionado con dicho número de tarjeta")
            self.variable_numero_tarjeta.set("")
            self.limpiar_datos_pago()
            self.activar_botones()
            return

        self.variable_contraseña_pensionados.set("")
        self.variable_numero_tarjeta.set("")
        View_modificar_pensionados(datos_pensionado = resultado, nombre_estacionamiento=nombre_estacionamiento)
        self.limpiar_datos_pago()
        self.ver_pensionados()
        self.activar_botones()

    def limpiar_datos_pago(self):
        """
        Limpia y reinicia los datos relacionados con el pago de pensiones en la interfaz gráfica.

        Esta funcion reinicia los valores y la informacion mostrada en la interfaz gráfica
        relacionados con el pago de pensiones.
        """
        self.etiqueta_informacion.configure(text="")
        self.etiqueta_informacion_pago.configure(text="")
        self.variable_numero_tarjeta.set("")
        self.variable_contraseña_pensionados.set("")
        self.caja_texto_numero_tarjeta.focus()
        self.Monto.set("")
        self.comboMensual.current(0)
        self.Vigencia.set("")
        self.Estatus.set("")
        self.vaciar_tipo_pago()
        self.ver_pensionados()

    def calcular_pago_media_pension(self, monto):
        """
        Calcula el pago de media pension para un pensionado según el monto de la pension.

        :param monto: (float) Monto de la pension.

        :return: (int) El pago de media pension.
        """
        mes_actual = date.today().month
        año_actual = date.today().year

        ultimo_dia_mes = date(año_actual, mes_actual, 1) + relativedelta(day=31)
        dias_mes = ultimo_dia_mes.day

        dias_faltantes = dias_mes - date.today().day
        pago = math.ceil((monto / dias_mes) * dias_faltantes)

        return pago


    def calcular_penalizacion_diaria(self, penalizacion_diaria, fecha_limite):
        """
        Calcula la penalizacion diaria basada en la diferencia de días entre la fecha límite y la fecha actual.

        :param penalizacion_diaria: (float) La cantidad de penalizacion por cada día de atraso.
        :param fecha_limite: (str or datetime) La fecha límite en formato "%Y-%m-%d %H:%M:%S".

        :return: (tuple) Una tupla que contiene la penalizacion total a pagar por los días de atraso y el número de días atrasados.
        """

        # Obtener la fecha y hora actual en formato deseado
        hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # hoy = '2023-07-30 11:59:59' 
        hoy = datetime.strptime(hoy, "%Y-%m-%d %H:%M:%S")

        # Convertir la fecha límite en un objeto datetime si es de tipo str
        if isinstance(fecha_limite, str):
            fecha_limite = datetime.strptime(fecha_limite, "%Y-%m-%d %H:%M:%S")

        # Calcular la cantidad de días de atraso
        fecha_atrasada = hoy - fecha_limite

        # print(f"fecha atrasada: {fecha_atrasada}")

        dias_atrasados = fecha_atrasada.days + 1  # Se suma 1 día para corregir fecha
        #if dias_atrasados == 0:dias_atrasados = 1

        # Calcular la penalizacion total
        penalizacion = dias_atrasados * penalizacion_diaria

        return penalizacion, dias_atrasados

    def tarjetas_expiradas(self):
        """
        Muestra las tarjetas vencidas en una ventana aparte.

        Esta funcion obtiene las tarjetas vencidas desde la base de datos, las muestra en una ventana aparte
        y luego desactiva las tarjetas vencidas en la base de datos.
        """
        tarjetas_expiradas = self.controlador_crud_pensionados.ver_tarjetas_expiradas()

        if len(tarjetas_expiradas) == 0:
            return

        self.mostrar_tabla_tarjetas_expiradas(tarjetas_expiradas)

    def mostrar_tabla_tarjetas_expiradas(self, datos):
        """
        Muestra una ventana con la tabla de tarjetas vencidas.

        :param datos: (list) Una lista de tuplas con los datos de las tarjetas vencidas.

        Esta funcion muestra una ventana con una tabla que contiene los datos de las tarjetas vencidas
        obtenidos desde la base de datos.
        """
        ventana = tk.Toplevel()
        ventana.title("Tarjetas vencidas")

        # Se elimina la funcionalidad del boton de cerrar
        ventana.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana())

        # Deshabilita los botones de minimizar y maximizar
        # ventana.attributes('-toolwindow', True)

        # Crear un Frame para contener la tabla y la etiqueta
        frame_tabla = tk.Frame(ventana)
        frame_tabla.pack(padx=10, pady=10)

        # Agregar etiqueta "Lista de tarjetas vencidas"
        etiqueta_titulo = tk.Label(frame_tabla, text="Lista de tarjetas vencidas", font=("Arial", 14))
        etiqueta_titulo.pack(side=tk.TOP, pady=10)

        # Crear el scroll de lado izquierdo
        scroll_y = tk.Scrollbar(frame_tabla, orient=tk.VERTICAL)

        # Crear la tabla utilizando el widget Treeview de ttk
        tabla = ttk.Treeview(frame_tabla, yscrollcommand=scroll_y.set)
        tabla["columns"] = ("Num_tarjeta", "Fecha_vigencia")

        # Configurar las columnas
        tabla.column("#0", width=0, stretch=tk.NO)  # Columna invisible para los índices
        tabla.column("Num_tarjeta", anchor=tk.CENTER, width=110)
        tabla.column("Fecha_vigencia", anchor=tk.CENTER, width=120)

        # Configurar los encabezados de las columnas
        tabla.heading("#0", text="", anchor=tk.W)
        tabla.heading("Num_tarjeta", text="Número de Tarjeta", anchor=tk.CENTER)
        tabla.heading("Fecha_vigencia", text="Fecha de Vigencia", anchor=tk.CENTER)

        # Insertar datos en la tabla
        for tarjeta, fecha in datos:
            tabla.insert("", "end", values=(tarjeta, fecha))

        # Configurar el scrollbar vertical para que controle la tabla
        scroll_y.config(command=tabla.yview)

        # Empacar el scrollbar vertical en el marco
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tabla.pack(padx=10, pady=10)

        def cerrar_ventana():
            # Obtener la fecha y hora actual en formato deseado
            hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.controlador_crud_pensionados.desactivar_tarjetas_expiradas(hoy)
            self.ver_pensionados()
            ventana.destroy()

        # Agregar boton "Aceptar" en color rojo centrado debajo de la tabla
        btn_aceptar = tk.Button(ventana, text="Aceptar", bg="red", command=cerrar_ventana, font=("Arial", 14))
        btn_aceptar.pack(side=tk.BOTTOM, pady=10)

        # Obtener las dimensiones de la ventana principal
        self.root.update_idletasks()
        ancho_ventana_principal = self.root.winfo_width()
        alto_ventana_principal = self.root.winfo_height()

        # Obtener las dimensiones de la pantalla
        ancho_pantalla = ventana.winfo_screenwidth()
        alto_pantalla = ventana.winfo_screenheight()

        # Calcular la posicion de la ventana secundaria para que quede en el centro de la pantalla
        x = self.root.winfo_x() + (ancho_ventana_principal - ventana.winfo_width()) // 2
        y = self.root.winfo_y() + (alto_ventana_principal - ventana.winfo_height()) // 2

        # Verificar que la ventana secundaria no quede fuera de la pantalla
        x = max(0, min(x, ancho_pantalla - ventana.winfo_width()))
        y = max(0, min(y, alto_pantalla - ventana.winfo_height()))

        # Posicionar la ventana secundaria en el centro de la pantalla
        ventana.geometry(f"+{x}+{y}")

        # Elevar la ventana secundaria al frente de todas las otras ventanas
        ventana.lift()

    def mostrar_importe(self, text_importe):
        """
        Muestra el importe en la interfaz gráfica.

        :param text_importe: (str) El importe a mostrar.

        Esta funcion muestra el importe en la interfaz gráfica, actualizando el valor en la etiqueta correspondiente.
        """
        self.importe.set(text_importe)
        self.IImporte.config(text=self.importe.get())

    def get_date_limit(self, date_start:datetime, Tolerance:int) -> datetime:
        """
        Calcula la fecha límite a partir de una fecha de inicio y una cantidad de días de Tolerancia.

        :param date_start (datetime): Fecha de inicio.
        :param Tolerance (int): Cantidad de días laborables a agregar.
        :return (datetime): Fecha límite después de agregar la cantidad de días laborables.
        """
        date_limit = date_start

        while Tolerance > 0:
            date_limit  += timedelta(days=1)
            # Verifica si el día no es fin de semana (lunes a viernes)
            if date_limit.weekday() < 5:
                Tolerance -= 1
        
        return date_limit

    def on_tab_changed(self, event):
        # Obtener el índice de la pestaña actual
        current_tab_index = self.cuaderno1.index(self.cuaderno1.select())

        # Comprobar si la pestaña actual es la que se desea
        if current_tab_index == 0:
            # Hacer focus en el widget deseado
            self.entry_placa.focus_set()
        
        # Comprobar si la pestaña actual es la que se desea
        elif current_tab_index == 1:
            # Hacer focus en el widget deseado
            self.entryfolio.focus_set()

        # Comprobar si la pestaña actual es la que se desea
        elif current_tab_index == 2:
            self.entry_cortes_anteriores.focus()
            self.Calcular_Corte()
            self.Puertoycontar()

        # Comprobar si la pestaña actual es la que se desea
        elif current_tab_index == 3:
            # Hacer focus en el widget deseado
            self.caja_texto_numero_tarjeta.focus_set()

    def get_day_name(self, day_number:int):
        days = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
        return days[day_number]

    def add_to_text_file(self, txt_file):
        pass


# aplicacion1=FormularioOperacion()
