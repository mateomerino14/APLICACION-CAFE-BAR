import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from Pop_up_Registro_Seccion import Pop_up_Registro_Seccion
from ModificacionSeccion import ModificacionSeccion
from Rutas import get_db_path


DB_PATH = get_db_path()


class Administracion_Secciones_Mesas(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        self.set_up()

    def set_up(self):
        self.numeroElemento = 0
        self.resultados = []
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.layoutPrincipal.setSpacing(25)
        self.crearAreaSecciones()
        self.showMaximized()

    def crearAreaSecciones(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT nombSeccion, descripcion FROM Seccion")
        self.resultados = c.fetchall()
        conn.close()

        titulo = QLabel("◷ SECCIONES ◷")
        titulo.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                qproperty-alignment: AlignCenter;
            }
        """)
        self.layoutPrincipal.addWidget(titulo)
        layoutSecciones = QHBoxLayout()
        layoutSecciones.setSpacing(25)
        self.botonAnterior = QPushButton("◀")
        self.botonAnterior.setCursor(Qt.PointingHandCursor)
        self.botonAnterior.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 28px;
                font-weight: bold;
                border-radius: 35px;
                min-width: 70px;
                max-width: 70px;
                min-height: 70px;
                max-height: 70px;
                border: 3px solid #2980b9;
            }
            QPushButton:hover {
                background-color: #2980b9;
                transform: scale(1.05);
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                border-color: #95a5a6;
                color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.botonAnterior.clicked.connect(self.anteriorSecuencia)

        self.layoutCentral = QHBoxLayout()
        self.layoutCentral.setSpacing(30)

        self.botonSiguiente = QPushButton("▶")
        self.botonSiguiente.setCursor(Qt.PointingHandCursor)
        self.botonSiguiente.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 28px;
                font-weight: bold;
                border-radius: 35px;
                min-width: 70px;
                max-width: 70px;
                min-height: 70px;
                max-height: 70px;
                border: 3px solid #2980b9;
            }
            QPushButton:hover {
                background-color: #2980b9;
                transform: scale(1.05);
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                border-color: #95a5a6;
                color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.botonSiguiente.clicked.connect(self.siguienteSecuencia)
        layoutSecciones.addWidget(self.botonAnterior, alignment=Qt.AlignCenter)
        layoutSecciones.addLayout(self.layoutCentral)
        layoutSecciones.addWidget(self.botonSiguiente, alignment=Qt.AlignCenter)
        self.layoutPrincipal.addLayout(layoutSecciones)
        self.actualizarVista()
        botonNuevo = QPushButton("➕ AÑADIR NUEVA SECCIÓN")
        botonNuevo.setCursor(Qt.PointingHandCursor)
        botonNuevo.clicked.connect(self.crearSeccionRegistro)
        botonNuevo.setFixedSize(350, 60)
        botonNuevo.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                padding: 15px 30px;
                border: 2px solid #219653;
            }
            QPushButton:hover {
                background-color: #219653;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.layoutPrincipal.addWidget(botonNuevo, alignment=Qt.AlignCenter)

    def crearSeccionRegistro(self):
        pagina = Pop_up_Registro_Seccion(self)
        pagina.exec_()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT nombSeccion, descripcion FROM Seccion")
        self.resultados = c.fetchall()
        conn.close()
        self.actualizarVista()

    def actualizarVista(self):
        self.vaciarLayout(self.layoutCentral)
        inicio = self.numeroElemento
        fin = min(inicio + 4, len(self.resultados))
        for i in range(inicio, fin):
            dupla = self.resultados[i]
            layoutElemento = QVBoxLayout()
            layoutElemento.setSpacing(15)

            boton = QPushButton(dupla[0])
            boton.setCursor(Qt.PointingHandCursor)
            boton.setFixedSize(220, 220)
            boton.setStyleSheet("""
                QPushButton {
                    background-color: #34495e;
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                    border-radius: 15px;
                    border: 3px solid #2c3e50;
                }
                QPushButton:hover {
                    background-color: #2c3e50;
                    transform: scale(1.03);
                }
                QPushButton:pressed {
                    background-color: #1a252f;
                }
            """)
            etiqueta = QLabel(dupla[1])
            etiqueta.setStyleSheet("""
                QLabel {
                    color: #2c3e50;
                    font-size: 16px;
                    font-weight: 500;
                    padding: 10px;
                    background-color: #ecf0f1;
                    border-radius: 8px;
                    border: 1px solid #bdc3c7;
                    qproperty-alignment: AlignCenter;
                }
            """)
            etiqueta.setFixedWidth(220)
            etiqueta.setFixedHeight(80)
            etiqueta.setWordWrap(True)
            etiqueta.setAlignment(Qt.AlignCenter)
            boton.clicked.connect(
                lambda _, nomSec=boton.text().strip(), descSec=etiqueta.text().strip(): self.cargarRegistro(
                    nomSec, descSec
                )
            )
            layoutElemento.addWidget(boton, alignment=Qt.AlignCenter)
            layoutElemento.addWidget(etiqueta, alignment=Qt.AlignCenter)
            self.layoutCentral.addLayout(layoutElemento)

        elementos_faltantes = 4 - (fin - inicio)
        for _ in range(elementos_faltantes):
            layoutVacio = QVBoxLayout()
            layoutVacio.setSpacing(15)
            botonVacio = QPushButton()
            botonVacio.setFixedSize(220, 220)
            botonVacio.setStyleSheet("""
                background: transparent; 
                border: 3px dashed #bdc3c7;
                border-radius: 15px;
            """)
            botonVacio.setEnabled(False)
            etiquetaVacia = QLabel()
            etiquetaVacia.setFixedSize(220, 80)
            layoutVacio.addWidget(botonVacio, alignment=Qt.AlignCenter)
            layoutVacio.addWidget(etiquetaVacia, alignment=Qt.AlignCenter)
            self.layoutCentral.addLayout(layoutVacio)
        self.actualizarBotones()

    def cargarRegistro(self, nomSeccion, descSec):
        self.pagina = ModificacionSeccion(nomSeccion, descSec)
        self.pagina.show()
        self.hide()
        self.pagina.destroyed.connect(self.actualizarYMostrar)

    def actualizarYMostrar(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT nombSeccion, descripcion FROM Seccion")
        self.resultados = c.fetchall()
        conn.close()
        self.actualizarVista()
        self.show()

    def siguienteSecuencia(self):
        self.numeroElemento += 4
        if self.numeroElemento >= len(self.resultados):
            self.numeroElemento = max(0, len(self.resultados) - 4)
        self.actualizarVista()

    def anteriorSecuencia(self):
        self.numeroElemento = max(0, self.numeroElemento - 4)
        self.actualizarVista()

    def actualizarBotones(self):
        self.botonAnterior.setEnabled(self.numeroElemento > 0)
        self.botonSiguiente.setEnabled(self.numeroElemento + 4 < len(self.resultados))

    def vaciarLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.vaciarLayout(item.layout())
                item.layout().deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = Administracion_Secciones_Mesas()
    pagina.show()
    sys.exit(app.exec_())
