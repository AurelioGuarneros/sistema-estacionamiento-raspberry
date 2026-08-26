# Laboratorio de simulación

Esta carpeta prueba la comunicación y las reglas del estacionamiento sin usar
GPIO, barreras ni impresoras USB. Trabaja únicamente con la base indicada en
`config/config.env` y guarda boletos, comprobantes y códigos QR en `resultados/`.

## Protección

Los registros de demostración RFID sólo pueden crearse cuando el nombre de la
base termina en `_prueba`. Al preparar la tarjeta sintética se reinician sus
movimientos anteriores para repetir la prueba. No utilice esta simulación
contra la base operativa.

## Interfaz gráfica

Después de ejecutar el instalador:

```bash
~/estacionamiento-prueba/simulacion/simular_punto.sh gui
```

La ventana permite:

1. expedir un boleto de Entrada;
2. cobrarlo en TPV, con o sin `BA BODEGA AURRERA 114254`;
3. validar el QR en Salida;
4. comprobar que una segunda lectura no abre nuevamente;
5. preparar y probar varias tarjetas RFID de pensionados en cualquier orden;
6. consultar y generar un corte de caja.

Al leer o seleccionar un boleto, TPV muestra la permanencia, el importe normal,
el descuento y el importe final antes de cobrar. Aplicar o quitar la promoción
recalcula estos valores para poder verificar la tarifa.

Las pestañas de TPV y Salida muestran todos los registros pendientes guardados
en MariaDB. Puede elegir cualquier fila con un clic y procesar los boletos
en un orden diferente al de expedición. Al terminar una operación, el campo de
lectura se limpia y queda listo para el siguiente vehículo. La pestaña RFID
también lista las tarjetas y su estado actual.

La pestaña `Corte` muestra los cobros que aún tienen `CorteInc=0`. Al generar
el corte, crea el registro en MariaDB y asigna esos cobros al número de corte
dentro de una sola transacción. En `resultados/` deja un comprobante `.txt` y
un correo `.eml` de muestra; la simulación no envía correo real.

El campo «Minutos de estancia simulada» cambia únicamente la hora de entrada
del boleto de laboratorio, para probar tarifas sin tener que esperar.

## Prueba automática

```bash
~/estacionamiento-prueba/simulacion/simular_punto.sh demo
~/estacionamiento-prueba/simulacion/simular_punto.sh demo-multiple
~/estacionamiento-prueba/simulacion/simular_punto.sh demo-rfid
~/estacionamiento-prueba/simulacion/simular_punto.sh demo-corte
```

La primera prueba hace Entrada → TPV → Salida, aplica la promoción y verifica
el rechazo del segundo uso. `demo-multiple` expide tres boletos, cobra y da
salida en órdenes distintos, dejando uno pendiente. `demo-rfid` prueba tres
pensionados que entran y salen en distinto orden. `demo-corte` comprueba la
cotización antes y después de la promoción y genera un corte real en la base de
laboratorio.

## Prueba manual en terminal

```bash
~/estacionamiento-prueba/simulacion/simular_punto.sh entrada --placa LAB-001 --hace-minutos 95
~/estacionamiento-prueba/simulacion/simular_punto.sh tpv CODIGO_ENTRADA --promocion "BA BODEGA AURRERA 114254"
~/estacionamiento-prueba/simulacion/simular_punto.sh salida CODIGO_SALIDA
```

Copie el código que muestra cada etapa en el siguiente comando.
