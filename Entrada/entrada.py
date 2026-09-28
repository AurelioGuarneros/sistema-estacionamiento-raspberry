from datetime import datetime, time, timedelta
import os
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
pin_sensor_autos = int(os.environ.get("ESTACIONAMIENTO_GPIO_SENSOR_AUTO", "21"))
pin_boton = int(os.environ.get("ESTACIONAMIENTO_GPIO_BOTON", "20"))
pin_sensor_boletos = int(os.environ.get("ESTACIONAMIENTO_GPIO_SENSOR_BOLETO", "16"))
sensor_boleto_activo_bajo = os.environ.get(
    "ESTACIONAMIENTO_SENSOR_BOLETO_ACTIVO_BAJO", "true"
).lower() in ("1", "true", "si", "yes")
tiempo_retiro_boleto = float(
    os.environ.get("ESTACIONAMIENTO_SENSOR_BOLETO_TIMEOUT", "30")
)
printer_vendor_id = int(os.environ.get("ESTACIONAMIENTO_PRINTER_VENDOR_ID", "04b8"), 16)
printer_product_id = int(os.environ.get("ESTACIONAMIENTO_PRINTER_PRODUCT_ID", "0e28"), 16)

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
io.setup(loop, io.IN, pull_up_down=io.PUD_UP)  # contacto seco: activo en bajo
# El botón conecta el GPIO a GND: LOW al presionar y HIGH al soltar.
io.setup(boton, io.IN, pull_up_down=io.PUD_UP)
# 0 V = boleto presente por defecto; nunca conecte 5 V al GPIO.
io.setup(SenBoleto, io.IN, pull_up_down=io.PUD_UP)
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
BanSenBoleto=0
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
        self._esperando_retiro = False
        self._sensor_vio_boleto = False
        self._inicio_espera_boleto = 0.0

        self.ExpedirRfid()
        # Leer primero los GPIO reales. Si check_inputs se ejecuta antes,
        # BanBoton conserva temporalmente el cero inicial y arma el boton sin
        # haber comprobado que fisicamente estaba suelto.
        self.IntBoton()
        self.Intloop()
        self.IntSenBoleto()
        self.check_inputs()

        self.ventana1.grid_rowconfigure(0, weight=1)
        self.ventana1.grid_columnconfigure(0, weight=1)
        self.cuaderno1.grid(column=0, row=0, sticky="nsew")
        self.ventana1.mainloop()
    ###########################Inicia Pagina1##########################
