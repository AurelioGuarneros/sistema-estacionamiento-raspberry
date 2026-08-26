#!/usr/bin/env python3
"""Comandos de simulación para Entrada, TPV, Salida y pensionados."""

import argparse
import sys
from datetime import datetime, timedelta

from nucleo import ErrorSimulacion, PROMOCION_BA, SistemaSimulado, ruta_resultados


def construir_parser():
    parser = argparse.ArgumentParser(description="Simulador del estacionamiento")
    sub = parser.add_subparsers(dest="punto", required=True)

    entrada = sub.add_parser("entrada", help="Expedir boleto o registrar RFID")
    entrada.add_argument("--placa", default="SIMULACION")
    entrada.add_argument("--rfid", type=int)
    entrada.add_argument("--hace-minutos", type=int, default=0,
                         help="Sólo para probar tarifas sin esperar")

    tpv = sub.add_parser("tpv", help="Cobrar boleto")
    tpv.add_argument("codigo", help="Código leído del QR de entrada")
    tpv.add_argument("--promocion", default="")

    salida = sub.add_parser("salida", help="Validar QR o RFID")
    salida.add_argument("codigo", nargs="?", help="Código QR de salida")
    salida.add_argument("--rfid", type=int)

    sub.add_parser("demo", help="Ejecutar Entrada → TPV → Salida y reuso")
    sub.add_parser("demo-multiple", help="Procesar varios boletos en distinto orden")
    preparar = sub.add_parser("preparar-rfid", help="Crear pensionado de laboratorio")
    preparar.add_argument("--rfid", type=int, default=9900001)
    sub.add_parser("demo-rfid", help="Probar varios pensionados en distinto orden")
    sub.add_parser("demo-corte", help="Cobrar boletos y generar un corte de prueba")
    return parser


