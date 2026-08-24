#!/usr/bin/env python3
"""Prueba el lector RFID y la consulta del pensionado sin mover la barrera."""

from operacion_entrada import Operacion


def main():
    print("PRUEBA DE LECTOR RFID - no abre la barrera")
    print("Acerque una tarjeta. Para terminar presione Ctrl+C.")
    db = Operacion()

    while True:
        lectura = input("RFID> ")
        normalizada = ''.join(lectura.strip().split())
        print("Lectura cruda:", repr(lectura))
        print("Valor normalizado:", repr(normalizada), "longitud:", len(normalizada))

        if not normalizada.isdigit():
            print("RESULTADO: el lector envió caracteres no numéricos")
            continue

        try:
            tarjeta = int(normalizada)
            id_cliente = db.ValidarPen(tarjeta)
            if id_cliente is None:
                print("RESULTADO: el lector funciona, pero la tarjeta no existe en Pensionados")
                continue

            datos = db.ConsultaPensionado(id_cliente)
            print("RESULTADO: tarjeta encontrada")
            print("Id_cliente:", id_cliente)
            print("Fecha_vigencia, Estatus, Vigencia, Tolerancia:", datos)
        except Exception as error:
            print("RESULTADO: error al consultar MariaDB:", error)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrueba finalizada")
