import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from Rutas import get_db_path, get_images_dir

DIRECCION_IMAGEN = get_images_dir()

DB_PATH = get_db_path()

class DarBajaEmpleados(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
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
        layoutFiltro.addStretch(2)
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
            consulta = """SELECT nomEmp, 
                 apellPatEmp, apellMatEmp, disponibleEmp FROM Empleado ORDER BY nomEmp ASC"""
            c = conn.cursor()
            resultado = c.execute(consulta)
        else:
            consulta = consulta = """SELECT nomEmp, 
                 apellPatEmp, apellMatEmp, disponibleEmp FROM Empleado WHERE nomEmp LIKE ? ORDER BY nomEmp ASC"""
            c = conn.cursor()
            resultado = c.execute(consulta,(f"{texto}%",))
        
        registros = resultado.fetchall()
        consultaAlias= """SELECT aliasEmp FROM Empleado WHERE nomEmp LIKE ? ORDER BY nomEmp ASC"""
        resultado2=c.execute(consultaAlias,(f"{texto}%",))
        regs=resultado2.fetchall()
        for f, registro in enumerate(registros):
            self.tabla.insertRow(f)
            elemento=regs[f]
            for c, campo in enumerate(registro):
                    if c==3:
                        casilla=QLabel()
                        if(campo==1):
                            casilla.setStyleSheet("""background-color:#00a135;""")
                        else:
                            casilla.setStyleSheet("""background-color:#ec5353;""")
                        self.tabla.setCellWidget(f,c,casilla)
                    else:
                        valor = str(campo) if campo is not None else ""
                        item = QTableWidgetItem(valor)
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setToolTip(valor) 
                        self.tabla.setItem(f, c, item)
                    if c==len(registro)-1:
                        boton=QPushButton()
                        boton.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\darBajaEmpleado.webp"))
                        boton.setIconSize(QSize(30,30))
                        boton.setCursor(Qt.PointingHandCursor)
                        boton.setStyleSheet("""background-color:transparent;""")
                        boton.clicked.connect(lambda checked, alias=elemento[0],fila=f:self.deshabilitarEmpleado(fila,alias))
                        self.tabla.setCellWidget(f,c+1,boton)
                        boton2=QPushButton()
                        boton2.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\habilitar.png"))
                        boton2.setCursor(Qt.PointingHandCursor)
                        boton2.setIconSize(QSize(30,30))
                        boton2.setStyleSheet("""background-color:transparent;""")
                        boton2.clicked.connect(lambda checked, alias=elemento[0],fila=f:self.habilitarEmpleado(fila,alias))
                        self.tabla.setCellWidget(f,c+2,boton2)
        
    def campoModificar(self):
        layoutCampoModificar=QHBoxLayout()
        layoutCampoModificar.setSpacing(0)
        campoModificar=QWidget()
        campoTabla=QWidget()
        layoutTabla=QVBoxLayout()
        campoTabla.setLayout(layoutTabla)
        self.tabla=QTableWidget()
        self.tabla.setStyleSheet("""
                             QTableWidget {
                                    background-color: #f8f9fa;  
                                    gridline-color: #dee2e6;    
                                    border: 1px solid #ced4da;  
                                    font-family: 'Segoe UI';   
                                    border-radius:10px;
                                    padding:10px;
                            }
                            QHeaderView::section{
                                background-color: #495057; 
                                color: #ffffff;             
                                font-weight: bold;         
                                border: none;    
                            }
                            QTableWidget::item {
                                color: #343a40; 
                                /* Color de texto oscuro */
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
        consulta = """SELECT nomEmp, 
             apellPatEmp, apellMatEmp, disponibleEmp FROM Empleado ORDER BY nomEmp ASC"""
        c = conn.cursor()
        resultado = c.execute(consulta)
        columnas = [desc[0] for desc in c.description]
        mapeo_nombres = {
            'nomEmp': 'Nombre',
            'apellPatEmp': 'Ap. Paterno',
            'apellMatEmp': 'Ap. Materno',
            'disponibleEmp': 'Disponibilidad',
        }
        columnasNuevas = [mapeo_nombres[colum] for colum in columnas]
        columnasNuevas.append("Accion")
        columnasNuevas.append("Accion")
        self.tabla.setColumnCount(len(columnasNuevas))
        self.tabla.setHorizontalHeaderLabels(columnasNuevas)
        self.tabla.setRowCount(0)
        anchos_columnas = {
            'Nombre': 300,
            'Ap. Paterno': 300,
            'Ap. Materno': 300,
            'Disponibilidad': 250,
            'Accion': 300
        }
        for i, col_name in enumerate(columnasNuevas):
            self.tabla.setColumnWidth(i, anchos_columnas.get(col_name, 100)) 
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        registros = resultado.fetchall()
        consultaAlias= """SELECT aliasEmp FROM Empleado ORDER BY nomEmp ASC"""
        resultado2=c.execute(consultaAlias)
        regs=resultado2.fetchall()
        for f, registro in enumerate(registros):
            self.tabla.insertRow(f)
            elemento=regs[f]
            for c, campo in enumerate(registro):
                    if c==3:
                        casilla=QLabel()
                        if(campo==1):
                            casilla.setStyleSheet("""background-color:#00a135;""")
                        else:
                            casilla.setStyleSheet("""background-color:#ec5353;""")
                        self.tabla.setCellWidget(f,c,casilla)
                    else:
                        valor = str(campo) if campo is not None else ""
                        item = QTableWidgetItem(valor)
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setToolTip(valor) 
                        self.tabla.setItem(f, c, item)
                    if c==len(registro)-1:
                        boton=QPushButton()
                        boton.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\darBajaEmpleado.webp"))
                        boton.setIconSize(QSize(30,30))
                        boton.setCursor(Qt.PointingHandCursor)
                        boton.setStyleSheet("""background-color:transparent;""")
                        boton.clicked.connect(lambda checked, alias=elemento[0],fila=f:self.deshabilitarEmpleado(fila,alias))
                        self.tabla.setCellWidget(f,c+1,boton)
                        boton2=QPushButton()
                        boton2.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\habilitar.png"))
                        boton2.setCursor(Qt.PointingHandCursor)
                        boton2.setIconSize(QSize(30,30))
                        boton2.setStyleSheet("""background-color:transparent;""")
                        boton2.clicked.connect(lambda checked, alias=elemento[0],fila=f:self.habilitarEmpleado(fila,alias))
                        self.tabla.setCellWidget(f,c+2,boton2)
        conn.close()
    

   
        
        
    def deshabilitarEmpleado(self,fila,alias):
        scroll_position = self.tabla.verticalScrollBar().value()
        conn=sqlite3.connect(DB_PATH)
        c=conn.cursor()
        consulta="""UPDATE Empleado
                     SET disponibleEmp=0 WHERE aliasEmp=?"""
        c.execute(consulta,(alias,))
        conn.commit()
        conn.close()
        self.filtrarDatos(self.campoBusqueda.text().strip())
        self.tabla.verticalScrollBar().setValue(scroll_position)
        
        
    def habilitarEmpleado(self,fila,alias):
        scroll_position = self.tabla.verticalScrollBar().value()
        conn=sqlite3.connect(DB_PATH)
        c=conn.cursor()
        consulta="""UPDATE Empleado
                     SET disponibleEmp=1 WHERE aliasEmp=?"""
        c.execute(consulta,(alias,))
        conn.commit()
        conn.close()
        self.filtrarDatos(self.campoBusqueda.text().strip())
        self.tabla.verticalScrollBar().setValue(scroll_position)
        
        
        
if __name__=="__main__":
    app = QApplication(sys.argv)
    pagina = DarBajaEmpleados()
    pagina.show()
    sys.exit(app.exec_())