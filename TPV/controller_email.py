import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from escpos.printer import Usb
from zipfile import ZipFile, ZIP_DEFLATED
from subprocess import run, CalledProcessError
from os import path, getcwd, remove, listdir, makedirs
from requests import get
from requests.exceptions import RequestException
from operacion_tpv import Operacion

dir_cortes = "Cortes"

# Nombre del estacionamiento
nombre_estacionamiento = 'Hidalgo 401'

# Datos de acceso a la cuenta de correo
username = os.environ.get('ESTACIONAMIENTO_SMTP_USER', '')
password = os.environ.get('ESTACIONAMIENTO_SMTP_PASSWORD', '')

# Correos para enviar la informacion
EMAIL_send_database = os.environ.get('ESTACIONAMIENTO_EMAIL_DATABASE', '')
EMAIL_send_corte = os.environ.get('ESTACIONAMIENTO_EMAIL_CORTE', '')
EMAIL_notification = os.environ.get('ESTACIONAMIENTO_EMAIL_NOTIFICACION', '')


class ToolsEmail:
    """Clase que proporciona herramientas relacionadas con el correo electronico y archivos."""

    def __init__(self):
        """Constructor de la clase"""
        self.DB = Operacion()

    def check_internet_connection(self, url: str = "http://www.google.com", timeout: int = 10) -> bool:
        """Comprueba si hay una conexion activa a Internet mediante una peticion HTTP a la URL dada.

        Args:
            url (str, optional): La URL a la que se realizará la peticion. Por defecto es "http://www.google.com".
            timeout (int, optional): El tiempo máximo en segundos para esperar la respuesta. Por defecto es 5.

        Returns:
            bool: True si hay una conexion activa a Internet, False si no se puede establecer la conexion.
        """
        try:
            response = get(url, timeout=timeout)
            # Lanza una excepcion si la respuesta HTTP no es exitosa
            response.raise_for_status()
            print("Conexion a Internet activa.")
            return True

        except RequestException:
            print("No se pudo establecer conexion a Internet.")
            return False

    def compress_to_zip(self, source: str, output_filename: str = None, is_dir: bool = False, rename:bool = True) -> str or None:
        """Comprime un archivo o directorio en un archivo ZIP.

        Args:
            source (str): Ruta al archivo o directorio que se comprimirá.
            output_filename (str): Nombre del archivo ZIP de salida. Si no se proporciona, se usará el nombre del archivo fuente con extensión ".zip".

        Returns:
            str or None: Ruta absoluta del archivo ZIP si la compresión es exitosa, None si hay algún error.
        """
        try:
            # Si no se proporciona un nombre de archivo de salida, usamos el nombre del archivo fuente con extensión ".zip"
            output_filename = output_filename or f"{source}.zip"

            if is_dir:
                position_number = len(f"{nombre_estacionamiento}_Corte_N°_")
                files = listdir(source)
                for id, file in enumerate(files):
                    _, ext = path.splitext(file)
                    if ext.lower() != ".txt":
                        files.remove(file)

                if rename:
                    if len(files) == 0:
                        return None

                    first_number = files[0][position_number:-4]
                    last_number = files[len(files)-1][position_number:-4]

                    numbers = f"Cortes {first_number} a {last_number}" if first_number != last_number else f"Corte {first_number}"
                    output_filename = f"{source[:-6]+numbers}.zip".replace(" ", "_")

            with ZipFile(output_filename, 'w', ZIP_DEFLATED) as zipf:
                if is_dir:
                    for file in files:
                        file_path = path.join(source, file)
                        # Agregar archivos del directorio al ZIP con su ruta relativa
                        zipf.write(file_path, arcname=path.relpath(file_path, source))
                else:
                    # Agregar archivo al ZIP con su nombre base
                    arcname = path.basename(source)
                    zipf.write(source, arcname)

            print("Archivo comprimido correctamente")
            return path.abspath(output_filename)

        except Exception as e:
            print(f'Error al comprimir el archivo: {e}')
            return None

    def is_file_empty(self, file_path) -> bool:
        """Verifica si un archivo está vacío o no.

        Args:
            file_path (str): La ruta del archivo que se va a verificar.

        Returns:
            bool: True si el archivo está vacío, False si no lo está.
        """
        try:
            # Obtiene el tamaño del archivo en bytes y verifica si es cero
            return True if path.getsize(file_path) == 0 else False

        except Exception as e:
            # Maneja cualquier error que pueda ocurrir
            print(f"Error al verificar el archivo: {e}")
            return False

    def remove_file(self, path_file: str) -> None:
        """
        Elimina un archivo del sistema.

        Esta funcion toma la ruta de un archivo como entrada y trata de eliminarlo del sistema de archivos.

        Args:
            path_file (str): La ruta del archivo que se va a eliminar.

        """
        try:
            # Intenta eliminar el archivo
            remove(path_file)
            print(f"Archivo [{path_file}] fue eliminado exitosamente.")
        except Exception as e:
            # Maneja cualquier error que pueda ocurrir al intentar eliminar el archivo
            print(f"No se pudo eliminar el archivo [{path_file}]: {e}")


    def get_DB(self, backup_path: str = '/ruta/de/respaldo/Parqueadero1.sql') -> str or None:
        """Genera un respaldo de la base de datos utilizando el comando mysqldump.

        Args:
            backup_path (str, optional): La ruta donde se guardará el archivo de respaldo. Por defecto es '/ruta/de/respaldo/Parqueadero1.sql'.

        Returns:
            str or None: La ruta del archivo de respaldo si se crea exitosamente, None si ocurre un error.
        """
        try:
            # Configuracion de la base de datos
            host = self.DB.host
            user = self.DB.user
            password = self.DB.password
            database = self.DB.database

            # Comando mysqldump (dependiendo del sistema operativo)
            command = f"mysqldump -h {host} -u {user} -p{password} {database} > {backup_path}"
            # command = f"cd C:/xampp/mysql/bin && mysqldump -h {host} -u {user} -p{password} {database} > {backup_path}"

            run(command, shell=True)

            if path.exists(backup_path) and not self.is_file_empty(backup_path):
                print("Base de datos respaldada exitosamente.")
                backup_path = path.abspath(backup_path)
                return backup_path
            else:
                print("El archivo de respaldo no se creo correctamente.")
                self.remove_file(backup_path)
                return None

        except CalledProcessError:
            print("Error al crear el respaldo.")
            self.remove_file(backup_path)
            return None

