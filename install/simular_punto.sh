#!/usr/bin/env bash
set -Eeuo pipefail

PUNTO="${1:-}"
case "$PUNTO" in
  entrada)
    printf '[SIMULACIÓN] Entrada instalada.\n'
    printf '[SIMULACIÓN] Botón y sensor: sin GPIO físico.\n'
    printf '[SIMULACIÓN] Impresión: se generaría un boleto de prueba.\n'
    printf '[SIMULACIÓN] Barrera de entrada: pulso de 3 segundos.\n'
    ;;
  tpv)
    printf '[SIMULACIÓN] TPV instalada.\n'
    printf '[SIMULACIÓN] MariaDB y correo requieren configurar config/config.env.\n'
    printf '[SIMULACIÓN] Impresión de comprobante: sin impresora física.\n'
    ;;
  salida)
    printf '[SIMULACIÓN] Salida instalada.\n'
    printf '[SIMULACIÓN] Lector QR/RFID: sin dispositivo físico.\n'
    printf '[SIMULACIÓN] Barrera de salida: pulso de 3 segundos.\n'
    ;;
  *) printf 'Uso: %s entrada|tpv|salida\n' "$0" >&2; exit 2 ;;
esac
