#programa de entrada en tenayuca 
from datetime import datetime, date, time, timedelta
formato = "%H:%M:%S"
from escpos.printer import *
import qrcode
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from tkinter import scrolledtext as st
from tkinter import font 
#from tkinter import label
# para impresion con  custom
import os
#import cups
#import time, pprint, cups
#from reportlab.lib.pagesizes import letter
#from reportlab.pdfgen import canvas
import re
import operacion_salida as operacion
import time
import traceback
import serial
import RPi.GPIO as io           # Importa libreria de I/O (entradas / salidas)
#Entrada
loop = 16                      #gpio16,pin36,entrada loop                    
boton = 12                     #gpio12,pin32,entrada boton
SenBoleto = 20                 #gpio20,pin38,sensor boleto

#salidas
barrera = 13                  #gpio13,pin33,Salida barrera
out1 = 19                     #gpio19,pin35,Salida indicador loop
out2 = 6                     #gpio6,pin31,Salida indicador boton
out3 = 26                     #gpio26,pin37,Salida indicador barrera
io.setmode(io.BCM)              # modo in/out pin del micro
io.setwarnings(False)           # no señala advertencias de pin ya usados
io.setup(loop,io.IN)             # configura en el micro las entradas
io.setup(boton,io.IN)             # configura en el micro las entradas
io.setup(SenBoleto,io.IN)             # configura en el micro las entradas
io.setup(barrera,io.OUT)           # configura en el micro las salidas
io.setup(out1,io.OUT)           # configura en el micro las salidas
io.setup(out2,io.OUT)
io.setup(out3,io.OUT)  
line=''
io.output(barrera,0)
io.output(out1,0)
io.output(out2,0)
io.output(out3,0)
BanLoop =0
BanBoton=0
BanSenBoleto=0
BanImpresion=0 #No ha impreso
# Configuracion de las entradas y las salidas del micro
# -----------------------------------------------------
class FormularioOperacion:
    def __init__(self):
        #creamos un objeto que esta en el archivo operacion dentro la clase Operacion
        self.operacion1=operacion.Operacion()
        self.ventana1=tk.Tk()
        self.ventana1.title("SALIDA DEL ESTACIONAMIENTO")
        self.ventana1.configure(bg="#081f3d")
        self.ventana1.attributes("-fullscreen", True)
        self.ventana1.bind(
            "<Escape>",
            lambda _event: self.ventana1.attributes("-fullscreen", False)
        )
        self.pantalla_salida_moderna()
        #self.botonpImprimir()
        #self.calcular_cambio()
        self.IntBoton()
        self.Intloop()
        self.ventana1.mainloop()
    ###########################Inicia Pagina1##########################
# Funcion de lectura de las entradas
# -----------------------------------
    def ExpedirRfid(self):    
        self.pagina1 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina1, text="Expedir Boleto")
        #enmarca los controles LabelFrame
        self.labelframe1=ttk.LabelFrame(self.pagina1, text=" ")
        self.labelframe1.grid(column=0, row=0, padx=0, pady=0)
        self.Adentroframe=ttk.LabelFrame(self.pagina1, text=" ")
        self.Adentroframe.grid(column=1, row=0, padx=0, pady=0)
        self.MaxId=tk.StringVar()
        self.entryMaxId=ttk.Entry(self.labelframe1, width=10, textvariable=self.MaxId, state="readonly")
        self.entryMaxId.grid(column=1, row=0, padx=4, pady=4)
        #self.lbltitulo=ttk.Label(self.labelframe1, text="FOLIO")
        #self.lbltitulo.grid(column=0, row=0, padx=0, pady=0)
        #self.presenciaAuto = ttk.Label(self.labelframe1, text="TIPO DE ENTRADA", width = 17)#, background = '#CCC')
        #self.presenciaAuto.grid(column=0, row=6, padx=0, pady=0)
        self.Bienvenida = ttk.Label(self.Adentroframe, text="BIENVENIDOS", width = 20, font=('Arial', 30))#, background = '#FD6')
        #self.Bienvenida.config(font=('Arial', 40))
        self.Bienvenida.grid(column=2, row=2, padx=0, pady=0)
        self.SenBol2 = ttk.Label(self.Adentroframe, text=".", width = 20, font=('Arial', 15))#, background = '#CCC') , background = 'green'
        self.SenBol2.grid(column=1, row=12, padx=0, pady=0)
        self.loopDet = ttk.Label(self.Adentroframe, text="1) OPRIMA EL BOTON ", width = 20, font=('Arial', 15), background = '#CCC') #, background = '#FD6')
        self.loopDet.grid(column=1, row=8, padx=0, pady=0)
        self.BotDet = ttk.Label(self.Adentroframe, text="Boton", width = 20, font=('Arial', 15), background = '#CCC')#, background = '#CCC')
        self.BotDet.grid(column=1, row=6, padx=0, pady=0)
        self.SenBol = ttk.Label(self.Adentroframe, text=".", width = 20, font=('Arial', 15))#, background = '#CCC') , background = 'green'
        self.SenBol.grid(column=1, row=10, padx=0, pady=0)
        
        #self.Reloj = ttk.Label(self.pagina1, text="Hora y fecha", width = 10, background = '#FD6')
        #self.Reloj.grid(column=0, row=6, padx=0, pady=0)

        self.Reloj = ttk.Label(self.pagina1, text="Reloj") #Creación del Label
        self.Reloj.config(width =10)
        self.Reloj.config(background="white") #Cambiar color de fondo
        self.Reloj.config(font=('Arial', 60)) #Cambiar tipo y tamaño de fuente 80
        self.Reloj.grid(column=1, row=12, padx=0, pady=0)  #4 
        
        self.mi_reloj = ttk.Label(self.pagina1, text="Reloj") #Creación del Label
        self.mi_reloj.config(width =10)
        self.mi_reloj.config(background="white") #Cambiar color de fondo
        self.mi_reloj.config(font=('Arial', 60)) #Cambiar tipo y tamaño de fuente 80
        self.mi_reloj.grid(column=1, row=14, padx=0, pady=0)       #6 
        self.boton2=tk.Button(self.pagina1, text="Salir del programa", command=quit, width=15, height=1, anchor="center", background="blue")
        self.boton2.grid(column=1, row=16, padx=4, pady=4)  
        #####tomar placas del auto
        self.Placa=tk.StringVar()
        self.entryPlaca=tk.Entry(self.labelframe1, width=15, textvariable=self.Placa)
        self.entryPlaca.grid(column=1, row=1, padx=4, pady=4)
        #self.lblPlaca=ttk.Label(self.labelframe1, text="COLOCAR PLACAS")
        #self.lblPlaca.grid(column=0, row=1, padx=0, pady=0)

        #self.labelhr=ttk.Label(self.labelframe1, text="HORA ENTRADA")
        #self.labelhr.grid(column=0, row=2, padx=0, pady=0)

        #self.scrolledtext=st.ScrolledText(self.Adentroframe, width=20, height=3)
        #self.scrolledtext.grid(column=1,row=0, padx=4, pady=4)
        #self.Autdentro=tk.Button(self.Adentroframe, text="Boletos sin Cobro", command=self.Autdentro, width=15, height=1, anchor="center")
        #self.Autdentro.grid(column=2, row=0, padx=4, pady=4)
        #self.labeRFID=ttk.Label(self.Adentroframe, text="LECTURA RFID")
        #self.labeRFID.grid(column=1, row=3, padx=0, pady=0)
        #self.RFID=tk.StringVar()
        #self.entryRFID=tk.Entry(self.Adentroframe, width=20, textvariable=self.RFID)
        #self.entryRFID.grid(column=1, row=1, padx=4, pady=4)
        #self.botonPent=tk.Button(self.Adentroframe, text="DeclararlaEnt", command= self.check_inputs, width=15, height=1, anchor="center")
        #self.botonPent.grid(column=2, row=1, padx=4, pady=4)            
 
        # La estacion de Salida no debe generar boletos de entrada.
        self.boton1=tk.Button(self.labelframe1, text="USE LECTOR QR", width=13, height=3, anchor="center", background="blue", state=tk.DISABLED)
        self.boton1.grid(column=1, row=4, padx=4, pady=4)

        ###Pensionados
        self.labelframe3=ttk.LabelFrame(self.pagina1, text="PENSIONADOS")
        self.labelframe3.grid(column=1, row=2, padx=0, pady=0)        
        self.labelTarjeta=ttk.Label(self.labelframe3, text="Tarjeta:")
        self.labelTarjeta.grid(column=0, row=2, padx=0, pady=0)
        self.NumTarjeta4=tk.StringVar()
        self.entryNumTarjeta4=tk.Entry(self.labelframe3, width=20, textvariable=self.NumTarjeta4)
        #self.entryNumTarjeta4.bind('Return', self.Pensionados)
        self.entryNumTarjeta4.grid(column=1, row=2, padx=4, pady=4)
        self.entryNumTarjeta4.focus()
        self.labelMensaje=ttk.Label(self.labelframe3, text="")
        self.labelMensaje.grid(column=2, row=2, padx=0, pady=0)

        #self.botonPensinados=tk.Button(self.labelframe3, text="Entrada", command=self.Pensionados, width=10, height=1, anchor="center")
        #self.botonPensinados.grid(column=2, row=2, padx=4, pady=4)  
    def SenBoleto(self): #Detecta presencia de automovil
        global BanSenBoleto
        if io.input(SenBoleto):
                 
                io.output(out3,1)#con un "1" se apaga el led
                #self.loopDet.config(text = "Inicio", background = '#CCC')                
                BanSenBoleto = 1
                print('siente boleto '+str(BanSenBoleto))
                #self.check_inputs()
        else:                
                 
                io.output(out3,0)                              
                #self.loopDet.config(text = "Auto", background = 'red')
                BanSenBoleto = 0
                #print('No siente boleto '+str(BanSenBoleto))
                #self.check_inputs()

    def Intloop(self): #Detecta presencia de automovil
        global BanLoop
        if io.input(loop):
                #print('hay auto') 
                io.output(out1,1)#con un "1" se apaga el led
                #self.loopDet.config(text = "Inicio", background = '#CCC')                
                BanLoop = 1
                #self.check_inputs()
        else:                
                #print('No hay auto') 
                io.output(out1,0)                              
                #self.loopDet.config(text = "Auto", background = 'red')
                BanLoop = 0
                #self.check_inputs()
    def IntBoton(self): #Detecta presencia de automovil
        global BanBoton
        if io.input(boton):
                        #self.BotDet.config(text = "Presione Boton",background="#CCC")
                        #print('Presiono boton')
                        io.output(out2,1)
                        BanBoton = 1
        else:
                        #print('Solto boton')            
                        io.output(out2,0)
                        #self.BotDet.config(text = "Imprimiendo",background="red")
                        BanBoton = 0
                        #self.agregarRegistroRFID()
    io.add_event_detect(16, io.BOTH, callback = Intloop)
 
    io.add_event_detect(12, io.BOTH, callback = IntBoton)
    
    io.add_event_detect(20, io.BOTH, callback = SenBoleto)


    def check_inputs(self):
        global BanBoton
        global BanLoop
        global BanImpresion
    
        if BanLoop == 1:
                self.loopDet.config(text = "OPRIMA BOTON", font=('Arial', 15), background = 'green')
                tarjeta=str(self.entryNumTarjeta4.get(),)
                if len(tarjeta) == 10:
                    #mb.showwarning("IMPORTANTE", "ENTRO")
                    self.Pensionados(self)
        else:
                self.loopDet.config(text = ".", font=('Arial', 15), background = '#CCC') #'#CCC'
                self.SenBol2.config(text = ".", font=('Arial', 15), background='#CCC')
                self.SenBol.config(text = ".", font=('Arial', 15), background='#CCC')
                self.labelMensaje.config(text= "Sin Tarjeta para acceder")
                self.NumTarjeta4.set("")               
                self.entryNumTarjeta4.focus()
               
        # Este archivo es la SALIDA. El bloque original provenia de la
        # boletera de Entrada e intentaba imprimir y registrar un boleto nuevo
        # al detectar el pulsador. En Salida la barrera se controla solamente
        # dentro de consultar(), despues de validar un QR pagado.
        if BanBoton == 0:
            self.BotDet.config(text=".", font=('Arial', 15), background='#CCC')
        else:
            self.BotDet.config(
                text="ESCANEE QR",
                font=('Arial', 15),
                background="orange"
            )

        now =datetime.now() 
        fecha1= now.strftime("%d-%b-%y")
        hora1= now.strftime("%H:%M:%S")    
        self.Reloj.config(text=fecha1)            
        self.mi_reloj.config(text=hora1)    
        self.ventana1.after(60, self.check_inputs)          # activa un timer de 50mSeg.
   
    def Autdentro(self):
        respuesta=self.operacion1.Autos_dentro()
        self.scrolledtext.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtext.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])+"\n\n")
     
    def agregarRegistroRFID(self):
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$impresion    $$$$$$$$$$$$$$$$$$$
        fechaEntro = datetime.today()
        fSTR=str(fechaEntro)
        corteNum = 0
        placa=str(self.Placa.get(), )                 
        datos=(fechaEntro, corteNum, placa)
        time.sleep(1)                            
        self.operacion1.altaRegistroRFID(datos) 
        MaxFolio=str(self.operacion1.MaxfolioEntrada())
        MaxFolio = MaxFolio.strip("[(,)]")
        n1 = MaxFolio
