# Instalación controlada

El instalador conserva los programas de Entrada, TPV y Salida sin modificar su
lógica. Tiene dos modalidades:

```bash
./install/instalar.sh --modo-simulacion --destino "$HOME/estacionamiento-prueba"
sudo ./install/instalar.sh --modo-raspberry --punto entrada
```

Los puntos válidos en Raspberry son `entrada`, `tpv` y `salida`.

En una Raspberry nueva puede ejecutar simplemente:

```bash
sudo ./install/instalar.sh
```

El instalador mostrará un menú para elegir Entrada, TPV o Salida, presentará
un resumen y solicitará confirmación antes de realizar cambios. El parámetro
`--punto` se conserva para instalaciones automatizadas.

Antes de instalar, el asistente comprueba y muestra:

- modelo de Raspberry Pi y arquitectura ARM;
- versión de Raspberry Pi OS y Python;
- interfaz de red activa;
- uso de NetworkManager (Trixie) o `dhcpcd` (sistemas anteriores);
- nombre de la conexión de NetworkManager cuando esté disponible.

Si el equipo, Python o la red no son compatibles, se detiene antes de instalar
paquetes o escribir configuración.

En Raspberry Pi OS Trixie, el asistente también solicita y prepara:

- nombre del equipo e IP fija mediante NetworkManager;
- puerta de enlace y DNS;
- nombre, usuario y contraseña privada de MariaDB;
- servidor, puerto, TLS, origen y destinos de correo cuando el punto es TPV.
- impresora Epson por VID/PID USB o impresora POS80 mediante `/dev/usb/lp0`.

La nueva IP no se activa durante la instalación; queda programada para el
siguiente reinicio, evitando cortar una sesión SSH o VNC a la mitad.

El programa se registra en el inicio automático del escritorio. Este método es
compatible con la sesión gráfica de Raspberry Pi OS Trixie y evita intentar
abrir Tkinter antes de que Wayland/XWayland esté disponible.

Cuando se selecciona TPV, el instalador:

- instala y habilita MariaDB;
- crea la base únicamente si todavía no contiene tablas;
- importa `database/schema.sql` sólo sobre esa base vacía;
- crea un usuario limitado a la red local;
- guarda en `/etc/estacionamiento/credenciales-clientes.env` los datos que se
  introducirán después en Entrada y Salida.

Las contraseñas no se muestran en el resumen ni se guardan en GitHub. Los
archivos privados quedan accesibles únicamente para `root` y el grupo
`estacionamiento`.

## Modo simulación

- Copia el sistema a una carpeta independiente.
- crea `config/config.env` a partir de `.env.example`;
- crea un entorno Python aislado en `venv/` e instala `requirements.txt`;
- verifica la sintaxis de todos los archivos Python;
- no instala servicios, no activa GPIO y no busca impresoras;
- instala automáticamente `python3-venv` y `python3-tk` en Debian/Ubuntu;
- genera boletos, comprobantes y códigos QR de laboratorio;
- permite probar Entrada → TPV → Salida y pensionados RFID.

Para abrir la simulación gráfica:

```bash
~/estacionamiento-prueba/simulacion/simular_punto.sh gui
```

Para ejecutar la comprobación automática del boleto y su uso único:

```bash
~/estacionamiento-prueba/simulacion/simular_punto.sh demo
```

La simulación debe apuntar únicamente a una base de laboratorio, por ejemplo
`Parqueadero1_prueba`. La creación de pensionados de demostración se bloquea
si el nombre de la base no termina en `_prueba`.

## Modo Raspberry

- instala el código en `/opt/estacionamiento`;
- copia únicamente el punto seleccionado; la TPV recibe además los archivos de
  estructura y migración de MariaDB;
- crea el grupo privado `estacionamiento`;
- conserva la configuración en `/etc/estacionamiento/config.env`;
- crea un entorno virtual en `/opt/estacionamiento/venv`;
- instala y habilita solamente el servicio del punto seleccionado.

El archivo privado queda con propietario `root`, grupo `estacionamiento` y
permisos `640`. No se sube a GitHub.

Después de instalar, complete los valores reales:

```bash
sudo nano /etc/estacionamiento/config.env
sudo systemctl restart estacionamiento-entrada.service
```

Cambie `entrada` por `tpv` o `salida`, según la máquina.

En la instalación de la TPV también se solicita la contraseña que protege el
botón **CONFIGURACION**. Se guarda únicamente en el archivo privado como
`ESTACIONAMIENTO_PASSWORD_CONFIGURACION`.

## Cambiar la impresora de la TPV

La selección se guarda en `/etc/estacionamiento/config.env`. Para una Epson
con acceso PyUSB:

```bash
ESTACIONAMIENTO_PRINTER_MODE=usb
ESTACIONAMIENTO_PRINTER_VENDOR_ID=04b8
ESTACIONAMIENTO_PRINTER_PRODUCT_ID=0e15
```

Para la impresora térmica POS80 `0416:5011` detectada como `usblp`:

```bash
ESTACIONAMIENTO_PRINTER_MODE=lp
ESTACIONAMIENTO_PRINTER_DEVICE=/dev/usb/lp0
ESTACIONAMIENTO_PRINTER_VENDOR_ID=0416
ESTACIONAMIENTO_PRINTER_PRODUCT_ID=5011
```

Después de cambiarla, reinicie la aplicación TPV o cierre y vuelva a abrir su
sesión gráfica.
