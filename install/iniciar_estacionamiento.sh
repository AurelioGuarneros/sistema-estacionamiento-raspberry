#!/usr/bin/env bash
set -Eeuo pipefail

PUNTO="${1:-}"
CONFIGURACION="/etc/estacionamiento/config.env"
RAIZ="/opt/estacionamiento"

case "$PUNTO" in
  entrada) CARPETA="Entrada"; PROGRAMA="entrada.py" ;;
  tpv) CARPETA="TPV"; PROGRAMA="tpv.py" ;;
  salida) CARPETA="Salida"; PROGRAMA="salida.py" ;;
  *) printf 'Punto inválido: %s\n' "$PUNTO" >&2; exit 2 ;;
esac

if [[ ! -r "$CONFIGURACION" ]]; then
  printf 'No se puede leer %s\n' "$CONFIGURACION" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$CONFIGURACION"
set +a

cd "$RAIZ/$CARPETA"
exec "$RAIZ/venv/bin/python" "$RAIZ/$CARPETA/$PROGRAMA"
