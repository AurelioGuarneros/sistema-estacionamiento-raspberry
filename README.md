# Sistema de estacionamiento Raspberry

Punto de partida confiable del sistema de estacionamiento con tres estaciones:

- `Entrada/entrada.py`: expedicion de boletos y acceso de pensionados.
- `TPV/tpv.py`: cobro, promociones, cortes y administracion.
- `Salida/salida.py`: validacion de pago, tolerancia de 15 minutos y salida de pensionados.

La base de datos central es MariaDB y se ejecuta en la Raspberry TPV.

La estructura versionada, sin datos operativos, se encuentra en `database/`.

## Seguridad

El repositorio no contiene contrasenas, respaldos de MariaDB ni cortes operativos. La configuracion privada se entrega a cada Raspberry mediante variables de entorno. `.env.example` documenta los nombres necesarios, pero nunca debe contener valores reales.

## Estado de esta version

Esta primera version conserva el funcionamiento de la base confiable. La unica adecuacion para publicarla fue separar credenciales y datos operativos del codigo fuente.

## Estructura

```text
Entrada/
  entrada.py
  operacion_entrada.py
Salida/
  salida.py
  operacion_salida.py
TPV/
  tpv.py
  operacion_tpv.py
```

## Próximas etapas

1. Instalacion reproducible en las Raspberry.
2. Empaquetado ejecutable sin distribuir el codigo fuente directamente.
3. Configuracion centralizada de IP y credenciales.
4. Mosquitto y Django para operacion, reportes y consulta remota.
