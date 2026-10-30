import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from Rutas import get_db_path

DB_PATH = get_db_path()


class Pop_up_Registro_Seccion(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("REGISTRO DE SECCIÓN")
        self.setFixedSize(500, 500)
        self.setStyleSheet("""
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        self.crearPantallaModificacion()

    def crearPantallaModificacion(self):
        main_style = """
            QDialog {
                background-color: #f8f9fa;
                border-radius: 0px;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 5px;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #ced4da;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                min-height: 30px;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                min-width: 120px;
            }
            QMessageBox {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 15px;
                font-weight: 500;
            }
            QMessageBox QDialogButtonBox {
                background: #f5f7fa;             
                border-top: 1px solid #e2e8f0;
                padding: 10px 16px;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 8px 18px;
                min-width: 110px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover { 
               background-color: #2980b9; 
            }
        """
        self.setStyleSheet(main_style)
        layoutDatos = QVBoxLayout(self)
        layoutDatos.setContentsMargins(40, 30, 40, 30)
        layoutDatos.setSpacing(20)
        titulo = QLabel("REGISTRO DE NUEVA SECCIÓN")
        titulo.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            qproperty-alignment: AlignCenter;
        """)
        layoutDatos.addWidget(titulo)
        campo_style = "margin-bottom: 15px;"
        label_style = "font-weight: 600; color: #34495e;"
        seccion = QLabel("Nombre de Sección:")
        seccion.setStyleSheet(label_style)
        self.campoSeccion = QLineEdit()
        self.campoSeccion.setMaxLength(17)
        self.campoSeccion.setPlaceholderText("Ej: Terraza Principal")
        self.campoSeccion.setStyleSheet(campo_style)
        letras_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+")
        self.campoSeccion.setValidator(QRegExpValidator(letras_regex))
        descipcion = QLabel("Descripción:")
        descipcion.setStyleSheet(label_style)
        self.campoDedscripcion = QLineEdit()
        self.campoDedscripcion.setMaxLength(40)
        self.campoDedscripcion.setPlaceholderText("Opcional")
        self.campoDedscripcion.setStyleSheet(campo_style)
        descripcion_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ0-9.,\\-\\s]*")
        self.campoDedscripcion.setValidator(QRegExpValidator(descripcion_regex))
        cantidad = QLabel("Cantidad de Mesas:")
        cantidad.setStyleSheet(label_style)
        self.campoCantidad = QLineEdit()
        self.campoCantidad.setPlaceholderText("Número entero")
        cantidad_regex = QRegExp("[0-9]*")
        self.campoCantidad.setValidator(QRegExpValidator(cantidad_regex))
        self.campoCantidad.setMaxLength(4)
        self.campoCantidad.setStyleSheet(campo_style)
        layoutDatos.addWidget(seccion)
        layoutDatos.addWidget(self.campoSeccion)
        layoutDatos.addWidget(descipcion)
        layoutDatos.addWidget(self.campoDedscripcion)
        layoutDatos.addWidget(cantidad)
        layoutDatos.addWidget(self.campoCantidad)
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(20)
        cancelar = QPushButton("CANCELAR")
        cancelar.setCursor(Qt.PointingHandCursor)
        cancelar.clicked.connect(self.cerrarVentanaCancelar)
        cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: 2px solid #c0392b;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        modificar = QPushButton("REGISTRAR")
        modificar.setCursor(Qt.PointingHandCursor)
        modificar.clicked.connect(self.subirInformacion)
        modificar.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: 2px solid #27ae60;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        botones_layout.addWidget(cancelar)
        botones_layout.addWidget(modificar)
        layoutDatos.addLayout(botones_layout)

    def subirInformacion(self):
        nombreSeccion = self.campoSeccion.text().strip()
        descripcionSeccion = self.campoDedscripcion.text().strip()
        cantidadTexto = self.campoCantidad.text().strip()
        lista = [nombreSeccion, cantidadTexto]
        for elem in lista:
            if elem == "":
                QMessageBox.information(self, "Advertencia", "¡Llene los campos solicitados porfavor!")
                return
        try:
            cantidad = int(cantidadTexto)
        except ValueError:
            QMessageBox.information(self, "Advertencia", "La cantidad de mesas debe ser un numero valido.")
            return
        if cantidad < 0:
            QMessageBox.information(self, "Advertencia", "La cantidad debe ser un numero mayor o igual a 0")
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            consulta = """SELECT * FROM Seccion WHERE nombSeccion=?"""
            c.execute(consulta, (nombreSeccion,))
            resultados = c.fetchall()
            if resultados:
                QMessageBox.information(self, "Advertencia", "¡Este nombre de seccion ya ha sido registrado!")
                return
            consulta = """INSERT INTO Seccion(nombSeccion,descripcion) VALUES(?,?)"""
            c.execute(consulta, (nombreSeccion, descripcionSeccion))

            indice = c.lastrowid
            for i in range(cantidad):
                consulta = """INSERT INTO Mesa(idMesa,idSeccion) VALUES(NULL,?)"""
                c.execute(consulta, (indice,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo registrar la seccion: {str(e)}")
            return
        finally:
            conn.close()
        QMessageBox.information(self, "Confirmación", "¡Se registro con exito!")
        self.cerrarVentana()

    def cerrarVentanaCancelar(self):
        self.reject()
        self.close()

    def cerrarVentana(self):
        self.accept()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = Pop_up_Registro_Seccion(None)
    pagina.show()
    sys.exit(app.exec_())
