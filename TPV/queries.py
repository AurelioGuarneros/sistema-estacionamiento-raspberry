import re
from pymysql import err
from tkinter import messagebox
from operacion_tpv import Operacion
import traceback

class Usuarios:
    """
    Clase para interactuar con la tabla de Usuarios en la base de datos.

    Esta clase proporciona métodos para agregar, consultar, ver, eliminar y actualizar usuarios en la tabla de Usuarios.
    """
    def __init__ (self):
        """
        Inicializa la clase Usuarios.

        Esta función inicializa la clase de la base de datos.
        """
        self.operacion = Operacion()

    def execute_query(self, query: str):
        """
        Ejecuta una consulta en la base de datos.

        :param query (str): La consulta SQL a ejecutar.

        :raises pymysql.err.OperationalError: Si la conexión se pierde.
        :raises err.ProgrammingError: Si la tabla no existe.

        :return:
            - result (list): Una lista con los resultados de la consulta.
        """
        try:
            # Inicia la conexion con la base de datos
            connection = self.operacion.abrir()

            # Crea un objeto cursor para ejecutar la consulta
            cursor = connection.cursor()

            # Se ejecuta la consulta
            cursor.execute(query)

            # Obtiene los resultados de la consulta
            result = cursor.fetchall()

            # Confirma los cambios en la base de datos
            connection.commit()

            # Cierra el cursor
            cursor.close()

            # Cierra la conexion cn la base de datos
            connection.close()

            # Retorna los resultados de la consulta
            return result

        except err.OperationalError as e:
            print(e)
            traceback.print_exc()
            if "10054" in str(e):
                print(e)
                messagebox.showwarning("Error", "Se ha perdido la conexión con el servidor.\nEl programa se cerrará, posterior a eso inicie nuevamente sesión\n\nEn caso de que el error persista contacte a un administrador.")

        except err.ProgrammingError as error:
            traceback.print_exc()
            print(error)
            # Aquí se ejecuta el código en caso de que se genere la excepción ProgrammingError
            error_message = str(error)
            match = re.search(r"\((\d+),", error_message)
            error_number = int(match.group(1))
            if error_number == 1146:
                print(error)
                messagebox.showwarning("Error", f"Error: La tabla no existe.\n Es probable que la conexión actual no cuente con la tabla a la que intenta acceder, de ser caso contrario contacte con un administrador.")
                return None

        except Exception as e:
            print(e)
            traceback.print_exc()
            messagebox.showwarning("Error", f"Error al realizar la consulta, por favor contacte con un administrador y muestre el siguiente error:\n Error: {str(e)} ")
            return None


    def agregar_usuarios(self, datos):
        """
        Agrega un nuevo usuario a la base de datos.

        :param datos: (tuple) Una tupla con los datos del nuevo usuario a agregar.

        Esta función agrega un nuevo usuario a la base de datos con los datos proporcionados.
        """
        datos = tuple(datos)

        query = f"INSERT INTO Usuarios (Usuario, Contrasena, Nom_usuario, Fecha_alta, Telefono1, TelefonoEmer, Sucursal) VALUES {datos};"

        # Se ejecuta la consulta
        self.execute_query(query)

    def consultar_usuario(self, id):
        """
        Consulta un usuario por su identificador en la base de datos.

        :param id: (int) El identificador del usuario a consultar.

        :return: (list) Una lista con los datos del usuario consultado.
        """
        query = f"SELECT Usuario, Contrasena, Nom_usuario, Telefono1, TelefonoEmer, Sucursal FROM Usuarios WHERE Id_usuario = {id}"

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado

    def ver_usuarios(self):
        """
        Obtiene y muestra todos los usuarios en la tabla.

        :return: (list) Una lista con los datos de todos los usuarios.
        """

        query = f"SELECT Id_usuario, Usuario, Nom_usuario, Fecha_alta, Telefono1, TelefonoEmer, Sucursal FROM Usuarios"

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado

    def eliminar_usuario(self, id):
        """
        Elimina un usuario de la base de datos.

        :param id: (int) El identificador del usuario a eliminar.

        Esta función elimina un usuario de la base de datos con el identificador proporcionado.
        """

        query = f"DELETE FROM Usuarios WHERE Id_usuario = {id}"

        # Se ejecuta la consulta
        self.execute_query(query)

    def actualizar_usuarios(self, datos, id):
        """
        Actualiza los datos de un usuario existente en la base de datos.

        :param datos: (tuple) Una tupla con los nuevos datos del usuario a actualizar.
        :param id: (int) El identificador del usuario a actualizar.

        Esta función actualiza los datos de un usuario existente en la base de datos.
        """
        datos = tuple(datos)

        query = f"UPDATE Usuarios SET Usuario = '{datos[0]}', Contrasena = '{datos[1]}', Nom_usuario = '{datos[2]}',  Telefono1 = '{datos[3]}', TelefonoEmer = '{datos[4]}', Sucursal = '{datos[5]}' WHERE Id_usuario = '{id}';"

        # Se ejecuta la consulta
        self.execute_query(query)

