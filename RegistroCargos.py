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

class RegistroCargos(QWidget):
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
        self.checkboxes = []  
        self.set_up()
    

    def set_up(self):
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.layoutPrincipal.setSpacing(0)
        self.anadirAreaRegistro()
        self.layoutPrincipal.addStretch(1)
        self.showMaximized()
    

    def anadirAreaRegistro(self):
        area = QWidget()
        area.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
            padding: 25px;
            border: 1px solid #d1d5db;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        """)
        area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layoutPrincipal.addWidget(area)
        layoutVertical = QVBoxLayout(area)
        layoutVertical.setContentsMargins(40, 40, 40, 40)
        layoutVertical.setSpacing(30)
        layoutCampos = QHBoxLayout()
        layoutCampos.setSpacing(20)
        nombre = QLabel("Nombre del Cargo: ")
        nombre.setStyleSheet("""
            font-size: 18px;
            font-weight: 500;
            color: #374151;
            padding: 5px 0;
        """)
        layoutCampos.addWidget(nombre)
        self.campoNombre = QComboBox()
        self.campoNombre.addItems(["Cajero","Mesero","Cocinero"])
        self.campoNombre.setStyleSheet("""
            border: 2px solid #d1d5db;
            border-radius: 6px;
            padding: 12px 15px;
            font-size: 16px;
        """)
        self.campoNombre.setMinimumHeight(40)
        self.campoNombre.setCurrentIndex(-1)
        layoutCampos.addWidget(self.campoNombre, 1)  
        layoutVertical.addLayout(layoutCampos)
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        separador.setStyleSheet("color: #e5e7eb;")
        layoutVertical.addWidget(separador)
        tituloPermisos = QLabel("Permisos de Acceso")
        tituloPermisos.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #374151;
            padding: 5px 0;
        """)
        layoutVertical.addWidget(tituloPermisos, alignment=Qt.AlignCenter)
        gridLayout = QGridLayout()
        gridLayout.setSpacing(25)
        gridLayout.setContentsMargins(50, 20, 50, 20)
        checkbox_style = """
            QCheckBox {
                font-size: 20px;
                color: #374151;
                spacing: 10px;
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border: 2px solid #4f46e5;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #4f46e5;
            }
            QCheckBox:hover {
                background-color: #f9fafb;
                border-radius: 6px;
            }
        """
        #, 'Clientes'
        opciones = ['Familia', 'Caja', 'Administracion', 'Productos', 
                   'Secciones', 'Stock', 'Promociones', 'Empleados', 'Reportes']
        self.checkboxes = []
        for i, opcion in enumerate(opciones):
            checkbox = QCheckBox(opcion, self)
            checkbox.setStyleSheet(checkbox_style)
            self.checkboxes.append(checkbox)
            fila = i // 5
            columna = i % 5
            gridLayout.addWidget(checkbox, fila, columna, alignment=Qt.AlignCenter)
        layoutVertical.addLayout(gridLayout)
        layoutVertical.addStretch(1)
        layoutBotones = QHBoxLayout()
        layoutBotones.setSpacing(30)
        layoutBotones.setContentsMargins(100, 20, 100, 10)
        botonSubir = QPushButton("Registrar Cargo")
        botonSubir.clicked.connect(self.subirDatos)
        botonCancelar = QPushButton("Cancelar")
        botonCancelar.clicked.connect(self.limpiarTodo)
        button_style = """
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 14px 28px;
                font-size: 16px;
                font-weight: 500;
            }
        """
        botonSubir.setStyleSheet(button_style + """
            QPushButton {
                background-color: #4f46e5;
                color: white;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
        """)
        botonCancelar.setStyleSheet(button_style + """
            QPushButton {
                background-color: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
            QPushButton:pressed {
                background-color: #d1d5db;
            }
        """)
        for btn in [botonSubir, botonCancelar]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumSize(180, 50)
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            layoutBotones.addWidget(btn)
        layoutVertical.addLayout(layoutBotones)


    def subirDatos(self):
        if not os.path.exists(DB_PATH):
            QMessageBox.critical(
                self,
                "Error de base de datos",
                f"No se encontró la base de datos en la ruta:\n{DB_PATH}"
            )
            return
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            c = conn.cursor()
            nuevoCargo = self.campoNombre.currentText().strip()
            if not nuevoCargo:
                QMessageBox.warning(self, "Advertencia", "El nombre del cargo no puede estar vacío")
                return
            pantallas_seleccionadas = [cb.text().strip() for cb in self.checkboxes if cb.isChecked()]
            if len(pantallas_seleccionadas) == 0:
                QMessageBox.information(self, "Advertencia", "Se debe dar acceso por lo menos a una página")
                return 
            conn.execute("BEGIN TRANSACTION")
            c.execute("INSERT INTO Cargo(nomCarg) VALUES(?)", (nuevoCargo,))
            id_cargo = c.lastrowid
            ids_pantallas = []
            for pantalla in pantallas_seleccionadas:
                c.execute("SELECT idPant FROM Pantalla WHERE nomPant=?", (pantalla,))
                resultado = c.fetchone()
                if resultado:
                    ids_pantallas.append(resultado[0])
                else:
                    raise ValueError(f"Pantalla '{pantalla}' no encontrada en la base de datos")
            
            for id_pantalla in ids_pantallas:
                c.execute("INSERT INTO PermisosCargo(idCarg, idPant) VALUES(?, ?)", 
                         (id_cargo, id_pantalla))
            conn.commit()
            QMessageBox.information(
                self,
                "Operación exitosa",
                "El cargo se registró correctamente con sus permisos"
            )
            self.limpiarTodo()
        except sqlite3.IntegrityError:
            if conn:
                conn.rollback()
            QMessageBox.critical(
                self,
                "Error",
                "Este cargo ya existe en la base de datos"
            )
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            QMessageBox.critical(
                self,
                "Error de base de datos",
                f"No se pudo completar la operación:\n{str(e)}"
            )
        except ValueError as e:
            if conn:
                conn.rollback()
            QMessageBox.warning(
                self,
                "Dato no encontrado",
                str(e)
            )
        except Exception as e:
            if conn:
                conn.rollback()
            QMessageBox.critical(
                self,
                "Error inesperado",
                f"Ocurrió un error no previsto:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
        
    def limpiarTodo(self):
        self.campoNombre.setCurrentIndex(-1)
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = RegistroCargos()
    pagina.show()
    sys.exit(app.exec_())