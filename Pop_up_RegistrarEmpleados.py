from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import sqlite3
import os
import sys
from SeguridadUtils import hashear_password

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'database', 'cafebar.db')

DB_PATH = get_db_path()

class Pop_up_RegistrarEmpleados(QDialog):
    def __init__(self, datosEmpleado, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmación de Registro")
        self.setFixedSize(500, 450) 
        self.setModal(True)
        self.setStyleSheet("""
            QDialog {
                font-family: 'Segoe UI', Arial, sans-serif;
                border-radius: 12px;
            }
            QLabel {
                font-size: 14px;
                color: #2d3748;
                margin-bottom: 5px;
            }
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
                min-width: 200px;
                selection-background-color: #bee3f8;
            }
            QLineEdit:focus {
                border-color: #63b3ed;
                background-color: #f0f9ff;
            }
            QPushButton {
                background-color: #4299e1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3182ce;
            }
            QPushButton:pressed {
                background-color: #2b6cb0;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        titulo = QLabel("COMPLETE SU REGISTRO")
        titulo.setStyleSheet("""
            font-weight: bold;
            font-size: 18px;
            color: #2b6cb0;
            margin-bottom: 5px;
            padding: 5px;
            background-color: #f3f3f3;
            border-radius: 6px;
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        mensaje = QLabel("Ingrese sus credenciales de acceso al sistema")
        mensaje.setStyleSheet("""
            font-size: 13px;
            color: #4a5568;
            margin-bottom: 15px;
        """)
        mensaje.setAlignment(Qt.AlignCenter)
        layout.addWidget(mensaje)
        layout_alias = QHBoxLayout()
        lbl_alias = QLabel("Usuario:")
        lbl_alias.setFixedWidth(100)
        lbl_alias.setStyleSheet("font-weight: bold;")
        self.campo1 = QLineEdit()
        self.campo1.setPlaceholderText("Ej: juan.perez")
        layout_alias.addWidget(lbl_alias)
        layout_alias.addWidget(self.campo1)
        layout.addLayout(layout_alias)
        layout_pass = QHBoxLayout()
        lbl_pass = QLabel("Contraseña:")
        lbl_pass.setFixedWidth(100)
        lbl_pass.setStyleSheet("font-weight: bold;")
        self.campo2 = QLineEdit()
        self.campo2.setPlaceholderText("Mínimo 6 caracteres")
        self.campo2.setEchoMode(QLineEdit.Password)
        layout_pass.addWidget(lbl_pass)
        layout_pass.addWidget(self.campo2)
        layout.addLayout(layout_pass)
        layout.addSpacing(10)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        btn_aceptar = QPushButton("Confirmar")
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #38a169;
            }
            QPushButton:hover {
                background-color: #2f855a;
            }
            QPushButton:pressed {
                background-color: #276749;
            }
        """)
        btn_aceptar.clicked.connect(lambda: self.registrarInformacion(datosEmpleado))
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e53e3e;
            }
            QPushButton:hover {
                background-color: #c53030;
            }
            QPushButton:pressed {
                background-color: #9b2c2c;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_aceptar)
        btn_layout.addWidget(btn_cancelar)
        btn_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(btn_layout)
        nota = QLabel("* Estos datos son necesarios para acceder al sistema")
        nota.setStyleSheet("font-size: 11px; color: #718096; font-style: italic;")
        nota.setAlignment(Qt.AlignCenter)
        layout.addWidget(nota)
        self.setLayout(layout)


    def registrarInformacion(self, datosEmpleado):
        try:
            if len(datosEmpleado) != 9:
                raise ValueError("Datos de empleado incompletos")
            c1, c2, c3, c4, c5, c6, c7, c8, c9 = datosEmpleado
            c10 = self.campo1.text().strip()
            c11 = self.campo2.text().strip()
            if not c10 or not c11:
                QMessageBox.warning(self, "Error", "Usuario y contraseña son obligatorios")
                return
            if len(c10) < 4:
                QMessageBox.warning(self, "Error", "El usuario debe tener al menos 4 caracteres")
                return
                
            if len(c11) < 6:
                QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 6 caracteres")
                return
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            try:
                c.execute("SELECT aliasEmp FROM Empleado WHERE aliasEmp=?", (c10,))
                if c.fetchone():
                    QMessageBox.warning(self, "Error", "Nombre de usuario ya existe")
                    return
                elif c10=="ADMINISTRADOR":
                    QMessageBox.warning(self, "Error", "Nombre de usuario ya existe")
                    return
                c.execute("SELECT idCargo FROM Cargo WHERE nomCarg=?", (c8,))
                resultado = c.fetchone()
                if not resultado:
                    raise ValueError("Cargo no encontrado")
                id_cargo = resultado[0]
                c11_hash = hashear_password(c11)
                consulta = """INSERT INTO Empleado(
                    aliasEmp, contEmp, ciEmp, nomEmp, 
                    apellPatEmp, apellMatEmp, numCelEmp,
                    direccionEmp, correoElEmp, idCargo, imgEmp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                c.execute(consulta, (
                    c10, c11_hash, c4, c1,
                    c2, c3, c5,
                    c6, c7, id_cargo, 
                    sqlite3.Binary(c9) if c9 else None
                ))
                conn.commit()
                QMessageBox.information(self, "Éxito", "Registro completado exitosamente")
                self.accept()
            finally:
                conn.close()
        except ValueError as ve:
            QMessageBox.warning(self, "Error de validación", str(ve))
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de base de datos", f"Error al registrar: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", f"Ocurrió un error: {str(e)}")