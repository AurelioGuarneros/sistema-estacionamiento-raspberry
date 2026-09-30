"""Configuracion comun de la impresora de comprobantes de la TPV."""

import os

from escpos.printer import File, Usb

from configuracion_tpv import configuracion_impresora


def crear_impresora():
    """Crea la impresora seleccionada en /etc/estacionamiento/config.env.

    Modos admitidos:
    - usb: acceso PyUSB por identificadores VID/PID (por ejemplo Epson).
    - lp: escritura ESC/POS al dispositivo usblp (por ejemplo POS80).
    """
    configuracion = configuracion_impresora()
    modo = configuracion.get(
        "modo", os.environ.get("ESTACIONAMIENTO_PRINTER_MODE", "usb")
    ).strip().lower()

    if modo == "lp":
        dispositivo = configuracion.get(
            "dispositivo",
            os.environ.get("ESTACIONAMIENTO_PRINTER_DEVICE", "/dev/usb/lp0"),
        ).strip()
        if not dispositivo.startswith("/dev/"):
            raise ValueError(
                "ESTACIONAMIENTO_PRINTER_DEVICE debe ser una ruta dentro de /dev"
            )
        return File(devfile=dispositivo, auto_flush=True)

    if modo == "usb":
        fabricante = int(configuracion.get(
            "vendor_id", os.environ.get("ESTACIONAMIENTO_PRINTER_VENDOR_ID", "04b8")
        ), 16)
        producto = int(configuracion.get(
            "product_id", os.environ.get("ESTACIONAMIENTO_PRINTER_PRODUCT_ID", "0e15")
        ), 16)
        return Usb(fabricante, producto, 0)

    raise ValueError(
        "ESTACIONAMIENTO_PRINTER_MODE debe ser 'usb' para Epson o 'lp' para POS80"
    )
