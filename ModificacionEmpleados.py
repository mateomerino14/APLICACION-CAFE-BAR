import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from functools import partial
from Pop_up_ModificacionEmpleado import Pop_up_ModificacionEmpleado

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

class ModificacionEmpleados(QWidget):
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
        layoutFiltro.addStretch(97)
        self.layoutPrincipal.addLayout(layoutFiltro)
     
        
    def filtrarDatos(self,texto):
        tabla=self.tabla
        tabla.setRowCount(0)
        conn = sqlite3.connect(DB_PATH) 
        if(texto==""):
            consulta = """SELECT aliasEmp, contEmp, ciEmp, nomEmp, 
                 apellPatEmp, apellMatEmp, numCelEmp,
                 direccionEmp, correoElEmp, nomCarg, imgEmp 
                 FROM Empleado E, Cargo C 
                 WHERE E.idCargo=C.idCargo AND disponibleEmp=1 
                 ORDER BY nomEmp ASC"""
            c = conn.cursor()
            resultado = c.execute(consulta)
        else:
            consulta = """SELECT aliasEmp, contEmp, ciEmp, nomEmp, 
                 apellPatEmp, apellMatEmp, numCelEmp,
                 direccionEmp, correoElEmp, nomCarg, imgEmp 
                 FROM Empleado E, Cargo C 
                 WHERE E.idCargo=C.idCargo AND disponibleEmp=1 AND nomEmp LIKE ?
                 ORDER BY nomEmp ASC"""
            c = conn.cursor()
            resultado = c.execute(consulta,(f"{texto}%",))
        
        registros = resultado.fetchall()
        for f, registro in enumerate(registros):
            self.tabla.insertRow(f)
            for c, campo in enumerate(registro):
                if c == len(registro)-1:
                    if campo:
                        pixmap = QPixmap()
                        pixmap.loadFromData(campo)
                        img = QLabel()
                        img.setStyleSheet("""background-color: #f8f9fa;""")
                        img.setPixmap(pixmap.scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                        img.setAlignment(Qt.AlignCenter)
                        self.tabla.setCellWidget(f, c, img)
                    else:
                        item = QTableWidgetItem("Sin imagen")
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tabla.setItem(f, c, item)
                    boton=QPushButton()
                    boton.setStyleSheet("""background-color: #f8f9fa;""")
                    boton.setCursor(Qt.PointingHandCursor)
                    boton.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\modificarEmpleado.jpg"))
                    boton.setIconSize(QSize(50,50))
                    boton.clicked.connect(lambda checked, fila=f: self.pantallaModificar(fila))
                    self.tabla.setCellWidget(f,c+1,boton)
                else:
                    valor = str(campo) if campo is not None else ""
                    item = QTableWidgetItem(valor)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setToolTip(valor) 
                    self.tabla.setItem(f, c, item)
        
        conn.close()
        
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
        layoutDatos=QVBoxLayout()
        layoutDatos.setSpacing(0)
        campoModificar.setLayout(layoutDatos)
        nombre = QLabel("NOMBRE")
        apellido = QLabel("APELLIDO PATERNO")
        apellido2 = QLabel("APELLIDO MATERNO")
        ci = QLabel("CI")
        numCelular = QLabel("NÚMERO DE CELULAR")
        idCargo = QLabel("CARGO")
        direccion = QLabel("DIRECCIÓN")
        correoElectronico = QLabel("CORREO ELECTRÓNICO")
    
        campoNombre=QLineEdit()
        campoApellido=QLineEdit()
        campoApellido2=QLineEdit()
        campoCi=QLineEdit()
        campoNumeroCelular=QLineEdit()
        campoCargo=QComboBox()
        campoDireccion=QLineEdit()
        campoCorreo=QLineEdit()
        
        nombre.setStyleSheet(editEstilo)
        apellido.setStyleSheet(editEstilo)
        apellido2.setStyleSheet(editEstilo)
        ci.setStyleSheet(editEstilo)
        numCelular.setStyleSheet(editEstilo)
        idCargo.setStyleSheet(editEstilo)
        direccion.setStyleSheet(editEstilo)
        correoElectronico.setStyleSheet(editEstilo)
        
        campoNombre.setStyleSheet(campoEscribirEstilo)
        campoApellido.setStyleSheet(campoEscribirEstilo)
        campoApellido2.setStyleSheet(campoEscribirEstilo)
        campoCi.setStyleSheet(campoEscribirEstilo)
        campoNumeroCelular.setStyleSheet(campoEscribirEstilo)
        campoCargo.setStyleSheet(campoEscribirEstilo)
        campoDireccion.setStyleSheet(campoEscribirEstilo)
        campoCorreo.setStyleSheet(campoEscribirEstilo)
        
        
        layout1=QHBoxLayout()
        layout2=QHBoxLayout()
        layout3=QHBoxLayout()
        layout4=QHBoxLayout()
        layout5=QHBoxLayout()
        layout6=QHBoxLayout()
        layout7=QHBoxLayout()
        layout8=QHBoxLayout()
        
        layout1.addWidget(nombre)
        layout1.addWidget(campoNombre)
        
        layout2.addWidget(apellido)
        layout2.addWidget(campoApellido)
        
        layout3.addWidget(apellido2)
        layout3.addWidget(campoApellido2)
        
        layout4.addWidget(ci)
        layout4.addWidget(campoCi)
        
        layout5.addWidget(numCelular)
        layout5.addWidget(campoNumeroCelular)
        
        layout6.addWidget(idCargo)
        layout6.addWidget(campoCargo)
        
        layout7.addWidget(direccion)
        layout7.addWidget(campoDireccion)
        
        layout8.addWidget(correoElectronico)
        layout8.addWidget(campoCorreo)
       
        layoutDatos.addLayout(layout1)
        layoutDatos.addLayout(layout2)
        layoutDatos.addLayout(layout3)
        layoutDatos.addLayout(layout4)
        layoutDatos.addLayout(layout5)
        layoutDatos.addLayout(layout6)
        layoutDatos.addLayout(layout7)
        layoutDatos.addLayout(layout8)
        imagen=QLabel()
        imagen.setFixedSize(140,140)
        imagen.setStyleSheet("""border:2px dashed gray;
                                border-radius:4px;""")
                                
                                
        layoutImagen=QHBoxLayout()      
        cancelar=QPushButton("CANCELAR")
        modificar=QPushButton("MODIFICAR")
        cancelar.setCursor(Qt.PointingHandCursor)
        modificar.setCursor(Qt.PointingHandCursor)
        botonEstilo1=("""border:2px solid black;
                        font-size:18px;
                        font-weight:bold;
                        border-radius:10px;
                        background-color:#ec5353;""")
        botonEstilo2=("""border:2px solid black;
                        font-size:18px;
                        font-weight:bold;
                        border-radius:10px;
                        background-color:#5CE65C;""")
        layoutCancelar=QVBoxLayout()
        layoutModificar=QVBoxLayout()
        cancelar.setStyleSheet(botonEstilo1)
        modificar.setStyleSheet(botonEstilo2)
        layoutCancelar.addStretch(100)
        layoutCancelar.addWidget(cancelar,alignment=Qt.AlignCenter,stretch=0)      
        layoutImagen.addLayout(layoutCancelar)            
        layoutImagen.addWidget(imagen,alignment=Qt.AlignCenter,stretch=100)
        layoutModificar.addStretch(100)
        layoutModificar.addWidget(modificar,alignment=Qt.AlignCenter,stretch=0)
        layoutImagen.addLayout(layoutModificar)  
        
        layoutDatos.addLayout(layoutImagen)
        
        layoutTabla=QVBoxLayout()
        campoTabla.setLayout(layoutTabla)
        
        self.tabla=QTableWidget()
        
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
        self.tabla.verticalHeader().setDefaultSectionSize(130)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setSelectionMode(QTableWidget.NoSelection) 
        self.tabla.setFocusPolicy(Qt.NoFocus)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers) 
        layoutTabla.addWidget(self.tabla)
        #layoutCampoModificar.addWidget(campoModificar)
        layoutCampoModificar.addWidget(campoTabla)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().setDefaultSectionSize(150)
        self.layoutPrincipal.addLayout(layoutCampoModificar)
        
    
    
    def cargarDatos(self):
        conn = sqlite3.connect(DB_PATH) 
        consulta = """SELECT aliasEmp, contEmp, ciEmp, nomEmp, 
             apellPatEmp, apellMatEmp, numCelEmp,
             direccionEmp, correoElEmp, nomCarg, imgEmp 
             FROM Empleado E, Cargo C 
             WHERE E.idCargo=C.idCargo AND disponibleEmp=1 
             ORDER BY nomEmp ASC"""
        c = conn.cursor()
        resultado = c.execute(consulta)
        columnas = [desc[0] for desc in c.description]
        mapeo_nombres = {
            'aliasEmp': 'Usuario',
            'contEmp': 'Contraseña',
            'ciEmp': 'CI',
            'nomEmp': 'Nombre',
            'apellPatEmp': 'Ap. Paterno',
            'apellMatEmp': 'Ap. Materno',
            'numCelEmp': 'Teléfono',
            'direccionEmp': 'Dirección',
            'correoElEmp': 'Correo',
            'nomCarg': 'Cargo',
            'imgEmp': 'Foto'
        }
        columnasNuevas = [mapeo_nombres[colum] for colum in columnas]
        columnasNuevas.append("Accion")
        self.tabla.setColumnCount(len(columnasNuevas))
        self.tabla.setHorizontalHeaderLabels(columnasNuevas)
        self.tabla.setRowCount(0)
        anchos_columnas = {
            'Usuario': 180,
            'Contraseña': 180,
            'CI': 80,
            'Nombre': 200,
            'Ap. Paterno': 180,
            'Ap. Materno': 180,
            'Teléfono': 100,
            'Dirección': 210,
            'Correo': 190,
            'Cargo': 100,
            'Foto': 150,
            'Accion': 60
        }
        for i, col_name in enumerate(columnasNuevas):
            self.tabla.setColumnWidth(i, anchos_columnas.get(col_name, 100)) 
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        registros = resultado.fetchall()
        for f, registro in enumerate(registros):
            self.tabla.insertRow(f)
            for c, campo in enumerate(registro):
                if c == len(registro)-1:
                    if campo:
                        img = QLabel()
                        pixmap = QPixmap()
                        pixmap.loadFromData(campo)
                        img.setPixmap(pixmap)
                        img.setAlignment(Qt.AlignCenter)
                        img.setContentsMargins(5, 5, 5, 5) 
                        img.setStyleSheet("margin: 0px; padding: 0px; border: none;")  
                        img.setScaledContents(True) 
                        img.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
                        self.tabla.setCellWidget(f, c, img)
                        
                    else:
                        item = QTableWidgetItem("Sin imagen")
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tabla.setItem(f, c, item)
                    boton=QPushButton()
                    boton.setStyleSheet("""background-color: #f8f9fa;""")
                    boton.setCursor(Qt.PointingHandCursor)
                    boton.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\modificarEmpleado.jpg"))
                    boton.setIconSize(QSize(50,50))
                    boton.clicked.connect(lambda checked, fila=f: self.pantallaModificar(fila))
                    self.tabla.setCellWidget(f,c+1,boton)
                else:
                    valor = str(campo) if campo is not None else ""
                    item = QTableWidgetItem(valor)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setToolTip(valor) 
                    self.tabla.setItem(f, c, item)
        
        conn.close()
    

    def pantallaModificar(self, fila):
        if not (0 <= fila < self.tabla.rowCount()):
            QMessageBox.warning(self, "Error", "Fila seleccionada no válida")
            return
        try:
            datos = []
            for c in range(self.tabla.columnCount()-1):
                if c == self.tabla.columnCount()-2: 
                    widget = self.tabla.cellWidget(fila, c)
                    if isinstance(widget, QLabel) and widget.pixmap():
                        pixmap = widget.pixmap()
                        byte_array = QByteArray()
                        buffer = QBuffer(byte_array)
                        buffer.open(QIODevice.WriteOnly)
                        pixmap.save(buffer, "PNG")
                        datos.append(byte_array)
                    else:
                        datos.append(None)
                else:
                    item = self.tabla.item(fila, c)
                    datos.append(item.text() if item else "")
            dialog = Pop_up_ModificacionEmpleado(datos,self)
            if dialog.exec_() == QDialog.Accepted:
                self.filtrarDatos(self.campoBusqueda.text())
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al modificar: {str(e)}")
        
        
         
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    pagina = ModificacionEmpleados()
    pagina.show()
    sys.exit(app.exec_())