class SendEmail:
    """Clase que permite enviar correos electronicos con archivos adjuntos."""

    def __init__(self, username: str, password: str, smtp_server: str = "smtp.pasesa.com.mx", smtp_port: int = 1025) -> None:
        """Inicializa una instancia de la clase SendEmail para enviar correos electronicos con archivos adjuntos.

        Args:
            username (str): El nombre de usuario para la cuenta de correo electronico.
            password (str): La contraseña para la cuenta de correo electronico.
            smtp_server (str, opcional): El servidor SMTP para el envío de correos. Por defecto es "smtp.pasesa.com.mx".
            smtp_port (int, opcional): El puerto del servidor SMTP. Por defecto es 1025.
        """
        self.username = username
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

        self.tools = ToolsEmail()

    def send_mail(self, to_email: str, subject: str, message: str, zip_file: str) -> bool:
        """Envía un correo electronico con un archivo adjunto.

        Args:
            to_email (str): La direccion de correo electronico del destinatario.
            subject (str): El asunto del correo electronico.
            message (str): El contenido del correo electronico.
            zip_file (str): Ruta al archivo que se adjuntará al correo.
        Returns:
            bool: True si el correo se envía exitosamente, False si hay algún error.
        """
        from_email = self.username

        # Verificar la conexion a Internet antes de intentar enviar el correo
        if not self.tools.check_internet_connection():
            return False

        try:
            # Crea la estructura del correo
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            # Adjuntar el archivo al correo
            with open(zip_file, 'rb') as f:
                attached_file = MIMEApplication(f.read(), _subtype="zip")
                filename = path.basename(zip_file)
                print(filename)
                attached_file.add_header('content-disposition', 'attachment', filename=filename)
                msg.attach(attached_file)

            # Conectar al servidor SMTP y enviar el correo
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                # Iniciar la conexion segura TLS
                server.starttls()
                # Inicio de sesion
                server.login(self.username, self.password)
                # Enviar correo
                server.sendmail(from_email, to_email, msg.as_string())
                # Terminar la sesion
                server.quit()

            print('Correo enviado exitosamente')
            return True

        except Exception as e:
            print(e)
            return False

# Inicializar herramientas de correo electronico y envío
tools = ToolsEmail()

