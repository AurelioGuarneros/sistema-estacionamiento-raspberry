#!/usr/bin/env bash
set -Eeuo pipefail

MODO=""
PUNTO=""
DESTINO=""
USUARIO_SERVICIO="${SUDO_USER:-${USER:-pi}}"
ASUMIR_SI=0
MODELO_EQUIPO=""
ARQUITECTURA=""
SISTEMA_OPERATIVO=""
VERSION_PYTHON=""
GESTOR_RED=""
INTERFAZ_RED=""
CONEXION_RED=""
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ORIGEN="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
# shellcheck source=lib/configuracion.sh
source "$SCRIPT_DIR/lib/configuracion.sh"

limpiar_temporales() {
  if [[ -n "${CONFIG_TEMP:-}" && -f "$CONFIG_TEMP" ]]; then
    rm -f "$CONFIG_TEMP"
  fi
}
trap limpiar_temporales EXIT

instalar_dependencias_sistema() {
  local paquetes=(python3-venv python3-tk git openssl libusb-1.0-0 usbutils)
  if ! command -v apt-get >/dev/null 2>&1; then
    printf 'Este instalador requiere una distribución basada en Debian/Ubuntu.\n' >&2
    exit 1
  fi
  case "$PUNTO" in
    entrada|salida) paquetes+=(python3-rpi-lgpio) ;;
    tpv) paquetes+=(mariadb-server mariadb-client) ;;
  esac
  if [[ "${EUID}" -eq 0 ]]; then
    apt-get update
    apt-get install -y "${paquetes[@]}"
  else
    sudo apt-get update
    sudo apt-get install -y "${paquetes[@]}"
  fi
}

mostrar_uso() {
  printf '%s\n' \
    "Uso:" \
    "  sudo ./install/instalar.sh" \
    "  ./install/instalar.sh --modo-simulacion [--destino RUTA]" \
    "  sudo ./install/instalar.sh --modo-raspberry [--punto entrada|tpv|salida] [--usuario USUARIO] [--si]"
}

seleccionar_punto_interactivo() {
  local opcion
  printf '\nSeleccione el destino de esta Raspberry:\n' >&2
  printf '  1) Entrada\n  2) TPV\n  3) Salida\n' >&2
  while true; do
    read -r -p "Opción [1-3]: " opcion
    case "$opcion" in
      1|entrada|Entrada) PUNTO="entrada"; return ;;
      2|tpv|TPV) PUNTO="tpv"; return ;;
      3|salida|Salida) PUNTO="salida"; return ;;
      *) printf 'Opción inválida. Escriba 1, 2 o 3.\n' >&2 ;;
    esac
  done
}

detectar_entorno_raspberry() {
  local conexion
  if [[ -r /proc/device-tree/model ]]; then
    MODELO_EQUIPO="$(tr -d '\0' < /proc/device-tree/model)"
  else
    MODELO_EQUIPO="Equipo no identificado"
  fi
  ARQUITECTURA="$(uname -m)"
  if [[ -r /etc/os-release ]]; then
    SISTEMA_OPERATIVO="$(. /etc/os-release; printf '%s' "${PRETTY_NAME:-Linux}")"
  else
    SISTEMA_OPERATIVO="Linux"
  fi
  VERSION_PYTHON="$(python3 --version 2>&1 || true)"

  if systemctl is-active --quiet NetworkManager 2>/dev/null && command -v nmcli >/dev/null 2>&1; then
    GESTOR_RED="NetworkManager"
  elif systemctl is-active --quiet dhcpcd 2>/dev/null; then
    GESTOR_RED="dhcpcd"
  else
    GESTOR_RED="no identificado"
  fi

  INTERFAZ_RED="$(ip route show default 2>/dev/null | awk 'NR == 1 {print $5}')"
  if [[ "$GESTOR_RED" == "NetworkManager" && -n "$INTERFAZ_RED" ]]; then
    conexion="$(nmcli -g GENERAL.CONNECTION device show "$INTERFAZ_RED" 2>/dev/null | head -n 1)"
    if [[ "$conexion" != "--" ]]; then
      CONEXION_RED="$conexion"
    fi
  fi
}

validar_entorno_raspberry() {
  case "$ARQUITECTURA" in
    aarch64|arm64|armv7l) ;;
    *)
      printf 'Arquitectura no admitida para instalación Raspberry: %s\n' "$ARQUITECTURA" >&2
      exit 2
      ;;
  esac
  if [[ "$MODELO_EQUIPO" != Raspberry\ Pi* ]]; then
    printf 'El equipo no fue identificado como Raspberry Pi: %s\n' "$MODELO_EQUIPO" >&2
    exit 2
  fi
  if [[ -z "$VERSION_PYTHON" ]]; then
    printf 'No se encontró Python 3.\n' >&2
    exit 2
  fi
  if [[ -z "$INTERFAZ_RED" ]]; then
    printf 'No se detectó una conexión de red predeterminada.\n' >&2
    exit 2
  fi
  if [[ "$GESTOR_RED" == "no identificado" ]]; then
    printf 'No se detectó NetworkManager ni dhcpcd.\n' >&2
    exit 2
  fi
}

