# Instalación controlada

El instalador conserva los programas de Entrada, TPV y Salida sin modificar su
lógica. Tiene dos modalidades:

```bash
./install/instalar.sh --modo-simulacion --destino "$HOME/estacionamiento-prueba"
sudo ./install/instalar.sh --modo-raspberry --punto entrada
```

Los puntos válidos en Raspberry son `entrada`, `tpv` y `salida`.

## Modo simulación

- Copia el sistema a una carpeta independiente.
- crea `config/config.env` a partir de `.env.example`;
- verifica la sintaxis de todos los archivos Python;
- no instala servicios, no activa GPIO y no busca impresoras;
- genera comandos de simulación en `simulacion/`.

## Modo Raspberry

- instala el código en `/opt/estacionamiento`;
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
