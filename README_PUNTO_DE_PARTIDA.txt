SISTEMA DE ESTACIONAMIENTO - BASE CONFIABLE
===========================================

Esta carpeta es el punto de partida oficial para las siguientes mejoras y
correcciones del sistema.

ESTRUCTURA
----------

Entrada/
    entrada.py
    operacion_entrada.py

Salida/
    salida.py
    operacion_salida.py

TPV/
    tpv.py
    operacion_tpv.py

Cada carpeta conserva los recursos y modulos auxiliares que necesita su punto.

EJECUCION
---------

Entrada:
    cd Entrada
    python3 entrada.py

Salida:
    cd Salida
    python3 salida.py

TPV:
    cd TPV
    python3 tpv.py

CAMBIO FUNCIONAL AUTORIZADO EN ESTA BASE
----------------------------------------

Solamente se agrego en Salida una tolerancia de 15 minutos contados desde la
fecha y hora de pago almacenada en Entradas.Salida.

- Dentro de los 15 minutos abre la barrera y muestra el tiempo restante.
- Después de 15 minutos no abre y muestra que la tolerancia vencio.
- El boleto sigue autorizado una sola vez.

Los cambios de nombre en imports solamente permiten utilizar los nombres
normalizados operacion_entrada.py, operacion_salida.py y operacion_tpv.py.
