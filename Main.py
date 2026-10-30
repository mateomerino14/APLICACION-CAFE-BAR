# Uso: python Main.py

import sys
from PyQt5.QtWidgets import QApplication
from Login import Login
from init_db import inciarBaseDatos


def main():
    inciarBaseDatos()
    aplicacion = QApplication(sys.argv)
    inicio = Login()
    inicio.show()
    sys.exit(aplicacion.exec_())


if __name__ == "__main__":
    main()
