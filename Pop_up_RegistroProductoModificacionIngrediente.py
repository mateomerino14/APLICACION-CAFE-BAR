from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from Rutas import get_db_path

DB_PATH = get_db_path()


class Pop_up_RegistroProductoModificacionIngrediente(QDialog):
    def __init__(self, elemento, lista, conjunto, parent=None):
        super().__init__(parent)
        self.nuevoIden = elemento
        self.nuevoIng = lista[0]
        self.nuevaDesc = lista[2]
        self.nuevCant = lista[1]
        self.nuevoIdIng = self._buscarIdIng(lista[0])
        self.setWindowTitle("MODIFICACIÓN DE INGREDIENTE")
        self.setFixedSize(480, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                font-weight: bold;
                color: #2c3e50;
                font-size: 14px;
                padding: 5px;
                background-color: rgba(255, 255, 255, 0.7);
                border-radius: 4px;
            }
            QComboBox, QLineEdit {
                background-color: white;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 1px solid #3498db;
                outline: none;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #ced4da;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #2c3e50;
                width: 0;
                height: 0;
                margin-right: 7px;
            }
        """)

        layoutPrincipal = QVBoxLayout()
        self.setLayout(layoutPrincipal)
        layout1 = QHBoxLayout()
        campo1 = QLabel("Ingrediente: ")
        campo1.setStyleSheet("""background-color: transparent;""")
        campo2 = QComboBox()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        consulta = """SELECT nomIng FROM Stock"""
        c.execute(consulta)
        resultados = [str(elem[0]) for elem in c.fetchall()]
        conn.close()
        campo2.addItems(resultados)
        campo2.setCurrentText(lista[0])
        layout1.addWidget(campo1)
        layout1.addWidget(campo2)
        layoutPrincipal.addLayout(layout1)
        layout2 = QHBoxLayout()
        campo3 = QLabel("Descripción: ")
        campo3.setStyleSheet("""background-color: transparent;""")
        campo4 = QLabel(lista[2])
        campo4.setWordWrap(True)
        campo4.setMinimumHeight(50)
        campo4.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px;
                font-weight: normal;
            }
        """)
        layout2.addWidget(campo3)
        layout2.addWidget(campo4)
        layoutPrincipal.addLayout(layout2)
        campo2.currentIndexChanged.connect(lambda: self.actualizar(campo2, campo4))
        layout3 = QHBoxLayout()
        campo5 = QLabel("Cantidad: ")
        campo5.setStyleSheet("""background-color: transparent;""")
        campo6 = QLineEdit(lista[1])
        campo6.setValidator(QRegExpValidator(QRegExp(r"[0-9]{1,8}(\.[0-9]{0,2})?")))
        campo6.setMaxLength(11)
        layout3.addWidget(campo5)
        layout3.addWidget(campo6)
        layoutPrincipal.addLayout(layout3)
        layout4 = QHBoxLayout()
        boton1 = QPushButton("Confirmar")
        boton2 = QPushButton("Cancelar")
        estilo_botones = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 100px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1d6fa5;
            }
        """
        boton1.setStyleSheet(estilo_botones)
        boton2.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 100px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a23526;
            }
        """)
        boton1.clicked.connect(
            lambda: self.cambiarIdentificador(
                conjunto, campo2.currentText(), campo2.currentText(), campo4.text(), campo6.text()
            )
        )
        boton2.clicked.connect(self.cerrarVentana)
        layout4.addWidget(boton1)
        layout4.addWidget(boton2)
        layoutPrincipal.addLayout(layout4)
        layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        layoutPrincipal.setSpacing(15)

    def _buscarIdIng(self, nombreIngrediente):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT idIng FROM Stock WHERE nomIng=?", (nombreIngrediente,))
            resultado = c.fetchone()
            conn.close()
            return resultado[0] if resultado else None
        except Exception:
            return None

    def actualizar(self, campo2, campo4):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        consulta = """SELECT idIng, descripcion FROM Stock WHERE nomIng=?"""
        c.execute(consulta, (campo2.currentText(),))
        actual = c.fetchone()
        conn.close()
        if actual:
            self.nuevoIdIng = actual[0]
            campo4.setText(actual[1] if actual[1] else "")

    def cambiarIdentificador(self, conjunto, nuevo, ingrediente, descripcion, cantidad):
        if cantidad == "":
            QMessageBox.critical(self, "Advertencia", "Debe llenar los campos necesarios")
            return

        nuevo_id = ingrediente

        conjunto_upper = {item.upper() for item in conjunto}

        if nuevo_id.upper() in conjunto_upper and nuevo_id != self.nuevoIden:
            msg = QMessageBox()
            msg.setStyleSheet("""
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
                QMessageBox QPushButton:hover { 
                    background-color: #2980b9; 
                }
            """)
            msg.setWindowTitle("Error")
            msg.setText("Este ingrediente ya está registrado")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        self.nuevoIden = nuevo_id
        self.nuevoIng = ingrediente
        self.nuevaDesc = descripcion
        self.nuevaCant = cantidad
        self.accept()

    def getIden(self):
        return self.nuevoIden, self.nuevoIng, self.nuevaDesc, self.nuevaCant, self.nuevoIdIng

    def cerrarVentana(self):
        self.close()
