#!/usr/bin/env python3
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from nucleo import (
    calcular_tarifa, cifrar_folio, construir_cotizacion, crear_codigo_salida,
    descifrar_folio, ErrorSimulacion, leer_codigo_salida, normalizar_promocion,
    normalizar_tarjeta, ResumenCorte, ResultadoSalida, SistemaSimulado,
    texto_permanencia, tolerancia_restante,
)


class RepositorioMemoria:
    def __init__(self):
        self.registros = {}

    def crear_entrada(self, fecha, placa):
        folio = len(self.registros) + 1
        self.registros[folio] = {
            "entrada": fecha, "placa": placa, "pago": None, "usado": False,
            "importe": None, "tarifa": None, "corte": 0,
        }
        return folio

    def cotizar(self, folio, promocion, fecha_consulta):
        fila = self.registros[folio]
        if fila["pago"] is not None:
            raise ErrorSimulacion("Este boleto ya fue cobrado.")
        return construir_cotizacion(
            folio, fila["entrada"], promocion, fecha_consulta
        )

    def cobrar(self, folio, promocion, fecha_pago):
        fila = self.registros[folio]
        if fila["pago"] is not None:
            raise ErrorSimulacion("Este boleto ya fue cobrado.")
        cotizacion = construir_cotizacion(
            folio, fila["entrada"], promocion, fecha_pago
        )
        fila["pago"] = fecha_pago
        fila["tarifa"] = cotizacion["tarifa"]
        fila["importe"] = cotizacion["importe_final"]
        return {
            "entrada": fila["entrada"],
            "pago": fecha_pago,
            "permanencia": cotizacion["permanencia"],
            "tarifa": cotizacion["tarifa"],
            "importe": cotizacion["importe_final"],
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

    def resumen_corte(self, fecha_fin=None):
        fin = fecha_fin or datetime.now().replace(microsecond=0)
        filas = [
            (folio, fila) for folio, fila in self.registros.items()
            if fila["pago"] is not None and fila["corte"] == 0
        ]
        inicio = min((fila["entrada"] for _, fila in filas), default=fin)
        return ResumenCorte(
            inicio, fin, len(filas),
            sum(fila["importe"] for _, fila in filas),
            tuple(folio for folio, _ in filas),
            sum(fila["pago"] is None for fila in self.registros.values()), 0,
        )

    def generar_corte(self, fecha_fin=None):
        resumen = self.resumen_corte(fecha_fin)
        if not resumen.folios:
            raise ErrorSimulacion("No hay cobros pendientes para generar el corte.")
        numero = 1 + max(
            (fila["corte"] for fila in self.registros.values()), default=0
        )
        for folio in resumen.folios:
            self.registros[folio]["corte"] = numero
        return numero, resumen


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

    def test_cotizacion_muestra_importe_antes_y_despues_de_promocion(self):
        entrada = datetime(2026, 8, 26, 8, 0, 0)
        consulta = entrada + timedelta(minutes=95)
        normal = construir_cotizacion(1, entrada, "", consulta)
        promocion = construir_cotizacion(1, entrada, "BA BODEGA AURRERA", consulta)
        self.assertEqual(normal["importe_final"], 20)
        self.assertEqual(promocion["importe_normal"], 20)
        self.assertEqual(promocion["descuento"], 15)
        self.assertEqual(promocion["importe_final"], 5)

    def test_tarjeta_vacia_usa_la_seleccion(self):
        self.assertEqual(normalizar_tarjeta("", "9900002"), 9900002)
        with self.assertRaisesRegex(ErrorSimulacion, "Capture o seleccione"):
            normalizar_tarjeta("", "")

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

    def test_corte_incluye_cobrados_una_sola_vez(self):
        with TemporaryDirectory() as temporal:
            repositorio = RepositorioMemoria()
            sistema = SistemaSimulado(Path(temporal), repositorio)
            ahora = datetime.now().replace(microsecond=0)
            primero = sistema.expedir("AUTO-1", ahora - timedelta(minutes=95))
            segundo = sistema.expedir("AUTO-2", ahora - timedelta(minutes=30))
            sistema.expedir("PENDIENTE", ahora - timedelta(minutes=10))
            sistema.cobrar(primero.codigo, "BA BODEGA AURRERA", ahora)
            sistema.cobrar(segundo.codigo, "", ahora)

            corte = sistema.generar_corte(ahora)
            self.assertEqual(corte.resumen.boletos, 2)
            self.assertEqual(corte.resumen.importe, 15)
            self.assertEqual(corte.resumen.pendientes_cobro, 1)
            self.assertTrue(corte.comprobante.is_file())
            self.assertTrue(corte.correo_simulado.is_file())
            with self.assertRaisesRegex(ErrorSimulacion, "No hay cobros pendientes"):
                sistema.generar_corte(ahora)


if __name__ == "__main__":
    unittest.main(verbosity=2)
