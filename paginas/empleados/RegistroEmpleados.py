import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from paginas.empleados.Pop_up_RegistrarEmpleados import Pop_up_RegistrarEmpleados
from nucleo.Rutas import get_db_path, get_resource_path

DB_PATH = get_db_path()


class RegistroEmpleados(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
          QMainWindow {
          background-color: #e6f2ff;
          font-family: 'Segoe UI', Arial, sans-serif;
          }
          QMessageBox {
              background: #ffffff;
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
        """)
        self.set_up()

    def set_up(self):
        self.layoutDatos = QHBoxLayout()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.anadirAreaRegistro()
        self.layoutPrincipal.setSpacing(50)
        self.layoutFoto = QVBoxLayout()
        self.foto = QLabel()
        self.anadirAreaFotoRegistro()
        self.layoutPrincipal.addStretch(1)
        self.showMaximized()

    def anadirAreaRegistro(self):
        labelEstilo = """
            font-size: 16px;
            font-family: Verdana;
            color: #2c3e50;
            font-weight: bold;
            margin-bottom: 5px;
        """

        camposEstilo = """
            background-color: white;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 0px;
            font-size: 15px;
        """

        botonesEstilo = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """

        widgetRegistro = QWidget()
        widgetRegistro.setStyleSheet("""
            background-color: white;
            margin-bottom: 30px;
            border-radius: 10px;
            border: 1px solid #d6d6d6;
        """)
        widgetRegistro.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        widgetRegistro.setLayout(self.layoutDatos)
        layoutCampos = QVBoxLayout()
        layoutCampos.setSpacing(15)
        layoutCampos.setContentsMargins(20, 20, 20, 20)
        layoutH1 = QHBoxLayout()
        layoutH1.setSpacing(10)
        nombre = QLabel("NOMBRE")
        nombre.setStyleSheet(labelEstilo)
        self.campo1 = QLineEdit()
        self.campo1.setStyleSheet(camposEstilo)
        letras_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+")
        self.campo1.setValidator(QRegExpValidator(letras_regex))
        self.campo1.setMaxLength(30)
        apellido = QLabel("APELLIDO PATERNO")
        apellido.setStyleSheet(labelEstilo)
        self.campo2 = QLineEdit()
        self.campo2.setStyleSheet(camposEstilo)
        self.campo2.setValidator(QRegExpValidator(letras_regex))
        self.campo2.setMaxLength(30)
        apellido2 = QLabel("APELLIDO MATERNO")
        apellido2.setStyleSheet(labelEstilo)
        self.campo3 = QLineEdit()
        self.campo3.setStyleSheet(camposEstilo)
        self.campo3.setValidator(QRegExpValidator(letras_regex))
        self.campo3.setMaxLength(30)

        def crear_grupo_campo(label, campo):
            grupo = QVBoxLayout()
            grupo.addWidget(label, alignment=Qt.AlignLeft)
            grupo.addWidget(campo)
            return grupo

        layoutH1.addLayout(crear_grupo_campo(nombre, self.campo1))
        layoutH1.addLayout(crear_grupo_campo(apellido, self.campo2))
        layoutH1.addLayout(crear_grupo_campo(apellido2, self.campo3))
        layoutCampos.addLayout(layoutH1)
        layoutH2 = QHBoxLayout()
        layoutH2.setSpacing(10)
        ci = QLabel("CI")
        ci.setStyleSheet(labelEstilo)
        self.campo4 = QLineEdit()
        self.campo4.setStyleSheet(camposEstilo)
        digitos_regex = QRegExp("[0-9]*")
        self.campo4.setValidator(QRegExpValidator(digitos_regex))
        self.campo4.setMaxLength(7)
        numCelular = QLabel("NÚMERO DE CELULAR")
        numCelular.setStyleSheet(labelEstilo)
        self.campo5 = QLineEdit()
        self.campo5.setStyleSheet(camposEstilo)
        self.campo5.setMaxLength(8)
        self.campo5.setValidator(QRegExpValidator(digitos_regex))
        idCargo = QLabel("CARGO")
        idCargo.setStyleSheet(labelEstilo)
        self.campo8 = QComboBox()
        self.campo8.setStyleSheet(camposEstilo)
        self.cargarDatosComboBox()
        layoutH2.addLayout(crear_grupo_campo(ci, self.campo4))
        layoutH2.addLayout(crear_grupo_campo(numCelular, self.campo5))
        layoutH2.addLayout(crear_grupo_campo(idCargo, self.campo8))
        layoutCampos.addLayout(layoutH2)
        layoutH3 = QHBoxLayout()
        layoutH3.setSpacing(10)
        direccion = QLabel("DIRECCIÓN")
        direccion.setStyleSheet(labelEstilo)
        self.campo6 = QLineEdit()
        self.campo6.setStyleSheet(camposEstilo)
        direccion_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ0-9#.,\\-\\s]*")
        self.campo6.setValidator(QRegExpValidator(direccion_regex))
        self.campo6.setMaxLength(30)
        correoElectronico = QLabel("CORREO ELECTRÓNICO")
        correoElectronico.setStyleSheet(labelEstilo)
        self.campo7 = QLineEdit()
        self.campo7.setStyleSheet(camposEstilo)
        regex_correo = QRegExpValidator(QRegExp(r"^[a-zA-Z][a-zA-Z0-9._-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"))
        self.campo7.setValidator(regex_correo)
        self.campo7.setMaxLength(30)
        layoutH3.addLayout(crear_grupo_campo(direccion, self.campo6))
        layoutH3.addLayout(crear_grupo_campo(correoElectronico, self.campo7))
        layoutCampos.addLayout(layoutH3)
        layoutBotones = QHBoxLayout()
        layoutBotones.setSpacing(20)
        layoutBotones.setContentsMargins(0, 20, 0, 0)
        confirmar = QPushButton("CONFIRMAR")
        confirmar.setStyleSheet(botonesEstilo)
        confirmar.setCursor(Qt.PointingHandCursor)
        confirmar.clicked.connect(
            lambda: self.activarPantallaPequena(
                self.campo1.text().strip(),  # nombre
                self.campo2.text().strip(),  # apell. pat
                self.campo3.text().strip(),  # apell. mat
                self.campo4.text().strip(),  # CI
                self.campo5.text().strip(),  # celular
                self.campo6.text().strip(),  # dirección (OPCIONAL)
                self.campo7.text().strip(),  # correo (OPCIONAL)
                self.campo8.currentText().strip(),  # cargo
            )
        )
        rechazar = QPushButton("CANCELAR")
        rechazar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        rechazar.setCursor(Qt.PointingHandCursor)
        rechazar.clicked.connect(
            lambda: self.limpiarTodo(
                self.campo1, self.campo2, self.campo3, self.campo4, self.campo5, self.campo6, self.campo7, self.campo8
            )
        )
        layoutBotones.addWidget(confirmar)
        layoutBotones.addWidget(rechazar)
        layoutBotones.setAlignment(Qt.AlignCenter)
        layoutCampos.addLayout(layoutBotones)
        self.layoutDatos.addLayout(layoutCampos)
        self.layoutPrincipal.addWidget(widgetRegistro)

    def cargarDatosComboBox(self):
        self.campo8.clear()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        consulta = """SELECT * FROM Cargo"""
        resultado = c.execute(consulta)
        for _, cargo in resultado.fetchall():
            self.campo8.addItem(cargo)
        conn.close()

    def activarPantallaPequena(self, c1, c2, c3, c4, c5, c6, c7, c8):
        if not c1 or not c2 or not c3:
            QMessageBox.warning(self, "Advertencia", "Ingrese los campos obligatorios")
            return
        if not c4 or len(c4) < 5:
            QMessageBox.warning(self, "Advertencia", "Ingrese un CI válido (mínimo 5 dígitos)")
            return
        if not c5 or len(c5) < 7:
            QMessageBox.warning(self, "Advertencia", "Ingrese un número de celular válido (mínimo 7 dígitos)")
            return
        if not c8:
            QMessageBox.warning(self, "Advertencia", "Seleccione un cargo")
            return
        lista = [c1, c2, c3, c4, c5, c6, c7, c8]
        pixmap = self.foto.pixmap()
        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        pixmap.save(buffer, "PNG")
        imagen_blob = buffer.data()
        buffer.close()
        lista.append(imagen_blob)
        mini = Pop_up_RegistrarEmpleados(lista, self)
        resultado = mini.exec_()
        if resultado == QDialog.Accepted:
            self.limpiarTodo(
                self.campo1, self.campo2, self.campo3, self.campo4, self.campo5, self.campo6, self.campo7, self.campo8
            )

    def limpiarTodo(self, campo1, campo2, campo3, campo4, campo5, campo6, campo7, campo8):
        campo1.clear()
        campo2.clear()
        campo3.clear()
        campo4.clear()
        campo5.clear()
        campo6.clear()
        campo7.clear()
        campo8.setCurrentIndex(-1)
        default_image_path = get_resource_path(os.path.join('Imagenes', 'camara.png'))
        if os.path.exists(default_image_path):
            pixmap = QPixmap(default_image_path)
        else:
            pixmap = QPixmap(200, 200)
            pixmap.fill(QColor("#3498db"))
        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.foto.setPixmap(pixmap)

    def anadirAreaFotoRegistro(self):
        self.foto.setAlignment(Qt.AlignCenter)
        self.foto.setFixedSize(300, 300)
        self.foto.setStyleSheet("""
            border: 3px dashed #95a5a6;
            border-radius: 10px;
            background-color: #f8f9fa;
        """)
        default_image_path = get_resource_path(os.path.join('Imagenes', 'camara.png'))
        if os.path.exists(default_image_path):
            pixmap = QPixmap(default_image_path)
        else:
            pixmap = QPixmap(150, 150)
            pixmap.fill(QColor("#3498db"))
        pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.foto.setPixmap(pixmap)
        self.layoutFoto.addWidget(self.foto)
        botonFoto = QPushButton("AÑADIR FOTO")
        botonFoto.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        botonFoto.setFixedWidth(200)
        botonFoto.setCursor(Qt.PointingHandCursor)
        botonFoto.clicked.connect(self.subirFoto)
        self.layoutFoto.addWidget(botonFoto, alignment=Qt.AlignCenter)
        self.layoutFoto.setAlignment(Qt.AlignCenter)
        self.layoutDatos.addLayout(self.layoutFoto)

    def subirFoto(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Seleccionar Foto", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)")
        if filename:
            pixmap = QPixmap(filename)
            pixmap = pixmap.scaled(self.foto.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.foto.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = RegistroEmpleados()
    pagina.show()
    sys.exit(app.exec_())
