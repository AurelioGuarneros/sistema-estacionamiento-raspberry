from datetime import datetime, date
from tkinter import messagebox as mb
from tkinter import *
import tkinter as tk
import operacion_tpv as operacion
from configuracion_tpv import AZUL, AZUL_CLARO, FONDO, ROJO, cargar_configuracion
#import subprocess

class Login_sistema:
    def __init__(self):
        self.operacion1=operacion.Operacion()    
        self.window = tk.Tk()
        self.window.title("Registro Inicio de Turno")        
        self.configuracion = cargar_configuracion()
        self.window.configure(bg=FONDO)
        self.fullScreenState = self.configuracion["general"]["pantalla_completa"]
        self.window.attributes('-fullscreen', self.fullScreenState)
        self.window.bind("<F11>", self.toggleFullScreen)
        self.window.bind("<Escape>", self.quitFullScreen)

        encabezado = tk.Frame(self.window, bg=AZUL, padx=24, pady=18)
        encabezado.pack(fill="x")
        tk.Label(
            encabezado,
            text=self.configuracion["general"]["nombre_estacionamiento"].upper(),
            bg=AZUL, fg="white", font=("Arial", 25, "bold")
        ).pack(side="left")
        tk.Label(
            encabezado, text="INICIO DE TURNO", bg=AZUL, fg=AZUL_CLARO,
            font=("Arial", 15, "bold")
        ).pack(side="left", padx=18, pady=(7, 0))
        tk.Button(
            encabezado, text="CERRAR", command=self.quitF, bg=ROJO, fg="white",
            activebackground="#8c1d18", activeforeground="white",
            font=("Arial", 12, "bold"), padx=18, pady=7, relief="flat"
        ).pack(side="right")

        contenido = tk.Frame(self.window, bg=FONDO)
        contenido.pack(fill="both", expand=True)
        self.labelframe1=tk.LabelFrame(
            contenido, text="  ACCESO AL PUNTO DE VENTA  ", bg="white", fg=AZUL,
            font=("Arial", 17, "bold"), padx=28, pady=24
        )
        self.labelframe1.place(relx=.5, rely=.46, anchor="center")
        #self.Adentroframe=tk.LabelFrame(self.window, text="Autos DENTRO")
        #self.Adentroframe.grid(column=2, row=0, padx=0, pady=0)
        self.Nombre=tk.StringVar()
        self.entryNombre=tk.Entry(self.labelframe1, width=22, textvariable=self.Nombre, font=("Arial", 16))
        self.entryNombre.grid(column=1, row=0, padx=12, pady=10)
        self.entryNombre.focus()
        self.Contraseña=tk.StringVar()
        self.entryContraseña=tk.Entry(self.labelframe1, width=22, textvariable=self.Contraseña, show="*", justify=tk.LEFT, font=("Arial", 16))
        self.entryContraseña.grid(column=1, row=1, padx=12, pady=10)
        self.Turno=tk.StringVar()
        self.entryTurno=tk.Entry(self.labelframe1, width=22, textvariable=self.Turno, font=("Arial", 16))
        self.entryTurno.grid(column=1, row=2, padx=12, pady=10)
        self.lblNombre=tk.Label(self.labelframe1, text="Usuario", bg="white", font=("Arial", 13, "bold"))
        self.lblNombre.grid(column=0, row=0, padx=0, pady=0)
        self.lblContraseña=tk.Label(self.labelframe1, text="Contraseña", bg="white", font=("Arial", 13, "bold"))
        self.lblContraseña.grid(column=0, row=1, padx=0, pady=0)
        self.lblTurno=tk.Label(self.labelframe1, text="Turno", bg="white", font=("Arial", 13, "bold"))
        self.lblTurno.grid(column=0, row=2, padx=0, pady=0)
        self.lblHorario1=tk.Label(self.labelframe1, text="1 · 7:00 a 15:00", bg="white", fg="#5d6d7e", font=("Arial", 11))
        self.lblHorario1.grid(column=2, row=0, padx=0, pady=0)
        self.lblHorario2=tk.Label(self.labelframe1, text="2 · 15:00 a 22:00", bg="white", fg="#5d6d7e", font=("Arial", 11))
        self.lblHorario2.grid(column=2, row=1, padx=0, pady=0)
        self.lblHorario3=tk.Label(self.labelframe1, text="3 · 22:00 a 7:00", bg="white", fg="#5d6d7e", font=("Arial", 11))
        self.lblHorario3.grid(column=2, row=2, padx=0, pady=0)
        self.lblValidar=tk.Label(self.labelframe1, text="Ingrese sus datos para continuar", bg="white", fg="#5d6d7e", font=("Arial", 11))
        self.lblValidar.grid(column=1, row=3, padx=0, pady=0)
        self.boton1=tk.Button(self.labelframe1, text="CANCELAR", command=self.quitF, width=12, anchor="center", background="#6c757d", foreground="white", font=("Arial", 12, "bold"), pady=8, relief="flat")
        self.boton1.grid(column=2, row=3, padx=4, pady=4)
        self.boton2=tk.Button(self.labelframe1, text="ENTRAR", command=self.abrirPrograma, width=12, anchor="center", background="#2e7d32", foreground="white", font=("Arial", 12, "bold"), pady=8, relief="flat")
        self.boton2.grid(column=0, row=3, padx=4, pady=4)                                                                                                                                
        self.window.mainloop()

    def abrirPrograma(self):
        usuario = self.Nombre.get()
        contrasena = self.Contraseña.get()
        turno = self.Turno.get()

        ##Validar que los campós no esten vacios
        ##Obtener datos del usuario, validamos usuario y contrasena
        if not usuario:
            mb.showwarning("IMPORTANTE", "Escriba su usuario")
            self.entryNombre.focus()
            return

        if not contrasena:
            mb.showwarning("IMPORTANTE", "Escriba su contraseña")
            self.entryContraseña.focus()
            return

        if not turno:
            mb.showwarning("IMPORTANTE", "Escriba su turno")
            self.entryTurno.focus()
            return

        informacion_usuario = self.operacion1.ConsultaUsuario(usuario) 

        if not informacion_usuario:
            mb.showwarning("IMPORTANTE", "El usuario ingresado no existe, revise su informacion")
            self.Nombre.set("")
            self.Contraseña.set("")
            self.Turno.set("")               
            self.entryNombre.focus() 
            return

        print("respuesta: ",informacion_usuario)
        for informacion in informacion_usuario:
            id_usuario = str(informacion[0])
            password_usuario = str(informacion[1])
            nombre = str(informacion[2])

        if contrasena != password_usuario:
            mb.showwarning("IMPORTANTE", "La Contraseña no coincide, volver a capturarla")
            ##limpiar el text de contraseña y poner el foco en ella.
            self.Contraseña.set("")               
            self.entryContraseña.focus()
            return

        inicio = datetime.today()
        info_usuario =(id_usuario, usuario, inicio, nombre, turno) 
        self.operacion1.ActuaizaUsuario(info_usuario)
        ##Cerrar la ventana
        self.quitF()
        from cobroFONLow import FormularioOperacion       
        FormularioOperacion()


    def toggleFullScreen(self, event):
        self.fullScreenState = not self.fullScreenState
        self.window.attributes("-fullscreen", self.fullScreenState)
        self.entryNombre.focus() 

    def quitFullScreen(self, event):
        self.fullScreenState = False
        self.window.attributes("-fullscreen", self.fullScreenState)

    def quitF(self):
        self.window.destroy()
        print('salir')

if __name__ == '__main__':
    app = Login_sistema()
