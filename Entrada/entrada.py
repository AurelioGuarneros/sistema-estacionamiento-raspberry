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
from pathlib import Path
from PIL import Image, ImageTk

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
        """Pantalla clásica funcional con apoyo visual independiente."""
        self.ventana1.geometry("800x480")
        self.ventana1.minsize(720, 430)
        self.pagina1 = tk.Frame(self.cuaderno1, bg="#eef3f8")
        self.cuaderno1.add(self.pagina1, text="Entrada")
        self.pagina1.grid_columnconfigure(0, weight=1)
        self.pagina1.grid_rowconfigure(1, weight=1)

        encabezado = tk.Frame(self.pagina1, bg="#0b3b71", pady=9)
        encabezado.grid(row=0, column=0, sticky="ew")
        tk.Label(
            encabezado, text="BIENVENIDO(A) AL ESTACIONAMIENTO",
            bg="#0b3b71", fg="white", font=("Arial", 24, "bold")
        ).pack()
        tk.Label(
            encabezado, text="ENTRADA", bg="#0b3b71", fg="#a9ddff",
            font=("Arial", 14, "bold")
        ).pack()

        cuerpo = tk.Frame(self.pagina1, bg="#eef3f8", padx=14, pady=10)
        cuerpo.grid(row=1, column=0, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=2)
        cuerpo.grid_columnconfigure(1, weight=3)
        cuerpo.grid_rowconfigure(0, weight=1)

        estados = tk.LabelFrame(
            cuerpo, text=" ESTADO DEL EQUIPO ", bg="white", fg="#17365d",
            font=("Arial", 13, "bold"), padx=12, pady=10
        )
        estados.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.loopDet = tk.Label(
            estados, text="NO HAY AUTO", bg="#d9e1e8", fg="#17202a",
            font=("Arial", 17, "bold"), pady=12
        )
        self.loopDet.pack(fill="x", pady=5)
        self.BotDet = tk.Label(
            estados, text="BOTÓN SUELTO", bg="#d9e1e8", fg="#17202a",
            font=("Arial", 17, "bold"), pady=12
        )
        self.BotDet.pack(fill="x", pady=5)
        self.SenBol = tk.Label(
            estados, text="ESPERANDO VEHÍCULO", bg="#d9e1e8", fg="#17202a",
            font=("Arial", 15, "bold"), pady=12
        )
        self.SenBol.pack(fill="x", pady=5)
        self.SenBol2 = tk.Label(estados, text="", bg="white")
        self.SenBol2.pack()

        visual = tk.LabelFrame(
            cuerpo, text=" INDICACIÓN VISUAL ", bg="#102a46", fg="white",
            font=("Arial", 13, "bold"), padx=6, pady=6
        )
        visual.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._imagenes_estado = self._cargar_imagenes_estado()
        self.imagen_estado = tk.Label(visual, bg="#102a46", bd=0)
        self.imagen_estado.pack(fill="both", expand=True)

        inferior = tk.Frame(self.pagina1, bg="#071a33", padx=18, pady=7)
        inferior.grid(row=2, column=0, sticky="ew")
        self.Reloj = tk.Label(
            inferior, text="", bg="#071a33", fg="#cfe9ff",
            font=("Arial", 16, "bold")
        )
        self.Reloj.pack(side="left")
        self.mi_reloj = tk.Label(
            inferior, text="", bg="#071a33", fg="white",
            font=("Arial", 25, "bold")
        )
        self.mi_reloj.pack(side="right")
        tk.Label(
            inferior, text="PENSIONADOS: ACERQUE SU TARJETA",
            bg="#071a33", fg="#8fd4ff", font=("Arial", 11, "bold")
        ).pack(side="bottom")

        # Controles originales conservados para operación y lectores.
        self.MaxId = tk.StringVar()
        self.Placa = tk.StringVar()
        self.NumTarjeta4 = tk.StringVar()
        self.entryNumTarjeta4 = tk.Entry(
            self.pagina1, textvariable=self.NumTarjeta4, width=1
        )
        self.entryNumTarjeta4.place(x=-50, y=-50)
        self.entryNumTarjeta4.bind("<Return>", self._rfid_enter)
        self.entryNumTarjeta4.bind("<KP_Enter>", self._rfid_enter)
        self.entryNumTarjeta4.bind("<KeyRelease>", self._rfid_tecla)
        self.entryNumTarjeta4.focus_set()
        self.labelMensaje = tk.Label(self.pagina1, text="")
        self.entryPlaca = tk.Entry(self.pagina1, textvariable=self.Placa)
        self.boton1 = tk.Button(
            self.pagina1, text="Generar Entrada", command=self.agregarRegistroRFID
        )
        self._mostrar_imagen_estado("sin_auto")

    def _cargar_imagenes_estado(self):
        estados = ("sin_auto", "auto", "oprima", "presionado", "ticket", "error")
        ruta = Path(__file__).resolve().parent / "recursos" / "entrada_interactiva.jpg"
        imagenes = {}
        try:
            lamina = Image.open(ruta).convert("RGB")
            ancho = lamina.width // 3
            alto = lamina.height // 2
            for estado, (columna, fila) in zip(
                estados, ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1))
            ):
                recorte = lamina.crop((
                    columna * ancho, fila * alto,
                    (columna + 1) * ancho, (fila + 1) * alto,
                ))
                recorte = recorte.resize((390, 245), Image.Resampling.LANCZOS)
                imagenes[estado] = ImageTk.PhotoImage(
                    recorte, master=self.ventana1
                )
        except (OSError, ValueError) as error:
            print("No se pudieron cargar las imágenes:", error)
        return imagenes

    def _mostrar_imagen_estado(self, estado):
        imagen = self._imagenes_estado.get(estado)
        if imagen is not None:
            self.imagen_estado.configure(image=imagen, text="")
        else:
            self.imagen_estado.configure(
                image="", text=estado.replace("_", " ").upper(),
                fg="white", font=("Arial", 22, "bold")
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
    
        if BanLoop == 1:
            self.loopDet.config(text="HAY AUTO", font=('Arial', 17, 'bold'), background='#2e9d63', foreground='white')
            self._mostrar_imagen_estado("auto")
        else:
            self.loopDet.config(text="NO HAY AUTO", font=('Arial', 17, 'bold'), background='#d9e1e8', foreground='#17202a')
            self._mostrar_imagen_estado("sin_auto")
            self.SenBol2.config(text = ".", font=('Arial', 15), background='#CCC')
            self.SenBol.config(text = ".", font=('Arial', 15), background='#CCC')
            BanImpresion = 1

        if BanBoton == 1:
            self.BotDet.config(text="BOTÓN PRESIONADO", font=('Arial', 17, 'bold'), background='#f0a23a', foreground='white')
            self._mostrar_imagen_estado("presionado")
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
                try:
                    self.agregarRegistroRFID()
                except Exception as error:
                    print("ERROR DE IMPRESIÓN:", error)
                    traceback.print_exc()
                    self.SenBol.config(
                        text="NO SE PUDO IMPRIMIR",
                        background="#c62828", foreground="white"
                    )
                    self._mostrar_imagen_estado("error")
                else:
                    self.SenBol.config(
                        text="TOME SU BOLETO",
                        background="#2e9d63", foreground="white"
                    )
                    self._mostrar_imagen_estado("ticket")
                BanImpresion = 0
            else:   
                self.SenBol.config(text="BOLETO YA GENERADO", font=('Arial', 15, 'bold'), background="#2e9d63", foreground="white")

        else: 
            # El boton ya fue visto en reposo; la proxima transicion a alto
            # sera una pulsacion real.
            BotonArmado = 1
            self.BotDet.config(text="BOTÓN SUELTO", font=('Arial', 17, 'bold'), background='#d9e1e8', foreground='#17202a')
            if BanLoop == 1 and BanImpresion == 1:
                self.SenBol.config(text="OPRIMA EL BOTÓN", font=('Arial', 15, 'bold'), background="#ffcc4d", foreground="#17202a")
                self._mostrar_imagen_estado("oprima")
            elif BanLoop == 1 and BanImpresion == 0:
                self.SenBol.config(text="PUEDE AVANZAR", font=('Arial', 15, 'bold'), background="#2e9d63", foreground="white")
            else:
                self.SenBol.config(text="ESPERANDO VEHÍCULO", font=('Arial', 15, 'bold'), background="#d9e1e8", foreground="#17202a")
            #if BanBoton == 1 and BanLoop==1:
           

            #BanImpresion = 1

        now =datetime.now() 
        meses = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre")
        fecha1 = f"{now.day} de {meses[now.month - 1]} de {now.year}"
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

