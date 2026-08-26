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
    preparar = sub.add_parser("preparar-rfid", help="Crear pensionado de laboratorio")
    preparar.add_argument("--rfid", type=int, default=9900001)
    sub.add_parser("demo-rfid", help="Probar entrada, salida y segundo uso RFID")
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
    elif args.punto == "preparar-rfid":
        print(sistema.db.preparar_pensionado_prueba(args.rfid))
    elif args.punto == "demo-rfid":
        tarjeta = 9900001
        print(sistema.db.preparar_pensionado_prueba(tarjeta))
        print(sistema.db.entrada_pensionado(tarjeta, datetime.now()))
        print(sistema.db.salida_pensionado(tarjeta, datetime.now()))
        try:
            sistema.db.salida_pensionado(tarjeta, datetime.now())
        except ErrorSimulacion as error:
            print(f"Segunda salida rechazada correctamente: {error}")
        else:
            raise ErrorSimulacion("La tarjeta abrió dos veces en la salida.")
        print("RESULTADO: FLUJO RFID CORRECTO")


if __name__ == "__main__":
    try:
        main()
    except ErrorSimulacion as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
