#!/usr/bin/env python3
"""Núcleo de simulación del estacionamiento, sin GPIO ni impresoras USB."""

from __future__ import annotations

import os
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pymysql
import qrcode


TABLA_CIFRADO = {
    "0": "5", "1": "3", "2": "9", "3": "1", "4": "7",
    "5": "0", "6": "8", "7": "4", "8": "6", "9": "2",
}
TABLA_DESCIFRADO = {valor: clave for clave, valor in TABLA_CIFRADO.items()}
PROMOCION_BA = "BA BODEGA AURRERA 114254"
TOLERANCIA_SALIDA_MINUTOS = 15


class ErrorSimulacion(RuntimeError):
    """Error esperado que puede mostrarse directamente al operador."""


def cargar_configuracion() -> None:
    """Carga config.env sin ejecutar su contenido como órdenes de shell."""
    ruta = os.environ.get("ESTACIONAMIENTO_CONFIG")
    if not ruta:
        return
    archivo = Path(ruta)
    if not archivo.is_file():
        raise ErrorSimulacion(f"No existe el archivo de configuración: {archivo}")
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        os.environ[clave.strip()] = valor


def cifrar_folio(folio: int, seguridad: Optional[int] = None) -> str:
    """Replica el formato corto que imprime actualmente Entrada."""
    if int(folio) < 1:
        raise ErrorSimulacion("El folio debe ser mayor que cero.")
    seguridad = seguridad if seguridad is not None else random.randint(10000, 99999)
    texto = f"{int(folio)}{int(seguridad):05d}"
    return "".join(TABLA_CIFRADO[d] for d in texto)


def descifrar_folio(codigo: str) -> int:
    """Replica el descifrado de TPV y rechaza un folio escrito sin cifrar."""
    codigo = codigo.strip()
    if len(codigo) <= 5 or not codigo.isdigit():
        raise ErrorSimulacion("El QR de entrada no tiene un formato válido.")
    try:
        texto = "".join(TABLA_DESCIFRADO[d] for d in codigo)
        folio = texto[:-5]
        if not folio:
            raise ValueError
        return int(folio)
    except (KeyError, ValueError) as error:
        raise ErrorSimulacion("No fue posible descifrar el folio de entrada.") from error


def crear_codigo_salida(fecha_entrada: datetime, folio: int) -> str:
    """Replica el QR que imprime la TPV para presentarlo en Salida."""
    return fecha_entrada.strftime("%Y-%m-%d %H:%M:%S") + str(int(folio))


def leer_codigo_salida(codigo: str) -> tuple[datetime, int]:
    codigo = codigo.strip()
    if len(codigo) <= 19:
        raise ErrorSimulacion("El QR de salida está incompleto.")
    try:
        fecha = datetime.strptime(codigo[:19], "%Y-%m-%d %H:%M:%S")
        folio = int(codigo[19:])
    except ValueError as error:
        raise ErrorSimulacion("El QR de salida no tiene un formato válido.") from error
    return fecha, folio


def normalizar_promocion(codigo: str) -> str:
    texto = " ".join((codigo or "").upper().split())
    if not texto:
        return "Normal"
    if texto == PROMOCION_BA or texto.startswith("BA BODEGA AURRERA"):
        return "BA BODEGA AURRERA"
    raise ErrorSimulacion("Promoción no reconocida; no se modificó el boleto.")