confirmar_instalacion() {
  local respuesta
  printf '\nResumen de instalación:\n'
  printf '  Equipo:  %s\n' "$MODELO_EQUIPO"
  printf '  Sistema: %s (%s)\n' "$SISTEMA_OPERATIVO" "$ARQUITECTURA"
  printf '  Python:  %s\n' "$VERSION_PYTHON"
  printf '  Red:     %s mediante %s\n' "$INTERFAZ_RED" "$GESTOR_RED"
  if [[ -n "$CONEXION_RED" ]]; then
    printf '  Conexión: %s\n' "$CONEXION_RED"
  fi
  printf '  Punto:   %s\n' "$PUNTO"
  printf '  Usuario: %s\n' "$USUARIO_SERVICIO"
  printf '  Programa: /opt/estacionamiento\n'
  printf '  Configuración privada: /etc/estacionamiento/config.env\n'
  mostrar_configuracion_recopilada
  if [[ "$ASUMIR_SI" -eq 1 ]]; then
    return
  fi
  read -r -p "¿Continuar? [s/N]: " respuesta
  case "$respuesta" in
    s|S|si|SI|sí|SÍ) ;;
    *) printf 'Instalación cancelada; no se realizaron cambios.\n'; exit 0 ;;
  esac
}

configurar_mariadb_tpv() {
  local cantidad_tablas patron_red archivo_temporal
  [[ "$PUNTO" == "tpv" ]] || return

  systemctl enable --now mariadb.service
  archivo_temporal="$(mktemp)"
  printf '[mysqld]\nbind-address=0.0.0.0\n' > "$archivo_temporal"
  install -o root -g root -m 0644 "$archivo_temporal" \
    /etc/mysql/mariadb.conf.d/60-estacionamiento.cnf
  rm -f "$archivo_temporal"
  systemctl restart mariadb.service

  cantidad_tablas="$(mariadb -Nse \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='${DB_NAME}';")"
  if [[ "$cantidad_tablas" == "0" ]]; then
    mariadb -e \
      "CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
    mariadb "$DB_NAME" < /opt/estacionamiento/database/schema.sql
    printf 'Base %s creada e inicializada.\n' "$DB_NAME"
  else
    printf 'La base %s ya contiene %s tablas; se conservó sin importar el esquema.\n' \
      "$DB_NAME" "$cantidad_tablas"
  fi

  patron_red="${IP_FIJA%.*}.%"
  mariadb -e \
    "CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
     ALTER USER '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
     GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
     CREATE USER IF NOT EXISTS '${DB_USER}'@'${patron_red}' IDENTIFIED BY '${DB_PASSWORD}';
     ALTER USER '${DB_USER}'@'${patron_red}' IDENTIFIED BY '${DB_PASSWORD}';
     GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'${patron_red}';
     FLUSH PRIVILEGES;"
  MYSQL_PWD="$DB_PASSWORD" mariadb \
    --host=127.0.0.1 --user="$DB_USER" --database="$DB_NAME" \
    -Nse 'SELECT 1;' >/dev/null
  printf 'Usuario MariaDB configurado para TPV y clientes de la red local.\n'
}

configurar_impresora_punto() {
  local regla_temporal
  [[ "$PUNTO" == "tpv" || "$PUNTO" == "entrada" ]] || return
  regla_temporal="$(mktemp)"
  printf 'SUBSYSTEM=="usb", ATTR{idVendor}=="%s", ATTR{idProduct}=="%s", MODE="0660", GROUP="lp"\n' \
    "${PRINTER_VENDOR_ID,,}" "${PRINTER_PRODUCT_ID,,}" > "$regla_temporal"
  install -o root -g root -m 0644 "$regla_temporal" \
    /etc/udev/rules.d/99-estacionamiento-impresora.rules
  rm -f "$regla_temporal"
  udevadm control --reload-rules
  udevadm trigger --subsystem-match=usb
  printf 'Permisos USB configurados para la impresora %s:%s.\n' \
    "$PRINTER_VENDOR_ID" "$PRINTER_PRODUCT_ID"
}

configurar_inicio_grafico() {
  local directorio_autostart="/home/${USUARIO_SERVICIO}/.config/autostart"
  install -o root -g estacionamiento -m 0755 \
    "$SCRIPT_DIR/iniciar_estacionamiento.sh" \
    /opt/estacionamiento/iniciar_estacionamiento.sh
  install -d -o "$USUARIO_SERVICIO" -g "$USUARIO_SERVICIO" -m 0755 \
    "$directorio_autostart"
  sed "s|@PUNTO@|${PUNTO}|g" "$SCRIPT_DIR/estacionamiento.desktop" \
    > "$directorio_autostart/estacionamiento.desktop"
  chown "$USUARIO_SERVICIO:$USUARIO_SERVICIO" \
    "$directorio_autostart/estacionamiento.desktop"
  chmod 0644 "$directorio_autostart/estacionamiento.desktop"
}

