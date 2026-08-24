from tkinter import messagebox as mb
import tkinter as tk
from tkinter import ttk

from queries import Usuarios


class View_modificar_usuarios:
    """Clase para mostrar la ventana de modificación de datos de un usuario."""

    def __init__(self, usuario_informacion=None, id=None):
        """
        Constructor de la clase. Inicializa la ventana y los atributos.

        Args:
            usuario_informacion (tuple): Tupla con la información del usuario a modificar.
            id (int): Identificador del usuario a modificar.

        Returns:
            None
        """
        self.query = Usuarios()

        self.usuario_informacion = usuario_informacion
        self.id = id

        # Crear la ventana principal
        self.panel_crud = tk.Toplevel()

        # Se elimina la funcionalidad del botón de cerrar
        self.panel_crud.protocol("WM_DELETE_WINDOW", lambda: self.desconectar())

        self.panel_crud.title(f'Modificar usuarios')

        # Configura la columna principal del panel para que use todo el espacio disponible
        self.panel_crud.columnconfigure(0, weight=1)

        # Variables para almacenar los datos del usuario
        self.usuario_nombre = tk.StringVar()
        self.usuario_nombre_completo = tk.StringVar()
        self.usuario_contraseña = tk.StringVar()
        self.usuario_telefono = tk.StringVar()
        self.usuario_telefono_emergencia = tk.StringVar()
        self.usuario_sucursal = tk.StringVar()

        # Establecer los valores iniciales de las variables con los datos del usuario a modificar
        self.usuario_nombre.set(self.usuario_informacion[0][0])
        self.usuario_contraseña.set(self.usuario_informacion[0][1])
        self.usuario_nombre_completo.set(self.usuario_informacion[0][2])
        self.usuario_telefono.set(self.usuario_informacion[0][3])
        self.usuario_telefono_emergencia.set(self.usuario_informacion[0][4])
        self.usuario_sucursal.set(self.usuario_informacion[0][5])

        # Llama a la función interface() que configura la interfaz gráfica
        self.interface()

        self.panel_crud.resizable(False, False)

        # Inicia el loop principal de la ventana
        self.panel_crud.mainloop()

    def interface(self):
        """Crea la interfaz gráfica de la ventana de modificación."""
        # Se crea un Label Frame principal para la sección superior
        seccion_superior = ttk.LabelFrame(self.panel_crud, text='')
        seccion_superior.columnconfigure(1, weight=1)
        seccion_superior.propagate(True)
        seccion_superior.grid(row=0, column=0, sticky=tk.NSEW)

        seccion_logo = ttk.LabelFrame(seccion_superior, text='')
        seccion_logo.grid(row=0, column=0, padx=5, sticky=tk.W)


        # Se crea un Label Frame para la sección de la conexión
        etiqueta_user = ttk.Label(seccion_superior, text=f'Bienvenido/a')
        etiqueta_user.grid(row=0, column=1, padx=5, pady=5)


        seccion_datos_usuario = ttk.LabelFrame(self.panel_crud, text="\tIngresa los datos del usuario a registrar")
        seccion_datos_usuario.grid(row=1, column=0,padx=10, pady=10)

        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_nombre_usuario = ttk.Label(seccion_datos_usuario, text='Nombre de usuario: ')
        etiqueta_nombre_usuario.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        self.campo_nombre_usuario = ttk.Entry(seccion_datos_usuario, textvariable=self.usuario_nombre)
        self.campo_nombre_usuario.grid(row=0, column=1, padx=5, pady=5)



        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_nombre_usuario = ttk.Label(seccion_datos_usuario, text='Nombre completo: ')
        etiqueta_nombre_usuario.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        campo_nombre_usuario = ttk.Entry(seccion_datos_usuario, textvariable=self.usuario_nombre_completo)
        campo_nombre_usuario.grid(row=1, column=1, padx=5, pady=5)

        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_nombre_usuario = ttk.Label(seccion_datos_usuario, text='Contraseña: ')
        etiqueta_nombre_usuario.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        campo_nombre_usuario = ttk.Entry(seccion_datos_usuario, textvariable=self.usuario_contraseña)
        campo_nombre_usuario.grid(row=2, column=1, padx=5, pady=5)


        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_nombre_usuario = ttk.Label(seccion_datos_usuario, text='Telefono: ')
        etiqueta_nombre_usuario.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        campo_nombre_usuario = ttk.Entry(seccion_datos_usuario, textvariable=self.usuario_telefono)
        campo_nombre_usuario.grid(row=4, column=1, padx=5, pady=5)

        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_nombre_usuario = ttk.Label(seccion_datos_usuario, text='Telefono de emergencia: ')
        etiqueta_nombre_usuario.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        campo_nombre_usuario = ttk.Entry(seccion_datos_usuario, textvariable=self.usuario_telefono_emergencia)
        campo_nombre_usuario.grid(row=5, column=1, padx=5, pady=5)


        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_nombre_usuario = ttk.Label(seccion_datos_usuario, text='Sucursal: ')
        etiqueta_nombre_usuario.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        campo_nombre_usuario = ttk.Entry(seccion_datos_usuario, textvariable=self.usuario_sucursal)
        campo_nombre_usuario.grid(row=6, column=1, padx=5, pady=5)

        # Crea un botón y lo empaqueta en la seccion_botones_consulta
        boton_agregar_usuario = ttk.Button(self.panel_crud, text='Modificar usuario', command=self.modificar_usuario, width=16)
        boton_agregar_usuario.grid(row=2, column=0, padx=5, pady=5)

        # Establecer el foco en el campo de entrada de texto para el nombre de usuario
        self.campo_nombre_usuario.focus()

    def modificar_usuario(self):
        """Modifica los datos del usuario en la base de datos."""
        try:
            # Obtener los datos del formulario
            usuario_nombre = self.usuario_nombre.get()
            usuario_contraseña = self.usuario_contraseña.get()
            usuario_nombre_completo = self.usuario_nombre_completo.get()
            usuario_telefono = self.usuario_telefono.get()
            usuario_telefono_emergencia = self.usuario_telefono_emergencia.get()
            usuario_sucursal = self.usuario_sucursal.get()

            # Validar los datos del formulario
            if len(usuario_nombre) == 0 or len(usuario_contraseña) == 0 or len(usuario_nombre_completo) == 0 or len(usuario_telefono) == 0 or len(usuario_telefono_emergencia) == 0 or len(usuario_sucursal) == 0:
                raise IndexError("No dejar campos en blanco")

            # Actualizar los datos del usuario en la base de datos
            datos_usuario = [usuario_nombre, usuario_contraseña, usuario_nombre_completo, usuario_telefono, usuario_telefono_emergencia, usuario_sucursal]
            self.query.actualizar_usuarios(datos_usuario, self.id)

            # Mostrar mensaje de éxito y cerrar la ventana
            mb.showinfo("Información", "El usuario fue modificado correctamente")
            self.desconectar()

        except Exception as e:
            mb.showerror("Error", e)
        except IndexError as e:
            mb.showerror("Error", e)

    def desconectar(self):
        """Cierra la ventana principal y detiene el hilo en el que se ejecuta."""
        self.panel_crud.quit()
        self.panel_crud.destroy()

