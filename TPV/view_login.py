import os
import tkinter as tk
from tkinter import ttk
from view_crud_usuarios_tpv import ViewCRUDUsuarios
from tkinter import messagebox as mb

class View_Login:
    """Clase de la vista del login."""
    def __init__(self):
        """Inicializa una instancia de la clase Login y crea la ventana principal de la interfaz."""
        # Crea la ventana principal
        self.window_login = tk.Toplevel()

        # Se elimina la funcionalidad del botón de cerrar
        self.window_login.protocol("WM_DELETE_WINDOW", lambda: self.desconectar())

        # Establece el tamaño de la ventana y su título
        self.window_login.title(f'Login')

        # Establece el tamaño máximo de la ventana para que ocupe toda la pantalla
        ancho_max = self.window_login.winfo_screenwidth()
        alto_max = self.window_login.winfo_screenheight()
        self.window_login.wm_maxsize(ancho_max, alto_max)

        # Establece la posición inicial de la ventana en la pantalla
        pos_x = int(ancho_max/3)
        pos_y = int(alto_max/10)
        self.window_login.geometry(f"+{pos_x}+{pos_y}")

        # Establece que la ventana no sea redimensionable
        self.window_login.resizable(False, False)

        # Crea las variables para los datos de usuario y tema
        self.user = tk.StringVar()
        self.password = tk.StringVar()

        # Llama al método "interface()" para construir la interfaz gráfica
        self.interface()

        # Inicia el loop principal de la ventana
        self.window_login.mainloop()

    def interface(self):
        """Define la interfaz gráfica de usuario."""
        # Crea un frame principal para la ventana
        self.seccion_principal = ttk.LabelFrame(self.window_login, text='')
        self.seccion_principal.grid(row=0, column=0, sticky=tk.NSEW)

        # Crea un frame para el formulario
        self.seccion_formulario = ttk.LabelFrame(self.seccion_principal, text='Ingresa los siguientes datos', padding=10)
        self.seccion_formulario.grid(row=0, column=0, sticky=tk.NSEW)

        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_user = ttk.Label(self.seccion_formulario, text='Nombre de usuario: ')
        etiqueta_user.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        campo_user = ttk.Entry(self.seccion_formulario, textvariable=self.user)
        campo_user.grid(row=0, column=1, padx=5, pady=5)

        # Crea la etiqueta para el campo de entrada de texto de la contraseña
        etiqueta_password = ttk.Label(self.seccion_formulario, text='Contraseña: ')
        etiqueta_password.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para la contraseña
        campo_password = ttk.Entry(self.seccion_formulario, textvariable=self.password, show= "*")
        campo_password.grid(row=1, column=1, padx=5, pady=5)

        # Crea el botón para ingresar los datos del usuario y llama al método get_data del controlador para procesar los datos
        self.boton_entrar = ttk.Button(self.seccion_principal, text='Entrar',
            command=lambda:{
                self.desactivar(),
                self.get_data(user=self.user.get(),
                              password=self.password.get()),
                self.activar()
                })
        self.boton_entrar.grid(row=1, column=0, padx=5, pady=5)
        
        campo_user.focus()

    def get_data(self, user=None, password=None):
        """Obtiene los datos de usuario y contraseña ingresados y verifica si son correctos.

        Args:
            user (str): Nombre de usuario ingresado.
            password (str): Contraseña ingresada.
        """
        usuario_admin = os.environ.get("ESTACIONAMIENTO_ADMIN_USER", "")
        password_admin = os.environ.get("ESTACIONAMIENTO_ADMIN_PASSWORD", "")
        if usuario_admin and password_admin and user == usuario_admin and password == password_admin:
            ViewCRUDUsuarios()
        else:
            mb.showerror("Error", "La contraseña es Equivocada, intente nuevamente")
            self.password.set("")

    def desconectar(self):
        """Cierra la ventana principal y detiene el hilo en el que se ejecuta."""
        # Detener el loop principal
        self.window_login.quit()
        # Destruye el panel principal
        self.window_login.destroy()

    def desactivar(self):
        """Desactiva los botones de la interfaz."""
        # Oculta la ventana
        self.window_login.withdraw()
        self.boton_entrar.config(state="disable")

    def activar(self):
        """Activa los botones de la interfaz."""
        self.password.set("")
        self.window_login.deiconify()
        self.boton_entrar.config(state="normal")

#View_Login()
