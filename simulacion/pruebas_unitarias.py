#!/usr/bin/env python3
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from nucleo import (
    calcular_tarifa, cifrar_folio, construir_cotizacion,
    construir_cotizacion_recobro, crear_codigo_salida, descifrar_folio,
    ErrorSimulacion, leer_codigo_salida, normalizar_promocion,
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
            "importe": None, "tarifa": None, "corte": 0, "recobros": [],
        }
        return folio

    def cotizar(self, folio, promocion, fecha_consulta):
        fila = self.registros[folio]
        if fila["pago"] is not None:
            return construir_cotizacion_recobro(
                folio, fila["entrada"], fila["pago"], promocion, fecha_consulta
            )
        return construir_cotizacion(
            folio, fila["entrada"], promocion, fecha_consulta
        )

    def cobrar(self, folio, promocion, fecha_pago):
        fila = self.registros[folio]
        es_recobro = fila["pago"] is not None
        cotizacion = (
            construir_cotizacion_recobro(
                folio, fila["entrada"], fila["pago"], promocion, fecha_pago
            )
            if es_recobro else
            construir_cotizacion(folio, fila["entrada"], promocion, fecha_pago)
        )
        if es_recobro:
            fila["recobros"].append({
                "importe": cotizacion["importe_final"], "corte": 0,
            })
        fila["pago"] = fecha_pago
        if not es_recobro:
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
        restantes = tolerancia_restante(fila["pago"], ahora)
        if restantes is None:
            return ResultadoSalida(folio, False, "Tolerancia vencida; requiere recobro")
        fila["usado"] = True
        return ResultadoSalida(folio, True, "Abre barrera simulada", restantes)

    def resumen_corte(self, fecha_fin=None):
        fin = fecha_fin or datetime.now().replace(microsecond=0)
        filas = [
            (folio, fila) for folio, fila in self.registros.items()
            if fila["pago"] is not None and fila["corte"] == 0
        ]
        recobros = [
            (folio, indice, recobro)
            for folio, fila in self.registros.items()
            for indice, recobro in enumerate(fila["recobros"], start=1)
            if recobro["corte"] == 0
        ]
        inicio = min((fila["entrada"] for _, fila in filas), default=fin)
        return ResumenCorte(
            inicio, fin, len(filas) + len(recobros),
            sum(fila["importe"] for _, fila in filas)
            + sum(recobro["importe"] for _, _, recobro in recobros),
            tuple(
                [str(folio) for folio, _ in filas]
                + [f"{folio}-R{indice}" for folio, indice, _ in recobros]
            ),
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
            if "-R" in folio:
                entrada, indice = folio.split("-R")
                self.registros[int(entrada)]["recobros"][int(indice) - 1]["corte"] = numero
            else:
                self.registros[int(folio)]["corte"] = numero
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

    def test_recobro_cobra_solo_tiempo_despues_de_tolerancia(self):
        pago = datetime(2026, 8, 26, 10, 0, 0)
        recobro = construir_cotizacion_recobro(
            1, pago - timedelta(hours=2), pago, "",
            pago + timedelta(minutes=16),
        )
        self.assertEqual(recobro["minutos_excedidos"], 1)
        self.assertEqual(recobro["importe_final"], 10)

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

    def test_no_permite_recobrar_dentro_de_tolerancia(self):
        with TemporaryDirectory() as temporal:
            sistema = SistemaSimulado(Path(temporal), RepositorioMemoria())
            entrada = sistema.expedir("AUTO-1", datetime.now().replace(microsecond=0))
            sistema.cobrar(entrada.codigo)
            with self.assertRaisesRegex(ErrorSimulacion, "todavía tiene"):
                sistema.cobrar(entrada.codigo)

    def test_boleto_vencido_se_recobra_sin_duplicar_corte_anterior(self):
        with TemporaryDirectory() as temporal:
            repo = RepositorioMemoria()
            sistema = SistemaSimulado(Path(temporal), repo)
            pago = datetime(2026, 8, 26, 10, 0, 0)
            entrada = sistema.expedir("VENCIDO", pago - timedelta(minutes=95))
            cobro_inicial = sistema.cobrar(entrada.codigo, "", pago)
            primer_corte = sistema.generar_corte(pago)
            self.assertEqual(primer_corte.resumen.importe, 20)

            regreso = pago + timedelta(minutes=16)
            salida_vencida = sistema.salir(cobro_inicial.codigo_salida, regreso)
            self.assertFalse(salida_vencida.autorizado)
            self.assertIn("recobro", salida_vencida.mensaje)
            recobro = sistema.cobrar(entrada.codigo, "", regreso)
            self.assertEqual(recobro.importe, 10)
            segundo_corte = sistema.generar_corte(regreso)
            self.assertEqual(segundo_corte.resumen.importe, 10)
            self.assertTrue(sistema.salir(recobro.codigo_salida, regreso).autorizado)

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
