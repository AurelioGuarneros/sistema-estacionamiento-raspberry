import os
import pymysql

class Operacion:
    def __init__(self):
        # La base de datos central esta en la Raspberry TPV.
        self.host = os.environ.get("ESTACIONAMIENTO_DB_HOST", "169.254.70.94")
        self.user = os.environ.get("ESTACIONAMIENTO_DB_USER", "")
        self.password = os.environ.get("ESTACIONAMIENTO_DB_PASSWORD", "")
        self.database = os.environ.get("ESTACIONAMIENTO_DB_NAME", "Parqueadero1")
    def abrir(self):
        conexion=pymysql.connect(host=self.host,
                                 user=self.user,
                                 passwd=self.password,
                                 database=self.database,
                                 port=3306,
                                 connect_timeout=5)

        return conexion

    def consulta(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="select Entrada, Salida, Placas from Entradas where id=%s"
       #sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def ActualizaSalida(self,estatus):
        cone=self.abrir()
        cursor=cone.cursor()
        # La condición se evalúa dentro de MariaDB para que el mismo boleto
        # solamente pueda autorizar una salida, incluso ante lecturas rápidas.
        estado, folio = estatus
        sql="""UPDATE Entradas
               SET Placas=%s
               WHERE id=%s AND COALESCE(Placas, '') <> %s"""
        cursor.execute(sql, (estado, folio, estado))
        actualizados=cursor.rowcount
        cone.commit()
        cone.close()
        return actualizados

 ####PENSIONADOS###### Actualizo el 16Julio22
    def ValidarPen(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT id_cliente FROM Pensionados WHERE Num_tarjeta=%s"
        cursor.execute(sql,datos)
        cone.close()
        return cursor.fetchall()
      
    def ConsultaPensionado(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT Fecha_vigencia, Estatus, Vigencia, Tolerancia FROM Pensionados where id_cliente=%s"
        cursor.execute(sql,datos)
        cone.close()
        return cursor.fetchall()

    def UpdMovsPens(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="UPDATE MovimientosPens SET Salida=%s, TiempoTotal =%s, Estatus=%s WHERE idcliente=%s and Salida is null"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def UpdPens2(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="UPDATE Pensionados SET Estatus=%s WHERE id_cliente=%s"
        #sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()


    def consultar_UpdMovsPens(self, datos):
        cone=self.abrir()
        cursor=cone.cursor()
        sql="SELECT	Entrada FROM MovimientosPens WHERE idcliente=%s and Salida is null"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()
        return cursor.fetchall()[0][0]

    def RegistrarSalidaPensionado(self, id_cliente, salida):
        """Registra una sola salida y devuelve el tiempo de estancia.

        Todo se realiza en una transaccion. Una segunda lectura no encuentra
        un movimiento abierto y, por lo tanto, no vuelve a autorizar la barrera.
        """
        cone=self.abrir()
        try:
            cursor=cone.cursor()
            sql_entrada="""SELECT Id_movs, Entrada
                           FROM MovimientosPens
                           WHERE idcliente=%s AND Salida IS NULL
                           ORDER BY Id_movs DESC
                           LIMIT 1 FOR UPDATE"""
            cursor.execute(sql_entrada, (id_cliente,))
            movimiento=cursor.fetchone()
            if movimiento is None or movimiento[1] is None:
                cone.rollback()
                return None

            id_movimiento, entrada = movimiento
            tiempo_total=str(salida-entrada).split('.')[0]

            sql_pensionado="""UPDATE Pensionados
                              SET Estatus=%s
                              WHERE id_cliente=%s AND Estatus=%s"""
            cursor.execute(
                sql_pensionado,
                ('Afuera', id_cliente, 'Adentro')
            )
            if cursor.rowcount != 1:
                cone.rollback()
                return None

            sql_movimiento="""UPDATE MovimientosPens
                              SET Salida=%s, TiempoTotal=%s, Estatus=%s
                              WHERE Id_movs=%s AND Salida IS NULL"""
            cursor.execute(
                sql_movimiento,
                (salida, tiempo_total, 'Afuera', id_movimiento)
            )
            if cursor.rowcount != 1:
                cone.rollback()
                return None

            cone.commit()
            return tiempo_total
        except Exception:
            cone.rollback()
            raise
        finally:
            cone.close()