class Pensionados(Usuarios):
    """
    Clase para interactuar con la tabla de Pensionados en la base de datos.

    Esta clase hereda de la clase Usuarios y proporciona métodos adicionales para agregar, consultar, ver, eliminar y actualizar pensionados en la tabla de Pensionados.
    """
    def agregar_pensionados(self, datos):
        """
        Agrega un nuevo pensionado a la base de datos.

        :param datos: (tuple) Una tupla con los datos del nuevo pensionado a agregar.

        Esta función agrega un nuevo pensionado a la base de datos con los datos proporcionados.
        """
        datos = tuple(datos)

        query = f"INSERT INTO Pensionados (Num_tarjeta, Nom_cliente, Apell1_cliente, Apell2_cliente, Fecha_alta, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle_num, Placas, Modelo_auto, Color_auto, Monto, Cortesia, Tolerancia, Vigencia) VALUES {datos};"

        # Se ejecuta la consulta
        self.execute_query(query)

    def consultar_pensionado(self, Num_tarjeta):
        """
        Consulta un pensionado por su número de tarjeta en la base de datos.

        :param Num_tarjeta: (int) El número de tarjeta del pensionado a consultar.

        :return: (list) Una lista con los datos del pensionado consultado.
        """
        query = f"SELECT Num_tarjeta, Nom_cliente, Apell1_cliente, Apell2_cliente, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle_num, Placas, Modelo_auto, Color_auto, Monto, Cortesia, Tolerancia, Fecha_vigencia, Vigencia FROM Pensionados WHERE Num_tarjeta = '{Num_tarjeta}'"

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado

    def ver_pensionados(self):
        """
        Obtiene y muestra todos los pensionados en la tabla.

        :return: (list) Una lista con los datos de todos los pensionados.
        """
        query = f"SELECT Num_tarjeta, Cortesia, Nom_cliente, Estatus, Fecha_vigencia, Tolerancia, Id_cliente, Vigencia FROM Pensionados ORDER BY Id_cliente DESC"

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado

    def eliminar_pensinado(self, id):
        """
        Elimina un pensionado de la base de datos.

        :param id: (int) El identificador del pensionado a eliminar.

        Esta función elimina un pensionado de la base de datos con el identificador proporcionado.
        """
        pass

    def actualizar_pensionado(self, datos_pensionado, Num_tarjeta):
        """
        Actualiza los datos de un pensionado existente en la base de datos.

        :param datos_pensionado: (tuple) Una tupla con los nuevos datos del pensionado a actualizar.
        :param Num_tarjeta: (int) El número de tarjeta del pensionado a actualizar.

        Esta función actualiza los datos de un pensionado existente en la base de datos.
        """
        datos_pensionado = tuple(datos_pensionado)
        vigencia = datos_pensionado[17]
        if vigencia == None: vigencia = 'Null'
        else: vigencia = f"""'{vigencia}'"""

        query =f"""UPDATE Pensionados SET Num_tarjeta = '{datos_pensionado[0]}', Nom_cliente = '{datos_pensionado[1]}', Apell1_cliente = '{datos_pensionado[2]}', Apell2_cliente = '{datos_pensionado[3]}', Telefono1 = '{datos_pensionado[4]}', Telefono2 = '{datos_pensionado[5]}', Ciudad = '{datos_pensionado[6]}', Colonia = '{datos_pensionado[7]}', CP = '{datos_pensionado[8]}', Calle_num = '{datos_pensionado[9]}', Placas = '{datos_pensionado[10]}', Modelo_auto = '{datos_pensionado[11]}', Color_auto = '{datos_pensionado[12]}', Monto = '{datos_pensionado[13]}', Cortesia = '{datos_pensionado[14]}', Tolerancia = {datos_pensionado[15]}, Ult_Cambio = '{datos_pensionado[16]}', Fecha_vigencia = {vigencia}, Vigencia = '{datos_pensionado[18]}' WHERE Num_tarjeta = '{Num_tarjeta}';"""

        # Se ejecuta la consulta
        self.execute_query(query)

    def desactivar_tarjetas_expiradas(self, hoy):
        """
        Desactiva las tarjetas de pensionados cuya vigencia ha expirado.

        :param hoy: (datetime) La fecha y hora actuales.

        Esta función desactiva las tarjetas de pensionados cuya vigencia ha expirado, asignándoles el estado "InactivaPerm".
        """
        query =f"""UPDATE Pensionados SET Vigencia = 'InactivaPerm', Fecha_vigencia = NULL, Estatus = 'Afuera', Ult_Cambio = '{hoy}' WHERE Fecha_vigencia < DATE_ADD(CURDATE(), INTERVAL -2 MONTH);"""

        # Se ejecuta la consulta
        self.execute_query(query)

    def ver_tarjetas_expiradas(self):
        """
        Obtiene y muestra todas las tarjetas de pensionados cuya vigencia ha expirado.

        :return: (list) Una lista con los números de tarjeta y fechas de vigencia de las tarjetas expiradas.
        """
        query =f"""SELECT Num_tarjeta, Fecha_vigencia FROM Pensionados WHERE Fecha_vigencia < DATE_ADD(CURDATE(), INTERVAL -2 MONTH) ORDER BY Id_cliente DESC;"""

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado


    def get_Entradas_Totales_Pensionados(self, folio):

        query =f"""SELECT COUNT(*) AS Entradas_Totales_Pensionados FROM MovimientosPens p INNER JOIN Cortes c ON p.Entrada BETWEEN c.FechaIni AND c.FechaFin WHERE c.Folio = {folio};"""

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado[0][0]

    def get_Salidas_Pensionados(self, corte):

        query =f"""SELECT COUNT(*) AS Salidas_Pensionados FROM MovimientosPens WHERE Estatus = "Afuera" AND Salida BETWEEN (SELECT FechaIni from Cortes WHERE Folio = {corte}) AND (SELECT FechaFin from Cortes WHERE Folio = {corte}) AND Corte = {corte};"""

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado[0][0]

    def get_Quedados_Pensionados(self):

        query =f"""SELECT COUNT(*) AS Quedados_Pensionados FROM MovimientosPens WHERE Estatus = "Adentro" AND Corte = 0;"""   

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado[0][0]

    def Actualizar_Entradas_Pension(self, corte):

        query = f"update MovimientosPens set Corte = {corte} where Corte = 0 AND Salida BETWEEN (SELECT FechaIni from Cortes WHERE Folio = {corte}) AND (SELECT FechaFin from Cortes WHERE Folio = {corte});"
        self.execute_query(query)

    def get_Anteriores_Pensionados(self, corte):
        query =f"""SELECT COALESCE(Pensionados_Quedados, 0) FROM Cortes WHERE Folio = {corte};"""   

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        # En el primer corte no existe un folio anterior (folio 0).
        # En ese caso no hay pensionados heredados del turno previo.
        return resultado[0][0] if resultado else 0

    def get_QR_id(self):
        query =f"""SELECT COALESCE(MAX(Id_cliente), 0) FROM Pensionados;"""

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        ID = resultado[0][0] + 1

        return ID