#        n2 = "1"
#        masuno = int(n1)+int(n2)
        masuno=n1
        masuno = str(masuno)
        self.MaxId.set(masuno)
        imgqr=(fSTR + masuno) 
        horaentrada = str(fechaEntro)
        horaentrada=horaentrada[:16]
        #self.labelhr.configure(text=(horaentrada, "Entró"))
        fSTR=str(fechaEntro)
        imgqr=(fSTR + masuno)
        #img = qrcode.make(fechaEntro)
        img = qrcode.make(imgqr)
        # Obtener imagen con el tamaño indicado
        reducida = img #.resize((100, 25))
        # Mostrar imagen reducida.show()
        # Guardar imagen obtenida con el formato JPEG
        reducida.save("reducida.png")
        f = open("reducida.png", "wb")
        img.save(f)
        f.close()
        #reducida2 =img2.resize((100, 75))
        #reducida2.save("reducida2.png")
        print("horaentrada",horaentrada)
        print("imgqr",imgqr)
        p = Usb(0x04b8, 0x0202, 0)#0202 04b8:0202
        #p = Usb(0x04b8, 0x0e28, 0)#esta es la impresora con sus valores que se obtienen con lsusb
        #p.set("center")
        #p.text("BOLETO DE ENTRADA\n")
        p.set("center")
        p.image("LOGODIR4.jpg")
        #p.set(font='b', height=4, align='right')
        p.set("center")
        p.text("\n")
        p.text("BOLETO DE ENTRADA\n")
        p.set(height=2, align='center')
        folioZZ=('FOLIO 000' + masuno)
        p.text(folioZZ+'\n')
        p.set("center")        
        p.text('Entro: '+horaentrada+'\n')
        #p.text('Monterrey No. 75'+placa+'\n')
        #p.text('Entrada (Durango)'+placa+'\n')
        p.set(align="center")
        #p.image("LOGO1.jpg")
        p.image("reducida.png")
        #p.image("AutoA.png")
        #p.text("            Le Atiende:               \n")
        p.text("--------------------------------------\n")
        p.cut()        
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$impresion fin$$$$$$$$$$$$$$$$                
        self.Placa.set('')

    def Pensionados(self,event): ##Actualizo 16JULIO22
        numtarjeta=str(self.NumTarjeta4.get(), )
        tarjeta=int(numtarjeta)
        print(tarjeta)
        Existe=self.operacion1.ValidarPen(tarjeta)
        #mb.showwarning("IMPORTANTE", str(Existe))
        if len(Existe) == 0 :
            #mb.showwarning("IMPORTANTE", "No existe Pensionado para ese Num de Tarjeta")
            self.labelMensaje.config(text= "No existe Pensionado"+ str(Existe)+str(tarjeta))
            self.NumTarjeta4.set("")               
            self.entryNumTarjeta4.focus()
            return False
        else:        
            respuesta=self.operacion1.ConsultaPensionado(Existe)
            #Fecha_vigencia, Estatus, Vigencia
            for fila in respuesta:
                VigAct=fila[0]
                Estatus=fila[1]
                Vigencia =fila[2]
                Tolerancia=int(fila[3])
                #print("Tolerancia: ",str(Tolerancia))
                if Estatus == 'Adentro' :
                    self.labelMensaje.config(text= "Ya está Adentro")
                    #mb.showwarning("IMPORTANTE", "NO PUEDE ACCEDER: Ya existe un auto adentro registrado")
                    self.NumTarjeta4.set("")               
                    self.entryNumTarjeta4.focus()
                    return False
                elif VigAct == 'Inactiva' :
                    self.labelMensaje.config(text= "Sin Vigencia Activa")
                    #mb.showwarning("IMPORTANTE", "SIN VIGENCIA ACTIVA: Pensionado sin pago, favor de realizar pago")
                    self.NumTarjeta4.set("")               
                    self.entryNumTarjeta4.focus()
                    return False                        
                elif VigAct <= datetime.today()+timedelta(days = Tolerancia):
                    datos1=('Afuera','VENCIDA', Existe)
                    self.labelMensaje.config(text= "Vigencia VENCIDA")
                    self.operacion1.UpdPensionado(datos1)
                    #mb.showwarning("IMPORTANTE", "NO PUEDE ACCEDER: La Vigencia esta vencida")
                    self.NumTarjeta4.set("")               
                    self.entryNumTarjeta4.focus()
                    return False
                else:
                    Entrada=datetime.today()
                    datos=(Existe, tarjeta, Entrada, 'Adentro')
                    datos1=('Adentro', Vigencia, Existe)
                    #mb.showinfo("Pago de Pension",'BIENVENIDO')
                    #sql="INSERT INTO PagosPens(id_cliente, num_tarjeta, Fecha_pago, Fecha_vigencia, Mensualidad, Monto) values (%s,%s,%s,%s,%s,%s)"
                    self.operacion1.MovsPensionado(datos)
                    self.operacion1.UpdPensionado(datos1)
                    self.NumTarjeta4.set("")               
                    self.entryNumTarjeta4.focus()
                    io.output(out3,1)#con un "1" se apaga el led
                    io.output(barrera,0)#con un "0" abre la barrera
                    time.sleep (1)
                    io.output(barrera,1)
                    self.NumTarjeta4.set("")               
                    self.entryNumTarjeta4.focus()                
                

    def pantalla_salida_moderna(self):
        """Pantalla publica de salida, optimizada para verse desde el auto."""
        azul="#081f3d"
        azul_claro="#123b67"
        blanco="#ffffff"
        verde="#178b55"
        gris="#eaf0f5"

        nombre=os.environ.get(
            "ESTACIONAMIENTO_NOMBRE",
            "CHAPULTEPEC"
        ).strip() or "CHAPULTEPEC"
        anuncio_titulo=os.environ.get(
            "ESTACIONAMIENTO_PUBLICIDAD_TITULO",
            "ESPACIO PUBLICITARIO"
        )
        anuncio_mensaje=os.environ.get(
            "ESTACIONAMIENTO_PUBLICIDAD_MENSAJE",
            "Gracias por su visita"
        )

        self.ventana1.grid_columnconfigure(0, weight=1)
        self.ventana1.grid_rowconfigure(1, weight=1)

        encabezado=tk.Frame(self.ventana1, bg=azul, padx=30, pady=18)
        encabezado.grid(column=0, row=0, sticky="ew")
        encabezado.grid_columnconfigure(1, weight=1)
        tk.Label(
            encabezado, text=nombre.upper(), bg=azul, fg=blanco,
            font=("Arial", 30, "bold")
        ).grid(column=0, row=0, sticky="w")
        tk.Label(
            encabezado, text="SALIDA", bg=azul, fg="#9fd2ff",
            font=("Arial", 20, "bold")
        ).grid(column=1, row=0, padx=24, sticky="w")
        self.reloj_salida=tk.Label(
            encabezado, text="", bg=azul, fg=blanco,
            font=("Arial", 16, "bold")
        )
        self.reloj_salida.grid(column=2, row=0, sticky="e")

        contenido=tk.Frame(self.ventana1, bg=gris, padx=20, pady=20)
        contenido.grid(column=0, row=1, sticky="nsew")
        contenido.grid_columnconfigure(0, weight=3)
        contenido.grid_columnconfigure(1, weight=2)
        contenido.grid_rowconfigure(0, weight=1)

        operacion=tk.Frame(
            contenido, bg=blanco, highlightbackground="#c9d6e2",
            highlightthickness=1, padx=28, pady=24
        )
        operacion.grid(column=0, row=0, padx=(0, 10), sticky="nsew")
        operacion.grid_columnconfigure(0, weight=1)
        operacion.grid_rowconfigure(2, weight=1)

        tk.Label(
            operacion, text="ESCANEE SU BOLETO O TARJETA",
            bg=blanco, fg=azul, font=("Arial", 22, "bold")
        ).grid(column=0, row=0, pady=(0, 12))

        self.folio=tk.StringVar()
        self.entryfolio=tk.Entry(
            operacion, textvariable=self.folio, justify="center",
            font=("Arial", 25, "bold"), relief="solid", bd=1,
            highlightthickness=2, highlightcolor="#2384c6",
            highlightbackground="#9eb4c8"
        )
        self.entryfolio.bind('<Return>', self.consultar)
        self.entryfolio.grid(column=0, row=1, sticky="ew", padx=45, pady=(0, 18))

        self.descripcion=tk.StringVar(value="LISTO PARA RECIBIR SU BOLETO")
        self.mensaje_salida=tk.Label(
            operacion, textvariable=self.descripcion, bg=azul_claro,
            fg=blanco, font=("Arial", 29, "bold"),
            wraplength=680, justify="center", padx=22, pady=28
        )
        self.mensaje_salida.grid(column=0, row=2, sticky="nsew")

        self.label15=tk.Label(
            operacion, text="Acerque el codigo QR al lector",
            bg=blanco, fg="#49657f", font=("Arial", 15, "bold"),
            wraplength=680, justify="center"
        )
        self.label15.grid(column=0, row=3, sticky="ew", pady=(15, 5))

        pensionados=tk.LabelFrame(
            operacion, text="  SALIDA DE PENSIONADOS  ", bg=blanco,
            fg=azul, font=("Arial", 12, "bold"), padx=12, pady=8
        )
        pensionados.grid(column=0, row=4, pady=(12, 0))
        tk.Label(
            pensionados, text="Tarjeta RFID", bg=blanco, fg=azul,
            font=("Arial", 12, "bold")
        ).grid(column=0, row=0, padx=8)
        self.NumTarjeta2=tk.StringVar()
        self.entryNumTarjeta2=tk.Entry(
            pensionados, width=18, textvariable=self.NumTarjeta2,
            font=("Arial", 15), justify="center"
        )
        self.entryNumTarjeta2.grid(column=1, row=0, padx=8)
        self.botonPensinados=tk.Button(
            pensionados, text="AUTORIZAR SALIDA",
            command=self._autorizar_pensionado_manual, bg=verde, fg=blanco,
            activebackground="#106b40", activeforeground=blanco,
            font=("Arial", 11, "bold"), relief="flat", padx=12, pady=7
        )
        self.botonPensinados.grid(column=2, row=0, padx=8)

        publicidad=tk.Frame(
            contenido, bg=azul, highlightbackground=azul,
            highlightthickness=1, padx=24, pady=24
        )
        publicidad.grid(column=1, row=0, padx=(10, 0), sticky="nsew")
        publicidad.grid_columnconfigure(0, weight=1)
        publicidad.grid_rowconfigure(1, weight=1)
        tk.Label(
            publicidad, text=anuncio_titulo.upper(), bg=azul,
            fg="#9fd2ff", font=("Arial", 18, "bold"),
            wraplength=390, justify="center"
        ).grid(column=0, row=0, sticky="ew", pady=(10, 18))
        tk.Label(
            publicidad, text=anuncio_mensaje, bg=azul, fg=blanco,
            font=("Arial", 28, "bold"), wraplength=390,
            justify="center", padx=12, pady=20
        ).grid(column=0, row=1, sticky="nsew")
        tk.Label(
            publicidad, text="ANUNCIE SU NEGOCIO AQUI",
            bg="#f2b705", fg=azul, font=("Arial", 14, "bold"),
            padx=12, pady=12
        ).grid(column=0, row=2, sticky="ew", pady=(18, 8))

        # Variables y controles heredados que siguen usando las funciones de
        # validacion, promociones y diagnostico, sin mostrarlos al conductor.
        oculto=tk.Frame(self.ventana1)
        self.precio=tk.StringVar()
        self.copia=tk.StringVar()
        self.ffeecha=tk.StringVar()
        self.importe=tk.StringVar()
        self.promo=tk.StringVar()
        self.PrTi=tk.StringVar()
        self.PonerFOLIO=tk.StringVar()
        self.cuantopagasen=tk.StringVar()
        self.elimportees=tk.StringVar()
        self.elcambioes=tk.StringVar()
        self.entrydescripcion=tk.Entry(oculto, textvariable=self.descripcion)
        self.entryprecio=tk.Entry(oculto, textvariable=self.precio)
        self.entrycopia=tk.Entry(oculto, textvariable=self.copia)
        self.entryffeecha=tk.Entry(oculto, textvariable=self.ffeecha)
        self.entryimporte=tk.Entry(oculto, textvariable=self.importe)
        self.entrypromo=tk.Entry(oculto, textvariable=self.promo)
        self.entryPrTi=tk.Entry(oculto, textvariable=self.PrTi)
        self.entryPonerFOLIO=tk.Entry(oculto, textvariable=self.PonerFOLIO)
        self.entrycuantopagasen=tk.Entry(oculto, textvariable=self.cuantopagasen)
        self.entryelimportees=tk.Entry(oculto, textvariable=self.elimportees)
        self.entryelcambioes=tk.Entry(oculto, textvariable=self.elcambioes)
        self.scrolledtxt=st.ScrolledText(oculto, width=1, height=1)
        self.label9=tk.Label(oculto)
        self.label11=tk.Label(oculto)
        self.label12=tk.Label(oculto)
        self.label7=tk.Label(oculto)
        self.label8=tk.Label(oculto)
        self.bcambio=tk.Button(oculto, command=self.calcular_cambio)
        self.labelPensionado=oculto

        self.descripcion.trace_add("write", self._actualizar_estado_salida)
        self.entryfolio.focus_set()
        self._actualizar_reloj_salida()

    def _actualizar_reloj_salida(self):
        self.reloj_salida.configure(
            text=datetime.now().strftime("%d-%m-%Y  %H:%M")
        )
        self.ventana1.after(1000, self._actualizar_reloj_salida)

    def _autorizar_pensionado_manual(self):
        self.folio.set(self.NumTarjeta2.get().strip())
        self.PensionadosOut()
        self.NumTarjeta2.set("")
        self.entryfolio.focus_set()

    def _actualizar_estado_salida(self, *_args):
        mensaje=self.descripcion.get().strip()
        texto=mensaje.lower()
        if not mensaje:
            color="#123b67"
        elif any(palabra in texto for palabra in (
            "abre barrera", "autoriz", "gracias", "bienvenido"
        )):
            color="#178b55"
        elif any(palabra in texto for palabra in (
            "no pagado", "vencida", "utilizado", "invalida", "error",
            "no existe", "ya salio", "sin vigencia", "no hay"
        )):
            color="#b3261e"
        else:
            color="#c47b00"
        self.mensaje_salida.configure(bg=color)