while (($#)); do
  case "$1" in
    --modo-simulacion) MODO="simulacion" ;;
    --modo-raspberry) MODO="raspberry" ;;
    --punto) PUNTO="${2:-}"; shift ;;
    --destino) DESTINO="${2:-}"; shift ;;
    --usuario) USUARIO_SERVICIO="${2:-}"; shift ;;
    --si) ASUMIR_SI=1 ;;
    -h|--help) mostrar_uso; exit 0 ;;
    *) printf 'Opción desconocida: %s\n' "$1" >&2; mostrar_uso; exit 2 ;;
  esac
  shift
done

if [[ -z "$MODO" ]]; then
  MODO="raspberry"
fi

copiar_proyecto() {
  local destino="$1"
  mkdir -p "$destino"
  cp -a "$ORIGEN/Entrada" "$destino/"
  cp -a "$ORIGEN/TPV" "$destino/"
  cp -a "$ORIGEN/Salida" "$destino/"
  cp -a "$ORIGEN/database" "$destino/"
  cp -a "$ORIGEN/requirements.txt" "$destino/"
}

copiar_punto() {
  local destino="$1"
  local punto="$2"
  local carpeta
  case "$punto" in
    entrada) carpeta="Entrada" ;;
    tpv) carpeta="TPV" ;;
    salida) carpeta="Salida" ;;
    *) printf 'Punto inválido al copiar: %s\n' "$punto" >&2; exit 2 ;;
  esac

  mkdir -p "$destino"
  cp -a "$ORIGEN/$carpeta" "$destino/"
  cp -a "$ORIGEN/requirements.txt" "$destino/"
  if [[ "$punto" == "tpv" ]]; then
    cp -a "$ORIGEN/database" "$destino/"
  fi
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
  printf 'Versión instalada: 0.4-recobros\n'
  printf 'Prueba un punto con:\n  %s/simulacion/simular_punto.sh entrada\n' "$destino"
}

instalar_raspberry() {
  if [[ "${EUID}" -ne 0 ]]; then
    printf 'El modo Raspberry debe ejecutarse con sudo.\n' >&2
    exit 2
  fi
  detectar_entorno_raspberry
  validar_entorno_raspberry
  if [[ -z "$PUNTO" ]]; then
    seleccionar_punto_interactivo
  fi
  case "$PUNTO" in entrada|tpv|salida) ;; *) printf 'Indique --punto entrada, tpv o salida.\n' >&2; exit 2 ;; esac
  id "$USUARIO_SERVICIO" >/dev/null 2>&1 || { printf 'No existe el usuario %s.\n' "$USUARIO_SERVICIO" >&2; exit 2; }

  recopilar_configuracion
  crear_configuracion_temporal
  confirmar_instalacion

  instalar_dependencias_sistema

  getent group estacionamiento >/dev/null || groupadd --system estacionamiento
  usermod -a -G estacionamiento,gpio,lp,plugdev,dialout "$USUARIO_SERVICIO"
  install -d -o root -g estacionamiento -m 0750 /etc/estacionamiento
  instalar_configuracion_privada
  configurar_impresora_punto

  install -d -o root -g estacionamiento -m 0755 /opt/estacionamiento
  copiar_punto /opt/estacionamiento "$PUNTO"
  if [[ "$PUNTO" == "entrada" ]]; then
    # La aplicación regenera este archivo en cada boleto. Debe pertenecer al
    # usuario del escritorio para que el inicio gráfico pueda imprimir el QR.
    touch /opt/estacionamiento/Entrada/reducida.png
    chown "$USUARIO_SERVICIO:$USUARIO_SERVICIO" \
      /opt/estacionamiento/Entrada/reducida.png
    chmod 0664 /opt/estacionamiento/Entrada/reducida.png
  fi
  python3 -m venv --system-site-packages /opt/estacionamiento/venv
  /opt/estacionamiento/venv/bin/pip install --upgrade pip
  /opt/estacionamiento/venv/bin/pip install -r /opt/estacionamiento/requirements.txt
  verificar_python /opt/estacionamiento

  configurar_mariadb_tpv

  configurar_inicio_grafico
  configurar_red_y_hostname
  printf '\nInicio gráfico instalado para el punto %s.\n' "$PUNTO"
  printf 'La instalación quedó preparada. Reinicie con:\n  sudo reboot\n'
  printf 'Después del reinicio, el programa abrirá al iniciar el escritorio.\n'
}

case "$MODO" in
  simulacion) instalar_simulacion ;;
  raspberry) instalar_raspberry ;;
  *) mostrar_uso; exit 2 ;;
esac
