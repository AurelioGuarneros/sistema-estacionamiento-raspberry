from tkinter import messagebox as mb
import tkinter as tk
from tkinter import ttk

from queries import Usuarios
from view_agregar_usuario_tpv import View_agregar_usuarios
from view_modificar_usuario_tpv import View_modificar_usuarios


class ViewCRUDUsuarios:
    """Clase para mostrar la ventana de administración de usuarios."""

    def __init__(self):
        """Constructor de la clase. Inicializa la ventana y los atributos."""
        # Crear la ventana principal
        self.panel_crud = tk.Toplevel()
        self.panel_crud.protocol("WM_DELETE_WINDOW", lambda: self.desconectar())
        self.panel_crud.title(f'Administración de usuarios -> CiudadMendoza')
        self.panel_crud.columnconfigure(0, weight=1)

        self.ID_usuario = tk.StringVar()
        self.registros = None
        self.controlador_crud_usuarios = Usuarios()
        self.interface()

        self.panel_crud.geometry(f"850x500")
        self.panel_crud.mainloop()

    def interface(self):
        """Crea la interfaz gráfica de la ventana."""
        # Crear un Label Frame principal para la sección superior
        seccion_superior = ttk.LabelFrame(self.panel_crud, text='')
        seccion_superior.columnconfigure(1, weight=1)
        seccion_superior.propagate(True)
        seccion_superior.grid(row=0, column=0, sticky=tk.NSEW)

        # Sección de bienvenida
        seccion_logo = ttk.LabelFrame(seccion_superior, text='')
        seccion_logo.grid(row=0, column=0, padx=5, sticky=tk.W)
        seccion_admin_usuarios = ttk.LabelFrame(seccion_superior, text=f'Bienvenido/a')
        seccion_admin_usuarios.grid(row=0, column=1, sticky=tk.NW)

        seccion_botones_admin_usuarios = ttk.LabelFrame(seccion_admin_usuarios, text="Selecciona qué deseas realizar")
        seccion_botones_admin_usuarios.grid(row=0, column=1, sticky=tk.NW)

        # Botón para agregar usuario
        boton_agregar_usuario = ttk.Button(seccion_botones_admin_usuarios, text='Agregar usuario',
            command=lambda: [View_agregar_usuarios(), self.ver_usuarios()], width=16)
        boton_agregar_usuario.grid(row=0, column=0, padx=5, pady=5)

        # Campo de entrada para el ID del usuario
        etiqueta_user = ttk.Label(seccion_botones_admin_usuarios, text='Ingresa el ID del usuario: ')
        etiqueta_user.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.campo_user = ttk.Entry(seccion_botones_admin_usuarios, textvariable=self.ID_usuario)
        self.campo_user.grid(row=0, column=2, padx=5, pady=5)

        # Botón para modificar usuario
        boton_modificar_usuario = ttk.Button(seccion_botones_admin_usuarios, text='Modificar usuario',
            command=self.modificar_usuario, width=16)
        boton_modificar_usuario.grid(row=0, column=3, padx=5, pady=5)

        # Botón para eliminar usuario
        boton_eliminar_usuario = ttk.Button(seccion_botones_admin_usuarios, text='Eliminar usuario',
                                            command=self.eliminar_usuario, width=16)
        boton_eliminar_usuario.grid(row=0, column=4, padx=5, pady=5)

        # Tabla de usuarios
        self.seccion_tabla = ttk.LabelFrame(self.panel_crud, text='')
        self.seccion_tabla.grid(row=2, column=0, sticky='NSEW', padx=5, pady=5)

        # Configuraciones de la tabla
        self.panel_crud.columnconfigure(0, weight=1)
        self.panel_crud.rowconfigure(2, weight=1)
        self.seccion_tabla.columnconfigure(0, weight=1)
        self.seccion_tabla.rowconfigure(0, weight=1)

        columnas = ['ID', 'Nombre de usuario', 'Nombre completo', 'Fecha Alta', 'Telefono', 'Telefono de Emergencia', 'Sucursal']

        # Crear un Treeview con una columna por cada campo de la tabla
        self.tabla = ttk.Treeview(self.seccion_tabla, columns=columnas)
        self.tabla.config(height=8)
        self.tabla.grid(row=0, column=0, sticky='NESW', padx=5, pady=5)

        # Define los encabezados de columna
        for i, headd in enumerate(columnas, start=1):
            self.tabla.heading(f'#{i}', text=headd)
            self.tabla.column(f'#{i}', width=100)

        self.tabla.column('#0', width=0, stretch=False)
        self.tabla.column('#1', width=25, stretch=False)
        self.tabla.column('#2', width=110, stretch=False)
        self.tabla.column('#3', width=210, stretch=False)
        self.tabla.column('#4', width=140, stretch=False)
        self.tabla.column('#5', width=100, stretch=False)
        self.tabla.column('#6', width=100, stretch=False)
        self.tabla.column('#7', width=120, stretch=False)

        # Crear un Scrollbar vertical y lo asocia con el Treeview
        scrollbar_Y = ttk.Scrollbar(self.seccion_tabla, orient='vertical', command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar_Y.set)
        scrollbar_Y.grid(row=0, column=1, sticky='NS')

        # Crear un Scrollbar horizontal y lo asocia con el Treeview
        scrollbar_X = ttk.Scrollbar(self.seccion_tabla, orient='horizontal', command=self.tabla.xview)
        self.tabla.configure(xscroll=scrollbar_X.set)
        scrollbar_X.grid(row=1, column=0, sticky='EW')

        self.tabla.grid(row=0, column=0, sticky='NESW', padx=5, pady=5, ipadx=5, ipady=5, columnspan=2, rowspan=2)

        self.seccion_tabla.grid_rowconfigure(0, weight=1, minsize=0)

        self.campo_user.focus()
        self.ver_usuarios()

    def llenar_tabla(self, registros):
        """
        Llena la tabla con los registros que cumplen con los criterios de búsqueda.

        Args:
            registros (list): Un conjunto de tuplas que representan los registros obtenidos de la base de datos.
        """
        # Limpia la tabla antes de llenarla con nuevos registros
        self.vaciar_tabla()

        if self.registros:
            for registro in registros:
                self.tabla.insert('', 'end', values=registro)

    def vaciar_tabla(self):
        """Elimina todas las filas de la tabla."""
        self.tabla.delete(*self.tabla.get_children())

    def consultar_usuario(self, id):
        """
        Consulta un usuario en la base de datos.

        Args:
            id (int): El ID del usuario a consultar.

        Returns:
            bool: True si el usuario existe, False en caso contrario.
        """
        self.registros = self.controlador_crud_usuarios.consultar_usuario(id=id)
        if self.registros:
            return True
        else:
            return False

    def ver_usuarios(self):
        """Muestra todos los usuarios en la tabla."""
        self.registros = self.controlador_crud_usuarios.ver_usuarios()
        self.llenar_tabla(self.registros)
        self.campo_user.focus()

    def eliminar_usuario(self):
        """Elimina un usuario de la base de datos."""
        id = self.ID_usuario.get()

        if id == "":
            mb.showerror("Error", "Ingresa un ID")
            self.campo_user.focus()
            return None

        pregunta = mb.askokcancel("Alerta", f"¿Estás seguro de eliminar al usuario con folio: {id}?")
        if pregunta:
            if self.consultar_usuario(id):
                self.controlador_crud_usuarios.eliminar_usuario(id)
                self.ver_usuarios()
                self.ID_usuario.set("")
                self.campo_user.focus()
            else:
                mb.showwarning("Error", f"No existe usuario con folio {id} o ya ha sido eliminado")
                self.ID_usuario.set("")
                self.ver_usuarios()
                self.campo_user.focus()
        else:
            self.ID_usuario.set("")
        self.campo_user.focus()

    def modificar_usuario(self):
        """Modifica un usuario en la base de datos."""
        id = self.ID_usuario.get()

        if id == "":
            mb.showerror("Error", "Ingresa un ID")
            self.campo_user.focus()
            return None

        pregunta = mb.askokcancel("Alerta", f"¿Estás seguro de modificar al usuario con folio: {id}?")

        if pregunta:
            if self.consultar_usuario(id):
                usuario_informacion = self.controlador_crud_usuarios.consultar_usuario(id=id)
                View_modificar_usuarios(usuario_informacion=usuario_informacion, id=id)
                self.ver_usuarios()
                self.ID_usuario.set("")
                self.campo_user.focus()
            else:
                mb.showwarning("Error", f"No existe usuario con folio {id}")
                self.ID_usuario.set("")
                self.ver_usuarios()
                self.campo_user.focus()
        else:
            self.ID_usuario.set("")
            self.campo_user.focus()

    def desconectar(self):
        """Cierra la ventana y detiene el hilo en el que se ejecuta."""
        self.panel_crud.quit()
        self.panel_crud.destroy()

# ViewCRUDUsuarios()