#########################fin de pagina1 inicio pagina2#########################
    def consulta_por_folio(self):
        self.pagina2 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina2, text=" VALIDA - SALIDA ")
        #en el frame
        self.labelframe2=ttk.LabelFrame(self.pagina2, text="Autos")
        self.labelframe2.grid(column=0, row=0, padx=5, pady=10)
        self.label1=ttk.Label(self.labelframe2, text="Lector QR")
        self.label1.grid(column=0, row=0, padx=4, pady=4)
        self.label3=ttk.Label(self.labelframe2, text="Entro:")
        self.label3.grid(column=0, row=1, padx=4, pady=4)
        self.label4=ttk.Label(self.labelframe2, text="Salio:")
        self.label4.grid(column=0, row=2, padx=4, pady=4)
        #en otro frame
        self.labelframe3=ttk.LabelFrame(self.pagina2, text="Datos del COBRO")
        self.labelframe3.grid(column=1, row=0, padx=5, pady=10)
        self.lbl1=ttk.Label(self.labelframe3, text="Hr Salida")
        self.lbl1.grid(column=0, row=1, padx=4, pady=4)
        self.lbl2=ttk.Label(self.labelframe3, text="TiempoTotal")
        self.lbl2.grid(column=0, row=2, padx=4, pady=4)
        self.lbl3=ttk.Label(self.labelframe3, text="Importe")
        self.lbl3.grid(column=0, row=3, padx=4, pady=4)

        self.labelPerdido=ttk.LabelFrame(self.pagina2, text="Perdido")
        self.labelPerdido.grid(column=2,row=1,padx=5, pady=10)
        self.lblFOLIO=ttk.Label(self.labelPerdido, text=" FOLIO PERDIDO")
        self.lblFOLIO.grid(column=0, row=1, padx=4, pady=4)
        self.PonerFOLIO=tk.StringVar()
        self.entryPonerFOLIO=tk.Entry(self.labelPerdido, width=15, textvariable=self.PonerFOLIO)
        self.entryPonerFOLIO.grid(column=1, row=1)
        self.boton2=tk.Button(self.labelPerdido, text="B./SIN cobro", command=self.BoletoDentro, width=10, height=2, anchor="center")
        self.boton2.grid(column=0, row=0)
        self.boton3=tk.Button(self.labelPerdido, text="Boleto Perdido", command=self.BoletoPerdido, width=10, height=2, anchor="center")
        self.boton3.grid(column=0, row=2)
        self.scrolledtxt=st.ScrolledText(self.labelPerdido, width=28, height=7)
        self.scrolledtxt.grid(column=1,row=0, padx=10, pady=10)
        self.labelpromo=ttk.LabelFrame(self.pagina2, text="Promociones")
        self.labelpromo.grid(column=2, row=0, padx=5, pady=10)
        self.promolbl=ttk.Label(self.labelpromo, text="Leer el  QR de Promocion")
        self.promolbl.grid(column=0, row=0, padx=4, pady=4)
        self.promolbl1=ttk.Label(self.labelpromo, text="Codigo QR")
        self.promolbl1.grid(column=0, row=1, padx=4, pady=4)
        self.promolbl2=ttk.Label(self.labelpromo, text="Tipo Prom")
        self.promolbl2.grid(column=0, row=2, padx=4, pady=4)
        self.labelcuantopagas=ttk.LabelFrame(self.pagina2, text='cual es el pago')
        self.labelcuantopagas.grid(column=0,row=1, padx=5, pady=10)
        self.cuantopagas=ttk.Label(self.labelcuantopagas, text="la cantidad entregada")
        self.cuantopagas.grid(column=0, row=0, padx=4, pady=4)
        self.importees=ttk.Label(self.labelcuantopagas, text="el importe es")
        self.importees.grid(column=0, row=1, padx=4, pady=4)
        self.cambio=ttk.Label(self.labelcuantopagas, text="el cambio es")
        self.cambio.grid(column=0, row=2, padx=4, pady=4)
        self.cuantopagasen=tk.StringVar()
        self.entrycuantopagasen=tk.Entry(self.labelcuantopagas, width=15, textvariable=self.cuantopagasen)
        #self.entrycuantopagasen.bind('<Return>',self.calcular_cambio)
        self.entrycuantopagasen.grid(column=1, row=0)
        self.elimportees=tk.StringVar()
        self.entryelimportees=tk.Entry(self.labelcuantopagas, width=15, textvariable=self.elimportees, state="readonly")
        self.entryelimportees.grid(column=1, row=1)
        self.elcambioes=tk.StringVar()
        self.entryelcambioes=tk.Entry(self.labelcuantopagas, width=15, textvariable=self.elcambioes, state="readonly")
        self.entryelcambioes.grid(column=1, row=2)
        self.label11=ttk.Label(self.labelframe3, text="DIAS")
        self.label11.grid(column=1, row=4, padx=1, pady=1)
        self.label12=ttk.Label(self.labelframe3, text="HORAS")
        self.label12.grid(column=1, row=5, padx=1, pady=1)
        self.label7=ttk.Label(self.labelframe3, text="MINUTOS")
        self.label7.grid(column=1, row=6, padx=1, pady=1)
        self.label8=ttk.Label(self.labelframe3, text="SEGUNDOS")
        self.label8.grid(column=1, row=7, padx=1, pady=1)
        self.label9=ttk.Label(self.labelframe3, text="TOTAL COBRO")
        self.label9.grid(column=1, row=8, padx=1, pady=1)
        self.label15=ttk.Label(self.pagina2, text="Viabilidad de COBRO")
        self.label15.grid(column=1, row=2, padx=0, pady=0)
        #se crea objeto para ver pedir el folio la etiqueta con texto
        self.folio=tk.StringVar()
        self.entryfolio=tk.Entry(self.labelframe2, textvariable=self.folio)
        self.entryfolio.bind('<Return>',self.consultar)#con esto se lee automatico y se va a consultar
        self.entryfolio.grid(column=1, row=0, padx=4, pady=4)
        #se crea objeto para mostrar el dato de la  Entrada solo lectura
        self.descripcion=tk.StringVar()
        self.entrydescripcion=ttk.Entry(self.labelframe2, textvariable=self.descripcion, state="readonly")
        self.entrydescripcion.grid(column=1, row=1, padx=4, pady=4)
        #se crea objeto para mostrar el dato la Salida solo lectura
        self.precio=tk.StringVar()
        self.entryprecio=ttk.Entry(self.labelframe2, textvariable=self.precio, state="readonly")
        self.entryprecio.grid(column=1, row=2, padx=4, pady=4)
        #se crea objeto para MOSTRAR LA HORA DEL CALCULO
        self.copia=tk.StringVar()
        self.entrycopia=tk.Entry(self.labelframe3, width=20, textvariable=self.copia, state = "readonly")
        self.entrycopia.grid(column=1, row=1)
        #SE CREA UN OBJETO caja de texto IGUAL A LOS DEMAS Y MUESTRA EL TOTAL DEL TIEMPO
        self.ffeecha=tk.StringVar()
        self.entryffeecha=tk.Entry(self.labelframe3, width=20, textvariable=self.ffeecha, state= "readonly")
        self.entryffeecha.grid(column=1, row=2)
        #SE CREA UN OBJETO caja de texto IGUAL A LOS DEMAS para mostrar el importe y llevarlo a guardar en BD
        self.importe=tk.StringVar()
        self.entryimporte=tk.Entry(self.labelframe3, width=20, textvariable=self.importe, state= "readonly")
        self.entryimporte.grid(column=1, row=3)
        #creamos un objeto para obtener la lectura de la PROMOCION
        self.promo=tk.StringVar()
        self.entrypromo=tk.Entry(self.labelpromo, width=20, textvariable=self.promo)
        self.entrypromo.grid(column=1, row=1)
        #este es donde pongo el tipo de PROMOCION
        self.PrTi=tk.StringVar()
        self.entryPrTi=tk.Entry(self.labelpromo, width=20, textvariable=self.PrTi, state= "readonly")
        self.entryPrTi.grid(column=1, row=2)
        #botones
        #self.boton1=tk.Button(self.labelframe2, text="Consultar", command=self.consultar, width=20, height=5, anchor="center")
        #self.boton1.grid(column=1, row=4)
        self.boton2=tk.Button(self.labelpromo, text="PROMOCION", command=self.CalculaPromocion, width=20, height=5, anchor="center")
        self.boton2.grid(column=1, row=4)
        #self.boton3=tk.Button(self.pagina2, text="COBRAR ", command=self.GuardarCobro, width=20, height=5, anchor="center", background="Cadetblue")
        #self.boton3.grid(column=1, row=1)
        #self.boton4=tk.Button(self.labelframe3, text="IMPRIMIR", command=self.Comprobante, width=10, height=2, anchor="center", background="Cadetblue")
        #self.boton4.grid(column=0, row=4)
        self.bcambio=tk.Button(self.labelcuantopagas, text="cambio", command=self.calcular_cambio, width=10, height=2, anchor="center", background="blue")
        self.bcambio.grid(column=0, row=4)
        
        ####PENSIONADOS
        self.labelPensionado=ttk.LabelFrame(self.pagina2, text="SALIDA PENSIONADO")
        self.labelPensionado.grid(column=1, row=1, padx=5, pady=10)
        self.labelTarjeta=ttk.Label(self.labelPensionado, text="Num. Tarjeta:")
        self.labelTarjeta.grid(column=0, row=2, padx=0, pady=0)
        self.NumTarjeta2=tk.StringVar()
        self.entryNumTarjeta2=tk.Entry(self.labelPensionado, width=15, textvariable=self.NumTarjeta2)
        self.entryNumTarjeta2.grid(column=1, row=2, padx=4, pady=4)
        self.botonPensinados=tk.Button(self.labelPensionado, text="Salida", command=self.PensionadosSalida, width=10, height=1, anchor="center")
        self.botonPensinados.grid(column=1, row=3, padx=4, pady=4)  
        
    def BoletoDentro(self):
        respuesta=self.operacion1.Autos_dentro()
        self.scrolledtxt.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtxt.insert(tk.END, "Folio num: "+str(fila[0])+"\nEntro: "+str(fila[1])+"\nPlacas: "+str(fila[2])+"\n\n")
    def BoletoPerdido(self):
       datos=str(self.PonerFOLIO.get(), )
       datos=int(datos)
       datos=str(datos)
       self.folio.set(datos)
       datos=(self.folio.get(), )
       respuesta=self.operacion1.consulta(datos)
       if len(respuesta)>0:
           self.descripcion.set(respuesta[0][0])
           self.precio.set(respuesta[0][1])
           self.CalculaPermanencia()#nos vamos a la funcion de calcular permanencia
           fecha = datetime.today()
           fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
           fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
           date_time_str=str(self.descripcion.get())
           date_time_obj= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
           date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
           date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
           ffeecha = fechaActual - date_time_mod2
            #self.label11.configure(text=(ffeecha.days, "dias"))
           segundos_vividos = ffeecha.seconds
           horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
        #    self.label12.configure(text=(horas_dentro, "horas"))
           minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
           if horas_dentro <= 24:
                importe = 200
           if horas_dentro > 24 or ffeecha.days >= 1:
                importe = 200+((ffeecha.days)*720 + (horas_dentro * 30))
           self.importe.set(importe)
           self.label9.configure(text =(importe, "cobro"))
           self.PrTi.set("Per")
           self.Comprobante()
           p = Usb(0x04b8, 0x0202, 0)
           #p = Usb(0x04b8, 0x0e28, 0)#esta es la impresora con sus valores que se obtienen con lsusb
           p.text('Boleto Perdido\n')
           FoliodelPerdido = str(self.PonerFOLIO.get(),)
           p.text('Folio boleto cancelado: '+FoliodelPerdido+'\n')
           fecha = datetime.today()
           fechaNota = datetime.today()
           fechaNota= fechaNota.strftime("%b-%d-%A-%Y %H:%M:%S")
           horaNota = str(fechaNota)
           p.set(align="left")
           p.set('Big line\n', font='b')
           p.text('Fecha: '+horaNota+'\n')
           EntradaCompro = str(self.descripcion.get(),)
           p.text('El auto entro: '+EntradaCompro+'\n')
           SalioCompro = str(self.copia.get(),)
           p.text('El auto salio: '+SalioCompro+'\n')
           self.GuardarCobro()
           self.PonerFOLIO.set("")
           p.cut()
           self.promo.set("")
           self.PonerFOLIO.set("")
         
       else:
           self.descripcion.set('')
           self.precio.set('')
           mb.showinfo("Información", "No NO")
    def consultar(self,event): ##Actualizo el 16julio22
        self.descripcion.set('')
        datos=str(self.folio.get(), )
        #print(datos)
        if len(datos) == 10:
            self.PensionadosOut(self)
            print("pensionado")
        elif len(datos) > 19:#con esto revisamos si lee el folio o la promocion
            datos=datos[19:]
            #print(datos)
            #datos=int(datos)
            datos=str(datos)
            print(str(datos))
            #self mb.showwarning("important", str(datos))
            respuesta=self.operacion1.consulta(datos)
            #self.folio.set(datos)
            #datos=(self.folio.get(), )
            if len(respuesta)>0:
                #self.descripcion.set(respuesta[0][0])
                #self.precio.set(respuesta[0][1])
                #self.CalculaPermanencia()#nos vamos a la funcion de calcular permanencia
                fechaActual = datetime.today()
                #print("Fecha Act 1 ", fechaActual)
                fecha_salida = respuesta[0][1]
                ##Para la version de ORIZABA se deja la salida abierta, no se hace
                ##Validación de Tolerancia
                for fila in respuesta:
                    EstAct = fila[2] #Obtenemos el dato de Placas, para validar que es boleto no se esta re-usando
                #print("Estatus Actual: ", EstAct)
                if fecha_salida == None:
                   print("Boleto No Pagado")
                   ### Label con mensaje de Tolerancia Vencida, No abre Barrera
                   self.descripcion.set('BOLETO NO PAGADO\nACUDA A CAJA')
                   self.precio.set('')
                   self.folio.set("")
                   self.entryfolio.focus()
                elif EstAct == "Afuera":
                   # El boleto ya fue usado para salir: no volver a abrir la barrera.
                   print("Boleto ya utilizado")
                   self.descripcion.set('Boleto ya utilizado, auto afuera')
                   self.precio.set('')
                   self.folio.set("")
                   self.entryfolio.focus()
                else:
                    # El boleto pagado dispone de 15 minutos para salir.
                    # total_seconds evita que una tolerancia mayor a un dia
                    # vuelva a contarse desde cero.
                    tolerancia = fechaActual - fecha_salida
                    segundos_transcurridos = int(tolerancia.total_seconds())

                    if segundos_transcurridos < 0 or segundos_transcurridos > 15 * 60:
                        minutos_vencidos, segundos_vencidos = divmod(
                            max(0, segundos_transcurridos),
                            60
                        )
                        mensaje=(
                            'TOLERANCIA VENCIDA - ACUDA A CAJA\n'
                            f'{minutos_vencidos:02d}:{segundos_vencidos:02d} '
                            'desde el pago'
                        )
                        print(mensaje)
                        self.descripcion.set(mensaje)
                        self.label15.configure(
                            text='SALIDA NO AUTORIZADA - LIMITE 15 MINUTOS'
                        )
                        self.precio.set('')
                        self.folio.set("")
                        self.entryfolio.focus()
                        return

                    segundos_restantes=(15 * 60)-segundos_transcurridos
                    minutos_restantes, segundos_restantes = divmod(
                        segundos_restantes,
                        60
                    )
                    tiempo_restante=(
                        f'{minutos_restantes:02d}:{segundos_restantes:02d}'
                    )
                    #Actualizamos Entradas, campo Placa con el dato "Afuera", con ello se marca el folio,
                    #para no ser re-usado para salir. La actualización condicional evita que dos
                    #lecturas casi simultáneas abran la barrera dos veces.
                    estatus=("Afuera",datos)
                    actualizados=self.operacion1.ActualizaSalida(estatus)
                    if actualizados == 1:
                        print("Abre Barrera - pulso de 3 segundos")
                        io.output(barrera,1)#abre la barrera
                        # Algunas tarjetas de control no reconocen un pulso de
                        # un segundo. Se mantiene la polaridad que ya funcionaba
                        # con boleto y se amplía el pulso a tres segundos.
                        time.sleep (3)
                        io.output(barrera,0)
                        self.descripcion.set(
                            'GRACIAS POR SU VISITA\nBARRERA ABIERTA'
                        )
                        self.label15.configure(
                            text='Tolerancia válida: restan '+tiempo_restante
                        )
                    else:
                        print("Boleto ya utilizado")
                        self.descripcion.set('Boleto ya utilizado, auto afuera')
                    self.folio.set("")
                    self.entryfolio.focus()
                    self.precio.set('')    
                ###Se comenta la condiconante de abajo, se activará en la Version Beta únicamente 16jun22
                #if tolerancia_minutos < 15 and tolerancia_minutos >= 0:
                   ###Abrimos Barrera
                   #print("Abre Barrera")
                   #io.output(barrera,1)#abre la barrera
                   #time.sleep (1)
                   #io.output(barrera,0)
                   #self.descripcion.set('Abre Barrera')
                   #self.folio.set("")
                   #self.entryfolio.focus()
                   #self.precio.set('')
                #else:
                   #print("Boleto Vencido")
                   ### Label con mensaje de Tolerancia Vencida
                   #self.descripcion.set('Boleto Vencido')
                   #self.precio.set('')
                   #self.folio.set("")
                   #self.entryfolio.focus()
                   #mb.showinfo("Información", "No existe un auto con dicho código")                               
            else:
                self.descripcion.set('No existe un auto con dicho código')
                self.precio.set('')
                self.folio.set("")
                self.entryfolio.focus()
        else:
            #mb.showinfo("Promocion", "leer primero el folio")
            self.folio.set("")
            self.entryfolio.focus()   
                ###Se comenta la condiconante de abajo, se activará en la Version Beta únicamente 16jun22
                #if tolerancia_minutos < 15 and tolerancia_minutos >= 0:
                   ###Abrimos Barrera
                   #print("Abre Barrera")
                   #io.output(barrera,1)#abre la barrera
                   #time.sleep (1)
                   #io.output(barrera,0)
                   #self.descripcion.set('Abre Barrera')
                   #self.folio.set("")
                   #self.entryfolio.focus()
                   #self.precio.set('')
                #else:
                   #print("Boleto Vencido")
                   ### Label con mensaje de Tolerancia Vencida
                   #self.descripcion.set('Boleto Vencido')
                   #self.precio.set('')
                   #self.folio.set("")
                   #self.entryfolio.focus()
                   #mb.showinfo("Información", "No existe un auto con dicho código")                               
            #else:
                #self.descripcion.set('No veo el numero ')
                #print("Abre Barrera de no reconocer")
                #io.output(barrera,1)#abre la barrera
                #time.sleep (1)
                #io.output(barrera,0)
                #self.descripcion.set('Abre Barrera')
                #self.folio.set("")
                #self.entryfolio.focus()
                #self.precio.set('')
                #self.precio.set('')
                #self.folio.set("")
                #self.entryfolio.focus()
        #else:
            #mb.showinfo("Promocion", "leer primero el folio")
            #self.folio.set("")
            #self.entryfolio.focus()
    ###PENSIONADOS
    @staticmethod
    def _limite_vigencia_pensionado(fecha_vigencia, tolerancia):
        """Agrega los dias habiles de tolerancia usados por la TPV."""
        limite=fecha_vigencia
        dias=max(0, tolerancia)
        while dias > 0:
            limite += timedelta(days=1)
            if limite.weekday() < 5:
                dias -= 1
        return limite

    def PensionadosOut(self,event=None): ##Actualizo el 24ago2026
        """Valida y registra la salida de un pensionado una sola vez."""
        lectura=str(self.folio.get(), ).strip()
        numtarjeta=''.join(lectura.split())
        print("RFID salida recibido:", repr(lectura), "normalizado:", repr(numtarjeta))

        try:
            if not numtarjeta or not numtarjeta.isdigit():
                self.descripcion.set('Tarjeta RFID invalida')
                return False

            tarjeta=int(numtarjeta)
            print("Tarjeta pensionado:", tarjeta)
            existe=self.operacion1.ValidarPen(tarjeta)
            if len(existe) == 0:
                self.descripcion.set('No existe Pensionado')
                return False

            # ValidarPen devuelve ((id_cliente,),). Extraemos el entero para
            # no enviar una tupla anidada a las consultas de MariaDB.
            id_cliente=existe[0][0]
            respuesta=self.operacion1.ConsultaPensionado((id_cliente,))
            if len(respuesta) == 0:
                self.descripcion.set('No hay datos del Pensionado')
                return False

            fecha_vigencia, estatus, vigencia, tolerancia = respuesta[0]
            try:
                tolerancia=int(tolerancia or 0)
            except (TypeError, ValueError):
                tolerancia=0

            print(
                "Pensionado:", id_cliente,
                "estatus:", estatus,
                "vigencia:", vigencia,
                "fecha:", fecha_vigencia,
                "tolerancia:", tolerancia
            )

            if estatus != 'Adentro':
                if estatus == 'Afuera':
                    self.descripcion.set('Ese Pensionado ya salio')
                else:
                    self.descripcion.set('Pensionado sin registro de Entrada')
                return False

            if vigencia != 'Activo' or fecha_vigencia is None:
                self.descripcion.set('Sin Vigencia Activa')
                return False

            limite=self._limite_vigencia_pensionado(
                fecha_vigencia,
                tolerancia
            )
            if datetime.today() > limite:
                self.descripcion.set('Vigencia Vencida')
                print("Vigencia vencida. Fecha limite:", limite)
                return False

            salida=datetime.today()
            tiempo_total=self.operacion1.RegistrarSalidaPensionado(
                id_cliente,
                salida
            )
            if tiempo_total is None:
                self.descripcion.set('No hay una Entrada abierta')
                print("No se autorizo: no existe movimiento abierto o ya salio")
                return False

            self.descripcion.set(
                'PENSIONADO AUTORIZADO\nBUEN VIAJE - BARRERA ABIERTA'
            )
            print(
                "RFID autorizado:", tarjeta,
                "estancia:", tiempo_total,
                "- abre barrera por 3 segundos"
            )
            io.output(barrera,1)#abre la barrera
            time.sleep(3)
            io.output(barrera,0)
            return True
        except Exception as error:
            self.descripcion.set('Error al registrar salida; revise terminal')
            print("ERROR al procesar salida de pensionado:", error)
            traceback.print_exc()
            return False
        finally:
            self.folio.set("")
            self.entryfolio.focus_set()

    def PensionadosSalida(self):
       numtarjeta=str(self.NumTarjeta2.get(), )
       #print(numtarjeta)
       if len(numtarjeta) == 0:
           mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
           return False
       else:
            tarjeta=int(numtarjeta)
            #print(tarjeta)
            respuesta=self.operacion1.ValidarTarj(tarjeta)
            #print(respuesta)
            if len(respuesta) == 0:
                mb.showwarning("IMPORTANTE", "No existe Pensionado para ese Num de Tarjeta")
                self.NumTarjeta2.set("")               
                self.entryNumTarjeta2.focus()
                return False
            else :
                for fila in respuesta:
                    Existe=fila[0]
                    Estatus=fila[1]
                    print(Existe)
                    if Existe == None :
                        mb.showwarning("IMPORTANTE", "No existe Pensionado para ese Num de Tarjeta")
                        self.NumTarjeta2.set("")               
                        self.entryNumTarjeta2.focus()
                        return False
                    elif Estatus == None:
                        mb.showwarning("IMPORTANTE", "Pensionado sin registro de Entrada")
                        self.NumTarjeta2.set("")               
                        self.entryNumTarjeta2.focus()
                        return False
                    elif Estatus == "Afuera":
                        mb.showwarning("IMPORTANTE", "El Pensionado de con ese Num de Tarjeta, ya esta Afuera")
                        self.NumTarjeta2.set("")               
                        self.entryNumTarjeta2.focus()
                        return False  
                    else:        
                        Salida=datetime.today()
                        datos=(Salida, 'Afuera', Existe)
                        datos1=('Afuera', Existe)
                        #sql="INSERT INTO PagosPens(id_cliente, num_tarjeta, Fecha_pago, Fecha_vigencia, Mensualidad, Monto) values (%s,%s,%s,%s,%s,%s)"
                        self.operacion1.UpdMovsPens(datos)
                        self.operacion1.UpdPens2(datos1)
                        self.NumTarjeta2.set("")               
                        self.entryNumTarjeta2.focus()
                        mb.showinfo("Pago de Pension",'Se registra SALIDA del auto')
                        #io.output(out3,1)#con un "1" se apaga el led
                        io.output(barrera,0)#con un "0" abre la barrera
                        time.sleep (1)
                        io.output(barrera,1)                         
            
    def CalculaPermanencia(self):# funcion que  CALCULA LA PERMANENCIA DEL FOLIO SELECCIONADO
        salida = str(self.precio.get(), )#deveria ser salida en lugar de precio pero asi estaba el base
        
        if len(salida)>5:#None tiene 4 letras si es mayor a 5 es que tiene ya la fecha
            self.label15.configure(text=("Este Boleto ya Tiene cobro"))
            self.elcambioes.set("")
            self.elimportees.set("")
            self.cuantopagasen.set("")
            self.descripcion.set('')
            self.precio.set('')
            self.copia.set("")
            self.importe.set("")
            self.ffeecha.set("")
            self.folio.set("")
            self.label7.configure(text=(""))
            self.label8.configure(text =(""))
            self.label9.configure(text =(""))
