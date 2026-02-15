import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from Pop_up_ModificacionProductos import Pop_up_ModificacionProductos

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'database', 'cafebar.db')

DB_PATH = get_db_path()

def get_images_dir():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'Imagenes')

DIRECCION_IMAGEN = get_images_dir()

class ModificacionProductos(QWidget):
    def __init__(self):
        super().__init__() 
        self.setStyleSheet("""
            background-color: #f8fafc;
            font-family: 'Segoe UI', Arial, sans-serif;
            """)
        self.set_up()
        
    def set_up(self):
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20,20,20,20)
        self.crearFiltro()
        self.campoModificar()
        self.showMaximized()
        
    def crearFiltro(self):
        layoutFiltro=QHBoxLayout()
        self.campoBusqueda=QLineEdit()
        self.campoBusqueda.setFixedWidth(300)
        textoBusqueda=QLabel("Nombre: ")
        botonBusqueda=QPushButton()
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
        botonBusqueda.clicked.connect(lambda:self.filtrarDatos(self.campoBusqueda.text().strip()))
        layoutFiltro.addStretch(3)
        layoutFiltro.addWidget(textoBusqueda,alignment=Qt.AlignLeft,stretch=0)
        layoutFiltro.addWidget(self.campoBusqueda,alignment=Qt.AlignLeft,stretch=60)
        layoutFiltro.addWidget(botonBusqueda,alignment=Qt.AlignLeft,stretch=40)
        layoutFiltro.addStretch(100)
        self.layoutPrincipal.addLayout(layoutFiltro)
     
    def filtrarDatos(self,texto):
        tabla=self.tabla
        tabla.setRowCount(0)
        conn = sqlite3.connect(DB_PATH) 
        if(texto==""):
            consulta = """SELECT P.idProd, P.nomProd, P.descripcion, P.precioVenta, 
                         P.costoFabricacion, S.nombre as Subcategoria, C.nomCategoria as Categoria
                         FROM Producto P
                         JOIN Subcategoria S ON P.idSubcategoria = S.idSubcategoria
                         JOIN Categoria C ON S.idCategoria = C.idCategoria
                         WHERE P.activo = 1
                         ORDER BY P.nomProd"""

            c = conn.cursor()
            resultado = c.execute(consulta)
        else:
            consulta = """SELECT P.idProd, P.nomProd, P.descripcion, P.precioVenta, 
                         P.costoFabricacion, S.nombre as Subcategoria, C.nomCategoria as Categoria
                         FROM Producto P
                         JOIN Subcategoria S ON P.idSubcategoria = S.idSubcategoria
                         JOIN Categoria C ON S.idCategoria = C.idCategoria
                         WHERE P.nomProd LIKE ? AND P.activo = 1
                         ORDER BY P.nomProd"""

            c = conn.cursor()
            resultado = c.execute(consulta,(f"{texto}%",))
        
        registros = resultado.fetchall()
            
        for f, registro in enumerate(registros):
            self.tabla.insertRow(f)
            for c, campo in enumerate(registro[1:]):
                if c == 5:
                    boton=QPushButton()
                    boton.setStyleSheet("""background-color: #f8f9fa;""")
                    boton.setCursor(Qt.PointingHandCursor)
                    boton.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\modificarEmpleado.jpg"))
                    boton.setIconSize(QSize(50,50))
                    boton.clicked.connect(lambda checked, fila=f, id_prod=registro[0]: self.pantallaModificar(fila, id_prod))
                    self.tabla.setCellWidget(f,c+1,boton)
                    
                valor = str(campo) if campo is not None else ""
                item = QTableWidgetItem(valor)
                item.setTextAlignment(Qt.AlignCenter)
                item.setToolTip(valor) 
                self.tabla.setItem(f, c, item)
                
        conn.close()
        
    def campoModificar(self):
        layoutCampoModificar = QHBoxLayout()
        layoutCampoModificar.setSpacing(0)
        campoTabla = QWidget()
        campoEstilo = """background-color:white;
                       margin-bottom:20px;
                       border-radius:10px;"""
        campoTabla.setStyleSheet(campoEstilo)
        
        layoutTabla = QVBoxLayout()
        campoTabla.setLayout(layoutTabla)
        
        self.tabla = QTableWidget()
        
        self.tabla.setStyleSheet("""
                             QTableWidget {
                                    background-color: #f8f9fa;  
                                    gridline-color: #dee2e6;    
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
        self.tabla.verticalHeader().setDefaultSectionSize(130)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setFocusPolicy(Qt.NoFocus)
        self.tabla.setSelectionMode(QTableWidget.NoSelection) 
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers) 
        layoutTabla.addWidget(self.tabla)
        
        layoutCampoModificar.addWidget(campoTabla)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().setDefaultSectionSize(150)
        self.layoutPrincipal.addLayout(layoutCampoModificar)
            
    def cargarDatos(self):
        conn = sqlite3.connect(DB_PATH) 
        consulta = """SELECT P.idProd, P.nomProd, P.descripcion, P.precioVenta, 
                     P.costoFabricacion, S.nombre as Subcategoria, C.nomCategoria as Categoria
                     FROM Producto P
                     JOIN Subcategoria S ON P.idSubcategoria = S.idSubcategoria
                     JOIN Categoria C ON S.idCategoria = C.idCategoria
                     WHERE P.activo = 1
                     ORDER BY P.nomProd"""
        c = conn.cursor()
        resultado = c.execute(consulta)
        
        columnasNuevas = ['Nombre', 'Descripción', 'Precio Venta', 'Costo Fabricación', 'Subcategoría', 'Categoría', 'Acción']
        self.tabla.setColumnCount(len(columnasNuevas))
        self.tabla.setHorizontalHeaderLabels(columnasNuevas)
        self.tabla.setRowCount(0)
        
        anchos_columnas = {
            'Nombre': 200,
            'Descripción': 500,
            'Precio Venta': 200,
            'Costo Fabricación': 200,
            'Subcategoría': 150,
            'Categoría': 150,
            'Acción': 100
        }
        
        for i, col_name in enumerate(columnasNuevas):
            self.tabla.setColumnWidth(i, anchos_columnas.get(col_name, 100))
        
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        registros = resultado.fetchall()
            
        for f, registro in enumerate(registros):
            self.tabla.insertRow(f)
            for c, campo in enumerate(registro[1:]):
                if c == 5:
                    boton=QPushButton()
                    boton.setStyleSheet("""background-color: #f8f9fa;""")
                    boton.setCursor(Qt.PointingHandCursor)
                    boton.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\modificarEmpleado.jpg"))
                    boton.setIconSize(QSize(50,50))
                    boton.clicked.connect(lambda checked, fila=f, id_prod=registro[0]: self.pantallaModificar(fila, id_prod))
                    self.tabla.setCellWidget(f,c+1,boton)
                    
                valor = str(campo) if campo is not None else ""
                item = QTableWidgetItem(valor)
                item.setTextAlignment(Qt.AlignCenter)
                item.setToolTip(valor) 
                self.tabla.setItem(f, c, item)
        conn.close()
    
    def pantallaModificar(self, fila, id_prod):
        scroll_position = self.tabla.verticalScrollBar().value() if hasattr(self, 'tabla') else 0
        
        if not (0 <= fila < self.tabla.rowCount()):
            QMessageBox.warning(self, "Error", "Fila seleccionada no válida")
            return
    
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            consulta_producto = """SELECT P.nomProd, P.descripcion, P.precioVenta, P.costoFabricacion, 
                                 P.imgProd, S.nombre, C.nomCategoria, S.idSubcategoria, C.idCategoria
                                 FROM Producto P
                                 JOIN Subcategoria S ON P.idSubcategoria = S.idSubcategoria
                                 JOIN Categoria C ON S.idCategoria = C.idCategoria
                                 WHERE P.idProd = ? AND P.activo = 1"""
            c.execute(consulta_producto, (id_prod,))
            producto_data = c.fetchone()
            consulta_ingredientes = """SELECT S.nomIng, S.descripcion, PI.cantidadIngNecesitada 
                                     FROM ProductosIngredientes PI
                                     JOIN Stock S ON PI.idIng = S.idIng
                                     WHERE PI.idProd = ? AND S.disponible = 1"""
            c.execute(consulta_ingredientes, (id_prod,))
            ingredientes_data = c.fetchall()
            
            conn.close()

            pagina = Pop_up_ModificacionProductos(id_prod, producto_data, ingredientes_data, self)
            pagina.exec_()
            if hasattr(self, 'tabla'):
                QTimer.singleShot(0, lambda: self.tabla.verticalScrollBar().setValue(scroll_position))
            self.filtrarDatos(self.campoBusqueda.text().strip())
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al modificar: {str(e)}")
            if hasattr(self, 'tabla'):
                self.tabla.verticalScrollBar().setValue(scroll_position)
        
if __name__=="__main__":
    app = QApplication(sys.argv)
    pagina = ModificacionProductos()
    pagina.show()
    sys.exit(app.exec_())