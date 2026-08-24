"""Prueba la conexion de Entrada (192.168.0.150) con la BD del TPV."""

from operacion_entrada import Operacion


def main():
    db = Operacion()
    conexion = db.abrir()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT DATABASE(), @@hostname, NOW()")
            base, servidor, fecha = cursor.fetchone()
        print("CONEXION CORRECTA")
        print(f"Punto: Entrada 192.168.0.150")
        print(f"Servidor TPV: {db.host}:3306 ({servidor})")
        print(f"Base de datos: {base}")
        print(f"Fecha del servidor: {fecha}")
    finally:
        conexion.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("ERROR DE CONEXION")
        print(error)
        raise SystemExit(1)