#            self.label10.configure(text=(""))
            self.label11.configure(text=(""))
            self.label12.configure(text=(""))
           # self.elimportees.configure(text=(""))
            self.entryfolio.focus()
        else:
            self.PrTi.set("Normal")    
            self.label15.configure(text="Lo puedes COBRAR")
            fecha = datetime.today()
            fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
            fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
            self.copia.set(fechaActual)
            date_time_str=str(self.descripcion.get())
            date_time_obj= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
            date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
            date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
            ffeecha = fechaActual - date_time_mod2
            self.label11.configure(text=(ffeecha.days, "dias"))
            segundos_vividos = ffeecha.seconds
            horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
            self.label12.configure(text=(horas_dentro, "horas"))
            minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
            self.label7.configure(text=(minutos_dentro, "minutos"))
            #calcular la diferencia de segundos
            seg1 = ffeecha.seconds
            #print ("dif = seg1 = ", seg1)
            seg2 = ffeecha.seconds/60
            #print ("dif/60 = seg2 = ", seg2)
            seg3 = int(seg2)
            #print ("entero y redondear seg3 = ", seg3)
            seg4 = seg2-seg3
            #print ("seg2 - seg 3 = seg4 = ", seg4)
            seg5 = seg4*60
            #print ("seg5 =", seg5)
            seg6 = round(seg5)
            #print  ("segundos dentro ===> ", seg6)
            self.label8.configure(text =(seg6, "segundos"))
            #self.label9.configure(text =(ffeecha, "tiempo dentro"))
            self.ffeecha.set(ffeecha)
            if minutos_dentro < 15 and minutos_dentro  >= 0:
                minutos = 1
            if minutos_dentro < 30 and minutos_dentro  >= 15:
                minutos = 2
            if minutos_dentro < 45 and minutos_dentro  >= 30:
                minutos = 3
            if minutos_dentro <= 59 and minutos_dentro  >= 45:
                minutos = 4
            if ffeecha.days == 0 and horas_dentro == 0:
               importe = 30
               self.importe.set(importe)
               #self.elimportees.set(importe)
               self.label9.configure(text =(importe, "cobro"))
               self.entrypromo.focus()
            else:
                importe = ((ffeecha.days)*720 + (horas_dentro * 30)+(minutos)*7.5)
                self.importe.set(importe)
                self.label9.configure(text =(importe, "Cobrar"))
                #self.calcular_cambio()
                self.entrypromo.focus()
    def calcular_cambio(self):
        elimporte=str(self.importe.get(), )
        self.elimportees.set(elimporte)
        valorescrito=str(self.cuantopagasen.get(),)
        elimporte=float(elimporte)
        valorescrito=int(valorescrito)
        mb.showinfo("Imp", elimporte)
        cambio=valorescrito-elimporte
        cambio=str(cambio)
        mb.showinfo("CMbn", cambio)
        self.elcambioes.set(cambio)
        self.Comprobante()#manda a llamar el comprobante y lo imprime
        self.GuardarCobro()#manda a llamar guardar cobro para cobrarlo y guardar registro
        io.output(out1,0)
        time.sleep(1)
        io.output(out1,1)

    def Comprobante(self):
        p = Usb(0x04b8, 0x0202, 0)
        #p = Usb(0x04b8, 0x0e28, 0)#esta es la impresora con sus valores que se obtienen con lsusb
        p.text("Comprobante de pago\n")
        p.image("LOGO1.jpg")
        #Compro de comprobante
        ImporteCompro=str(self.importe.get(),)
        p.text("El importe es $"+ImporteCompro+"\n")
        EntradaCompro = str(self.descripcion.get(),)
        p.text('El auto entro: '+EntradaCompro+'\n')
        SalioCompro = str(self.copia.get(),)
        p.text('El auto salio: '+SalioCompro+'\n')
        TiempoCompro = str(self.ffeecha.get(),)
        p.text('El auto permanecio: '+TiempoCompro+'\n')
        folioactual=str(self.folio.get(), )
        p.text('El folio del boleto es: '+folioactual+'\n')
        p.text('Le atendio: ')
        p.cut()
    def GuardarCobro(self):
        salida = str(self.precio.get(), )#deveria ser salida en lugar de precio pero asi estaba el base

        if len(salida)>5:
            self.label15.configure(text=("con salida, INMODIFICABLE"))
            mb.showinfo("Información", "Ya Tiene Salida")
            self.descripcion.set('')
            self.precio.set('')
            self.copia.set("")
            self.importe.set("")
            self.ffeecha.set("")
            self.folio.set("")
            self.label7.configure(text=(""))
            self.label8.configure(text =(""))
            self.label9.configure(text =(""))
            self.label11.configure(text=(""))
            self.label12.configure(text=(""))
            self.label15.configure(text=(""))
            self.entryfolio.focus()
        else:
            #self.Comprobante()
            self.label15.configure(text=(salida, "SI se debe modificar"))
            importe1 =str(self.importe.get(),)
            mb.showinfo("impte1", importe1)
            folio1= str(self.folio.get(),)
            valorhoy = str(self.copia.get(),)
            fechaActual1 = datetime.strptime(valorhoy, '%Y-%m-%d %H:%M:%S' )
            fechaActual= datetime.strftime(fechaActual1,'%Y-%m-%d %H:%M:%S' )
            ffeecha1= str(self.ffeecha.get(),)
            valor=str(self.descripcion.get(),)
            fechaOrigen = datetime.strptime(valor, '%Y-%m-%d %H:%M:%S')
            promoTipo = str(self.PrTi.get(),)
            vobo = "lmf"#este
            datos=(vobo, importe1, ffeecha1, fechaOrigen, fechaActual, promoTipo, folio1)
            self.operacion1.guardacobro(datos)
            self.descripcion.set('')
            self.precio.set('')
            self.copia.set("")
            self.label7.configure(text=(""))
            self.label8.configure(text =(""))
            self.label9.configure(text =(""))
            self.label11.configure(text=(""))
            self.label12.configure(text=(""))
            self.label15.configure(text=(""))
            self.importe.set("")
            self.ffeecha.set("")
            self.folio.set("")
            self.PrTi.set("")
            #self.elcambioes.set("")
            #self.elimportees.set("")
            #self.cuantopagasen.set("")
            self.entryfolio.focus()#se posiciona en leer qr
    def CalculaPromocion(self):
        TipoPromocion = str(self.promo.get(), )#se recibe el codigo
        TipoProIni=TipoPromocion[:8]
        if TipoProIni==("AM ADMIN"):
           NumP=TipoPromocion[10:]
           self.importe.set(0)
           self.label9.configure(text =(0, "cobro"))
           self.PrTi.set("ADMIN")