def send_database() -> str:
    """
    Envía el corte por correo electronico.

    Returns:
        str: Mensaje informativo sobre el resultado del envío del correo.
    """

    email_database = SendEmail(
        username=username, 
        password=password)

    # Generar ruta y obtener el archivo de respaldo de la base de datos
    path_db = getcwd() + f'/db_{nombre_estacionamiento.replace(" ", "_")}.sql'
    db_file = tools.get_DB(path_db)

    if db_file is None:
        return "Error: No se pudo generar el respaldo de la base de datos\n"

    zip_file = tools.compress_to_zip(db_file)
    tools.remove_file(db_file)

    # Crear el asunto y mensaje del correo
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"[{nombre_estacionamiento}][{hora}] Envio de Base de datos"
    message = f"Base de datos del estacionamiento: {nombre_estacionamiento}."

    # Enviar el correo y manejar el resultado
    if email_database.send_mail(to_email=EMAIL_send_database, subject=subject, message=message, zip_file=zip_file):
        tools.remove_file(zip_file)
        return "Base de datos enviada exitosamente\n"

    tools.remove_file(zip_file)
    return "Error: No se pudo enviar la base de datos\n"

def send_corte() -> str:
    """
    Envía la base de datos por correo electronico.

    Returns:
        str: Mensaje informativo sobre el resultado del envío del correo.
    """
    dir_path = path.abspath(dir_cortes)
    makedirs(dir_path, exist_ok=True)
    files = listdir(dir_path)
    if len(files) == 0: return "No hay cortes para enviar\n"


    # Inicializar herramientas de correo electronico y envío
    email_corte = SendEmail(
        username=username, 
        password=password)

    zip_file = tools.compress_to_zip(source=dir_path, is_dir=True)

    if zip_file is None:
        return "Error: No se pudo enviar el corte\n"

    # Crear el asunto y mensaje del correo
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"[{nombre_estacionamiento}]-[{hora}] Envio de {path.basename(zip_file).replace('_', ' ')[:-4]}"
    message = f"Corte del estacionamiento: {nombre_estacionamiento}."

    # Enviar el correo y manejar el resultado
    if email_corte.send_mail(to_email=EMAIL_send_corte, subject=subject, message=message, zip_file=zip_file):
        tools.remove_file(zip_file)

        for id, file in enumerate(files):
            file_path = path.join(dir_path, file)
            _, ext = path.splitext(file)
            if ext.lower() == ".txt":
                tools.remove_file(file_path)

        return "Corte enviado exitosamente\n"

    tools.remove_file(zip_file)
    return "Error: No se pudo enviar el corte\n"

def send_other_corte():
    """
    Envía la base de datos por correo electronico.

    Returns:
        str: Mensaje informativo sobre el resultado del envío del correo.
    """
    dir_path = path.abspath("Reimpresion_Cortes/")
    makedirs(dir_path, exist_ok=True)
    files = listdir(dir_path)
    if len(files) == 0: return

    # Inicializar herramientas de correo electronico y envío
    email_corte = SendEmail(
        username=username, 
        password=password)

    zip_file = tools.compress_to_zip(source=dir_path, is_dir=True, rename=False)

    # Crear el asunto y mensaje del correo
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"[{nombre_estacionamiento}]-[{hora}] Notificacion de reimpresion de corte"
    message = f"Notificacion de reimpresion de corte del estacionamiento: {nombre_estacionamiento}."

    # Enviar el correo y manejar el resultado
    email_corte.send_mail(to_email=EMAIL_notification, subject=subject, message=message, zip_file=zip_file)

    tools.remove_file(zip_file)


def main() -> None:
    """
    Funcion principal del programa para enviar la base de datos por correo electronico y mostrar el resultado.
    """
    try: 
        # Ejecutar la funcion para enviar los correos electronicos
        message_send_database = send_database()
        message_send_corte = send_corte()

        # Instanciar el objeto Usb para imprimir el resultado
        printer = Usb(0x04b8, 0x0e15, 0)

        # Alinea al centro el texto
        printer.set(align = "center")

        # Imprimir separadores y mensaje de resultado en la consola
        printer.text("-" * 30 + "\n")
        printer.text(f"{message_send_database}\n")
        printer.text(f"{message_send_corte}\n")
        printer.text("-" * 30 + "\n")
        printer.cut()
        printer.close()

        # Imprimir el mensaje en la consola
        print(message_send_database)
        print(message_send_corte)
    except Exception as e:
        print(e)

