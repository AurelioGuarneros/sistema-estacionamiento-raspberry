#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEMA_FILE="$SCRIPT_DIR/schema.sql"
DATABASE_NAME="Parqueadero1"

if ! command -v mariadb >/dev/null 2>&1; then
    echo "MariaDB no está instalado."
    echo "Instálelo con: sudo apt update && sudo apt install mariadb-server"
    exit 1
fi

if [[ ! -f "$SCHEMA_FILE" ]]; then
    echo "No se encontró: $SCHEMA_FILE"
    exit 1
fi

read -r -p "Usuario administrador de MariaDB [Aurelio]: " DB_ADMIN_USER
DB_ADMIN_USER="${DB_ADMIN_USER:-Aurelio}"

echo "Se comprobará si la base $DATABASE_NAME ya contiene tablas."
echo "MariaDB solicitará la contraseña de $DB_ADMIN_USER."
TABLE_COUNT="$(mariadb -u "$DB_ADMIN_USER" -p -Nse \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$DATABASE_NAME';")"

if [[ "$TABLE_COUNT" != "0" ]]; then
    echo "Operación cancelada: $DATABASE_NAME contiene $TABLE_COUNT tablas."
    echo "No se modificó la base existente."
    exit 1
fi

echo "Se instalará una base nueva llamada $DATABASE_NAME."
echo "MariaDB volverá a solicitar la contraseña de $DB_ADMIN_USER."
mariadb -u "$DB_ADMIN_USER" -p -e \
    "CREATE DATABASE IF NOT EXISTS $DATABASE_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
mariadb -u "$DB_ADMIN_USER" -p "$DATABASE_NAME" < "$SCHEMA_FILE"

echo "Estructura instalada correctamente."
mariadb -u "$DB_ADMIN_USER" -p -e \
    "SELECT table_name FROM information_schema.tables WHERE table_schema='$DATABASE_NAME' ORDER BY table_name;"