#           mb.showinfo("ADMIN",NumP)
           self.promo.set("")
###########starbucks
        if TipoProIni==("ST STARB"):
           NumP=TipoPromocion[12:]
           fecha = datetime.today()
           fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
           fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
           date_time_str=str(self.descripcion.get())
           date_time_obj= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
           date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
           date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
           ffeecha = fechaActual - date_time_mod2            #self.label11.configure(text=(ffeecha.days, "dias"))
           segundos_vividos = ffeecha.seconds
           horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
           minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
           if minutos_dentro >=0 and minutos_dentro<=15:
                importe = 0
           if minutos_dentro >15 and minutos_dentro < 60:
                importe = 20
           if horas_dentro == 1 and minutos_dentro <=30:
                importe = 20
           if horas_dentro == 1 and minutos_dentro <= 45 and minutos_dentro > 30:
                importe = 27.5
           if horas_dentro == 1 and minutos_dentro < 60 and minutos_dentro > 45:
                importe = 35
           if horas_dentro == 2 and minutos_dentro <=15:
                importe = 42.5
           if horas_dentro == 2 and minutos_dentro >15 and minutos_dentro <= 30:
                importe = 50
           if horas_dentro == 2 and minutos_dentro >30 and minutos_dentro <= 45:
                importe = 57.5
           if horas_dentro == 2 and minutos_dentro >45 and minutos_dentro < 60:
                importe = 65
           if horas_dentro == 3 and minutos_dentro <=15:
                importe = 72.5
           if horas_dentro == 3 and minutos_dentro >15 and minutos_dentro <= 30:
                importe = 80
           if horas_dentro == 3 and minutos_dentro >30 and minutos_dentro <= 45:
                importe = 87.5
           if horas_dentro == 3 and minutos_dentro >45 and minutos_dentro < 60:
                importe = 95
           if horas_dentro >= 4:
                importe = ((ffeecha.days)*720 + (horas_dentro * 30)+(minutos)*1)
           self.importe.set(importe)
           self.label9.configure(text =(importe, "cobro"))
           self.PrTi.set("StB")
           #mb.showinfo("STARBUCKS",NumP)
           self.promo.set("")
