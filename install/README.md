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
