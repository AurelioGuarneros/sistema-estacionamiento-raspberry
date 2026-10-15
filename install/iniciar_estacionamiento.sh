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

DIRECTORIO_DATOS="${ESTACIONAMIENTO_DATA_DIR:-/var/lib/estacionamiento}"
mkdir -p "$DIRECTORIO_DATOS"
REGISTRO="$DIRECTORIO_DATOS/inicio-${PUNTO}.log"
cd "$RAIZ/$CARPETA"
printf '\n[%s] Inicio de %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$PUNTO" >> "$REGISTRO"
exec "$RAIZ/venv/bin/python" "$RAIZ/$CARPETA/$PROGRAMA" >> "$REGISTRO" 2>&1

