#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BASE="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
CONFIG="${BASE}/config/config.env"
PYTHON="${BASE}/venv/bin/python"

if [[ ! -x "$PYTHON" ]]; then
  printf 'No existe el entorno Python: %s\nEjecute nuevamente el instalador.\n' "$PYTHON" >&2
  exit 1
fi
if [[ ! -f "$CONFIG" ]]; then
  printf 'No existe la configuración: %s\n' "$CONFIG" >&2
  exit 1
fi

export ESTACIONAMIENTO_CONFIG="$CONFIG"
export ESTACIONAMIENTO_SIM_ROOT="$BASE"

case "${1:-}" in
  gui)
    exec "$PYTHON" "$SCRIPT_DIR/simulador_gui.py"
    ;;
  entrada|tpv|salida|demo|demo-multiple|preparar-rfid|demo-rfid)
    exec "$PYTHON" "$SCRIPT_DIR/simular.py" "$@"
    ;;
  pruebas)
    exec "$PYTHON" "$SCRIPT_DIR/pruebas_unitarias.py"
    ;;
  *)
    printf '%s\n' \
      "Uso:" \
      "  $0 gui" \
      "  $0 demo" \
      "  $0 demo-multiple" \
      "  $0 demo-rfid" \
      "  $0 preparar-rfid [--rfid TARJETA]" \
      "  $0 entrada [--placa PLACA] [--hace-minutos N] [--rfid TARJETA]" \
      "  $0 tpv CODIGO_QR [--promocion 'BA BODEGA AURRERA 114254']" \
      "  $0 salida CODIGO_QR [--rfid TARJETA]" \
      "  $0 pruebas" >&2
    exit 2
    ;;
esac