def calcular_tarifa(minutos_totales: int, tarifa: str = "Normal") -> int:
    """Tarifa Hidalgo 401: público $10/h y Bodega Aurrera según tabla."""
    minutos_totales = max(0, int(minutos_totales))
    if minutos_totales > 24 * 60:
        raise ErrorSimulacion("La tabla vigente sólo define importes hasta 24 horas.")
    if tarifa == "BA BODEGA AURRERA" and minutos_totales <= 120:
        return 5
    horas_cobradas = max(1, (minutos_totales + 59) // 60)
    if tarifa == "BA BODEGA AURRERA":
        return 5 + (horas_cobradas - 2) * 10
    return horas_cobradas * 10


def texto_permanencia(inicio: datetime, fin: datetime) -> str:
    segundos = max(0, int((fin - inicio).total_seconds()))
    dias, segundos = divmod(segundos, 86400)
    horas, segundos = divmod(segundos, 3600)
    minutos, segundos = divmod(segundos, 60)
    if dias:
        return f"{dias} día(s), {horas:02d}:{minutos:02d}:{segundos:02d}"
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"


def tolerancia_restante(fecha_pago: datetime, ahora: datetime) -> Optional[int]:
    """Devuelve segundos restantes; None indica salida fuera de tolerancia."""
    transcurridos = int((ahora - fecha_pago).total_seconds())
    limite = TOLERANCIA_SALIDA_MINUTOS * 60
    if transcurridos < 0 or transcurridos > limite:
        return None
    return limite - transcurridos


def generar_qr(codigo: str, ruta: Path) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    qrcode.make(codigo).save(ruta)
    return ruta


@dataclass
class ResultadoEntrada:
    folio: int
    fecha: datetime
    codigo: str
    qr: Path
    boleto: Path


@dataclass
class ResultadoCobro:
    folio: int
    entrada: datetime
    pago: datetime
    permanencia: str
    tarifa: str
    importe: int
    codigo_salida: str
    qr: Path
    comprobante: Path


@dataclass
class ResultadoCotizacion:
    folio: int
    entrada: datetime
    consulta: datetime
    permanencia: str
    tarifa: str
    importe_normal: int
    descuento: int
    importe_final: int


@dataclass
class ResultadoSalida:
    folio: int
    autorizado: bool
    mensaje: str
    segundos_restantes: int = 0


@dataclass
class ResumenCorte:
    inicio: datetime
    fin: datetime
    boletos: int
    importe: float
    folios: tuple[int, ...]
    pendientes_cobro: int
    pensionados_adentro: int


@dataclass
class ResultadoCorte:
    folio: int
    resumen: ResumenCorte
    comprobante: Path
    correo_simulado: Path


def construir_cotizacion(
    folio: int, entrada: datetime, promocion: str, fecha_consulta: datetime
) -> dict:
    """Calcula el precio sin modificar el boleto en la base de datos."""
    minutos = max(0, int((fecha_consulta - entrada).total_seconds() // 60))
    tarifa = normalizar_promocion(promocion)
    importe_normal = calcular_tarifa(minutos, "Normal")
    importe_final = calcular_tarifa(minutos, tarifa)
    return {
        "folio": int(folio),
        "entrada": entrada,
        "consulta": fecha_consulta,
        "permanencia": texto_permanencia(entrada, fecha_consulta),
        "tarifa": tarifa,
        "importe_normal": importe_normal,
        "descuento": importe_normal - importe_final,
        "importe_final": importe_final,
    }


def normalizar_tarjeta(valor: object, seleccion: object = "") -> int:
    """Acepta la lectura RFID o, si está vacía, la tarjeta seleccionada."""
    texto = str(valor or "").strip() or str(seleccion or "").strip()
    if not texto:
        raise ErrorSimulacion("Capture o seleccione una tarjeta de pensionado.")
    if not texto.isdigit():
        raise ErrorSimulacion("La tarjeta de pensionado debe contener sólo números.")
    return int(texto)


class RepositorioMariaDB:
    def __init__(self) -> None:
        cargar_configuracion()
        self.host = os.environ.get("ESTACIONAMIENTO_DB_HOST", "127.0.0.1")
        self.user = os.environ.get("ESTACIONAMIENTO_DB_USER", "")
        self.password = os.environ.get("ESTACIONAMIENTO_DB_PASSWORD", "")
        self.database = os.environ.get("ESTACIONAMIENTO_DB_NAME", "Parqueadero1_prueba")

    def abrir(self):
        return pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=3306,
            connect_timeout=5,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

    def verificar(self) -> tuple[str, str, datetime]:
        with self.abrir() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT DATABASE() base, @@hostname servidor, NOW() fecha")
                fila = cursor.fetchone()
        return fila["base"], fila["servidor"], fila["fecha"]

    def crear_entrada(self, fecha: datetime, placa: str) -> int:
        with self.abrir() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Entradas (Entrada, CorteInc, Placas) VALUES (%s, 0, %s)",
                    (fecha, placa),
                )
                folio = cursor.lastrowid
            conexion.commit()
        return int(folio)

    def listar_pendientes_cobro(self) -> list[dict]:
        """Boletos expedidos que todavía pueden cobrarse, en cualquier orden."""
        with self.abrir() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT id, Entrada, COALESCE(Placas, '') Placas "
                    "FROM Entradas WHERE Salida IS NULL "
                    "AND COALESCE(Placas, '') <> 'Afuera' ORDER BY id"
                )
                filas = cursor.fetchall()
        for fila in filas:
            # La aplicación vigente obtiene el folio de la parte cifrada y no
            # conserva los cinco dígitos de seguridad en la base de datos.
            fila["codigo_entrada"] = cifrar_folio(int(fila["id"]), 11111)
        return filas

    def listar_pendientes_salida(self) -> list[dict]:
        """Boletos pagados cuyo QR todavía no ha sido utilizado en Salida."""
        with self.abrir() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT id, Entrada, Salida, COALESCE(Placas, '') Placas "
                    "FROM Entradas WHERE Salida IS NOT NULL "
                    "AND COALESCE(Placas, '') <> 'Afuera' ORDER BY Salida, id"
                )
                filas = cursor.fetchall()
        ahora = datetime.now().replace(microsecond=0)
        for fila in filas:
            fila["codigo_salida"] = crear_codigo_salida(fila["Entrada"], int(fila["id"]))
            restantes = tolerancia_restante(fila["Salida"], ahora)
            fila["estado_tolerancia"] = (
                "VENCIDA" if restantes is None
                else f"{restantes // 60:02d}:{restantes % 60:02d}"
            )
        return filas

    def listar_pensionados(self) -> list[dict]:
        """Tarjetas disponibles para elegirlas sin depender de la última leída."""
        with self.abrir() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT Num_tarjeta, COALESCE(Nom_cliente, '') Nom_cliente, "
                    "COALESCE(Estatus, '') Estatus, Fecha_vigencia, "
                    "COALESCE(Vigencia, '') Vigencia FROM Pensionados "
                    "ORDER BY Num_tarjeta"
                )
                return cursor.fetchall()

    def cotizar(self, folio: int, promocion: str, fecha_consulta: datetime) -> dict:
        with self.abrir() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT id, Entrada, Salida, Placas FROM Entradas WHERE id=%s",
                    (folio,),
                )
                fila = cursor.fetchone()
        if fila is None:
            raise ErrorSimulacion("No existe un auto con ese boleto.")
        if fila["Salida"] is not None:
            raise ErrorSimulacion("Este boleto ya fue cobrado.")
        if fila["Placas"] == "Afuera":
            raise ErrorSimulacion("Este boleto ya fue utilizado en la salida.")
        return construir_cotizacion(folio, fila["Entrada"], promocion, fecha_consulta)

    def cobrar(self, folio: int, promocion: str, fecha_pago: datetime) -> dict:
        with self.abrir() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, Entrada, Salida, Placas FROM Entradas "
                        "WHERE id=%s FOR UPDATE",
                        (folio,),
                    )
                    fila = cursor.fetchone()
                    if fila is None:
                        raise ErrorSimulacion("No existe un auto con ese boleto.")
                    if fila["Salida"] is not None:
                        raise ErrorSimulacion("Este boleto ya fue cobrado.")
                    if fila["Placas"] == "Afuera":
                        raise ErrorSimulacion("Este boleto ya fue utilizado en la salida.")
                    entrada = fila["Entrada"]
                    cotizacion = construir_cotizacion(
                        folio, entrada, promocion, fecha_pago
                    )
                    tarifa = cotizacion["tarifa"]
                    importe = cotizacion["importe_final"]
                    permanencia = cotizacion["permanencia"]
                    qr_promo = PROMOCION_BA if tarifa != "Normal" else None
                    cursor.execute(
                        "UPDATE Entradas SET Salida=%s, TiempoTotal=%s, Importe=%s, "
                        "vobo='lmf', TarifaPreferente=%s, QRpromo=%s WHERE id=%s AND Salida IS NULL",
                        (fecha_pago, permanencia, importe, tarifa, qr_promo, folio),
                    )
                    if cursor.rowcount != 1:
                        raise ErrorSimulacion("El boleto cambió mientras se procesaba el cobro.")
                conexion.commit()
                return {
                    "entrada": entrada,
                    "pago": fecha_pago,
                    "permanencia": permanencia,
                    "tarifa": tarifa,
                    "importe": importe,
                }
            except Exception:
                conexion.rollback()
                raise

    def listar_pendientes_corte(self) -> list[dict]:
        """Cobros realizados que aún no pertenecen a ningún corte."""
        with self.abrir() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT id, Salida, COALESCE(TarifaPreferente, 'Normal') Tarifa, "
                    "COALESCE(Importe, 0) Importe FROM Entradas "
                    "WHERE CorteInc=0 AND Salida IS NOT NULL AND Importe IS NOT NULL "
                    "ORDER BY Salida, id"
                )
                return cursor.fetchall()

    def resumen_corte(self, fecha_fin: Optional[datetime] = None) -> ResumenCorte:
        fecha_fin = fecha_fin or datetime.now().replace(microsecond=0)
        with self.abrir() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT MAX(FechaFin) ultima FROM Cortes")
                ultima = cursor.fetchone()["ultima"]
                cursor.execute(
                    "SELECT id, Entrada, COALESCE(Importe, 0) Importe FROM Entradas "
                    "WHERE CorteInc=0 AND Salida IS NOT NULL AND Importe IS NOT NULL "
                    "ORDER BY id"
                )
                cobrados = cursor.fetchall()
                cursor.execute(
                    "SELECT COUNT(*) cantidad FROM Entradas "
                    "WHERE Salida IS NULL AND COALESCE(Placas, '') <> 'Afuera'"
                )
                pendientes = int(cursor.fetchone()["cantidad"])
                cursor.execute(
                    "SELECT COUNT(*) cantidad FROM Pensionados WHERE Estatus='Adentro'"
                )
                pensionados = int(cursor.fetchone()["cantidad"])
        inicio = ultima or (
            min((fila["Entrada"] for fila in cobrados), default=fecha_fin)
        )
        return ResumenCorte(
            inicio=inicio,
            fin=fecha_fin,
            boletos=len(cobrados),
            importe=float(sum(float(fila["Importe"]) for fila in cobrados)),
            folios=tuple(int(fila["id"]) for fila in cobrados),
            pendientes_cobro=pendientes,
            pensionados_adentro=pensionados,
        )

    def generar_corte(self, fecha_fin: Optional[datetime] = None) -> tuple[int, ResumenCorte]:
        """Crea un corte y asigna sus cobros de forma atómica."""
        fecha_fin = fecha_fin or datetime.now().replace(microsecond=0)
        with self.abrir() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("SELECT MAX(FechaFin) ultima FROM Cortes FOR UPDATE")
                    ultima = cursor.fetchone()["ultima"]
                    cursor.execute(
                        "SELECT id, Entrada, COALESCE(Importe, 0) Importe FROM Entradas "
                        "WHERE CorteInc=0 AND Salida IS NOT NULL AND Importe IS NOT NULL "
                        "ORDER BY id FOR UPDATE"
                    )
                    cobrados = cursor.fetchall()
                    if not cobrados:
                        raise ErrorSimulacion("No hay cobros pendientes para generar el corte.")
                    cursor.execute(
                        "SELECT COUNT(*) cantidad FROM Entradas "
                        "WHERE Salida IS NULL AND COALESCE(Placas, '') <> 'Afuera'"
                    )
                    pendientes = int(cursor.fetchone()["cantidad"])
                    cursor.execute(
                        "SELECT COUNT(*) cantidad FROM Pensionados WHERE Estatus='Adentro'"
                    )
                    pensionados = int(cursor.fetchone()["cantidad"])
                    inicio = ultima or min(fila["Entrada"] for fila in cobrados)
                    folios = tuple(int(fila["id"]) for fila in cobrados)
                    importe = float(sum(float(fila["Importe"]) for fila in cobrados))
                    cursor.execute(
                        "INSERT INTO Cortes "
                        "(FechaIni, FechaFin, Importe, NumBoletos, TipoDCorte, "
                        "Quedados, idInicial, NumBolQued, Pensionados_Quedados) "
                        "VALUES (%s, %s, %s, %s, 1, %s, %s, %s, %s)",
                        (
                            inicio, fecha_fin, importe, len(folios), pendientes,
                            max(folios), pendientes, pensionados,
                        ),
                    )
                    numero_corte = int(cursor.lastrowid)
                    marcadores = ",".join(["%s"] * len(folios))
                    cursor.execute(
                        f"UPDATE Entradas SET CorteInc=%s WHERE CorteInc=0 "
                        f"AND id IN ({marcadores})",
                        (numero_corte, *folios),
                    )
                    if cursor.rowcount != len(folios):
                        raise ErrorSimulacion(
                            "Los cobros cambiaron mientras se generaba el corte. Intente nuevamente."
                        )
                conexion.commit()
            except Exception:
                conexion.rollback()
                raise
        return numero_corte, ResumenCorte(
            inicio, fecha_fin, len(folios), importe, folios, pendientes, pensionados
        )

    def autorizar_salida(self, folio: int, fecha_qr: datetime, ahora: datetime) -> ResultadoSalida:
        with self.abrir() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "SELECT Entrada, Salida, Placas FROM Entradas WHERE id=%s FOR UPDATE",
                        (folio,),
                    )
                    fila = cursor.fetchone()
                    if fila is None:
                        return ResultadoSalida(folio, False, "Boleto inexistente")
                    if fila["Entrada"].replace(microsecond=0) != fecha_qr.replace(microsecond=0):
                        return ResultadoSalida(folio, False, "El QR no corresponde a la entrada registrada")
                    if fila["Salida"] is None:
                        return ResultadoSalida(folio, False, "Boleto no pagado")
                    if fila["Placas"] == "Afuera":
                        return ResultadoSalida(folio, False, "Boleto ya utilizado, auto afuera")
                    restantes = tolerancia_restante(fila["Salida"], ahora)
                    if restantes is None:
                        return ResultadoSalida(folio, False, "Tolerancia de 15 minutos vencida")
                    cursor.execute(
                        "UPDATE Entradas SET Placas='Afuera' "
                        "WHERE id=%s AND COALESCE(Placas, '') <> 'Afuera'",
                        (folio,),
                    )
                    if cursor.rowcount != 1:
                        conexion.rollback()
                        return ResultadoSalida(folio, False, "Boleto ya utilizado, auto afuera")
                conexion.commit()
                return ResultadoSalida(
                    folio, True,
                    f"Abre barrera (simulada); tolerancia restante {restantes // 60:02d}:{restantes % 60:02d}",
                    restantes,
                )
            except Exception:
                conexion.rollback()
                raise

    def entrada_pensionado(self, tarjeta: int, ahora: datetime) -> str:
        with self.abrir() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "SELECT Id_cliente, Fecha_vigencia, Estatus, Vigencia, Tolerancia "
                        "FROM Pensionados WHERE Num_tarjeta=%s FOR UPDATE",
                        (int(tarjeta),),
                    )
                    fila = cursor.fetchone()
                    if fila is None:
                        raise ErrorSimulacion("Tarjeta de pensionado no registrada.")
                    if fila["Vigencia"] != "Activo" or fila["Fecha_vigencia"] is None:
                        raise ErrorSimulacion("Tarjeta sin vigencia activa.")
                    limite = sumar_dias_habiles(
                        fila["Fecha_vigencia"], int(fila["Tolerancia"] or 0)
                    )
                    if limite < ahora:
                        raise ErrorSimulacion("Pensión vencida.")
                    if fila["Estatus"] == "Adentro":
                        raise ErrorSimulacion("El pensionado ya se encuentra adentro.")
                    cursor.execute(
                        "UPDATE Pensionados SET Estatus='Adentro' WHERE Id_cliente=%s",
                        (fila["Id_cliente"],),
                    )
                    cursor.execute(
                        "INSERT INTO MovimientosPens "
                        "(Idcliente, num_tarjeta, Entrada, Estatus, Corte) "
                        "VALUES (%s, %s, %s, 'Adentro', 0)",
                        (fila["Id_cliente"], int(tarjeta), ahora),
                    )
                conexion.commit()
                return "Entrada de pensionado autorizada; abre barrera simulada"
            except Exception:
                conexion.rollback()
                raise

    def salida_pensionado(self, tarjeta: int, ahora: datetime) -> str:
        with self.abrir() as conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute(
                        "SELECT Id_cliente, Estatus, Fecha_vigencia, Vigencia, Tolerancia "
                        "FROM Pensionados WHERE Num_tarjeta=%s FOR UPDATE",
                        (int(tarjeta),),
                    )
                    pensionado = cursor.fetchone()
                    if pensionado is None:
                        raise ErrorSimulacion("Tarjeta de pensionado no registrada.")
                    if pensionado["Estatus"] != "Adentro":
                        raise ErrorSimulacion("El pensionado no tiene una entrada abierta.")
                    if pensionado["Vigencia"] != "Activo" or pensionado["Fecha_vigencia"] is None:
                        raise ErrorSimulacion("Tarjeta sin vigencia activa.")
                    limite = sumar_dias_habiles(
                        pensionado["Fecha_vigencia"], int(pensionado["Tolerancia"] or 0)
                    )
                    if limite < ahora:
                        raise ErrorSimulacion("Pensión vencida.")
                    cursor.execute(
                        "SELECT Id_movs, Entrada FROM MovimientosPens "
                        "WHERE Idcliente=%s AND Salida IS NULL "
                        "ORDER BY Id_movs DESC LIMIT 1 FOR UPDATE",
                        (pensionado["Id_cliente"],),
                    )
                    movimiento = cursor.fetchone()
                    if movimiento is None:
                        raise ErrorSimulacion("No existe una entrada abierta para este pensionado.")
                    permanencia = texto_permanencia(movimiento["Entrada"], ahora)
                    cursor.execute(
                        "UPDATE MovimientosPens SET Salida=%s, TiempoTotal=%s, Estatus='Afuera' "
                        "WHERE Id_movs=%s AND Salida IS NULL",
                        (ahora, permanencia, movimiento["Id_movs"]),
                    )
                    if cursor.rowcount != 1:
                        raise ErrorSimulacion("La salida del pensionado ya fue registrada.")
                    cursor.execute(
                        "UPDATE Pensionados SET Estatus='Afuera' WHERE Id_cliente=%s",
                        (pensionado["Id_cliente"],),
                    )
                conexion.commit()
                return f"Salida de pensionado autorizada; estancia {permanencia}"
            except Exception:
                conexion.rollback()
                raise

    def preparar_pensionado_prueba(self, tarjeta: int = 9900001) -> str:
        """Crea o reactiva una tarjeta exclusivamente en la base de laboratorio."""
        if not self.database.lower().endswith("_prueba"):
            raise ErrorSimulacion(
                "Por seguridad, los datos de demostración sólo se crean en una base *_prueba."
            )
        ahora = datetime.now().replace(microsecond=0)
        vigencia = ahora + timedelta(days=30)
        with self.abrir() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT Id_cliente FROM Pensionados WHERE Num_tarjeta=%s "
                    "ORDER BY Id_cliente LIMIT 1",
                    (int(tarjeta),),
                )
                fila = cursor.fetchone()
                if fila:
                    # Sólo para el registro sintético de la base de laboratorio:
                    # elimina pruebas anteriores y deja un estado repetible.
                    cursor.execute(
                        "DELETE FROM MovimientosPens WHERE Idcliente=%s",
                        (fila["Id_cliente"],),
                    )
                    cursor.execute(
                        "UPDATE Pensionados SET Nom_cliente='PENSIONADO PRUEBA', "
                        "Fecha_vigencia=%s, Vigencia='Activo', Estatus='Afuera', "
                        "Tolerancia='0' WHERE Id_cliente=%s",
                        (vigencia, fila["Id_cliente"]),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO Pensionados "
                        "(Num_tarjeta, Nom_cliente, Fecha_alta, Fecha_vigencia, "
                        "Vigencia, Estatus, Tolerancia, Cortesia) "
                        "VALUES (%s, 'PENSIONADO PRUEBA', %s, %s, "
                        "'Activo', 'Afuera', '0', 'No')",
                        (int(tarjeta), ahora, vigencia),
                    )
            conexion.commit()
        return f"Pensionado de prueba listo: tarjeta {int(tarjeta)}"


