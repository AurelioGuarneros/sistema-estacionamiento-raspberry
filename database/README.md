# Base de datos MariaDB

La base central del estacionamiento se llama `Parqueadero1` y se instala en la Raspberry TPV.

## Contenido

- `schema.sql`: fotografía vigente de la estructura completa, sin registros reales.
- `migrations/001_estructura_inicial.sql`: punto inicial para controlar cambios futuros.
- `instalar_base.sh`: asistente para instalar la estructura en una TPV nueva.

## Instalación en una TPV nueva

Desde la raíz del repositorio:

```bash
cd database
chmod +x instalar_base.sh
./instalar_base.sh
```

El usuario administrativo sugerido es `Aurelio`. El instalador solicitará la contraseña directamente en MariaDB; no la guarda ni la muestra.

## Actualizaciones futuras

Cada modificación estructural debe agregarse como una migración nueva, sin alterar las migraciones ya aplicadas:

```text
002_nombre_del_cambio.sql
003_otro_cambio.sql
```

Los respaldos que contienen boletos, cobros, usuarios o pensionados no deben almacenarse en GitHub.

## Advertencia

`schema.sql` contiene instrucciones `DROP TABLE IF EXISTS`. El instalador se detiene si detecta tablas existentes para evitar borrar una base en operación. Para una instalación nueva, la base debe estar vacía.
