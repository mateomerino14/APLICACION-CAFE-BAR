import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from functools import partial
from Pop_up_ModificacionIngredientes import Pop_up_ModificacionIngredientes

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

DIRECCION_IMAGENES = get_images_dir()


class ModificacionIngredientes(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background-color: #f8fafc;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        self.set_up()
        
    def set_up(self):
        self.layoutDatos = QHBoxLayout()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20,20,20,20)
        self.crearFiltro()
        self.campoModificar()
        self.showMaximized()

    def cargarNombresIngredientes(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT nomIng FROM Stock")
            nombres = [row[0] for row in c.fetchall()]
            conn.close()
            return nombres
        except:
            return []

    #No tocar
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

        
        botonBusqueda.setIcon(QIcon(f"{DIRECCION_IMAGENES}\\lupa.png"))
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
            consulta = """SELECT idIng,nomIng,descripcion,cantidadStock,unidadMedida,COALESCE(precioExtra,0)
                          FROM Stock
                          ORDER BY nomIng ASC"""
            c = conn.cursor()
            resultado = c.execute(consulta)
        else:
            consulta = """SELECT idIng,nomIng,descripcion,cantidadStock,unidadMedida,COALESCE(precioExtra,0)
                 FROM Stock
                 WHERE nomIng LIKE ?
                 ORDER BY nomIng ASC"""
            c = conn.cursor()
            resultado = c.execute(consulta,(f"{texto}%",))
        
        registros = resultado.fetchall()
        for f, registro in enumerate(registros):
            self.tabla.insertRow(f)
            for c, campo in enumerate(registro):
                if c!=0:
                    if c == len(registro)-1: 
                        boton=QPushButton()
                        boton.setStyleSheet("""background-color: #f8f9fa;""")
                        boton.setCursor(Qt.PointingHandCursor)
                        boton.setIcon(QIcon(f"{DIRECCION_IMAGENES}\\modificarEmpleado.jpg"))
                        boton.setIconSize(QSize(50,50))
                        boton.clicked.connect(lambda checked,fila=f,idIng=registro[0]: self.pantallaModificar(idIng,fila))
                        self.tabla.setCellWidget(f,c,boton)
      
                    valor = str(campo) if campo is not None else ""
                    item = QTableWidgetItem(valor)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setToolTip(valor) 
                    self.tabla.setItem(f, c-1, item)
        
        conn.close()
        
        
        
    #No tocar     
    def campoModificar(self):
        layoutCampoModificar=QHBoxLayout()
        layoutCampoModificar.setSpacing(0)
        campoModificar=QWidget()
        campoTabla=QWidget()
        campoEstilo="""background-color:white;
                       margin-bottom:20px;
                       border-radius:10px;"""
                      
        editEstilo=("""font-size:15px;
                       font-weight:bold;
                       """)
        campoEscribirEstilo=("""border:1px solid black;
                                border-radius:3px;""")
        campoModificar.setStyleSheet(campoEstilo)
        campoTabla.setStyleSheet(campoEstilo)
        layoutTabla=QVBoxLayout()
        campoTabla.setLayout(layoutTabla)
        
        self.tabla=QTableWidget()
        self.tabla.setFocusPolicy(False)
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
        consulta = """SELECT idIng,nomIng,descripcion,cantidadStock,unidadMedida,COALESCE(precioExtra,0)
                      FROM Stock
                      ORDER BY nomIng ASC"""
        c = conn.cursor()
        resultado = c.execute(consulta)
        columnas = [desc[0] for desc in c.description]
        columnas.pop(0)
        mapeo_nombres = {
            'nomIng': 'Nombre',
            'descripcion': 'Descripcion',
            'cantidadStock': 'Cantidad',
            'unidadMedida': 'Unidad de Medida',
            'COALESCE(precioExtra,0)': 'Precio Extra'
        }
        
        columnasNuevas = [mapeo_nombres[colum] for colum in columnas]
        columnasNuevas.append("Accion")
        self.tabla.setColumnCount(len(columnasNuevas))
        self.tabla.setHorizontalHeaderLabels(columnasNuevas)
        self.tabla.setRowCount(0)
        anchos_columnas = {
            'Nombre': 300,
            'Descripcion': 380,
            'Cantidad': 250,
            'Unidad de Medida': 250,
            'Precio Extra': 200
        }
        for i, col_name in enumerate(columnasNuevas):
            self.tabla.setColumnWidth(i, anchos_columnas.get(col_name, 100)) 
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        registros = resultado.fetchall()
        for f, registro in enumerate(registros):
            self.tabla.insertRow(f)
            for c, campo in enumerate(registro):
               if c!=0:
                    if c == len(registro)-1:  
                        boton=QPushButton()
                        boton.setStyleSheet("""background-color: #f8f9fa;""")
                        boton.setCursor(Qt.PointingHandCursor)
                        boton.setIcon(QIcon(f"{DIRECCION_IMAGENES}\\modificarEmpleado.jpg"))
                        boton.setIconSize(QSize(50,50))
                        boton.clicked.connect(lambda checked,fila=f,idIng=registro[0]: self.pantallaModificar(idIng,fila))
                        self.tabla.setCellWidget(f,c,boton)
                    valor = str(campo) if campo is not None else ""
                    item = QTableWidgetItem(valor)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setToolTip(valor) 
                    self.tabla.setItem(f, c-1, item)
        conn.close()
    

    def pantallaModificar(self, idIng, fila):
        if not (0 <= fila < self.tabla.rowCount()):
            QMessageBox.warning(self, "Error", "Fila seleccionada no válida")
            return
        try:
            datos = [idIng]
            for c in range(self.tabla.columnCount()-1): 
                item = self.tabla.item(fila, c)
                datos.append(item.text() if item else "")
            scroll_pos = self.tabla.verticalScrollBar().value()
            pagina = Pop_up_ModificacionIngredientes(datos, self)
            pagina.nombres_existentes = self.cargarNombresIngredientes()
            pagina.exec_()
            self.filtrarDatos(self.campoBusqueda.text().strip())
            self.tabla.verticalScrollBar().setValue(scroll_pos)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al modificar: {str(e)}")
        
    
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    pagina = ModificacionIngredientes()
    pagina.show()
    sys.exit(app.exec_())