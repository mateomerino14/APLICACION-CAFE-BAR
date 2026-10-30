import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from Rutas import get_db_path, get_resource_path

DB_PATH = get_db_path()
DIRECCION_IMAGEN = get_resource_path('Imagenes')


class RegistroClientes(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setStyleSheet("""
            self{background-color: #e6f2ff;
            font-family: 'Segoe UI', Arial, sans-serif;}
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
        self.set_up()

    def set_up(self):
        self.layoutDatos = QHBoxLayout()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.anadirAreaRegistro()
        self.showMinimized()

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
        widgetRegistro.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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
        self.campo1.setMaxLength(20)
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
        nit = QLabel("NIT")
        nit.setStyleSheet(labelEstilo)
        self.campo4 = QLineEdit()
        self.campo4.setStyleSheet(camposEstilo)
        self.campo4.setValidator(QIntValidator())
        self.campo4.setMaxLength(10)
        correoElectronico = QLabel("CORREO ELECTRÓNICO")
        correoElectronico.setStyleSheet(labelEstilo)
        self.campo5 = QLineEdit()
        self.campo5.setStyleSheet(camposEstilo)
        regex_correo = QRegExpValidator(QRegExp(r"^[a-zA-Z][a-zA-Z0-9._-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"))
        self.campo5.setValidator(regex_correo)
        self.campo5.setMaxLength(40)
        layoutH2.addLayout(crear_grupo_campo(nit, self.campo4))
        layoutH2.addLayout(crear_grupo_campo(correoElectronico, self.campo5))
        layoutCampos.addLayout(layoutH2)
        layoutBotones = QHBoxLayout()
        layoutBotones.setSpacing(20)
        layoutBotones.setContentsMargins(0, 20, 0, 0)
        confirmar = QPushButton("CONFIRMAR")
        confirmar.setStyleSheet(botonesEstilo)
        confirmar.setCursor(Qt.PointingHandCursor)
        confirmar.clicked.connect(self.confirmarRegistro)
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
        rechazar.clicked.connect(self.limpiarTodo)
        layoutBotones.addWidget(confirmar)
        layoutBotones.addWidget(rechazar)
        layoutBotones.setAlignment(Qt.AlignCenter)
        layoutCampos.addLayout(layoutBotones)
        self.layoutDatos.addLayout(layoutCampos)
        self.layoutPrincipal.addWidget(widgetRegistro)
        self.anadirImagen()
        self.layoutPrincipal.addStretch(1)

    def anadirImagen(self):
        imagen = QLabel()
        imagen_path = get_resource_path(os.path.join('Imagenes', 'atencion.jpg'))
        if os.path.exists(imagen_path):
            pixmap = QPixmap(imagen_path)
        else:
            pixmap = QPixmap(400, 400)
            pixmap.fill(QColor("#3498db"))
        tamaño_circular = 400
        circular_pixmap = QPixmap(tamaño_circular, tamaño_circular)
        circular_pixmap.fill(Qt.transparent)
        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, tamaño_circular, tamaño_circular)
        painter.setClipPath(path)
        pixmap_escalada = pixmap.scaled(
            tamaño_circular, tamaño_circular, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )
        painter.drawPixmap(0, 0, pixmap_escalada)
        painter.end()
        imagen.setPixmap(circular_pixmap)
        imagen.setAlignment(Qt.AlignCenter)
        imagen.setFixedSize(tamaño_circular, tamaño_circular)
        imagen.setStyleSheet("""background-color:transparent;""")
        self.layoutPrincipal.addWidget(imagen, alignment=Qt.AlignCenter)

    def confirmarRegistro(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        lista = [self.campo1, self.campo2, self.campo3, self.campo4, self.campo5]
        for elem in lista:
            if elem.text() == "":
                QMessageBox.information(self, "Advertencia", "Llene todos los campos obligatorios por favor")
                return
        try:
            nit_value = int(self.campo4.text())
        except ValueError:
            QMessageBox.information(self, "Advertencia", "El NIT debe ser un número válido")
            return
        consulta = """SELECT * FROM Cliente WHERE nit=?"""
        registros = c.execute(consulta, (nit_value,))
        resultados = registros.fetchone()

        if resultados is not None:
            QMessageBox.information(self, "Advertencia", "Este cliente ya ha sido registrado")
            return

        consulta = """INSERT INTO Cliente(nit, nombCli, apellPatCli, apellMatCli, correoElCli) 
                    VALUES (?, ?, ?, ?, ?)"""
        c.execute(
            consulta,
            (
                nit_value,  # nit
                self.campo1.text(),  # nombCli
                self.campo2.text(),  # apellPatCli
                self.campo3.text(),  # apellMatCli
                self.campo5.text(),  # correoElCli
            ),
        )
        QMessageBox.information(self, "Confirmación", "Se ha registrado con éxito")
        self.limpiarTodo()
        conn.commit()
        conn.close()

    def limpiarTodo(self):
        self.campo1.clear()
        self.campo2.clear()
        self.campo3.clear()
        self.campo4.clear()
        self.campo5.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = RegistroClientes()
    pagina.show()
    sys.exit(app.exec_())