class SistemaSimulado:
    def __init__(self, resultados: Path, repositorio: Optional[RepositorioMariaDB] = None):
        self.resultados = resultados
        self.resultados.mkdir(parents=True, exist_ok=True)
        self.db = repositorio or RepositorioMariaDB()

    def expedir(self, placa: str = "SIMULACION", fecha: Optional[datetime] = None) -> ResultadoEntrada:
        fecha = fecha or datetime.now().replace(microsecond=0)
        folio = self.db.crear_entrada(fecha, placa or "SIMULACION")
        codigo = cifrar_folio(folio)
        qr = generar_qr(codigo, self.resultados / f"entrada_{folio}.png")
        boleto = self.resultados / f"entrada_{folio}.txt"
        boleto.write_text(
            "BOLETO DE ENTRADA - SIMULACIÓN\n"
            f"Folio: {folio}\nEntrada: {fecha:%Y-%m-%d %H:%M:%S}\n"
            f"Placas: {placa or 'SIMULACION'}\nCódigo QR: {codigo}\n",
            encoding="utf-8",
        )
        return ResultadoEntrada(folio, fecha, codigo, qr, boleto)

    def cobrar(self, codigo_entrada: str, promocion: str = "", fecha: Optional[datetime] = None) -> ResultadoCobro:
        folio = descifrar_folio(codigo_entrada)
        fecha = fecha or datetime.now().replace(microsecond=0)
        datos = self.db.cobrar(folio, promocion, fecha)
        codigo_salida = crear_codigo_salida(datos["entrada"], folio)
        qr = generar_qr(codigo_salida, self.resultados / f"salida_{folio}.png")
        comprobante = self.resultados / f"comprobante_{folio}.txt"
        comprobante.write_text(
            "COMPROBANTE DE PAGO - SIMULACIÓN\n"
            f"Folio: {folio}\nEntrada: {datos['entrada']:%Y-%m-%d %H:%M:%S}\n"
            f"Pago: {datos['pago']:%Y-%m-%d %H:%M:%S}\n"
            f"Permanencia: {datos['permanencia']}\nTarifa: {datos['tarifa']}\n"
            f"Importe: ${datos['importe']}.00\nCódigo QR de salida: {codigo_salida}\n"
            "Tolerancia para salir: 15 minutos\n",
            encoding="utf-8",
        )
        return ResultadoCobro(
            folio, datos["entrada"], datos["pago"], datos["permanencia"],
            datos["tarifa"], datos["importe"], codigo_salida, qr, comprobante,
        )

    def cotizar(
        self, codigo_entrada: str, promocion: str = "", fecha: Optional[datetime] = None
    ) -> ResultadoCotizacion:
        folio = descifrar_folio(codigo_entrada)
        datos = self.db.cotizar(
            folio, promocion, fecha or datetime.now().replace(microsecond=0)
        )
        return ResultadoCotizacion(
            datos["folio"], datos["entrada"], datos["consulta"],
            datos["permanencia"], datos["tarifa"], datos["importe_normal"],
            datos["descuento"], datos["importe_final"],
        )

    def generar_corte(self, fecha: Optional[datetime] = None) -> ResultadoCorte:
        numero, resumen = self.db.generar_corte(fecha)
        comprobante = self.resultados / f"corte_{numero}.txt"
        texto = (
            "CORTE DE CAJA - SIMULACIÓN\n"
            f"Corte: {numero}\nInicio: {resumen.inicio:%Y-%m-%d %H:%M:%S}\n"
            f"Fin: {resumen.fin:%Y-%m-%d %H:%M:%S}\n"
            f"Boletos cobrados: {resumen.boletos}\n"
            f"Importe total: ${resumen.importe:.2f}\n"
            f"Folios: {', '.join(map(str, resumen.folios))}\n"
            f"Boletos pendientes de cobro: {resumen.pendientes_cobro}\n"
            f"Pensionados adentro: {resumen.pensionados_adentro}\n"
        )
        comprobante.write_text(texto, encoding="utf-8")
        correo = self.resultados / f"correo_corte_{numero}.eml"
        correo.write_text(
            "Subject: Corte de caja de simulacion " + str(numero) + "\n"
            "Content-Type: text/plain; charset=UTF-8\n\n" + texto,
            encoding="utf-8",
        )
        return ResultadoCorte(numero, resumen, comprobante, correo)

    def salir(self, codigo_salida: str, fecha: Optional[datetime] = None) -> ResultadoSalida:
        fecha_qr, folio = leer_codigo_salida(codigo_salida)
        return self.db.autorizar_salida(
            folio, fecha_qr, fecha or datetime.now().replace(microsecond=0)
        )


def ruta_resultados() -> Path:
    base = Path(os.environ.get("ESTACIONAMIENTO_SIM_ROOT", Path(__file__).resolve().parents[1]))
    return base / "resultados"


def sumar_dias_habiles(fecha: datetime, dias: int) -> datetime:
    limite = fecha
    pendientes = max(0, int(dias))
    while pendientes:
        limite += timedelta(days=1)
        if limite.weekday() < 5:
            pendientes -= 1
    return limite