# Funcion de lectura de las entradas
# -----------------------------------
    def ExpedirRfid(self):
        """Construye la pantalla de Entrada sin alterar la lógica de seguridad."""
        self.ventana1.configure(bg="#f4f6f8")
        self.ventana1.attributes("-fullscreen", True)
        self.ventana1.bind("<Escape>", lambda _event: self.ventana1.attributes("-fullscreen", False))
        self.ventana1.bind("<F11>", lambda _event: self.ventana1.attributes(
            "-fullscreen", not self.ventana1.attributes("-fullscreen")
        ))

        self.pagina1 = tk.Frame(self.cuaderno1, bg="#f4f6f8")
        self.cuaderno1.add(self.pagina1, text="Entrada")
        self.pagina1.grid_columnconfigure(0, weight=1)
        self.pagina1.grid_rowconfigure(1, weight=1)

        # Variables que utiliza la lógica existente.
        self.MaxId = tk.StringVar()
        self.Placa = tk.StringVar()
        self.NumTarjeta4 = tk.StringVar()

        encabezado = tk.Frame(self.pagina1, bg="#17365d", padx=24, pady=18)
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(0, weight=1)
        tk.Label(
            encabezado,
            text="BIENVENIDO(A) AL ESTACIONAMIENTO",
            bg="#17365d",
            fg="white",
            font=("Arial", 30, "bold")
        ).grid(row=0, column=0)
        tk.Label(
            encabezado,
            text="ENTRADA",
            bg="#17365d",
            fg="#d9eaf7",
            font=("Arial", 18, "bold")
        ).grid(row=1, column=0, pady=(6, 0))

        cuerpo = tk.Frame(self.pagina1, bg="#f4f6f8", padx=30, pady=22)
        cuerpo.grid(row=1, column=0, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_rowconfigure(1, weight=1)

        self.SenBol = tk.Label(
            cuerpo,
            text="ESPERE UN MOMENTO",
            bg="white",
            fg="#17365d",
            font=("Arial", 30, "bold"),
            relief="solid",
            borderwidth=1,
            padx=20,
            pady=24
        )
        self.SenBol.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        estados = tk.Frame(cuerpo, bg="#f4f6f8")
        estados.grid(row=1, column=0, sticky="nsew")
        for columna in range(3):
            estados.grid_columnconfigure(columna, weight=1)

        self.loopDet = tk.Label(
            estados, text="SIN AUTO", bg="#cfd4da", fg="#20252a",
            font=("Arial", 20, "bold"), padx=12, pady=18
        )
        self.loopDet.grid(row=0, column=0, padx=6, sticky="ew")

        self.BotDet = tk.Label(
            estados, text="BOTÓN EN ESPERA", bg="#cfd4da", fg="#20252a",
            font=("Arial", 20, "bold"), padx=12, pady=18
        )
        self.BotDet.grid(row=0, column=1, padx=6, sticky="ew")

        self.SenBol2 = tk.Label(
            estados, text="BOLETO EN ESPERA", bg="#cfd4da", fg="#20252a",
            font=("Arial", 20, "bold"), padx=12, pady=18
        )
        self.SenBol2.grid(row=0, column=2, padx=6, sticky="ew")

        reloj = tk.Frame(cuerpo, bg="#f4f6f8")
        reloj.grid(row=2, column=0, pady=24)
        self.mi_reloj = tk.Label(
            reloj, text="00:00:00", bg="#f4f6f8", fg="#17202a",
            font=("Arial", 62, "bold")
        )
        self.mi_reloj.grid(row=0, column=0)
        self.Reloj = tk.Label(
            reloj, text="", bg="#f4f6f8", fg="#5d6d7e",
            font=("Arial", 24)
        )
        self.Reloj.grid(row=1, column=0)

        # El lector RFID se comporta como teclado. El campo permanece discreto
        # pero enfocado para conservar el acceso de pensionados.
        pie = tk.Frame(self.pagina1, bg="#e8edf2", padx=20, pady=10)
        pie.grid(row=2, column=0, sticky="ew")
        pie.grid_columnconfigure(1, weight=1)
        tk.Label(
            pie, text="PENSIONADOS: ACERQUE SU TARJETA",
            bg="#e8edf2", fg="#34495e", font=("Arial", 13, "bold")
        ).grid(row=0, column=0, padx=(0, 12))
        self.entryNumTarjeta4 = tk.Entry(
            pie, width=2, textvariable=self.NumTarjeta4,
            bg="#e8edf2", fg="#e8edf2", insertbackground="#e8edf2",
            relief="flat", highlightthickness=0
        )
        self.entryNumTarjeta4.bind("<Return>", self._rfid_enter)
        self.entryNumTarjeta4.bind("<KP_Enter>", self._rfid_enter)
        self.entryNumTarjeta4.bind("<KeyRelease>", self._rfid_tecla)
        self.entryNumTarjeta4.grid(row=0, column=1, sticky="w")

        # Controles de diagnóstico conservados sin mostrarlos al público.
        self.labelframe1 = tk.Frame(self.pagina1)
        self.entryMaxId = tk.Entry(
            self.labelframe1, width=10, textvariable=self.MaxId, state="readonly"
        )
        self.entryPlaca = tk.Entry(
            self.labelframe1, width=15, textvariable=self.Placa
        )
        self.labelMensaje = tk.Label(self.labelframe1, text="")
        self.Bienvenida = tk.Label(self.labelframe1, text="BIENVENIDOS")

        self.entryNumTarjeta4.focus_set()

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
        if io.input(loop) == io.LOW:
            print('hay auto') 
            io.output(out1,0)#con un "1" se apaga el led
            BanLoop = 1
        else:
            io.output(out1,1)                              
            BanLoop = 0

    def IntBoton(self): #Detecta presencia de automovil
        global BanBoton
        if io.input(boton) == io.LOW:
            print('Presiono boton')
            io.output(out2,0)
            BanBoton = 1
        else:
            io.output(out2,1)
            BanBoton = 0

    def IntSenBoleto(self, channel=None):
        """Lee el sensor; no abre la barrera desde la interrupción."""
        global BanSenBoleto
        nivel = io.input(SenBoleto)
        activo = nivel == io.LOW if sensor_boleto_activo_bajo else nivel == io.HIGH
        BanSenBoleto = int(activo)

    io.add_event_detect(loop, io.BOTH, callback = Intloop)
    io.add_event_detect(boton, io.BOTH, callback = IntBoton)
    io.add_event_detect(SenBoleto, io.BOTH, callback = IntSenBoleto, bouncetime=30)


    def check_inputs(self):
        global BanBoton, BanLoop, BanImpresion, BotonArmado
    
        if BanLoop == 1:
            self.loopDet.config(text = "Hay auto", font=('Arial', 20, 'bold'), background = 'green')
        else:
            self.loopDet.config(text = ".", font=('Arial', 20, 'bold'), background = '#CCC') #'#CCC'
            self.SenBol2.config(text = ".", font=('Arial', 20, 'bold'), background='#CCC')
            self.SenBol.config(text = ".", font=('Arial', 20, 'bold'), background='#CCC')
            BanImpresion = 1

        if BanBoton == 1:
            self.BotDet.config(text = "presiono btn", font=('Arial', 20, 'bold'), background='#CCC') #'#CCC'
            # Protección de arranque: un nivel bajo presente al iniciar no
            # cuenta como pulsación. Primero debe detectarse el botón suelto.
            if BotonArmado == 0:
                self.BotDet.config(
                    text="SUELTE BOTON",
                    font=('Arial', 20, 'bold'),
                    background='orange'
                )
            # Nunca abrir ni imprimir si no se detecta un vehiculo.
            elif BanLoop != 1:
                print('Boton ignorado: no hay auto')
                self.BotDet.config(
                    text="SIN AUTO - BOTON IGNORADO",
                    font=('Arial', 20, 'bold'),
                    background='orange'
                )
                BotonArmado = 0
            elif BanImpresion == 1 and not self._esperando_retiro:
                # Primero imprime; la barrera continúa cerrada.
                BotonArmado = 0
                BanImpresion = 0
                try:
                    self.agregarRegistroRFID()
                    self._esperando_retiro = True
                    self._sensor_vio_boleto = False
                    self._inicio_espera_boleto = time.monotonic()
                    self.SenBol.config(text="2) TOME SU BOLETO",
                                       font=('Arial', 20, 'bold'), background="orange")
                    print("Boleto impreso; esperando presencia y retiro")
                except Exception:
                    BanImpresion = 1
                    self.SenBol.config(text="ERROR IMPRESION - BARRERA CERRADA",
                                       font=('Arial', 20, 'bold'), background="red")
                    traceback.print_exc()
            else:   
                self.SenBol.config(text = "press btn sin impresion", font=('Arial', 20, 'bold'), background= "red") 

        else: 
            # El botón ya fue visto en reposo (HIGH); la próxima transición a
            # LOW será una pulsación real.
            BotonArmado = 1
            self.BotDet.config(text = "solto btn", font=('Arial', 20, 'bold'), background='#CCC') #'#CCC'       
            if not self._esperando_retiro:
                self.SenBol.config(text = "", font=('Arial', 20, 'bold'), background="#CCC")
            #if BanBoton == 1 and BanLoop==1:
           

            #BanImpresion = 1

        # Se exige la secuencia presente -> retirado. Un cable roto o un
        # sensor que nunca cambia no puede abrir la barrera.
        if self._esperando_retiro:
            if BanSenBoleto == 1:
                self._sensor_vio_boleto = True
                self.SenBol.config(text="2) TOME SU BOLETO",
                                   font=('Arial', 20, 'bold'), background="orange")
            elif self._sensor_vio_boleto:
                self._esperando_retiro = False
                self._sensor_vio_boleto = False
                if BanLoop == 1:
                    self.SenBol.config(text="3) AVANCE",
                                       font=('Arial', 20, 'bold'), background="green")
                    self._abrir_barrera()
                else:
                    self.SenBol.config(text="SIN AUTO - BARRERA CERRADA",
                                       font=('Arial', 20, 'bold'), background="red")
                    print("Retiro confirmado sin automóvil: no se abre")
            elif time.monotonic() - self._inicio_espera_boleto >= tiempo_retiro_boleto:
                self._esperando_retiro = False
                self.SenBol.config(text="SENSOR SIN BOLETO - BARRERA CERRADA",
                                   font=('Arial', 20, 'bold'), background="red")
                print("Tiempo agotado: no se confirmó la presencia del boleto")

        now =datetime.now() 
        fecha1= now.strftime("%d-%b-%y")
        hora1= now.strftime("%H:%M:%S")    
        self.Reloj.config(text=fecha1)            
        self.mi_reloj.config(text=hora1)    
        self.ventana1.after(60, self.check_inputs)          # activa un timer de 50mSeg.

     
    def _abrir_barrera(self):
        """Pulso activo-bajo posterior a la confirmación de retiro."""
        print("Retiro confirmado - abre barrera")
        io.output(barrera, io.LOW)
        time.sleep(1)
        io.output(barrera, io.HIGH)

    def agregarRegistroRFID(self):
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$impresion    $$$$$$$$$$$$$$$$$$$
        fechaEntro = datetime.today()
        fSTR=str(fechaEntro)
        corteNum = 0
        placa=str(self.Placa.get(), )                 
        datos=(fechaEntro, corteNum, placa)
        time.sleep(1)                            
        n1=str(self.operacion1.altaRegistroRFID(datos))
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
        p = Usb(printer_vendor_id, printer_product_id, 0)
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
