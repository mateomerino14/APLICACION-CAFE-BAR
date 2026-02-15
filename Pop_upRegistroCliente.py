# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt
import sqlite3
import os
import sys

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'database', 'cafebar.db')

DB_PATH = get_db_path()

class Pop_upRegistroCliente(QDialog):
    def __init__(self, parent=None, tabla=None):
        super().__init__(parent)
        self.tabla = tabla
        self.setWindowTitle("Registro Rápido de Cliente")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("NIT:"))
        self.nit_input = QLineEdit()
        layout.addWidget(self.nit_input)
        layout.addWidget(QLabel("Nombre:"))
        self.nombre_input = QLineEdit()
        layout.addWidget(self.nombre_input)
        layout.addWidget(QLabel("Apellido Paterno:"))
        self.apellido_paterno_input = QLineEdit()
        layout.addWidget(self.apellido_paterno_input)
        layout.addWidget(QLabel("Apellido Materno:"))
        self.apellido_materno_input = QLineEdit()
        layout.addWidget(self.apellido_materno_input)
        layout.addWidget(QLabel("Correo Electrónico:"))
        self.correo_input = QLineEdit()
        layout.addWidget(self.correo_input)
        botones_layout = QHBoxLayout()
        self.btn_registrar = QPushButton("Registrar")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_registrar.clicked.connect(self.registrar_cliente)
        self.btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(self.btn_registrar)
        botones_layout.addWidget(self.btn_cancelar)
        layout.addLayout(botones_layout)
        self.setLayout(layout)
    

    def registrar_cliente(self):
        nit = self.nit_input.text().strip()
        nombre = self.nombre_input.text().strip()
        apellido_paterno = self.apellido_paterno_input.text().strip()
        apellido_materno = self.apellido_materno_input.text().strip()
        correo = self.correo_input.text().strip()
        if not nit or not nombre or not apellido_paterno or not apellido_materno:
            QMessageBox.warning(self, "Campos incompletos", 
                               "Por favor, complete todos los campos obligatorios.")
            return
        try:
            nit_val = int(nit)
        except ValueError:
            QMessageBox.warning(self, "NIT inválido", 
                               "El NIT debe contener solo números.")
            return
        if correo and "@" not in correo:
            QMessageBox.warning(self, "Correo inválido", 
                               "Por favor, ingrese un correo electrónico válido.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT nit FROM Cliente WHERE nit = ?", (nit,))
            if c.fetchone():
                QMessageBox.warning(self, "NIT duplicado", 
                                   "El NIT ingresado ya existe en la base de datos.")
                conn.close()
                return
            c.execute("""
                INSERT INTO Cliente (nit, nombCli, apellPatCli, apellMatCli, correoElCli)
                VALUES (?, ?, ?, ?, ?)
            """, (nit, nombre, apellido_paterno, apellido_materno, correo))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Registro exitoso", 
                                   "Cliente registrado correctamente.")
            if self.tabla and hasattr(self.parent(), 'filtrarDatosClientes'):
                self.parent().filtrarDatosClientes("", self.tabla)
            self.accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error de base de datos", 
                                f"Ocurrió un error al registrar el cliente: {str(e)}")