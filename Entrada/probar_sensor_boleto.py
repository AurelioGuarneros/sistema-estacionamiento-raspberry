#!/usr/bin/env python3
"""Prueba física del sensor de boleto sin configurar ni accionar la barrera."""

import argparse
import signal
import time

import RPi.GPIO as GPIO


def main():
    parser = argparse.ArgumentParser(
        description="Muestra BOLETO PRESENTE/BOQUILLA LIBRE; no usa salidas GPIO."
    )
    parser.add_argument("--gpio", type=int, default=16, help="GPIO en numeración BCM")
    parser.add_argument(
        "--activo-alto",
        action="store_true",
        help="Use esta opción si el sensor entrega 3.3 V cuando hay boleto",
    )
    args = parser.parse_args()
    if not 0 <= args.gpio <= 27:
        parser.error("GPIO debe estar entre 0 y 27")

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(args.gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    detenido = False

    def detener(signum, frame):
        nonlocal detenido
        detenido = True

    signal.signal(signal.SIGINT, detener)
    signal.signal(signal.SIGTERM, detener)

    print(f"Prueba segura en GPIO BCM {args.gpio}. La barrera NO se acciona.")
    print("Cambie el estado del sensor varias veces. Ctrl+C para terminar.")
    anterior = None
    try:
        while not detenido:
            nivel = GPIO.input(args.gpio)
            presente = nivel == GPIO.HIGH if args.activo_alto else nivel == GPIO.LOW
            if presente != anterior:
                estado = "BOLETO PRESENTE" if presente else "BOQUILLA LIBRE"
                print(f"{time.strftime('%H:%M:%S')}  nivel={nivel}  {estado}", flush=True)
                anterior = presente
            time.sleep(0.05)
    finally:
        GPIO.cleanup(args.gpio)
        print("Prueba terminada; GPIO liberado.")


if __name__ == "__main__":
    main()
