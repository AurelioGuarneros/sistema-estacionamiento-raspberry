"""Configuracion comun de la impresora de comprobantes de la TPV."""

import os

from escpos.printer import File, Usb


def crear_impresora():
    """Crea la impresora seleccionada en /etc/estacionamiento/config.env.

    Modos admitidos:
    - usb: acceso PyUSB por identificadores VID/PID (por ejemplo Epson).
    - lp: escritura ESC/POS al dispositivo usblp (por ejemplo POS80).
    """
    modo = os.environ.get("ESTACIONAMIENTO_PRINTER_MODE", "usb").strip().lower()

    if modo == "lp":
        dispositivo = os.environ.get(
            "ESTACIONAMIENTO_PRINTER_DEVICE", "/dev/usb/lp0"
        ).strip()
        if not dispositivo.startswith("/dev/"):
            raise ValueError(
                "ESTACIONAMIENTO_PRINTER_DEVICE debe ser una ruta dentro de /dev"
            )
        return File(devfile=dispositivo, auto_flush=True)

    if modo == "usb":
        fabricante = int(
            os.environ.get("ESTACIONAMIENTO_PRINTER_VENDOR_ID", "04b8"), 16
        )
        producto = int(
            os.environ.get("ESTACIONAMIENTO_PRINTER_PRODUCT_ID", "0e15"), 16
        )
        return Usb(fabricante, producto, 0)

    raise ValueError(
        "ESTACIONAMIENTO_PRINTER_MODE debe ser 'usb' para Epson o 'lp' para POS80"
    )
