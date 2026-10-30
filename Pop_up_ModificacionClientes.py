import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from Rutas import get_db_path

DB_PATH = get_db_path()


class Pop_up_ModificacionClientes(QDialog):
    def __init__(self, datos, parent=None):
        super().__init__()
        self.setWindowTitle("MODIFICACIÓN DE CLIENTE")
        self.setFixedSize(500, 500)
        self.move(800, 220)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f0f5ff, stop: 1 #d9e6ff);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
             QMessageBox {
                 background: #ffffff;
             }
             QMessageBox QLabel {
                 color: #2c3e50;
                 font-size: 15px;
                 font-weight: 500;
                 background:transparent;
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
             QMessageBox QPushButton:hover { background-color: #2980b9; }
        """)
        self.crearPantallaModificacion(datos)

    def crearPantallaModificacion(self, datos):
        campoEstilo = """
           QLineEdit {
               background-color: white;
               border: 2px solid #dce4ec;
               border-radius: 8px;
               padding: 8px;
               font-size: 14px;
               selection-background-color: #3498db;
           }
           QLineEdit:focus {
               border: 2px solid #3498db;
               background-color: #f7f9fc;
           }
       """
        editEstilo = """
           QLabel {
               font-size: 14px;
               font-weight: bold;
               color: #2c3e50;
               padding: 3px;
           }
       """
        layoutDatos = QVBoxLayout(self)
        titulo = QLabel("DATOS DEL CLIENTE")
        titulo.setStyleSheet("""
           QLabel {
               font-size: 22px;
               color: #2980b9;
               font-weight: bold;
               margin-bottom: 20px;
               padding: 5px;
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #e8f4ff, stop: 1 #c5e1ff);
               border-radius: 10px;
               border: 1px solid #a0c5e8;
           }
       """)
        layoutDatos.addWidget(titulo, alignment=Qt.AlignCenter)
        layoutDatos.setSpacing(10)
        layoutDatos.setContentsMargins(40, 40, 40, 40)
        nit = QLabel("NIT ")
        nombre = QLabel("NOMBRE: ")
        apellido = QLabel("APELLIDO PATERNO: ")
        apellido2 = QLabel("APELLIDO MATERNO: ")
        correoElectronico = QLabel("CORREO ELECTRÓNICO: ")
        self.campoNit = QLineEdit()
        self.campoNit.setValidator(QIntValidator())
        self.campoNit.setMaxLength(10)
        self.campoNit.setText(datos[0])
        self.campoNombre = QLineEdit()
        letras_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+")
        self.campoNombre.setValidator(QRegExpValidator(letras_regex))
        self.campoNombre.setMaxLength(20)
        self.campoNombre.setText(datos[1])
        self.campoApellido = QLineEdit()
        self.campoApellido.setValidator(QRegExpValidator(letras_regex))
        self.campoApellido.setMaxLength(30)
        self.campoApellido.setText(datos[2])
        self.campoApellido2 = QLineEdit()
        self.campoApellido2.setValidator(QRegExpValidator(letras_regex))
        self.campoApellido2.setMaxLength(30)
        self.campoApellido2.setText(datos[3])
        self.campoCorreo = QLineEdit()
        regex_correo = QRegExpValidator(QRegExp(r"^[a-zA-Z][a-zA-Z0-9._-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"))
        self.campoCorreo.setValidator(regex_correo)
        self.campoCorreo.setMaxLength(40)
        self.campoCorreo.setText(datos[4])
        nit.setStyleSheet(editEstilo)
        nombre.setStyleSheet(editEstilo)
        apellido.setStyleSheet(editEstilo)
        apellido2.setStyleSheet(editEstilo)
        correoElectronico.setStyleSheet(editEstilo)
        self.campoNit.setStyleSheet(campoEstilo)
        self.campoNombre.setStyleSheet(campoEstilo)
        self.campoApellido.setStyleSheet(campoEstilo)
        self.campoApellido2.setStyleSheet(campoEstilo)
        self.campoCorreo.setStyleSheet(campoEstilo)
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()
        layout5 = QHBoxLayout()
        layout1.addWidget(nit)
        layout1.addWidget(self.campoNit)
        layout2.addWidget(nombre)
        layout2.addWidget(self.campoNombre)
        layout3.addWidget(apellido)
        layout3.addWidget(self.campoApellido)
        layout4.addWidget(apellido2)
        layout4.addWidget(self.campoApellido2)
        layout5.addWidget(correoElectronico)
        layout5.addWidget(self.campoCorreo)
        layoutDatos.addLayout(layout1)
        layoutDatos.addLayout(layout2)
        layoutDatos.addLayout(layout3)
        layoutDatos.addLayout(layout4)
        layoutDatos.addLayout(layout5)
        layoutBotones = QHBoxLayout()
        cancelar = QPushButton("CANCELAR")
        modificar = QPushButton("MODIFICAR")
        cancelar.setCursor(Qt.PointingHandCursor)
        cancelar.clicked.connect(self.cerrarVentanaCancelar)
        modificar.setCursor(Qt.PointingHandCursor)
        modificar.clicked.connect(lambda: self.modificarRegistro(datos))
        botonEstilo1 = """
           QPushButton {
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #e74c3c, stop: 1 #c0392b);
               color: white;
               border: none;
               border-radius: 8px;
               padding: 12px 25px;
               font-weight: bold;
               font-size: 15px;
           }
           QPushButton:hover {
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #ff6b6b, stop: 1 #ee5253);
           }
           QPushButton:pressed {
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #c0392b, stop: 1 #e74c3c);
           }
       """
        botonEstilo2 = """
           QPushButton {
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #2ecc71, stop: 1 #27ae60);
               color: white;
               border: none;
               border-radius: 8px;
               padding: 12px 25px;
               font-weight: bold;
               font-size: 15px;
           }
           QPushButton:hover {
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #32ff7e, stop: 1 #3ae374);
           }
           QPushButton:pressed {
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #27ae60, stop: 1 #2ecc71);
           }
       """
        layoutCancelar = QVBoxLayout()
        layoutModificar = QVBoxLayout()
        cancelar.setStyleSheet(botonEstilo1)
        modificar.setStyleSheet(botonEstilo2)
        layoutCancelar.addStretch(100)
        layoutCancelar.addWidget(cancelar, alignment=Qt.AlignCenter, stretch=20)
        layoutBotones.addStretch(1)
        layoutBotones.addLayout(layoutCancelar)
        layoutModificar.addStretch(100)
        layoutModificar.addWidget(modificar, alignment=Qt.AlignCenter, stretch=20)
        layoutBotones.addLayout(layoutModificar)
        layoutBotones.addStretch(1)
        layoutBotones.setSpacing(20)
        layoutDatos.addLayout(layoutBotones)

    def modificarRegistro(self, datos):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        campos_obligatorios = [
            self.campoNit.text(),
            self.campoNombre.text(),
            self.campoApellido.text(),
            self.campoApellido2.text(),
            self.campoCorreo.text(),
        ]
        if any(campo == "" for campo in campos_obligatorios):
            QMessageBox.warning(self, "Advertencia", "Todos los campos son obligatorios")
            self.conn.close()
            return
        try:
            consulta = """UPDATE Cliente 
                       SET nit=?, nombCli=?, apellPatCli=?, apellMatCli=?, correoElCli=?
                       WHERE nit=?"""
            self.cursor.execute(
                consulta,
                (
                    int(self.campoNit.text()),
                    self.campoNombre.text(),
                    self.campoApellido.text(),
                    self.campoApellido2.text(),
                    self.campoCorreo.text(),
                    int(datos[0]),
                ),
            )
            self.conn.commit()
            QMessageBox.information(self, "Confirmación", "¡Se modificó con éxito!")
            self.conn.close()
            self.cerrarVentana()
        except Exception:
            QMessageBox.warning(self, "Error", "El NIT debe ser un número unico y valido")
        finally:
            self.conn.close()

    def cerrarVentanaCancelar(self):
        self.reject()
        self.close()

    def cerrarVentana(self):
        self.accept()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    datos_ejemplo = ["1234567890", "Juan", "Pérez", "González", "juan@email.com"]
    pagina = Pop_up_ModificacionClientes(datos_ejemplo)
    pagina.show()
    sys.exit(app.exec_())