########## Promocion Sonora
        if TipoProIni==("SG SONOR"):
           NumP=TipoPromocion[15:]
           fecha = datetime.today()
           fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
           fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
           date_time_str=str(self.descripcion.get())
           date_time_obj= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
           date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
           date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
           ffeecha = fechaActual - date_time_mod2
           segundos_vividos = ffeecha.seconds
           horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
           minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
           if minutos_dentro < 60:
               importe = 50
           if horas_dentro >= 1 and horas_dentro <= 3 :
                importe = 50
           if horas_dentro == 3 and minutos_dentro <=15:
                importe = 50
           if horas_dentro == 3 and minutos_dentro >= 16:
                importe = 70
           if horas_dentro >= 4 and horas_dentro < 8:
                importe = 70
           if horas_dentro == 8 and minutos_dentro <=15:
                importe = 77
           if horas_dentro == 8 and minutos_dentro >=16:
                importe = 85
           if horas_dentro == 9 and minutos_dentro <=15:
                importe = 100
           if horas_dentro == 9 and minutos_dentro >=16:
                importe = 115              
           if horas_dentro >= 10:
                importe = ((ffeecha.days)*720 + (horas_dentro * 30)+(minutos_dentro)*1)
           self.importe.set(importe)
           self.label9.configure(text =(importe, "cobro"))
           self.PrTi.set("SNR")
          # mb.showinfo("SONORA",NumP)
           self.promo.set("")
#############promocion at pote
        if TipoProIni==("AT APOTE"):
           NumP=TipoPromocion[10:]
           self.importe.set(70)
           self.label9.configure(text =(70, "cobro"))
           self.PrTi.set("APOTEK")
#           mb.showinfo("ADMIN",NumP)
           self.promo.set("")
############ promocion crepas and wafles
        if TipoProIni==("CW CREPE"):
           NumP=TipoPromocion[18:]
           fecha = datetime.today()
           fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
           fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
           date_time_str=str(self.descripcion.get())
           date_time_obj= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
           date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
           date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
           ffeecha = fechaActual - date_time_mod2
           segundos_vividos = ffeecha.seconds
           horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
           minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
           if minutos_dentro >=0 and minutos_dentro<60:
                importe = 40
           if horas_dentro == 1 and minutos_dentro <= 45:
                importe = 40
           if horas_dentro == 1 and minutos_dentro >45 and minutos_dentro  < 60:
                importe = 45
           if horas_dentro == 2 and minutos_dentro >= 1:
                importe = 45
           if horas_dentro == 2 and minutos_dentro >15 and minutos_dentro  < 60:
                importe = 50
           if horas_dentro == 3 and minutos_dentro <=15:
                importe = 57.5
           if horas_dentro == 3 and minutos_dentro >15 and minutos_dentro <= 30:
                importe = 57.5
           if horas_dentro == 3 and minutos_dentro >30 and minutos_dentro <= 45:
                importe = 65
           if horas_dentro == 3 and minutos_dentro >45 and minutos_dentro < 60:
                importe = 65
           if horas_dentro >= 4:
                importe = ((ffeecha.days)*720 + (horas_dentro * 30)+(minutos)*1)
           self.importe.set(importe)
           self.label9.configure(text =(importe, "cobro"))
           self.PrTi.set("C&W")
          # mb.showinfo("CREPES&WAFLES",NumP)
           self.promo.set("")
