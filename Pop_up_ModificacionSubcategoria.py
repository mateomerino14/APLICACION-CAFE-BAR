import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'database', 'cafebar.db')

DB_PATH = get_db_path()

class Pop_up_ModificacionSubcategoria(QDialog):
    def __init__(self, elemento, conjunto, imagen_data=None, parent=None):
        super().__init__(parent)
        self.nuevaSub = elemento
        self.nuevaImagen = imagen_data
        self.setWindowTitle("MODIFICAR SUBCATEGORÍA")
        self.setFixedSize(650, 730)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8fcff, stop: 1 #e3f0ff);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                font-weight: 600;
                color: #2c3e50;
                font-size: 14px;
                background: transparent;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 14px;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                transform: translateY(1px);
            }
            QMessageBox {
                background: #ffffff;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 15px;
                font-weight: 500;
                background: transparent;
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
        self.conjunto = conjunto
        self.initUI()
        

    def initUI(self):
        layoutPrincipal = QVBoxLayout(self)
        layoutPrincipal.setSpacing(20)
        layoutPrincipal.setContentsMargins(30, 30, 30, 30)
        titulo_container = QFrame()
        titulo_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #e67e22, stop: 1 #d35400);
                border-radius: 12px;
                padding: 10px;
            }
        """)
        titulo_layout = QHBoxLayout(titulo_container)
        titulo_layout.setContentsMargins(0, 0, 0, 0)
        titulo = QLabel("✏️ MODIFICAR SUBCATEGORÍA")
        titulo.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                background: transparent;
                padding: 5px;
            }
        """)
        titulo.setAlignment(Qt.AlignCenter)
        titulo_layout.addWidget(titulo)
        layoutPrincipal.addWidget(titulo_container)
        
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 15px;
                border: 1px solid #d0e0f0;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        nombre_layout = QHBoxLayout()
        nombre_label = QLabel("📛 NOMBRE:")
        nombre_label.setFixedWidth(150)
        nombre_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #2c3e50;")
        self.campo2 = QLineEdit(self.nuevaSub)
        self.campo2.setPlaceholderText("Ingrese el nombre de la subcategoría")
        self.campo2.setMinimumHeight(40)
        nombre_layout.addWidget(nombre_label)
        nombre_layout.addWidget(self.campo2)
        form_layout.addLayout(nombre_layout)
        imagen_container = QFrame()
        imagen_container.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #e2e8f0;
            }
        """)
        imagen_layout = QVBoxLayout(imagen_container)
        imagen_header = QHBoxLayout()
        imagen_label = QLabel("🖼️ IMAGEN:")
        imagen_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #2c3e50;")
        btnSeleccionarImagen = QPushButton("📁 Cambiar Imagen")
        btnSeleccionarImagen.setCursor(Qt.PointingHandCursor)
        btnSeleccionarImagen.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #9b59b6, stop: 1 #8e44ad);
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #8e44ad, stop: 1 #7d3c98);
            }
        """)
        btnSeleccionarImagen.clicked.connect(self.seleccionarImagen)
        imagen_header.addWidget(imagen_label)
        imagen_header.addStretch()
        imagen_header.addWidget(btnSeleccionarImagen)
        imagen_layout.addLayout(imagen_header)
        imagen_preview_container = QHBoxLayout()
        imagen_preview_container.addStretch()
        self.imagenLabel = QLabel()
        self.imagenLabel.setFixedSize(200, 200)
        self.imagenLabel.setAlignment(Qt.AlignCenter)
        self.imagenLabel.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 3px solid #e67e22;
                border-radius: 15px;
                padding: 5px;
            }
        """)
        if self.nuevaImagen and isinstance(self.nuevaImagen, (bytes, bytearray)):
            pixmap = QPixmap()
            pixmap.loadFromData(self.nuevaImagen)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.imagenLabel.setPixmap(pixmap)
        else:
            self.imagenLabel.setText("SIN IMAGEN")
            self.imagenLabel.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    border: 3px dashed #e67e22;
                    border-radius: 15px;
                    color: #7f8c8d;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
        imagen_preview_container.addWidget(self.imagenLabel)
        imagen_preview_container.addStretch()
        imagen_layout.addLayout(imagen_preview_container)
        form_layout.addWidget(imagen_container)
        layoutPrincipal.addWidget(form_container)
        botones_container = QFrame()
        botones_container.setStyleSheet("background: transparent; margin-top: 10px;")
        botones_layout = QHBoxLayout(botones_container)
        botones_layout.setSpacing(20)
        btn_cancelar = QPushButton("CANCELAR")
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.setMinimumHeight(45)
        btn_cancelar.setMinimumWidth(150)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e74c3c, stop: 1 #c0392b);
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c0392b, stop: 1 #a93226);
            }
        """)
        btn_cancelar.clicked.connect(self.cerrarVentana)
        btn_confirmar = QPushButton("CONFIRMAR")
        btn_confirmar.setCursor(Qt.PointingHandCursor)
        btn_confirmar.setMinimumHeight(45)
        btn_confirmar.setMinimumWidth(150)
        btn_confirmar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2ecc71, stop: 1 #27ae60);
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #27ae60, stop: 1 #1e8449);
            }
        """)
        btn_confirmar.clicked.connect(self.cambiarSub)
        botones_layout.addStretch()
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(btn_confirmar)
        botones_layout.addStretch()
        layoutPrincipal.addWidget(botones_container)
    

    def seleccionarImagen(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Imagen",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    self.nuevaImagen = f.read()
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.imagenLabel.setPixmap(pixmap)
                    self.imagenLabel.setStyleSheet("""
                        QLabel {
                            background-color: white;
                            border: 3px solid #27ae60;
                            border-radius: 15px;
                            padding: 5px;
                        }
                    """)
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Error")
                msg.setText(f"No se pudo cargar la imagen: {str(e)}")
                msg.exec_()
    

    def cambiarSub(self):
        nuevo = self.campo2.text().strip()
        if not nuevo:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText("La subcategoría no puede estar vacía")
            msg.exec_()
            return
        if nuevo.upper() in {item.upper() for item in self.conjunto}:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText(f"La subcategoría '{nuevo}' ya existe")
            msg.exec_()
            return
        self.nuevaSub = nuevo
        self.accept()
    

    def getSub(self):
        return self.nuevaSub
    

    def getImagen(self):
        return self.nuevaImagen
    

    def cerrarVentana(self):
        self.reject()