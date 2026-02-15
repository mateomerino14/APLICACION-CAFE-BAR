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

class Pop_up_ModificacionCargos(QDialog):
    def __init__(self, datos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MODIFICACIÓN DE CARGOS")
        self.setFixedSize(800, 600)
        self.setStyleSheet("""
            QDialog {
                background: #f8fafc;
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
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background: white;
            }
        """)
        
        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(main_widget)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layoutDatos = QVBoxLayout(main_widget)
        layoutDatos.setSpacing(20)
        layoutDatos.setContentsMargins(30, 25, 30, 25)
        titulo = QLabel("MODIFICACIÓN DE CARGOS")
        titulo.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #2c3e50;
                font-weight: bold;
                padding: 15px 0px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3498db, stop: 1 #2c3e50);
                border-radius: 8px;
                color: white;
                margin-bottom: 5px;
            }
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layoutDatos.addWidget(titulo)
        layoutCargo = QHBoxLayout()
        cargo = QLabel("Cargo:")
        campoCargo = QLabel(str(datos[0]))
        label_style = """
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
                padding: 8px 5px;
            }
        """
        campo_style = """
            QLabel {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                color: #495057;
                font-weight: 500;
                min-height: 20px;
            }
        """
        cargo.setStyleSheet(label_style)
        campoCargo.setStyleSheet(campo_style)
        campoCargo.setMinimumHeight(40)
        campoCargo.setAlignment(Qt.AlignCenter)
        layoutCargo.addWidget(cargo)
        layoutCargo.addWidget(campoCargo)
        layoutDatos.addLayout(layoutCargo)
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        separador.setStyleSheet("""
            QFrame {
                background-color: #dee2e6;
                margin: 15px 0px;
                height: 2px;
                border: none;
            }
        """)
        layoutDatos.addWidget(separador)
        tituloSecciones = QLabel("PERMISOS DE ACCESO")
        tituloSecciones.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                background-color: #6c757d;
                padding: 10px 15px;
                border-radius: 6px;
                margin-bottom: 5px;
            }
        """)
        tituloSecciones.setAlignment(Qt.AlignCenter)
        layoutDatos.addWidget(tituloSecciones)
        checkbox_style = """
            QCheckBox {
                font-size: 14px;
                color: #495057;
                spacing: 12px;
                padding: 8px 12px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #dee2e6;
            }
            QCheckBox:hover {
                background-color: #e9ecef;
                border: 1px solid #ced4da;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #adb5bd;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background-color: #28a745;
                border: 2px solid #218838;
                image: url(none);
            }
            QCheckBox::indicator:unchecked:hover {
                border: 2px solid #6c757d;
            }
        """
        seccion1 = QCheckBox("📋 Familia")
        seccion2 = QCheckBox("📁 Secciones")
        seccion3 = QCheckBox("💰 Caja")
        seccion5 = QCheckBox("📦 Stock")
        seccion6 = QCheckBox("📊 Reportes")
        seccion7 = QCheckBox("⚙️ Administracion")
        seccion8 = QCheckBox("🍽️ Productos")
        seccion9 = QCheckBox("🎯 Promociones")
        seccion10 = QCheckBox("👤 Empleados")
        checkboxes = [seccion1, seccion2, seccion3, seccion5, 
                     seccion6, seccion7, seccion8, seccion9, seccion10]
        for checkbox in checkboxes:
            checkbox.setStyleSheet(checkbox_style)
            checkbox.setCursor(Qt.PointingHandCursor)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.addWidget(seccion1, 0, 0)
        grid_layout.addWidget(seccion2, 0, 1)
        grid_layout.addWidget(seccion3, 0, 2)
        grid_layout.addWidget(seccion5, 0, 3)
        grid_layout.addWidget(seccion6, 1, 0)
        grid_layout.addWidget(seccion7, 1, 1)
        grid_layout.addWidget(seccion8, 1, 2)
        grid_layout.addWidget(seccion9, 1, 3)
        grid_layout.addWidget(seccion10, 2, 0)
        layoutDatos.addLayout(grid_layout)
        layoutDatos.addStretch(1)
        layoutBotones = QHBoxLayout()
        cancelar = QPushButton("CANCELAR")
        modificar = QPushButton("GUARDAR CAMBIOS")
        boton_cancelar_style = """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #dc3545, stop: 1 #c82333);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 14px;
                min-width: 130px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c82333, stop: 1 #bd2130);
            }
            QPushButton:pressed {
                background: #bd2130;
                padding: 11px 24px;
            }
        """
        
        boton_guardar_style = """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #28a745, stop: 1 #218838);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 14px;
                min-width: 130px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #218838, stop: 1 #1e7e34);
            }
            QPushButton:pressed {
                background: #1e7e34;
                padding: 11px 24px;
            }
        """
        cancelar.setStyleSheet(boton_cancelar_style)
        modificar.setStyleSheet(boton_guardar_style)
        cancelar.setCursor(Qt.PointingHandCursor)
        modificar.setCursor(Qt.PointingHandCursor)
        cancelar.clicked.connect(self.cerrarVentanaCancelar)
        modificar.clicked.connect(lambda: self.guardarCargos(datos[0]))
        layoutBotones.addStretch(1)
        layoutBotones.addWidget(cancelar)
        layoutBotones.addSpacing(20)
        layoutBotones.addWidget(modificar)
        layoutBotones.addStretch(1)
        layoutDatos.addLayout(layoutBotones)
        self.objetos = checkboxes
        listaPaginas = datos[1].split(',')
        conjunto = set(listaPaginas)
        for checkbox in self.objetos:
            nombre_checkbox = checkbox.text().split(' ', 1)[1] if ' ' in checkbox.text() else checkbox.text()
            if nombre_checkbox in conjunto:
                checkbox.setChecked(True)
           
    def cerrarVentanaCancelar(self):
        self.reject()
        
    def guardarCargos(self, nomCargo):
        marcados = []
        for elem in self.objetos:
            if elem.isChecked():
                nombre = elem.text().split(' ', 1)[1] if ' ' in elem.text() else elem.text()
                marcados.append(nombre)    
        if len(marcados) == 0:
            QMessageBox.warning(self, "Advertencia", "Se debe dar acceso por lo menos a una página")
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        consultaIdCargo = """SELECT idCargo FROM Cargo WHERE nomCarg=?"""
        c.execute(consultaIdCargo, (nomCargo,))
        resultado = c.fetchone()
        idCargo = resultado[0]
        eliminar = """DELETE FROM PermisosCargo WHERE idCarg=?"""
        c.execute(eliminar, (idCargo,))
        for elem in marcados:
            idConsulta = """SELECT idPant FROM Pantalla WHERE nomPant=?"""
            c.execute(idConsulta, (elem,))
            resultado = c.fetchone()
            if resultado:
                idPantalla = resultado[0]
                consulta = """INSERT INTO PermisosCargo(idCarg, idPant) VALUES (?, ?)"""
                c.execute(consulta, (idCargo, idPantalla))    
        conn.commit()
        conn.close()   
        QMessageBox.information(self, "Confirmación", "Se ha registrado con éxito la modificación")
        self.accept()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_start_position'):
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    datos_ejemplo = ["Administrador","Familia","Secciones","Caja","Stock","Reportes","Administración"]
    pagina = Pop_up_ModificacionCargos(datos_ejemplo)
    pagina.show()
    sys.exit(app.exec_())