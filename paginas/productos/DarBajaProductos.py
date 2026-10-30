import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from nucleo.Rutas import get_db_path, get_images_dir

DB_PATH = get_db_path()
DIRECCION_IMAGEN = get_images_dir()


class DarBajaProductos(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMessageBox {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-weight: 500;
                font-size: 15px;
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
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.crearFiltro()
        self.campoModificar()
        self.showMaximized()

    def crearFiltro(self):
        layoutFiltro = QHBoxLayout()
        self.campoBusqueda = QLineEdit()
        self.campoBusqueda.setFixedWidth(300)
        textoBusqueda = QLabel("Nombre: ")
        botonBusqueda = QPushButton()
        self.campoBusqueda.setStyleSheet("""
                            QLineEdit {
                                padding: 8px 12px;
                                font-size: 16px;
                                border: 2px solid #4a7dbc;
                                border-radius: 6px;
                                background-color: white;
                            }
                            QLineEdit:focus {
                                border-color: #6a9cec;
                            }
                        """)
        textoBusqueda.setStyleSheet("""
                            font-size: 18px;
                            font-weight: bold;
                            color: #4a7dbc;
                            background-color:transparent;
                        """)
        botonBusqueda.setStyleSheet("""
                            QPushButton {
                                background-color: #4a7dbc;
                                border: none;
                                border-radius: 6px;
                                padding: 8px;
                            }
                            QPushButton:hover {
                                background-color: #6a9cec;
                            }
                        """)
        botonBusqueda.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\lupa.png"))
        botonBusqueda.clicked.connect(lambda: self.filtrarDatos(self.campoBusqueda.text().strip()))
        layoutFiltro.addStretch(3)
        layoutFiltro.addWidget(textoBusqueda, alignment=Qt.AlignLeft, stretch=0)
        layoutFiltro.addWidget(self.campoBusqueda, alignment=Qt.AlignLeft, stretch=60)
        layoutFiltro.addWidget(botonBusqueda, alignment=Qt.AlignLeft, stretch=40)
        layoutFiltro.addStretch(97)
        self.layoutPrincipal.addLayout(layoutFiltro)

    def filtrarDatos(self, texto):
        tabla = self.tabla
        tabla.setRowCount(0)
        conn = sqlite3.connect(DB_PATH)
        if texto == "":
            consulta = """SELECT nomProd,activo FROM Producto ORDER BY nomProd ASC"""
            c = conn.cursor()
            resultado = c.execute(consulta)
        else:
            consulta = consulta = """SELECT nomProd,activo FROM Producto WHERE nomProd LIKE ? ORDER BY nomProd ASC"""
            c = conn.cursor()
            resultado = c.execute(consulta, (f"{texto}%",))
        registros = resultado.fetchall()
        consultaAlias = """SELECT nomProd FROM Producto WHERE nomProd LIKE ? ORDER BY nomProd ASC"""
        resultado2 = c.execute(consultaAlias, (f"{texto}%",))
        regs = resultado2.fetchall()
        for f, registro in enumerate(registros):
            self.tabla.insertRow(f)
            elemento = regs[f]
            for c, campo in enumerate(registro):
                if c == 1:
                    casilla = QLabel()
                    if campo == 1:
                        casilla.setStyleSheet("""background-color:#00a135;""")
                    else:
                        casilla.setStyleSheet("""background-color:#ec5353;""")
                    self.tabla.setCellWidget(f, c, casilla)
                else:
                    valor = str(campo) if campo is not None else ""
                    item = QTableWidgetItem(valor)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setToolTip(valor)
                    self.tabla.setItem(f, c, item)
                if c == len(registro) - 1:
                    boton = QPushButton()
                    boton.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\darBajaEmpleado.webp"))
                    boton.setIconSize(QSize(30, 30))
                    boton.setCursor(Qt.PointingHandCursor)
                    boton.setStyleSheet("""background-color:transparent;""")
                    boton.clicked.connect(
                        lambda checked, alias=elemento[0], fila=f: self.deshabilitarProducto(fila, alias)
                    )
                    self.tabla.setCellWidget(f, c + 1, boton)
                    boton2 = QPushButton()
                    boton2.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\habilitar.png"))
                    boton2.setCursor(Qt.PointingHandCursor)
                    boton2.setIconSize(QSize(30, 30))
                    boton2.setStyleSheet("""background-color:transparent;""")
                    boton2.clicked.connect(
                        lambda checked, alias=elemento[0], fila=f: self.habilitarProducto(fila, alias)
                    )
                    self.tabla.setCellWidget(f, c + 2, boton2)

    def campoModificar(self):
        layoutCampoModificar = QHBoxLayout()
        layoutCampoModificar.setSpacing(0)
        campoModificar = QWidget()
        campoTabla = QWidget()
        campoTabla.setStyleSheet("""background-color:transparent;""")
        layoutTabla = QVBoxLayout()
        campoTabla.setLayout(layoutTabla)
        self.tabla = QTableWidget()
        self.tabla.setStyleSheet("""
                             QTableWidget {
                                    background-color: white;  
                                    gridline-color: #dee2e6;    
                                    padding:10px;
                                    border-radius:8px;
                                    border: 1px solid #ced4da;  
                                    font-family: 'Segoe UI';    
                            }
                            QHeaderView::section{
                                background-color: #495057;  
                                color: #ffffff;          
                                font-weight: bold;         
                                border: none;    
                            }
                            QTableWidget::item {
                                color: #343a40; 
                            }
                            QHeaderView {
                                margin: 0;
                                padding: 0;
                            }
                            QScrollBar::handle:vertical {
                                background: #adb5bd; 
                                border-radius: 5px;
                            }
                            QScrollBar:vertical {
                                width: 10px; 
                                background: #f1f3f5;  
                                border: none;
                            }
                            """)
        self.cargarDatos()
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setFocusPolicy(Qt.NoFocus)
        self.tabla.setSelectionMode(QTableWidget.NoSelection)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layoutTabla.addWidget(self.tabla)
        layoutCampoModificar.addWidget(campoTabla)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().setDefaultSectionSize(80)
        self.layoutPrincipal.addLayout(layoutCampoModificar)

    def cargarDatos(self):
        conn = sqlite3.connect(DB_PATH)
        consulta = """SELECT nomProd,activo FROM Producto ORDER BY nomProd ASC"""
        c = conn.cursor()
        resultado = c.execute(consulta)
        columnas = [desc[0] for desc in c.description]
        mapeo_nombres = {
            'nomProd': 'Nombre',
            'activo': 'Disponibilidad',
        }
        columnasNuevas = [mapeo_nombres[colum] for colum in columnas]
        columnasNuevas.append("Accion")
        columnasNuevas.append("Accion")
        self.tabla.setColumnCount(len(columnasNuevas))
        self.tabla.setHorizontalHeaderLabels(columnasNuevas)
        self.tabla.setRowCount(0)
        anchos_columnas = {'Nombre': 600, 'Disponibilidad': 500, 'Accion': 350}
        for i, col_name in enumerate(columnasNuevas):
            self.tabla.setColumnWidth(i, anchos_columnas.get(col_name, 100))
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        registros = resultado.fetchall()
        consultaAlias = """SELECT nomProd FROM Producto ORDER BY nomProd ASC"""
        resultado2 = c.execute(consultaAlias)
        regs = resultado2.fetchall()
        for f, registro in enumerate(registros):
            self.tabla.insertRow(f)
            elemento = regs[f]
            for c, campo in enumerate(registro):
                if c == 1:
                    casilla = QLabel()
                    if campo == 1:
                        casilla.setStyleSheet("""background-color:#00a135;""")
                    else:
                        casilla.setStyleSheet("""background-color:#ec5353;""")
                    self.tabla.setCellWidget(f, c, casilla)
                else:
                    valor = str(campo) if campo is not None else ""
                    item = QTableWidgetItem(valor)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setToolTip(valor)
                    self.tabla.setItem(f, c, item)
                if c == len(registro) - 1:
                    boton = QPushButton()
                    boton.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\darBajaEmpleado.webp"))
                    boton.setIconSize(QSize(30, 30))
                    boton.setCursor(Qt.PointingHandCursor)
                    boton.setStyleSheet("""background-color:transparent;""")
                    boton.clicked.connect(
                        lambda checked, alias=elemento[0], fila=f: self.deshabilitarProducto(fila, alias)
                    )
                    self.tabla.setCellWidget(f, c + 1, boton)
                    boton2 = QPushButton()
                    boton2.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\habilitar.png"))
                    boton2.setCursor(Qt.PointingHandCursor)
                    boton2.setIconSize(QSize(30, 30))
                    boton2.setStyleSheet("""background-color:transparent;""")
                    boton2.clicked.connect(
                        lambda checked, alias=elemento[0], fila=f: self.habilitarProducto(fila, alias)
                    )
                    self.tabla.setCellWidget(f, c + 2, boton2)
        conn.close()

    def deshabilitarProducto(self, fila, alias):
        scroll_position = self.tabla.verticalScrollBar().value()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        consulta = """UPDATE Producto
                     SET activo=0 WHERE nomProd=?"""
        c.execute(consulta, (alias,))
        conn.commit()
        conn.close()
        self.filtrarDatos(self.campoBusqueda.text().strip())
        self.tabla.verticalScrollBar().setValue(scroll_position)

    def habilitarProducto(self, fila, alias):
        scroll_position = self.tabla.verticalScrollBar().value()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        consulta = """UPDATE Producto
                     SET activo=1 WHERE nomProd=?"""
        c.execute(consulta, (alias,))
        conn.commit()
        conn.close()
        self.filtrarDatos(self.campoBusqueda.text().strip())
        self.tabla.verticalScrollBar().setValue(scroll_position)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = DarBajaProductos()
    pagina.show()
    sys.exit(app.exec_())
