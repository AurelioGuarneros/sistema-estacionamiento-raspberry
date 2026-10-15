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
        self._rfid_after_id = None
        self._rfid_en_proceso = False

        self.ExpedirRfid()
        # Leer primero los GPIO reales. Si check_inputs se ejecuta antes,
        # BanBoton conserva temporalmente el cero inicial y arma el boton sin
        # haber comprobado que fisicamente estaba suelto.
        self.IntBoton()
        self.Intloop()
        self.check_inputs()

        self.ventana1.mainloop()
    ###########################Inicia Pagina1##########################
# Funcion de lectura de las entradas
# -----------------------------------
    def ExpedirRfid(self):
        """Construye una pantalla guiada por los sensores de la boletera."""
        self.ventana1.configure(bg="#071a33")
        self.ventana1.geometry("800x480")
        self.ventana1.minsize(720, 430)
        self.ventana1.bind("<Escape>", lambda _e: self.ventana1.attributes("-fullscreen", False))

        self.MaxId = tk.StringVar()
        self.Placa = tk.StringVar()
        self.NumTarjeta4 = tk.StringVar()
        self._estado_visual = None
        self._fase_animacion = 0
        self._ticket_visible_hasta = 0

        self.pantalla = tk.Canvas(
            self.ventana1, bg="#071a33", highlightthickness=0
        )
        self.pantalla.pack(fill="both", expand=True)

        # El lector RFID trabaja como teclado. La entrada queda fuera del área
        # visible para no distraer al conductor.
        self.entryNumTarjeta4 = tk.Entry(
            self.ventana1, textvariable=self.NumTarjeta4, width=1
        )
        self.entryNumTarjeta4.place(x=-50, y=-50)
        self.entryNumTarjeta4.bind("<Return>", self._rfid_enter)
        self.entryNumTarjeta4.bind("<KP_Enter>", self._rfid_enter)
        self.entryNumTarjeta4.bind("<KeyRelease>", self._rfid_tecla)
        self.entryNumTarjeta4.focus_set()

        self.labelMensaje = tk.Label(
            self.ventana1, text="", bg="#071a33", fg="white"
        )
        self._actualizar_visual("sin_auto", forzar=True)

    def _texto_centrado(self, y, texto, tamano, color="white", negrita=True):
        ancho = max(self.pantalla.winfo_width(), 800)
        estilo = "bold" if negrita else "normal"
        self.pantalla.create_text(
            ancho / 2, y, text=texto, fill=color,
            font=("DejaVu Sans", tamano, estilo), justify="center"
        )

    def _dibujar_auto(self, activo):
        ancho = max(self.pantalla.winfo_width(), 800)
        centro = ancho / 2
        color = "#20c997" if activo else "#60758d"
        self.pantalla.create_rectangle(
            centro - 125, 205, centro + 125, 270,
            fill=color, outline="", width=0
        )
        self.pantalla.create_polygon(
            centro - 75, 205, centro - 38, 165,
            centro + 62, 165, centro + 105, 205,
            fill=color, outline=""
        )
        self.pantalla.create_polygon(
            centro - 52, 199, centro - 28, 174,
            centro + 52, 174, centro + 78, 199,
            fill="#bde7ff", outline=""
        )
        for x in (centro - 78, centro + 78):
            self.pantalla.create_oval(
                x - 23, 248, x + 23, 294, fill="#17202a", outline="#dbe7f3", width=4
            )
        sensor = "#41f08a" if activo else "#40556e"
        for radio in (22, 36, 50):
            self.pantalla.create_arc(
                centro - 190 - radio, 195 - radio,
                centro - 190 + radio, 195 + radio,
                start=300, extent=120, style="arc", outline=sensor, width=4
            )

    def _dibujar_boton(self, presionado=False):
        ancho = max(self.pantalla.winfo_width(), 800)
        centro = ancho / 2
        desplazamiento = 9 if presionado else 0
        pulso = 8 if self._fase_animacion % 2 else 0
        self.pantalla.create_oval(
            centro - 70 - pulso, 197 - pulso,
            centro + 70 + pulso, 337 + pulso,
            fill="#17365d", outline="#55b7ff", width=5
        )
        self.pantalla.create_oval(
            centro - 52, 214 + desplazamiento,
            centro + 52, 318 + desplazamiento,
            fill="#ffb000" if not presionado else "#e35d35",
            outline="white", width=5
        )
        # Mano y dedo apuntando al pulsador.
        dedo_y = 180 + desplazamiento
        self.pantalla.create_oval(
            centro + 92, dedo_y - 20, centro + 137, dedo_y + 25,
            fill="#ffd6ad", outline="#8a5b38", width=2
        )
        self.pantalla.create_rectangle(
            centro + 70, dedo_y, centro + 116, dedo_y + 88,
            fill="#ffd6ad", outline="#8a5b38", width=2
        )
        self.pantalla.create_polygon(
            centro + 70, dedo_y + 18,
            centro + 20, 230 + desplazamiento,
            centro + 38, 252 + desplazamiento,
            centro + 88, dedo_y + 43,
            fill="#ffd6ad", outline="#8a5b38"
        )

    def _dibujar_ticket(self):
        ancho = max(self.pantalla.winfo_width(), 800)
        centro = ancho / 2
        self.pantalla.create_rectangle(
            centro - 135, 160, centro + 135, 330,
            fill="white", outline="#41f08a", width=6
        )
        self.pantalla.create_text(
            centro, 190, text="BOLETO DE ENTRADA",
            fill="#17365d", font=("DejaVu Sans", 18, "bold")
        )
        for x, y, medida in (
            (-82, -15, 34), (-36, -15, 18), (25, -15, 28),
            (-82, 30, 18), (-45, 25, 30), (18, 28, 18), (55, 25, 32)
        ):
            self.pantalla.create_rectangle(
                centro + x, 240 + y, centro + x + medida, 240 + y + medida,
                fill="#071a33", outline=""
            )
        self.pantalla.create_text(
            centro, 307, text="RETÍRELO Y AVANCE",
            fill="#17365d", font=("DejaVu Sans", 18, "bold")
        )

    def _actualizar_visual(self, estado, forzar=False):
        if not forzar and estado == self._estado_visual and self._fase_animacion % 8:
            return
        self._estado_visual = estado
        self.pantalla.delete("all")
        ancho = max(self.pantalla.winfo_width(), 800)
        self.pantalla.create_rectangle(0, 0, ancho, 92, fill="#0b3b71", outline="")
        self._texto_centrado(31, "BIENVENIDO(A) AL ESTACIONAMIENTO", 25)
        self._texto_centrado(68, "ENTRADA", 15, "#9dd8ff")

        if estado == "sin_auto":
            self._dibujar_auto(False)
            self._texto_centrado(122, "NO HAY VEHÍCULO", 25, "#c8d6e5")
            self._texto_centrado(348, "Avance hasta el sensor", 20, "#9dd8ff")
        elif estado == "auto":
            self._dibujar_auto(True)
            self._texto_centrado(122, "VEHÍCULO DETECTADO", 25, "#41f08a")
            self._texto_centrado(348, "Permanezca detenido un momento", 19, "#dcecff")
        elif estado == "oprima":
            self._dibujar_boton(False)
            self._texto_centrado(122, "OPRIMA EL BOTÓN", 29, "#ffcc4d")
            self._texto_centrado(356, "Un solo toque para recibir su boleto", 18, "#dcecff")
        elif estado == "presionado":
            self._dibujar_boton(True)
            self._texto_centrado(122, "BOTÓN PRESIONADO", 27, "#ffcc4d")
            self._texto_centrado(356, "Estamos preparando su boleto…", 19, "#dcecff")
        elif estado == "ticket":
            self._dibujar_ticket()
            self._texto_centrado(122, "TOME SU BOLETO", 30, "#41f08a")
            self._texto_centrado(356, "La barrera está abriendo", 19, "#dcecff")
        elif estado == "avance":
            self._dibujar_auto(True)
            self._texto_centrado(122, "PUEDE AVANZAR", 30, "#41f08a")
            self._texto_centrado(348, "Gracias por su visita", 20, "#dcecff")

        meses = (
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        )
        ahora = datetime.now()
        fecha = f"{ahora.day} de {meses[ahora.month - 1]} de {ahora.year}"
        self.pantalla.create_text(
            24, 438, text=fecha, anchor="w", fill="#dcecff",
            font=("DejaVu Sans", 14, "bold")
        )
        self.pantalla.create_text(
            ancho - 24, 438, text=ahora.strftime("%H:%M:%S"), anchor="e",
            fill="white", font=("DejaVu Sans", 25, "bold")
        )
        self.pantalla.create_text(
            ancho / 2, 468, text="PENSIONADOS: ACERQUE SU TARJETA",
            fill="#9dd8ff", font=("DejaVu Sans", 12, "bold")
        )

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

        self._fase_animacion += 1
        ahora_mono = time.monotonic()

        if BanLoop != 1:
            BanImpresion = 1
            self._ticket_visible_hasta = 0
            estado = "sin_auto"
        elif ahora_mono < self._ticket_visible_hasta:
            estado = "ticket"
        elif BanImpresion == 0:
            estado = "avance"
        elif BanBoton == 1:
            estado = "presionado"
        elif BotonArmado == 0:
            estado = "auto"
        else:
            estado = "oprima"

        if BanBoton == 1:
            if BotonArmado == 0:
                # Al arrancar, un botón sostenido no debe expedir boletos.
                estado = "presionado"
            elif BanLoop != 1:
                BotonArmado = 0
                estado = "sin_auto"
            elif BanImpresion == 1:
                BotonArmado = 0
                self._actualizar_visual("presionado", forzar=True)
                self.ventana1.update_idletasks()
                io.output(barrera, 0)
                time.sleep(1)
                io.output(barrera, 1)
                self.agregarRegistroRFID()
                BanImpresion = 0
                self._ticket_visible_hasta = time.monotonic() + 5
                estado = "ticket"
        else:
            BotonArmado = 1

        self._actualizar_visual(estado)
        self.ventana1.after(100, self.check_inputs)

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

