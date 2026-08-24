from datetime import datetime, time, timedelta
formato = "%H:%M:%S"
from escpos.printer import *
import qrcode
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb

import operacion_entrada as operacion
import time
import traceback

# libreria de I/O (entradas / salidas)
import RPi.GPIO as io

# Pines
pin_sensor_autos = 4
pin_boton = 18
pin_sensor_boletos = 23

#Entrada
loop = pin_sensor_autos                      #gpio16,pin36,entrada loop                    
boton = pin_boton                     #gpio12,pin32,entrada boton
SenBoleto = pin_sensor_boletos                 #gpio20,pin38,sensor boleto

#salidas
barrera = 13                  #gpio13,pin33,Salida barrera
out1 = 19                     #gpio19,pin35,Salida indicador loop
out2 = 6                     #gpio6,pin31,Salida indicador boton
out3 = 26                     #gpio26,pin37,Salida indicador barrera
io.setmode(io.BCM)              # modo in/out pin del micro
io.setwarnings(False)           # no señala advertencias de pin ya usados
io.setup(loop,io.IN)             # configura en el micro las entradas
# El programa considera nivel alto como boton presionado. El pull-down evita
# que el GPIO quede flotando durante el arranque de la Raspberry.
io.setup(boton,io.IN, pull_up_down=io.PUD_DOWN)
# io.setup(SenBoleto,io.IN)             # configura en el micro las entradas
# La barrera de Entrada es activa en bajo. Se inicializa en alto desde el
# mismo setup para evitar un pulso de apertura antes de ejecutar io.output().
io.setup(barrera,io.OUT, initial=io.HIGH)
io.setup(out1,io.OUT)           # configura en el micro las salidas
io.setup(out2,io.OUT)
io.setup(out3,io.OUT)  
line=''
io.output(barrera,1)
io.output(out1,0)
io.output(out2,0)
io.output(out3,0)
BanLoop =0
BanBoton=0
BotonArmado=0 #No se acepta hasta detectar primero el boton suelto
# BanSenBoleto=0
BanImpresion=0 #No ha impreso
# Configuracion de las entradas y las salidas del micro
# -----------------------------------------------------
class FormularioOperacion:
    def __init__(self):
        #creamos un objeto que esta en el archivo operacion dentro la clase Operacion
        self.operacion1=operacion.Operacion()
        self.ventana1=tk.Tk()
        self.ventana1.title("BOLETERA DE ENTRADA")
        self.ventana1.configure(bg = 'blue')
        self.cuaderno1 = ttk.Notebook(self.ventana1)
        self.cuaderno1.config(cursor="")
        self._rfid_after_id = None
        self._rfid_en_proceso = False

        self.ExpedirRfid()
        # Leer primero los GPIO reales. Si check_inputs se ejecuta antes,
        # BanBoton conserva temporalmente el cero inicial y arma el boton sin
        # haber comprobado que fisicamente estaba suelto.
        self.IntBoton()
        self.Intloop()
        self.check_inputs()

        self.cuaderno1.grid(column=0, row=0, padx=5, pady=5)
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
       
 
        self.boton1=tk.Button(self.labelframe1, text="Generar Entrada", command=self.agregarRegistroRFID, width=13, height=3, anchor="center", background="blue")
        self.boton1.grid(column=1, row=4, padx=4, pady=4)

        ###Pensionados
        self.labelframe3=ttk.LabelFrame(self.pagina1, text="PENSIONADOS")
        self.labelframe3.grid(column=1, row=2, padx=0, pady=0)        
        self.labelTarjeta=ttk.Label(self.labelframe3, text="Tarjeta:")
        self.labelTarjeta.grid(column=0, row=2, padx=0, pady=0)
        self.NumTarjeta4=tk.StringVar()
        self.entryNumTarjeta4=tk.Entry(self.labelframe3, width=20, textvariable=self.NumTarjeta4)
        # La mayoria de los lectores RFID funcionan como teclado y terminan
        # la lectura con Enter. Tambien se deja un temporizador corto para
        # lectores configurados sin Enter.
        self.entryNumTarjeta4.bind('<Return>', self._rfid_enter)
        self.entryNumTarjeta4.bind('<KP_Enter>', self._rfid_enter)
        self.entryNumTarjeta4.bind('<KeyRelease>', self._rfid_tecla)
        self.entryNumTarjeta4.grid(column=1, row=2, padx=4, pady=4)
        self.entryNumTarjeta4.focus()
        self.labelMensaje=ttk.Label(
            self.labelframe3,
            text="Acerque tarjeta con el vehiculo presente"
        )
        self.labelMensaje.grid(column=2, row=2, padx=0, pady=0)

    def _cancelar_rfid_pendiente(self):
        if self._rfid_after_id is not None:
            try:
                self.ventana1.after_cancel(self._rfid_after_id)
            except tk.TclError:
                pass
            self._rfid_after_id = None

    def _rfid_tecla(self, event=None):
        """Procesa lectores que no envian Enter al terminar el codigo."""
        if event is not None and event.keysym in ('Return', 'KP_Enter'):
            return
        self._cancelar_rfid_pendiente()
        if self.NumTarjeta4.get().strip():
            self._rfid_after_id = self.ventana1.after(350, self.Pensionados)

    def _rfid_enter(self, event=None):
        self._cancelar_rfid_pendiente()
        self.Pensionados()
        return 'break'

    def Intloop(self): #Detecta presencia de automovil
        global BanLoop
        if io.input(loop):
            print('hay auto') 
            io.output(out1,0)#con un "1" se apaga el led
            BanLoop = 1
        else:
            io.output(out1,1)                              
            BanLoop = 0

    def IntBoton(self): #Detecta presencia de automovil
        global BanBoton
        if io.input(boton):
            print('Presiono boton')
            io.output(out2,0)
            BanBoton = 1
        else:
            io.output(out2,1)
            BanBoton = 0

    io.add_event_detect(loop, io.BOTH, callback = Intloop)
    io.add_event_detect(boton, io.BOTH, callback = IntBoton)


    def check_inputs(self):
        global BanBoton, BanLoop, BanImpresion, BotonArmado
    
        if BanLoop == 1:
            self.loopDet.config(text = "Hay auto", font=('Arial', 15), background = 'green')
        else:
            self.loopDet.config(text = ".", font=('Arial', 15), background = '#CCC') #'#CCC'
            self.SenBol2.config(text = ".", font=('Arial', 15), background='#CCC')
            self.SenBol.config(text = ".", font=('Arial', 15), background='#CCC')
            BanImpresion = 1

        if BanBoton == 1:
            self.BotDet.config(text = "presiono btn", font=('Arial', 15), background='#CCC') #'#CCC'
            # Protección de arranque: un nivel alto presente al iniciar no
            # cuenta como pulsacion. Primero debe detectarse el boton suelto.
            if BotonArmado == 0:
                self.BotDet.config(
                    text="SUELTE BOTON",
                    font=('Arial', 15),
                    background='orange'
                )
            # Nunca abrir ni imprimir si no se detecta un vehiculo.
            elif BanLoop != 1:
                print('Boton ignorado: no hay auto')
                self.BotDet.config(
                    text="SIN AUTO - BOTON IGNORADO",
                    font=('Arial', 15),
                    background='orange'
                )
                BotonArmado = 0
            elif BanImpresion == 1:
                # Se desarma antes de abrir para que mantener presionado el
                # boton no genere otra entrada.
                BotonArmado = 0
                #self.SenBol.config(text = "AVANCE", font=('Arial', 15), background= "green") #'#CCC'
                print('mando abrir barrera')
                io.output(barrera,0)#con un "0" abre la barrera
                time.sleep (1)
                io.output(barrera,1)
                self.agregarRegistroRFID()                
                BanImpresion = 0
            else:   
                self.SenBol.config(text = "press btn sin impresion", font=('Arial', 15), background= "red") 

        else: 
            # El boton ya fue visto en reposo; la proxima transicion a alto
            # sera una pulsacion real.
            BotonArmado = 1
            self.BotDet.config(text = "solto btn", font=('Arial', 15), background='#CCC') #'#CCC'       
            self.SenBol.config(text = "", font=('Arial', 15), background="#CCC")
            #if BanBoton == 1 and BanLoop==1:
           

            #BanImpresion = 1

        now =datetime.now() 
        fecha1= now.strftime("%d-%b-%y")
        hora1= now.strftime("%H:%M:%S")    
        self.Reloj.config(text=fecha1)            
        self.mi_reloj.config(text=hora1)    
        self.ventana1.after(60, self.check_inputs)          # activa un timer de 50mSeg.

     
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
        print("MaxFolio 1 ", MaxFolio)
        MaxFolio = MaxFolio.strip("[(,)]")
        print("MaxFolio 2 ", MaxFolio)
        n1 = MaxFolio
        print("n1 ", n1)
