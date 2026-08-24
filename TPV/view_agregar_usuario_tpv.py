from tkinter import messagebox as mb
import tkinter as tk
from tkinter import ttk


from datetime import datetime

from queries import Usuarios

class View_agregar_usuarios:
    """
    Clase para mostrar la ventana de agregar usuarios.
    """
    def __init__(self):
        """
        Constructor de la clase. Inicializa la ventana y los atributos.
        """
        self.query = Usuarios()
        self.panel_crud = tk.Toplevel()
        self.panel_crud.protocol("WM_DELETE_WINDOW", lambda: self.desconectar())
        self.panel_crud.title(f'Agregar usuarios')
        self.panel_crud.columnconfigure(0, weight=1)

        # Variables para almacenar datos de usuario
        self.usuario_nombre = tk.StringVar()
        self.usuario_nombre_completo = tk.StringVar()
        self.usuario_contraseña = tk.StringVar()
        self.usuario_telefono = tk.StringVar()
        self.usuario_telefono_emergencia = tk.StringVar()
        self.usuario_sucursal = tk.StringVar()

        self.registros = None
        self.interface()

        self.panel_crud.resizable(False, False)
        self.panel_crud.mainloop()

    def interface(self):
        """
        Crea la interfaz gráfica de la ventana.
        """
        seccion_superior = ttk.LabelFrame(self.panel_crud, text='')
        seccion_superior.columnconfigure(1, weight=1)
        seccion_superior.propagate(True)
        seccion_superior.grid(row=0, column=0, sticky=tk.NSEW)

        etiqueta_user = ttk.Label(seccion_superior, text=f'Bienvenido/a')
        etiqueta_user.grid(row=0, column=1, padx=5, pady=5)

        seccion_datos_usuario = ttk.LabelFrame(self.panel_crud, text="\tIngresa los datos del usuario a registrar")
        seccion_datos_usuario.grid(row=1, column=0, padx=10, pady=10)

        etiqueta_nombre_usuario = ttk.Label(seccion_datos_usuario, text='Nombre de usuario: ')
        etiqueta_nombre_usuario.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.campo_nombre_usuario = ttk.Entry(seccion_datos_usuario, textvariable=self.usuario_nombre)
        self.campo_nombre_usuario.grid(row=0, column=1, padx=5, pady=5)

        etiqueta_nombre_usuario = ttk.Label(seccion_datos_usuario, text='Nombre completo: ')
        etiqueta_nombre_usuario.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        campo_nombre_usuario = ttk.Entry(seccion_datos_usuario, textvariable=self.usuario_nombre_completo)
        campo_nombre_usuario.grid(row=1, column=1, padx=5, pady=5)

        etiqueta_nombre_usuario = ttk.Label(seccion_datos_usuario, text='Contraseña: ')
        etiqueta_nombre_usuario.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        campo_nombre_usuario = ttk.Entry(seccion_datos_usuario, textvariable=self.usuario_contraseña, show="*")
        campo_nombre_usuario.grid(row=2, column=1, padx=5, pady=5)

        etiqueta_nombre_usuario = ttk.Label(seccion_datos_usuario, text='Telefono: ')
        etiqueta_nombre_usuario.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        campo_nombre_usuario = ttk.Entry(seccion_datos_usuario, textvariable=self.usuario_telefono)
        campo_nombre_usuario.grid(row=4, column=1, padx=5, pady=5)

        etiqueta_nombre_usuario = ttk.Label(seccion_datos_usuario, text='Telefono de emergencia: ')
        etiqueta_nombre_usuario.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

        campo_nombre_usuario = ttk.Entry(seccion_datos_usuario, textvariable=self.usuario_telefono_emergencia)
        campo_nombre_usuario.grid(row=5, column=1, padx=5, pady=5)

        etiqueta_nombre_usuario = ttk.Label(seccion_datos_usuario, text='Sucursal: ')
        etiqueta_nombre_usuario.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)

        campo_nombre_usuario = ttk.Entry(seccion_datos_usuario, textvariable=self.usuario_sucursal)
        campo_nombre_usuario.grid(row=6, column=1, padx=5, pady=5)

        boton_agregar_usuario = ttk.Button(self.panel_crud,  text='Agregar usuario', command=self.agregar_usuario, width=16)
        boton_agregar_usuario.grid(row=2, column=0, padx=5, pady=5)

        self.campo_nombre_usuario.focus()

    def agregar_usuario(self):
        """
        Agrega un nuevo usuario a la base de datos con los datos proporcionados en la interfaz.
        """
        try:
            usuario_nombre = self.usuario_nombre.get()
            usuario_contraseña = self.usuario_contraseña.get()
            usuario_nombre_completo = self.usuario_nombre_completo.get()
            usuario_fecha_alta =  datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            usuario_telefono = self.usuario_telefono.get()
            usuario_telefono_emergencia = self.usuario_telefono_emergencia.get()
            usuario_sucursal = self.usuario_sucursal.get()

            if len(usuario_nombre) == 0 or len(usuario_contraseña) == 0 or len(usuario_nombre_completo) == 0 or len(usuario_fecha_alta) == 0 or len(usuario_telefono) == 0 or len(usuario_telefono_emergencia) == 0 or len(usuario_sucursal) == 0:
                raise IndexError("No dejar campos en blanco")

            datos_usuario = [usuario_nombre, usuario_contraseña, usuario_nombre_completo, usuario_fecha_alta, usuario_telefono, usuario_telefono_emergencia, usuario_sucursal]

            self.query.agregar_usuarios(datos_usuario)

            self.desconectar()
        except Exception as e:
            mb.showerror("Error", e)
        except IndexError as e:
            mb.showerror("Error", e)

    def desconectar(self):
        """
        Cierra la ventana y detiene el hilo en el que se ejecuta.
        """
        self.panel_crud.quit()
        self.panel_crud.destroy()
