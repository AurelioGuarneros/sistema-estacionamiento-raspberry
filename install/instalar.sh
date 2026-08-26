#!/usr/bin/env bash
set -Eeuo pipefail

MODO=""
PUNTO=""
DESTINO=""
USUARIO_SERVICIO="${SUDO_USER:-${USER:-pi}}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ORIGEN="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

instalar_dependencias_sistema() {
  local comando=(apt-get install -y python3-venv python3-tk)
  if command -v python3 >/dev/null 2>&1 \
      && python3 -m venv --help >/dev/null 2>&1 \
      && python3 -c 'import tkinter' >/dev/null 2>&1; then
    return
  fi
  if ! command -v apt-get >/dev/null 2>&1; then
    printf 'Este instalador requiere una distribución basada en Debian/Ubuntu.\n' >&2
    exit 1
  fi
  if [[ "${EUID}" -eq 0 ]]; then
    apt-get update
    "${comando[@]}"
  else
    sudo apt-get update
    sudo "${comando[@]}"
  fi
}

mostrar_uso() {
  printf '%s\n' \
    "Uso:" \
    "  ./install/instalar.sh --modo-simulacion [--destino RUTA]" \
    "  sudo ./install/instalar.sh --modo-raspberry --punto entrada|tpv|salida [--usuario USUARIO]"
}

while (($#)); do
  case "$1" in
    --modo-simulacion) MODO="simulacion" ;;
    --modo-raspberry) MODO="raspberry" ;;
    --punto) PUNTO="${2:-}"; shift ;;
    --destino) DESTINO="${2:-}"; shift ;;
    --usuario) USUARIO_SERVICIO="${2:-}"; shift ;;
    -h|--help) mostrar_uso; exit 0 ;;
    *) printf 'Opción desconocida: %s\n' "$1" >&2; mostrar_uso; exit 2 ;;
  esac
  shift
done

copiar_proyecto() {
  local destino="$1"
  mkdir -p "$destino"
  cp -a "$ORIGEN/Entrada" "$destino/"
  cp -a "$ORIGEN/TPV" "$destino/"
  cp -a "$ORIGEN/Salida" "$destino/"
  cp -a "$ORIGEN/database" "$destino/"
  cp -a "$ORIGEN/requirements.txt" "$destino/"
}

verificar_python() {
  local raiz="$1"
  local interprete="${2:-python3}"
  local encontrados=0
  while IFS= read -r -d '' archivo; do
    "$interprete" -m py_compile "$archivo"
    encontrados=$((encontrados + 1))
  done < <(find "$raiz" -type f -name '*.py' -print0)
  printf 'Sintaxis verificada: %s archivos Python.\n' "$encontrados"
}

instalar_simulacion() {
  local destino="${DESTINO:-${ORIGEN}/prueba_laptop}"
  if [[ "$destino" == "$ORIGEN" ]]; then
    printf 'El destino de simulación no puede ser el repositorio original.\n' >&2
    exit 2
  fi
  copiar_proyecto "$destino/aplicacion"
  mkdir -p "$destino/config" "$destino/simulacion"
  if [[ ! -f "$destino/config/config.env" ]]; then
    cp "$ORIGEN/.env.example" "$destino/config/config.env"
    chmod 600 "$destino/config/config.env"
  fi
  cp -a "$ORIGEN/simulacion/." "$destino/simulacion/"
  cp "$SCRIPT_DIR/simular_punto.sh" "$destino/simulacion/"
  chmod +x "$destino/simulacion/"*.py "$destino/simulacion/"*.sh

  instalar_dependencias_sistema
  if [[ ! -x "$destino/venv/bin/python" ]]; then
    python3 -m venv "$destino/venv"
  fi
  "$destino/venv/bin/python" -m pip install --upgrade pip
  "$destino/venv/bin/python" -m pip install -r "$destino/aplicacion/requirements.txt"
  verificar_python "$destino/aplicacion" "$destino/venv/bin/python"
  verificar_python "$destino/simulacion" "$destino/venv/bin/python"
  printf '\nInstalación de simulación terminada en:\n  %s\n' "$destino"
  printf 'Prueba un punto con:\n  %s/simulacion/simular_punto.sh entrada\n' "$destino"
}

instalar_raspberry() {
  if [[ "${EUID}" -ne 0 ]]; then
    printf 'El modo Raspberry debe ejecutarse con sudo.\n' >&2
    exit 2
  fi
  case "$PUNTO" in entrada|tpv|salida) ;; *) printf 'Indique --punto entrada, tpv o salida.\n' >&2; exit 2 ;; esac
  id "$USUARIO_SERVICIO" >/dev/null 2>&1 || { printf 'No existe el usuario %s.\n' "$USUARIO_SERVICIO" >&2; exit 2; }

  instalar_dependencias_sistema

  getent group estacionamiento >/dev/null || groupadd --system estacionamiento
  usermod -a -G estacionamiento,gpio,lp,dialout "$USUARIO_SERVICIO"
  install -d -o root -g estacionamiento -m 0750 /etc/estacionamiento
  if [[ ! -f /etc/estacionamiento/config.env ]]; then
    install -o root -g estacionamiento -m 0640 "$ORIGEN/.env.example" /etc/estacionamiento/config.env
    printf 'Se creó /etc/estacionamiento/config.env; debe completar sus valores.\n'
  fi

  install -d -o root -g estacionamiento -m 0755 /opt/estacionamiento
  copiar_proyecto /opt/estacionamiento
  python3 -m venv /opt/estacionamiento/venv
  /opt/estacionamiento/venv/bin/pip install --upgrade pip
  /opt/estacionamiento/venv/bin/pip install -r /opt/estacionamiento/requirements.txt
  verificar_python /opt/estacionamiento

  local servicio="estacionamiento-${PUNTO}.service"
  local carpeta ejecutable
  case "$PUNTO" in
    entrada) carpeta="Entrada"; ejecutable="entrada.py" ;;
    tpv) carpeta="TPV"; ejecutable="tpv.py" ;;
    salida) carpeta="Salida"; ejecutable="salida.py" ;;
  esac
  sed -e "s|@USUARIO@|${USUARIO_SERVICIO}|g" \
      -e "s|@PUNTO@|${PUNTO}|g" \
      -e "s|@CARPETA@|${carpeta}|g" \
      -e "s|@EJECUTABLE@|${ejecutable}|g" \
      "$SCRIPT_DIR/systemd/estacionamiento@.service" > "/etc/systemd/system/${servicio}"
  systemctl daemon-reload
  systemctl enable "$servicio"
  printf '\nServicio instalado: %s\n' "$servicio"
  printf 'Complete config.env y después ejecute:\n  sudo systemctl start %s\n' "$servicio"
}

case "$MODO" in
  simulacion) instalar_simulacion ;;
  raspberry) instalar_raspberry ;;
  *) mostrar_uso; exit 2 ;;
esac
