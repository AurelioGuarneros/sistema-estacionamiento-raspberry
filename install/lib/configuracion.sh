#!/usr/bin/env bash

# Funciones compartidas por el instalador interactivo. Este archivo se carga
# desde instalar.sh y no debe ejecutarse directamente.

NOMBRE_EQUIPO=""
IP_FIJA=""
PREFIJO_RED="24"
PUERTA_ENLACE=""
DNS_RED=""
DB_HOST=""
DB_USER="estacionamiento_app"
DB_PASSWORD=""
DB_NAME="Parqueadero1"
SMTP_HOST=""
SMTP_PORT="587"
SMTP_TLS="true"
SMTP_USER=""
SMTP_PASSWORD=""
EMAIL_DATABASE=""
EMAIL_CORTE=""
EMAIL_NOTIFICACION=""
PRINTER_MODE="usb"
PRINTER_DEVICE="/dev/usb/lp0"
PRINTER_VENDOR_ID="04b8"
PRINTER_PRODUCT_ID="0e15"
PASSWORD_CONFIGURACION=""
CONFIG_TEMP=""

validar_ipv4() {
  local direccion="$1"
  local octeto
  local -a octetos
  IFS='.' read -r -a octetos <<< "$direccion"
  [[ "${#octetos[@]}" -eq 4 ]] || return 1
  for octeto in "${octetos[@]}"; do
    [[ "$octeto" =~ ^[0-9]{1,3}$ ]] || return 1
    ((10#$octeto >= 0 && 10#$octeto <= 255)) || return 1
  done
}

validar_identificador() {
  [[ "$1" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]
}

validar_hostname() {
  [[ "$1" =~ ^[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?$ ]]
}

validar_puerto() {
  [[ "$1" =~ ^[0-9]{1,5}$ ]] && ((10#$1 >= 1 && 10#$1 <= 65535))
}

validar_usb_id() {
  [[ "$1" =~ ^[0-9A-Fa-f]{4}$ ]]
}

validar_dispositivo_impresora() {
  [[ "$1" =~ ^/dev/[A-Za-z0-9._/-]+$ ]]
}

validar_secreto_sql() {
  [[ "$1" =~ ^[A-Za-z0-9._@%+!-]{12,128}$ ]]
}

preguntar_valor() {
  local variable="$1"
  local texto="$2"
  local predeterminado="${3:-}"
  local valor
  if [[ -n "$predeterminado" ]]; then
    read -r -p "$texto [$predeterminado]: " valor
    valor="${valor:-$predeterminado}"
  else
    read -r -p "$texto: " valor
  fi
  printf -v "$variable" '%s' "$valor"
}

preguntar_ipv4() {
  local variable="$1"
  local texto="$2"
  local predeterminado="${3:-}"
  local respuesta_ipv4
  while true; do
    preguntar_valor respuesta_ipv4 "$texto" "$predeterminado"
    if validar_ipv4 "$respuesta_ipv4"; then
      printf -v "$variable" '%s' "$respuesta_ipv4"
      return
    fi
    printf 'Dirección IPv4 inválida: %s\n' "$respuesta_ipv4" >&2
  done
}

preguntar_secreto() {
  local variable="$1"
  local texto="$2"
  local permitir_vacio="${3:-no}"
  local valor confirmacion
  while true; do
    read -r -s -p "$texto: " valor
    printf '\n'
    if [[ -z "$valor" && "$permitir_vacio" == "si" ]]; then
      printf -v "$variable" '%s' ""
      return
    fi
    if ! validar_secreto_sql "$valor"; then
      printf 'Use de 12 a 128 caracteres: letras, números y . _ @ %% + ! -\n' >&2
      continue
    fi
    read -r -s -p "Repita el valor: " confirmacion
    printf '\n'
    if [[ "$valor" != "$confirmacion" ]]; then
      printf 'Los valores no coinciden.\n' >&2
      continue
    fi
    printf -v "$variable" '%s' "$valor"
    return
  done
}

preguntar_password_local() {
  local variable="$1"
  local texto="$2"
  local valor confirmacion
  while true; do
    read -r -s -p "$texto: " valor
    printf '\n'
    if ((${#valor} < 4 || ${#valor} > 64)); then
      printf 'Use una contraseña de 4 a 64 caracteres.\n' >&2
      continue
    fi
    read -r -s -p "Repita la contraseña: " confirmacion
    printf '\n'
    if [[ "$valor" != "$confirmacion" ]]; then
      printf 'Las contraseñas no coinciden.\n' >&2
      continue
    fi
    printf -v "$variable" '%s' "$valor"
    return
  done
}

proponer_ip() {
  local base="$1"
  local ultimo
  case "$PUNTO" in
    tpv) ultimo="210" ;;
    entrada) ultimo="211" ;;
    salida) ultimo="212" ;;
  esac
  if validar_ipv4 "$base"; then
    printf '%s.%s' "${base%.*}" "$ultimo"
  fi
}

comprobar_ip_disponible() {
  local direccion="$1"
  local ip_actual
  ip_actual="$(ip -4 -o address show dev "$INTERFAZ_RED" 2>/dev/null | awk 'NR == 1 {split($4, partes, "/"); print partes[1]}')"
  if [[ "$direccion" == "$ip_actual" ]]; then
    return
  fi
  if ping -c 1 -W 1 "$direccion" >/dev/null 2>&1; then
    printf 'La dirección %s ya responde en la red. Elija otra IP.\n' "$direccion" >&2
    exit 2
  fi
}

recopilar_configuracion() {
  local gateway_actual ip_propuesta password_generada
  gateway_actual="$(ip route show default 2>/dev/null | awk 'NR == 1 {print $3}')"
  NOMBRE_EQUIPO="${PUNTO}-lab"
  preguntar_valor NOMBRE_EQUIPO "Nombre de esta Raspberry" "$NOMBRE_EQUIPO"
  validar_hostname "$NOMBRE_EQUIPO" || {
    printf 'Nombre de equipo inválido: use letras, números y guiones, sin guion al inicio o al final.\n' >&2
    exit 2
  }

  ip_propuesta="$(proponer_ip "$gateway_actual")"
  preguntar_ipv4 IP_FIJA "IP fija para ${PUNTO}" "$ip_propuesta"
  comprobar_ip_disponible "$IP_FIJA"
  preguntar_ipv4 PUERTA_ENLACE "Puerta de enlace" "$gateway_actual"
  preguntar_ipv4 DNS_RED "Servidor DNS" "$PUERTA_ENLACE"

  preguntar_valor DB_NAME "Nombre de la base de datos" "$DB_NAME"
  validar_identificador "$DB_NAME" || {
    printf 'Nombre de base inválido: %s\n' "$DB_NAME" >&2
    exit 2
  }
  preguntar_valor DB_USER "Usuario de aplicación MariaDB" "$DB_USER"
  validar_identificador "$DB_USER" || {
    printf 'Usuario MariaDB inválido: %s\n' "$DB_USER" >&2
    exit 2
  }

  if [[ "$PUNTO" == "tpv" ]]; then
    DB_HOST="127.0.0.1"
    password_generada="$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')"
    DB_PASSWORD="$password_generada"
    printf 'Se generó automáticamente una contraseña segura para MariaDB.\n'
    printf 'Se guardará en un archivo privado para configurar Entrada y Salida.\n'
    preguntar_password_local PASSWORD_CONFIGURACION \
      "Contraseña para abrir la configuración de la TPV"

    local impresora_detectada opcion_impresora
    if lsusb 2>/dev/null | grep -qi '0416:5011'; then
      PRINTER_MODE="lp"
      PRINTER_VENDOR_ID="0416"
      PRINTER_PRODUCT_ID="5011"
      printf 'Impresora POS80 detectada en %s.\n' "$PRINTER_DEVICE"
    else
      impresora_detectada="$(lsusb 2>/dev/null | awk '/Epson/ {print $6; exit}')"
    fi
    if [[ "${impresora_detectada:-}" =~ ^([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})$ ]]; then
      PRINTER_VENDOR_ID="${BASH_REMATCH[1]}"
      PRINTER_PRODUCT_ID="${BASH_REMATCH[2]}"
      printf 'Impresora USB detectada: %s:%s\n' "$PRINTER_VENDOR_ID" "$PRINTER_PRODUCT_ID"
    fi

    printf '\nSeleccione la impresora de la TPV:\n'
    printf '  1) Epson por USB (VID/PID)\n'
    printf '  2) POS80 mediante /dev/usb/lp0\n'
    while true; do
      if [[ "$PRINTER_MODE" == "lp" ]]; then
        read -r -p "Opción [1-2] [2]: " opcion_impresora
        opcion_impresora="${opcion_impresora:-2}"
      else
        read -r -p "Opción [1-2] [1]: " opcion_impresora
        opcion_impresora="${opcion_impresora:-1}"
      fi
      case "$opcion_impresora" in
        1) PRINTER_MODE="usb"; break ;;
        2) PRINTER_MODE="lp"; break ;;
        *) printf 'Opción inválida. Escriba 1 o 2.\n' >&2 ;;
      esac
    done

    preguntar_valor PRINTER_VENDOR_ID "ID fabricante USB de la impresora" "$PRINTER_VENDOR_ID"
    preguntar_valor PRINTER_PRODUCT_ID "ID producto USB de la impresora" "$PRINTER_PRODUCT_ID"
    validar_usb_id "$PRINTER_VENDOR_ID" && validar_usb_id "$PRINTER_PRODUCT_ID" || {
      printf 'Los identificadores USB deben tener exactamente cuatro dígitos hexadecimales.\n' >&2
      exit 2
    }
    if [[ "$PRINTER_MODE" == "lp" ]]; then
      preguntar_valor PRINTER_DEVICE "Dispositivo Linux de la impresora" "$PRINTER_DEVICE"
      validar_dispositivo_impresora "$PRINTER_DEVICE" || {
        printf 'Ruta de impresora inválida: %s\n' "$PRINTER_DEVICE" >&2
        exit 2
      }
    fi

    printf '\nConfiguración de correo de TPV (puede dejarla vacía y completarla después).\n'
    preguntar_valor SMTP_HOST "Servidor SMTP" ""
    if [[ -n "$SMTP_HOST" ]]; then
      preguntar_valor SMTP_PORT "Puerto SMTP" "$SMTP_PORT"
      validar_puerto "$SMTP_PORT" || { printf 'Puerto SMTP inválido (1-65535).\n' >&2; exit 2; }
      preguntar_valor SMTP_TLS "Usar TLS (true/false)" "$SMTP_TLS"
      case "$SMTP_TLS" in true|false) ;; *) printf 'TLS debe ser true o false.\n' >&2; exit 2 ;; esac
      preguntar_valor SMTP_USER "Correo origen" ""
      preguntar_secreto SMTP_PASSWORD "Contraseña o clave de aplicación del correo" si
      preguntar_valor EMAIL_DATABASE "Destino de respaldos" ""
      preguntar_valor EMAIL_CORTE "Destino de cortes" ""
      preguntar_valor EMAIL_NOTIFICACION "Destino de avisos" "$EMAIL_CORTE"
    fi
  else
    preguntar_ipv4 DB_HOST "IP de la TPV" "${IP_FIJA%.*}.210"
    preguntar_secreto DB_PASSWORD "Contraseña MariaDB generada por TPV"
  fi
}

mostrar_configuracion_recopilada() {
  printf '  Hostname: %s\n' "$NOMBRE_EQUIPO"
  printf '  IP fija: %s/%s\n' "$IP_FIJA" "$PREFIJO_RED"
  printf '  Gateway: %s\n' "$PUERTA_ENLACE"
  printf '  DNS:     %s\n' "$DNS_RED"
  printf '  MariaDB: %s@%s/%s\n' "$DB_USER" "$DB_HOST" "$DB_NAME"
  if [[ "$PUNTO" == "tpv" && -n "$SMTP_HOST" ]]; then
    printf '  SMTP:    %s:%s, origen %s\n' "$SMTP_HOST" "$SMTP_PORT" "$SMTP_USER"
  fi
  if [[ "$PUNTO" == "tpv" ]]; then
    if [[ "$PRINTER_MODE" == "lp" ]]; then
      printf '  Impresora: POS80 %s (%s:%s)\n' \
        "$PRINTER_DEVICE" "$PRINTER_VENDOR_ID" "$PRINTER_PRODUCT_ID"
    else
      printf '  Impresora: Epson USB %s:%s\n' "$PRINTER_VENDOR_ID" "$PRINTER_PRODUCT_ID"
    fi
  fi
}

escapar_valor_env() {
  local valor="$1"
  valor="${valor//\\/\\\\}"
  valor="${valor//\"/\\\"}"
  printf '"%s"' "$valor"
}

crear_configuracion_temporal() {
  CONFIG_TEMP="$(mktemp)"
  chmod 600 "$CONFIG_TEMP"
  {
    printf 'ESTACIONAMIENTO_PUNTO=%s\n' "$(escapar_valor_env "$PUNTO")"
    printf 'ESTACIONAMIENTO_HOSTNAME=%s\n' "$(escapar_valor_env "$NOMBRE_EQUIPO")"
    printf 'ESTACIONAMIENTO_DB_HOST=%s\n' "$(escapar_valor_env "$DB_HOST")"
    printf 'ESTACIONAMIENTO_DB_USER=%s\n' "$(escapar_valor_env "$DB_USER")"
    printf 'ESTACIONAMIENTO_DB_PASSWORD=%s\n' "$(escapar_valor_env "$DB_PASSWORD")"
    printf 'ESTACIONAMIENTO_DB_NAME=%s\n' "$(escapar_valor_env "$DB_NAME")"
    printf 'ESTACIONAMIENTO_SMTP_HOST=%s\n' "$(escapar_valor_env "$SMTP_HOST")"
    printf 'ESTACIONAMIENTO_SMTP_PORT=%s\n' "$(escapar_valor_env "$SMTP_PORT")"
    printf 'ESTACIONAMIENTO_SMTP_TLS=%s\n' "$(escapar_valor_env "$SMTP_TLS")"
    printf 'ESTACIONAMIENTO_SMTP_USER=%s\n' "$(escapar_valor_env "$SMTP_USER")"
    printf 'ESTACIONAMIENTO_SMTP_PASSWORD=%s\n' "$(escapar_valor_env "$SMTP_PASSWORD")"
    printf 'ESTACIONAMIENTO_EMAIL_DATABASE=%s\n' "$(escapar_valor_env "$EMAIL_DATABASE")"
    printf 'ESTACIONAMIENTO_EMAIL_CORTE=%s\n' "$(escapar_valor_env "$EMAIL_CORTE")"
    printf 'ESTACIONAMIENTO_EMAIL_NOTIFICACION=%s\n' "$(escapar_valor_env "$EMAIL_NOTIFICACION")"
    printf 'ESTACIONAMIENTO_PRINTER_MODE=%s\n' "$(escapar_valor_env "$PRINTER_MODE")"
    printf 'ESTACIONAMIENTO_PRINTER_DEVICE=%s\n' "$(escapar_valor_env "$PRINTER_DEVICE")"
    printf 'ESTACIONAMIENTO_PRINTER_VENDOR_ID=%s\n' "$(escapar_valor_env "$PRINTER_VENDOR_ID")"
    printf 'ESTACIONAMIENTO_PRINTER_PRODUCT_ID=%s\n' "$(escapar_valor_env "$PRINTER_PRODUCT_ID")"
    if [[ "$PUNTO" == "tpv" ]]; then
      printf 'ESTACIONAMIENTO_PASSWORD_CONFIGURACION=%s\n' \
        "$(escapar_valor_env "$PASSWORD_CONFIGURACION")"
    fi
    printf 'DISPLAY=":0"\n'
  } > "$CONFIG_TEMP"
}

instalar_configuracion_privada() {
  local destino="/etc/estacionamiento/config.env"
  if [[ -f "$destino" ]]; then
    cp -a "$destino" "${destino}.respaldo-$(date +%Y%m%d-%H%M%S)"
  fi
  install -o root -g estacionamiento -m 0640 "$CONFIG_TEMP" "$destino"
  if [[ "$PUNTO" == "tpv" ]]; then
    {
      printf 'ESTACIONAMIENTO_DB_HOST=%s\n' "$(escapar_valor_env "$IP_FIJA")"
      printf 'ESTACIONAMIENTO_DB_USER=%s\n' "$(escapar_valor_env "$DB_USER")"
      printf 'ESTACIONAMIENTO_DB_PASSWORD=%s\n' "$(escapar_valor_env "$DB_PASSWORD")"
      printf 'ESTACIONAMIENTO_DB_NAME=%s\n' "$(escapar_valor_env "$DB_NAME")"
    } > /etc/estacionamiento/credenciales-clientes.env
    chown root:estacionamiento /etc/estacionamiento/credenciales-clientes.env
    chmod 0640 /etc/estacionamiento/credenciales-clientes.env
  fi
  rm -f "$CONFIG_TEMP"
  CONFIG_TEMP=""
}

configurar_red_y_hostname() {
  hostnamectl set-hostname "$NOMBRE_EQUIPO"
  if grep -q '^127\.0\.1\.1' /etc/hosts; then
    sed -i "s/^127\.0\.1\.1.*/127.0.1.1\t${NOMBRE_EQUIPO}/" /etc/hosts
  else
    printf '127.0.1.1\t%s\n' "$NOMBRE_EQUIPO" >> /etc/hosts
  fi
  if [[ "$GESTOR_RED" != "NetworkManager" || -z "$CONEXION_RED" ]]; then
    printf 'La configuración automática de IP requiere NetworkManager.\n' >&2
    exit 2
  fi
  nmcli connection modify "$CONEXION_RED" \
    ipv4.method manual \
    ipv4.addresses "${IP_FIJA}/${PREFIJO_RED}" \
    ipv4.gateway "$PUERTA_ENLACE" \
    ipv4.dns "$DNS_RED"
  printf 'La IP fija se activará después de reiniciar.\n'
}