def main():
    args = construir_parser().parse_args()
    sistema = SistemaSimulado(ruta_resultados())
    if args.punto == "entrada":
        if args.rfid is not None:
            print(sistema.db.entrada_pensionado(args.rfid, datetime.now()))
            return
        fecha = datetime.now().replace(microsecond=0) - timedelta(minutes=args.hace_minutos)
        r = sistema.expedir(args.placa, fecha)
        print("ENTRADA AUTORIZADA - barrera simulada 3 segundos")
        print(f"Folio: {r.folio}")
        print(f"Código QR de entrada: {r.codigo}")
        print(f"Boleto: {r.boleto}")
        print(f"Imagen QR: {r.qr}")
    elif args.punto == "tpv":
        r = sistema.cobrar(args.codigo, args.promocion)
        print("COBRO CORRECTO")
        print(f"Folio: {r.folio} | Permanencia: {r.permanencia}")
        print(f"Tarifa: {r.tarifa} | Importe: ${r.importe}.00")
        print(f"Código QR de salida: {r.codigo_salida}")
        print(f"Comprobante: {r.comprobante}")
        print(f"Imagen QR: {r.qr}")
    elif args.punto == "salida":
        if args.rfid is not None:
            print(sistema.db.salida_pensionado(args.rfid, datetime.now()))
            return
        if not args.codigo:
            raise ErrorSimulacion("Indique el código QR de salida o --rfid.")
        r = sistema.salir(args.codigo)
        print("SALIDA AUTORIZADA" if r.autorizado else "SALIDA RECHAZADA")
        print(r.mensaje)
        if not r.autorizado:
            raise SystemExit(2)
    elif args.punto == "demo":
        print("1. Entrada simulada con estancia de 95 minutos")
        entrada = sistema.expedir("LAB-001", datetime.now().replace(microsecond=0) - timedelta(minutes=95))
        print(f"   Folio {entrada.folio}; QR {entrada.codigo}")
        print("2. Cobro con promoción Bodega Aurrera")
        cobro = sistema.cobrar(entrada.codigo, PROMOCION_BA)
        print(f"   Importe ${cobro.importe}.00; QR salida {cobro.codigo_salida}")
        print("3. Primera lectura en Salida")
        salida = sistema.salir(cobro.codigo_salida)
        print(f"   {salida.mensaje}")
        if not salida.autorizado:
            raise ErrorSimulacion("La primera salida debió ser autorizada.")
        print("4. Segunda lectura del mismo QR")
        repetida = sistema.salir(cobro.codigo_salida)
        print(f"   {repetida.mensaje}")
        if repetida.autorizado:
            raise ErrorSimulacion("La segunda lectura no debió abrir la barrera.")
        print("RESULTADO: FLUJO COMPLETO CORRECTO")
    elif args.punto == "demo-multiple":
        ahora = datetime.now().replace(microsecond=0)
        print("1. Se expiden tres boletos independientes")
        entradas = [
            sistema.expedir("ORDEN-1", ahora - timedelta(minutes=40)),
            sistema.expedir("ORDEN-2", ahora - timedelta(minutes=95)),
            sistema.expedir("ORDEN-3", ahora - timedelta(minutes=10)),
        ]
        print("   Folios:", ", ".join(str(item.folio) for item in entradas))
        print("2. Se cobran fuera de orden: segundo y después primero")
        cobro_segundo = sistema.cobrar(entradas[1].codigo, fecha=ahora)
        cobro_primero = sistema.cobrar(entradas[0].codigo, fecha=ahora)
        print(f"   Cobrados: {cobro_segundo.folio}, {cobro_primero.folio}")
        print(f"   El folio {entradas[2].folio} permanece pendiente de cobro")
        print("3. Salen en otro orden: primero y después segundo")
        salida_primero = sistema.salir(cobro_primero.codigo_salida, ahora)
        salida_segundo = sistema.salir(cobro_segundo.codigo_salida, ahora)
        print(f"   Folio {cobro_primero.folio}: {salida_primero.mensaje}")
        print(f"   Folio {cobro_segundo.folio}: {salida_segundo.mensaje}")
        if not salida_primero.autorizado or not salida_segundo.autorizado:
            raise ErrorSimulacion("Un boleto válido no abrió la barrera.")
        repetido = sistema.salir(cobro_primero.codigo_salida, ahora)
        if repetido.autorizado:
            raise ErrorSimulacion("Un boleto utilizado abrió dos veces.")
        print("4. Reuso rechazado correctamente:", repetido.mensaje)
        print("RESULTADO: VARIOS BOLETOS Y ORDEN DISTINTO CORRECTOS")
    elif args.punto == "preparar-rfid":
        print(sistema.db.preparar_pensionado_prueba(args.rfid))
    elif args.punto == "demo-rfid":
        tarjetas = (9900001, 9900002, 9900003)
        print("1. Se preparan tres pensionados independientes")
        for tarjeta in tarjetas:
            print("  ", sistema.db.preparar_pensionado_prueba(tarjeta))
        print("2. Entran en orden 1, 2, 3")
        for tarjeta in tarjetas:
            print(f"   {tarjeta}: {sistema.db.entrada_pensionado(tarjeta, datetime.now())}")
        print("3. Salen en orden 2, 1, 3")
        for tarjeta in (tarjetas[1], tarjetas[0], tarjetas[2]):
            print(f"   {tarjeta}: {sistema.db.salida_pensionado(tarjeta, datetime.now())}")
        try:
            sistema.db.salida_pensionado(tarjetas[0], datetime.now())
        except ErrorSimulacion as error:
            print(f"Segunda salida rechazada correctamente: {error}")
        else:
            raise ErrorSimulacion("La tarjeta abrió dos veces en la salida.")
        print("RESULTADO: VARIOS PENSIONADOS Y ORDEN DISTINTO CORRECTOS")
    elif args.punto == "demo-corte":
        ahora = datetime.now().replace(microsecond=0)
        print("1. Se expiden y cobran dos boletos")
        primero = sistema.expedir("CORTE-1", ahora - timedelta(minutes=95))
        segundo = sistema.expedir("CORTE-2", ahora - timedelta(minutes=30))
        cotizacion = sistema.cotizar(primero.codigo, PROMOCION_BA, ahora)
        print(
            f"   Folio {primero.folio}: normal ${cotizacion.importe_normal:.2f}; "
            f"descuento ${cotizacion.descuento:.2f}; final ${cotizacion.importe_final:.2f}"
        )
        sistema.cobrar(primero.codigo, PROMOCION_BA, ahora)
        sistema.cobrar(segundo.codigo, "", ahora)
        print("2. Se genera el corte")
        corte = sistema.generar_corte(ahora)
        print(
            f"   Corte {corte.folio}: {corte.resumen.boletos} boletos; "
            f"total ${corte.resumen.importe:.2f}"
        )
        print(f"   Comprobante: {corte.comprobante}")
        print(f"   Correo simulado: {corte.correo_simulado}")
        print("RESULTADO: CORTE GENERADO CORRECTAMENTE")


if __name__ == "__main__":
    try:
        main()
    except ErrorSimulacion as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