###################### Fin de Pagina2 Inicio Pagina3 ###############################
    def listado_completo(self):
        self.pagina3 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina3, text="Módulo de Corte")
        self.labelframe1=ttk.LabelFrame(self.pagina3, text="Autos")
        self.labelframe1.grid(column=0, row=0, padx=1, pady=1)
        self.labelframe2=ttk.LabelFrame(self.pagina3, text="Generar Corte")
        self.labelframe2.grid(column=1, row=0, padx=0, pady=0)
        self.labelframe3=ttk.LabelFrame(self.pagina3, text="Consulta Cortes Anteriores")
        self.labelframe3.grid(column=0, row=1, padx=0, pady=0)

        self.labelframe4=ttk.LabelFrame(self.pagina3, text="Cuadro Comparativo")
        self.labelframe4.grid(column=1, row=1, padx=0, pady=0)
        self.lblSal=ttk.Label(self.labelframe4, text="Salida de Autos")
        self.lblSal.grid(column=3, row=1, padx=1, pady=1)
        self.lblS=ttk.Label(self.labelframe4, text="Entrada de Autos")
        self.lblS.grid(column=3, row=2, padx=1, pady=1)
        self.lblAnterior=ttk.Label(self.labelframe4, text="Autos del Turno anterior")
        self.lblAnterior.grid(column=3, row=3, padx=1, pady=1)
        self.lblEnEstac=ttk.Label(self.labelframe4, text="Autos en Estacionamiento")
        self.lblEnEstac.grid(column=3, row=4, padx=1, pady=1)
        self.lblC=ttk.Label(self.labelframe4, text="Boletos Cobrados:")
        self.lblC.grid(column=0, row=1, padx=1, pady=1)
        self.lblE=ttk.Label(self.labelframe4, text="Boletos Expedidos:")
        self.lblE.grid(column=0, row=2, padx=1, pady=1)
        self.lblA=ttk.Label(self.labelframe4, text="Boletos Turno Anterior:")
        self.lblA.grid(column=0, row=3, padx=1, pady=1)
        self.lblT=ttk.Label(self.labelframe4, text="Boletos Por Cobrar:")
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
        self.boton6=tk.Button(self.labelframe4, text="Consulta Bol-Sensor", command=self.Puertoycontar, width=15, height=3, anchor="center")
        self.boton6.grid(column=1, row=0, padx=1, pady=1)

        self.FrmCancelado=ttk.LabelFrame(self.pagina3, text="Boleto Cancelado")
        self.FrmCancelado.grid(column=0, row=2, padx=0, pady=0)
        self.labelCorte=ttk.Label(self.labelframe2, text="El Total del CORTE es:")
        self.labelCorte.grid(column=0, row=1, padx=0, pady=0)
        self.label2=ttk.Label(self.labelframe2, text="La Fecha de CORTE es:")
        self.label2.grid(column=0, row=2, padx=1, pady=1)
        self.label3=ttk.Label(self.labelframe2, text="El CORTE Inicia ")
        self.label3.grid(column=0, row=3, padx=1, pady=1)
        self.label4=ttk.Label(self.labelframe2, text="El Numero de CORTE es:")
        self.label4.grid(column=0, row=4, padx=1, pady=1)
        self.label5=ttk.Label(self.labelframe3, text="CORTE a Consultar :")
        self.label5.grid(column=0, row=1, padx=1, pady=1)
        self.label6=ttk.Label(self.labelframe3, text="Fecha y hora del CORTE")
        self.label6.grid(column=0, row=2, padx=1, pady=1)

        self.lblCancelado=ttk.Label(self.FrmCancelado, text="COLOCAR FOLIO")
        self.lblCancelado.grid(column=0, row=1, padx=4, pady=4)
        self.FolioCancelado=tk.StringVar()
        self.entryFOLIOCancelado=tk.Entry(self.FrmCancelado, width=15, textvariable=self.FolioCancelado)
        self.entryFOLIOCancelado.grid(column=1, row=1)
        self.boton7=tk.Button(self.FrmCancelado, text="B./SIN cobro", command=self.BoletoDentro2, width=15, height=3, anchor="center")
        self.boton7.grid(column=0, row=0, padx=1, pady=1)
        #self.boton8=tk.Button(self.FrmCancelado, text="desglose", command=self.desglose_cobrados, width=15, height=3, anchor="center")
        #self.boton8.grid(column=1, row=3, padx=1, pady=1)

        self.btnCancelado=tk.Button(self.FrmCancelado, text="Cancelar Boleto ", command=self.BoletoCancelado, width=10, height=2, anchor="center")
        self.btnCancelado.grid(column=0, row=2)
        self.scrolledtxt2=st.ScrolledText(self.FrmCancelado, width=28, height=7)
        self.scrolledtxt2.grid(column=1,row=0, padx=1, pady=1)
        self.ImporteCorte=tk.StringVar()
        self.entryImporteCorte=tk.Entry(self.labelframe2, width=20, textvariable=self.ImporteCorte, state= "readonly", borderwidth=5)
        self.entryImporteCorte.grid(column=1, row=1)
        self.FechaCorte=tk.StringVar()
        self.entryFechaCorte=tk.Entry(self.labelframe2, width=20, textvariable=self.FechaCorte, state= "readonly")
        self.entryFechaCorte.grid(column=1, row=2)
        self.FechUCORTE=tk.StringVar()
        self.entryFechUCORTE=tk.Entry(self.labelframe2, width=20, textvariable=self.FechUCORTE, state= "readonly")
        self.entryFechUCORTE.grid(column=1, row=3)
        self.CortesAnteri=tk.StringVar()
        self.CortesAnteri=tk.Entry(self.labelframe3, width=20, textvariable=self.CortesAnteri)
        self.CortesAnteri.grid(column=1, row=1)
        self.boton1=ttk.Button(self.labelframe1, text="Todas las Entradas", command=self.listar)
        self.boton1.grid(column=0, row=0, padx=4, pady=4)
        self.boton2=ttk.Button(self.labelframe1, text="Entradas sin corte", command=self.listar1)
        self.boton2.grid(column=0, row=2, padx=4, pady=4)
        self.boton3=tk.Button(self.labelframe2, text="Calcular Corte", command=self.Calcular_Corte, width=15, height=1)
        self.boton3.grid(column=2, row=0, padx=4, pady=4)
        self.boton4=tk.Button(self.labelframe2, text="Guardar Corte", command=self.Guardar_Corte, width=15, height=1, anchor="center", background="blue")
        self.boton4.grid(column=2, row=4, padx=4, pady=4)
        self.boton5=tk.Button(self.labelframe3, text="Imprimir salidas  Corte", command=self.desglose_cobrados, width=15, height=3, anchor="center")
        self.boton5.grid(column=1, row=2, padx=4, pady=4)
        self.scrolledtext1=st.ScrolledText(self.labelframe1, width=30, height=4)
        self.scrolledtext1.grid(column=0,row=1, padx=1, pady=1)
    def BoletoDentro2(self):
        respuesta=self.operacion1.Autos_dentro()
        self.scrolledtxt2.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtxt2.insert(tk.END, "Folio num: "+str(fila[0])+"\nEntro: "+str(fila[1])+"\nPlacas: "+str(fila[2])+"\n\n")
    def desglose_cobrados(self):
        Numcorte=str(self.CortesAnteri.get(), )
        Numcorte=int(Numcorte)
        Numcorte=str(Numcorte)
        io.output(out1,0)
        time.sleep(1)
        io.output(out1,1)
        respuesta=self.operacion1.desglose_cobrados(Numcorte)
        self.scrolledtxt2.delete("1.0", tk.END)
        p = Usb(0x04b8, 0x0202, 0)
        #p = Usb(0x04b8, 0x0e28, 0)#esta es la impresora con sus valores que se obtienen con lsusb
        p.text("El Numero de corte es "+Numcorte+'\n')
        for fila in respuesta:
            self.scrolledtxt2.insert(tk.END, "cobro: "+str(fila[0])+"\nImporte: $"+str(fila[1])+"\nCuantos: "+str(fila[2])+"\n\n")
            p.text('Tipo de cobro :')
            p.text(str(fila[0]))
            p.text('\n')
            p.text('Importe :')
            p.text(str(fila[1]))
            p.text('\n')
            p.text('Cuantos ')
            p.text(str(fila[2]))
            p.text('\n')
        else:
            p.cut()
    def BoletoCancelado(self):
       datos=str(self.FolioCancelado.get(), )
       datos=int(datos)
       datos=str(datos)
       self.folio.set(datos)
       datos=(self.folio.get(), )
       respuesta=self.operacion1.consulta(datos)
       if len(respuesta)>0:
           self.descripcion.set(respuesta[0][0])
           self.precio.set(respuesta[0][1])
           self.CalculaPermanencia()#nos vamos a la funcion de calcular permanencia
           fecha = datetime.today()
           fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
           fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
           date_time_str=str(self.descripcion.get())
           date_time_obj= datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
           date_time_mod = datetime.strftime(date_time_obj, '%Y/%m/%d/%H/%M/%S')
           date_time_mod2 = datetime.strptime(date_time_mod, '%Y/%m/%d/%H/%M/%S')
           ffeecha = fechaActual - date_time_mod2
            #self.label11.configure(text=(ffeecha.days, "dias"))
           segundos_vividos = ffeecha.seconds
           horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
        #    self.label12.configure(text=(horas_dentro, "horas"))
           minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)
           if horas_dentro <= 24:
                importe = 0
           if horas_dentro > 24 or ffeecha.days >= 1:
                importe =0
           self.importe.set(importe)
           self.label9.configure(text =(importe, "cobro"))
           self.PrTi.set("CDO")
           self.promo.set("")
           p = Usb(0x04b8, 0x0202, 0)
           #p = Usb(0x04b8, 0x0e28, 0)#esta es la impresora con sus valores que se obtienen con lsusb
           p.text('Boleto Cancelado\n')
           FoliodelCancelado = str(self.FolioCancelado.get(),)
           p.text('Folio boleto cancelado: '+FoliodelCancelado+'\n')
           fecha = datetime.today()
           fechaNota = datetime.today()
           fechaNota= fechaNota.strftime("%b-%d-%A-%Y %H:%M:%S")
           horaNota = str(fechaNota)
           p.set(align="left")
           p.set('Big line\n', font='b')
           p.text('Fecha: '+horaNota+'\n')
           EntradaCompro = str(self.descripcion.get(),)
           p.text('El auto entro: '+EntradaCompro+'\n')
           SalioCompro = str(self.copia.get(),)
           p.text('El auto salio: '+SalioCompro+'\n')
           self.GuardarCobro()
           self.FolioCancelado.set("")
           p.cut()

       else:
           self.descripcion.set('')
           self.precio.set('')
           mb.showinfo("Información", "No No")
    def listar(self):
        respuesta=self.operacion1.recuperar_todos()
        self.scrolledtext1.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtext1.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])+"\nSalio: "+str(fila[2])+"\n\n")
    def listar1(self):
        respuesta=self.operacion1.recuperar_sincobro()
        self.scrolledtext1.delete("1.0", tk.END)
        #respuesta=str(respuesta)
        for fila in respuesta:
            self.scrolledtext1.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])+"\nSalio: "+str(fila[2])+"\nImporte: "+str(fila[3])+"\n\n")
            p = Usb(0x04b8, 0x0202, 0)
            #p = Usb(0x04b8, 0x0e28, 0)#esta es la impresora con sus valores que se obtienen con lsusb
            p.text('Entrada Num :')
            p.text(str(fila[0]))
            p.text('\n')
            p.text('Entro :')
            p.text(str(fila[1]))
            p.text('\n')
            p.text('Salio :')
            p.text(str(fila[2]))
            p.text('\n')
            p.text('importe :')
            p.text(str(fila[3]))
            p.text('\n')
        else:
            p.cut()
    def Calcular_Corte(self):
        respuesta=self.operacion1.corte()
        self.ImporteCorte.set(respuesta)
        ##obtengamo la fechaFin del ultimo corte
        ultiCort1=str(self.operacion1.UltimoCorte())
        #mb.showinfo("msj uno",ultiCort1)
        startLoc = 20
        endLoc = 43
        ultiCort1=(ultiCort1)[startLoc: endLoc]
        ultiCort1 = ultiCort1.strip('),')
        if len(ultiCort1) <= 17:
                            # mb.showinfo("msj dos",ultiCort1)
                             ultiCort1= datetime.strptime(ultiCort1, '%Y, %m, %d, %H, %M')
        else:
            ultiCort1= datetime.strptime(ultiCort1, '%Y, %m, %d, %H, %M, %S')        
            #mb.showinfo("msj tres",ultiCort1)
        ultiCort1 = datetime.strftime(ultiCort1, '%Y/%m/%d/%H/%M/%S')
        ultiCort1 = datetime.strptime(ultiCort1, '%Y/%m/%d/%H/%M/%S')
        self.FechUCORTE.set(ultiCort1)# donde el label no esta bloqueada
        ###ahora obtenemos la fecha del corte ha realizar
        fecha = datetime.today()
        fecha1= fecha.strftime("%Y-%m-%d %H:%M:%S")
        fechaActual= datetime.strptime(fecha1, '%Y-%m-%d %H:%M:%S')
        self.FechaCorte.set(fechaActual)#donde el label esta bloqueado
    def Guardar_Corte(self):
        self.Puertoycontar()
        ##la fecha final de este corte que es la actual
        fechaDECorte = str(self.FechaCorte.get(),)
        fechaDECorte = datetime.strptime(fechaDECorte, '%Y-%m-%d %H:%M:%S' )
        ######la fecha del inicial obtiene de labase de datos
        fechaInicio1 = str(self.FechUCORTE.get(),)
        fechaInicio2 = datetime.strptime(fechaInicio1, '%Y-%m-%d %H:%M:%S')
        fechaInicio = fechaInicio2
        ######el importe se obtiene de la suma
        ImpCorte2 =str(self.ImporteCorte.get(),)
        #este quita lo que no sea numero esto de abajo
        #self.label2.configure(text ="".join([x for x in ImpCorte2 if x.isdigit()]) )
        Im38 = "".join([x for x in ImpCorte2 if x.isdigit()])
        #mete los valores a la base de datos
        AEE = 0#str(self.AutosEnEstacionamiento.get(),)
        maxnumid=str(self.operacion1.MaxfolioEntrada())
        maxnumid = "".join([x for x in maxnumid if x.isdigit()])#con esto solo obtenemos los numeros
        maxnumid=int(maxnumid)
        maxnumid=str(maxnumid)
        pasa = str(self.BDentro.get(),)
        NumBolQued = pasa.strip('(),')
        datos=(Im38, fechaInicio, fechaDECorte,AEE,maxnumid,NumBolQued)
        self.operacion1.GuarCorte(datos)
        maxnum1=str(self.operacion1.Maxfolio_Cortes())
        maxnum = "".join([x for x in maxnum1 if x.isdigit()])#con esto solo obtenemos los numeros
        maxnum=int(maxnum)
        maxnum=str(maxnum)
        vobo = "cor"#este es para que la instruccion no marque error
        ActEntradas = (maxnum, vobo )
        self.label4.configure(text=("Numero de corte",maxnum))
        p = Usb(0x04b8, 0x0202, 0)
        #p = Usb(0x04b8, 0x0e28, 0)#esta es la impresora con sus valores que se obtienen con lsusb
        p.text("CORTE Num "+maxnum+"\n")
        p.text('IMPORTE: $ '+Im38+'\n')
        ultiCort1=str(self.FechUCORTE.get(),)
        ultiCort4= datetime.strptime(ultiCort1, '%Y-%m-%d %H:%M:%S')
        ultiCort5 = datetime.strftime(ultiCort4, '%A %d %m %Y a las %H:%M:%S')
        p.text('Inicio:')
        p.text(ultiCort5)
        p.text('\n')
        valorFEsteCorte = str(self.FechaCorte.get(),)
        fechaDECorte = datetime.strptime(valorFEsteCorte, '%Y-%m-%d %H:%M:%S' )
        fechaDECorte = datetime.strftime(fechaDECorte, '%A %d %m %Y a las %H:%M:%S' )
        p.text('Final :')
        p.text(str(fechaDECorte))
        p.text('\n')
        BolCobrImpresion=str(self.BoletosCobrados.get(),)
        p.text("Boletos Cobrados: "+BolCobrImpresion+"\n")
        #SalidasSen =  int(self.SalidaAutos.get(),)
        #SalidasSen =  str(SalidasSen)
        #p.text("Salidas Sensor: "+SalidasSen+"\n")
        BEDespuesCorteImpre = str(self.BEDespuesCorte.get(),)
        p.text('Boletos Expedidos: '+BEDespuesCorteImpre+'\n')
        #EntradasSen = int(self.SensorEntrada.get(),)
        #EntradasSen =  str(EntradasSen)
        #p.text('Entradas Sensor: '+EntradasSen+'\n')
        BAnterioresImpr=str(self.BAnteriores.get(),)#######
        p.text("Boletos Turno Anterior: "+BAnterioresImpr+"\n")
        #AutosAnteriores = int(self.Autos_Anteriores.get(),)
        #AutosAnteriores = str(AutosAnteriores)
        #p.text('Sensor Turno Anterior: '+AutosAnteriores+'\n')
        BDentroImp = str(self.BDentro.get(),)
        p.text('Boletos por Cobrar: '+BDentroImp+'\n')
        AutosEnEstacImpre = str(self.AutosEnEstacionamiento.get(),)
        #p.text('Autos en estacionamiento por sensor: '+AutosEnEstacImpre+'\n')
        p.text('Le atendio: PASE S.A. de C.V.')
        #Bandera = o
        self.ImporteCorte.set("")
        p.cut()
        self.operacion1.ActualizarEntradasConcorte(ActEntradas)
        vobo='ant'
        self.operacion1.NocobradosAnt(vobo)
        #ser = serial.Serial('/dev/ttyAMA0', 9600)
        #Enviamos el caracter por serial, codificado en Unicode
        #entrada='c'
        #ser.write(str(entrada).encode())
    def Puertoycontar(self):
        #ser = serial.Serial('/dev/ttyAMA0', 9600)
        #Enviamos el caracter por serial, codificado en Unicode
        #entrada='e'
        #ser.write(str(entrada).encode())
        #Leemos lo que hay en el puerto y quitamos lo que no queremos
        #sArduino = str(ser.readline())
        #sArduino = "" .join([x for x in sArduino if x.isdigit()])#esto es para solo poner numeros
        #CuantosEntradas=str(self.operacion1.EntradasSensor())
        #sArduino = 1
        #CuantosEntradas = CuantosEntradas.strip('(),')
        #self.SensorEntrada.set(CuantosEntradas)
        #entrada='a'
        #ser.write(str(entrada).encode())
        #Leemos lo que hay en el puerto y quitamos lo que no queremos
        #sArduino = str(ser.readline())
        #sArduino = "" .join([x for x in sArduino if x.isdigit()])#esto es para solo poner num
        #CuantosSalidas=str(self.operacion1.SalidasSensor())
        #sArduino =1
        #CuantosSalidas = CuantosSalidas.strip('(),')
        #self.SalidaAutos.set(CuantosSalidas)
        #EntradasSen = int(self.SensorEntrada.get(),)
        #SalidasSen =  int(self.SalidaAutos.get(),)
        CuantosBoletosCobro=str(self.operacion1.CuantosBoletosCobro())
        CuantosBoletosCobro = CuantosBoletosCobro.strip('(),')
        self.BoletosCobrados.set(CuantosBoletosCobro)
        BEDCorte=str(self.operacion1.BEDCorte())
        BEDCorte = BEDCorte.strip('(),')
        self.BEDespuesCorte.set(BEDCorte)
        BAnteriores=str(self.operacion1.BAnteriores())
        BAnteriores = BAnteriores.strip('(),')
        self.BAnteriores.set(BAnteriores)
        MaxFolioCorte=str(self.operacion1.Maxfolio_Cortes())
        MaxFolioCorte=MaxFolioCorte.strip('(),')
        QuedadosBol=str(self.operacion1.Quedados_Sensor(MaxFolioCorte))
        QuedadosBol=QuedadosBol.strip('(),')
        self.BAnteriores.set(QuedadosBol)
        maxNumidIni=str(self.operacion1.MaxnumId())
        maxNumidIni = "".join([x for x in maxNumidIni if x.isdigit()])#con esto solo obtenemos los numeros
        maxNumidIni=int(maxNumidIni)
        maxFolioEntradas= str(self.operacion1.MaxfolioEntrada())
        maxFolioEntradas = "".join([x for x in maxFolioEntradas if x.isdigit()])#con esto solo obtenemos los numero
        maxFolioEntradas=int(maxFolioEntradas)
        BEDCorte=maxFolioEntradas-maxNumidIni
        BEDCorte=str(BEDCorte)
        self.BEDespuesCorte.set(BEDCorte)
        CuantosAutosdentro=str(self.operacion1.CuantosAutosdentro())
        MaxFolioCorte=str(self.operacion1.Maxfolio_Cortes())
        MaxFolioCorte=MaxFolioCorte.strip('(),')
        dentroCorte=str(self.operacion1.Quedados_Sensor(MaxFolioCorte))
        CuantosAutosdentro = CuantosAutosdentro.strip('(),')
        dentroCorte = dentroCorte.strip('(),')
        self.BDentro.set(CuantosAutosdentro)
        self.Autos_Anteriores.set(dentroCorte)
        #AutosAnteriores = int(self.Autos_Anteriores.get(),)
        #Cuantos_hay_dentro = ((AutosAnteriores + EntradasSen) - SalidasSen)
        #self.AutosEnEstacionamiento.set(Cuantos_hay_entro)

aplicacion1=FormularioOperacion()


