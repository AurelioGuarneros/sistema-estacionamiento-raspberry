#!/usr/bin/env python3
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from nucleo import (
    calcular_tarifa, cifrar_folio, crear_codigo_salida, descifrar_folio,
    ErrorSimulacion, leer_codigo_salida, normalizar_promocion, ResultadoSalida,
    SistemaSimulado, texto_permanencia, tolerancia_restante,
)


class RepositorioMemoria:
    def __init__(self):
        self.registros = {}

    def crear_entrada(self, fecha, placa):
        folio = len(self.registros) + 1
        self.registros[folio] = {
            "entrada": fecha, "placa": placa, "pago": None, "usado": False,
        }
        return folio

    def cobrar(self, folio, promocion, fecha_pago):
        fila = self.registros[folio]
        if fila["pago"] is not None:
            raise ErrorSimulacion("Este boleto ya fue cobrado.")
        tarifa = normalizar_promocion(promocion)
        minutos = int((fecha_pago - fila["entrada"]).total_seconds() // 60)
        fila["pago"] = fecha_pago
        return {
            "entrada": fila["entrada"],
            "pago": fecha_pago,
            "permanencia": texto_permanencia(fila["entrada"], fecha_pago),
            "tarifa": tarifa,
            "importe": calcular_tarifa(minutos, tarifa),
        }

    def autorizar_salida(self, folio, fecha_qr, ahora):
        fila = self.registros[folio]
        if fila["entrada"] != fecha_qr:
            return ResultadoSalida(folio, False, "QR incorrecto")
        if fila["pago"] is None:
            return ResultadoSalida(folio, False, "Boleto no pagado")
        if fila["usado"]:
            return ResultadoSalida(folio, False, "Boleto ya utilizado")
        fila["usado"] = True
        return ResultadoSalida(folio, True, "Abre barrera simulada", 900)


class PruebasNucleo(unittest.TestCase):
    def test_folio_cifrado_compatible(self):
        self.assertEqual(descifrar_folio(cifrar_folio(428937, 12345)), 428937)

    def test_codigo_salida(self):
        fecha = datetime(2026, 8, 26, 1, 2, 3)
        codigo = crear_codigo_salida(fecha, 49)
        self.assertEqual(leer_codigo_salida(codigo), (fecha, 49))

    def test_tarifa_normal_redondea_hora(self):
        self.assertEqual(calcular_tarifa(1), 10)
        self.assertEqual(calcular_tarifa(60), 10)
        self.assertEqual(calcular_tarifa(61), 20)

    def test_tarifa_bodega_aurrera(self):
        promo = normalizar_promocion("BA BODEGA AURRERA 114254")
        self.assertEqual(calcular_tarifa(120, promo), 5)
        self.assertEqual(calcular_tarifa(121, promo), 15)
        self.assertEqual(calcular_tarifa(24 * 60, promo), 225)

    def test_tolerancia_salida_15_minutos(self):
        pago = datetime(2026, 8, 26, 1, 0, 0)
        self.assertEqual(tolerancia_restante(pago, pago), 900)
        self.assertEqual(tolerancia_restante(pago, pago + timedelta(minutes=15)), 0)
        self.assertIsNone(tolerancia_restante(pago, pago + timedelta(seconds=901)))

    def test_flujo_completo_y_segundo_uso(self):
        with TemporaryDirectory() as temporal:
            sistema = SistemaSimulado(Path(temporal), RepositorioMemoria())
            entrada = sistema.expedir(
                "LAB-001", datetime.now().replace(microsecond=0) - timedelta(minutes=95)
            )
            cobro = sistema.cobrar(entrada.codigo, "BA BODEGA AURRERA 114254")
            primera = sistema.salir(cobro.codigo_salida)
            segunda = sistema.salir(cobro.codigo_salida)
            self.assertEqual(cobro.importe, 5)
            self.assertTrue(entrada.boleto.is_file())
            self.assertTrue(cobro.comprobante.is_file())
            self.assertTrue(primera.autorizado)
            self.assertFalse(segunda.autorizado)

    def test_varios_boletos_en_orden_distinto(self):
        with TemporaryDirectory() as temporal:
            repositorio = RepositorioMemoria()
            sistema = SistemaSimulado(Path(temporal), repositorio)
            ahora = datetime.now().replace(microsecond=0)
            primero = sistema.expedir("AUTO-1", ahora - timedelta(minutes=40))
            segundo = sistema.expedir("AUTO-2", ahora - timedelta(minutes=95))
            tercero = sistema.expedir("AUTO-3", ahora - timedelta(minutes=10))

            # El segundo se cobra antes que el primero; el tercero queda pendiente.
            cobro_segundo = sistema.cobrar(segundo.codigo, fecha=ahora)
            cobro_primero = sistema.cobrar(primero.codigo, fecha=ahora)
            self.assertEqual(cobro_segundo.folio, segundo.folio)
            self.assertEqual(cobro_primero.folio, primero.folio)
            self.assertIsNone(repositorio.registros[tercero.folio]["pago"])

            # También pueden salir en un orden distinto al del cobro.
            salida_primero = sistema.salir(cobro_primero.codigo_salida, ahora)
            salida_segundo = sistema.salir(cobro_segundo.codigo_salida, ahora)
            self.assertTrue(salida_primero.autorizado)
            self.assertTrue(salida_segundo.autorizado)
            self.assertFalse(
                sistema.salir(cobro_primero.codigo_salida, ahora).autorizado
            )

    def test_no_permite_cobrar_dos_veces(self):
        with TemporaryDirectory() as temporal:
            sistema = SistemaSimulado(Path(temporal), RepositorioMemoria())
            entrada = sistema.expedir("AUTO-1", datetime.now().replace(microsecond=0))
            sistema.cobrar(entrada.codigo)
            with self.assertRaisesRegex(ErrorSimulacion, "ya fue cobrado"):
                sistema.cobrar(entrada.codigo)


if __name__ == "__main__":
    unittest.main(verbosity=2)