#        n2 = "1"
#        masuno = int(n1)+int(n2)
        masuno=n1
        print("masuno 1 ", masuno)
        masuno = str(masuno)
        print("masuno 2 ", masuno)
        self.MaxId.set(masuno)
        
        # El TPV espera un folio cifrado corto. Antes se imprimia la fecha
        # completa mas el folio y el TPV lo confundia con una promocion.
        folio_cifrado = self.operacion1.cifrar_folio(folio=masuno)

        # Generar el QR compatible con descifrar_folio() del TPV.
        self.operacion1.generar_QR(folio_cifrado)


        imgqr=folio_cifrado
        horaentrada = str(fechaEntro)
        horaentrada=horaentrada[:16]
        #self.labelhr.configure(text=(horaentrada, "Entró"))
        fSTR=str(fechaEntro)
        print("fSTR ", fSTR)
        print("imgqr ",imgqr)
        #reducida2 =img2.resize((100, 75))
        #reducida2.save("reducida2.png")
        print("horaentrada",horaentrada)
        print("imgqr",imgqr)
        
        
        #p = Usb(0x04b8, 0x0202, 0)#0202 04b8:
        p = Usb(0x04b8, 0x0e28, 0)
        #p.set("center")
        #p.text("BOLETO DE ENTRADA\n")
        p.set("center")
        p.image("LOGO1.jpg")
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
        p.text("--------------------------------------\n")
        p.text("--------------------------------------\n")
        p.text("                                      \n")
        p.text("                                      \n")
        p.text("                                      \n")
        p.text("                                      \n")
        p.cut()
        p.close()
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$impresion fin$$$$$$$$$$$$$$$$               
        self.Placa.set('')

    @staticmethod
    def _limite_vigencia(fecha_vigencia, tolerancia):
        """Agrega los dias habiles de tolerancia usados por la TPV."""
        limite = fecha_vigencia
        dias = max(0, tolerancia)
        while dias > 0:
            limite += timedelta(days=1)
            if limite.weekday() < 5:
                dias -= 1
        return limite

    def _limpiar_lector_rfid(self):
        self.NumTarjeta4.set("")
        self.entryNumTarjeta4.focus_set()

    def Pensionados(self, event=None):
        """Valida la tarjeta, registra la entrada y abre una sola vez."""
        global BanLoop

        self._rfid_after_id = None
        if self._rfid_en_proceso:
            return False

        lectura = self.NumTarjeta4.get().strip()
        # Algunos lectores agregan espacios, tabulador o salto de linea.
        numtarjeta = ''.join(lectura.split())
        print("RFID recibido:", repr(lectura), "normalizado:", repr(numtarjeta))

        if not numtarjeta:
            return False
        if not numtarjeta.isdigit():
            self.labelMensaje.config(text="Tarjeta inválida: sólo debe contener números")
            print("RFID rechazado: contiene caracteres no numéricos")
            self._limpiar_lector_rfid()
            return False
        if BanLoop != 1:
            self.labelMensaje.config(text="Tarjeta leída, pero no se detecta vehículo")
            print("RFID leído correctamente, pero el sensor de auto está inactivo")
            self._limpiar_lector_rfid()
            return False

        self._rfid_en_proceso = True
        try:
            tarjeta = int(numtarjeta)
            id_cliente = self.operacion1.ValidarPen(tarjeta)
            if id_cliente is None:
                self.labelMensaje.config(text="Tarjeta no registrada: " + numtarjeta)
                print("RFID no existe en Pensionados:", tarjeta)
                return False

            respuesta = self.operacion1.ConsultaPensionado(id_cliente)
            if respuesta is None:
                self.labelMensaje.config(text="No hay datos del pensionado")
                return False

            fecha_vigencia, estatus, vigencia, tolerancia = respuesta
            try:
                tolerancia = int(tolerancia or 0)
            except (TypeError, ValueError):
                tolerancia = 0

            print(
                "Pensionado:", id_cliente,
                "estatus:", estatus,
                "vigencia:", vigencia,
                "fecha:", fecha_vigencia,
                "tolerancia:", tolerancia
            )

            if estatus == 'Adentro':
                self.labelMensaje.config(text="El pensionado ya está adentro")
                return False
            if vigencia != 'Activo' or fecha_vigencia is None:
                self.labelMensaje.config(text="Tarjeta sin vigencia activa")
                return False

            limite = self._limite_vigencia(fecha_vigencia, tolerancia)
            if datetime.today() > limite:
                self.operacion1.UpdPensionado(('Afuera', id_cliente))
                self.labelMensaje.config(text="Vigencia vencida")
                print("Vigencia vencida. Fecha límite:", limite)
                return False

            entrada = datetime.today()
            registrado = self.operacion1.RegistrarEntradaPensionado(
                id_cliente,
                tarjeta,
                entrada
            )
            if not registrado:
                self.labelMensaje.config(text="El pensionado ya está adentro")
                return False

            self.labelMensaje.config(text="Acceso autorizado - abre barrera")
            print("RFID autorizado:", tarjeta, "- abre barrera por 3 segundos")
            io.output(barrera,0)
            time.sleep(3)
            io.output(barrera,1)
            return True
        except Exception as error:
            self.labelMensaje.config(text="Error al validar RFID; revise la terminal")
            print("ERROR al procesar pensionado:", error)
            traceback.print_exc()
            return False
        finally:
            self._limpiar_lector_rfid()
            self._rfid_en_proceso = False
                




aplicacion1=FormularioOperacion()
