# Puesta en marcha: sensor de boleto en Raspberry Pi OS 13 Trixie

Esta prueba es para una Raspberry física de **Entrada**. No usa el simulador.

## Conexión prevista

La numeración es BCM:

- sensor de automóvil: GPIO 4;
- botón: GPIO 18;
- sensor de boleto: GPIO 23;
- barrera: GPIO 13, salida activa en bajo;
- tierra del sensor: GND de la Raspberry.

El valor predeterminado del sensor de boleto es **activo en bajo**:

- boleto presente: GPIO 23 conectado a GND;
- boquilla libre: GPIO 23 en alto mediante el pull-up interno.

No aplique 5 V a ningún GPIO. Si el sensor trabaja a 5/12/24 V, use contacto seco,
optoacoplador o salida de colector abierto correctamente adaptada a 3.3 V.

## Instalación limpia en Trixie

Use Raspberry Pi OS 13 Trixie con escritorio y conecte primero red, teclado y pantalla.

```bash
sudo apt update
sudo apt install -y git
git clone https://github.com/AurelioGuarneros/sistema-estacionamiento-raspberry.git
cd sistema-estacionamiento-raspberry
git switch sensor-boleto-entrada
chmod +x install/instalar.sh
sudo ./install/instalar.sh --modo-raspberry --punto entrada
```

El instalador pedirá IP fija, acceso MariaDB de la TPV, impresora, GPIO y polaridad.
No reinicie todavía.

## Prueba física aislada

Detenga temporalmente el arranque de Entrada y pruebe sólo el sensor:

```bash
sudo systemctl stop estacionamiento-entrada.service 2>/dev/null || true
cd /opt/estacionamiento/Entrada
/opt/estacionamiento/venv/bin/python probar_sensor_boleto.py --gpio 23
```

Debe observar alternadamente:

- `BOQUILLA LIBRE` sin papel;
- `BOLETO PRESENTE` al colocar papel frente al sensor;
- `BOQUILLA LIBRE` al retirarlo.

Esta prueba no configura GPIO 13 y no puede abrir la barrera.

Si la lectura aparece invertida, ejecute:

```bash
/opt/estacionamiento/venv/bin/python probar_sensor_boleto.py --gpio 23 --activo-alto
```

y cambie en `/etc/estacionamiento/config.env`:

```ini
ESTACIONAMIENTO_SENSOR_BOLETO_ACTIVO_BAJO=false
```

## Primera prueba completa

Mantenga desacoplada la potencia del motor y pruebe inicialmente el GPIO de barrera
con un LED, relevador de prueba o multímetro.

```bash
sudo systemctl start estacionamiento-entrada.service
journalctl -u estacionamiento-entrada.service -f
```

Secuencia aceptada:

1. detectar automóvil;
2. soltar y presionar botón;
3. registrar e imprimir un boleto;
4. detectar boleto presente;
5. detectar retiro del boleto;
6. emitir un solo pulso de apertura.

La barrera debe permanecer cerrada si el sensor nunca detecta papel o si vence el
tiempo configurado.

Después de confirmar la secuencia con la potencia desacoplada, conecte el control de
la barrera y repita una sola prueba supervisada. Finalmente:

```bash
sudo reboot
```
