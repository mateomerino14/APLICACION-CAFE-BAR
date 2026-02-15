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

class Pop_up_ModificacionEmpleado(QDialog):
   def __init__(self,datos,parent=None):
        super().__init__()
        self.setWindowTitle("MODIFICACION DE EMPLEADO")
        self.setFixedSize(500,840)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f0f5ff, stop: 1 #d9e6ff);
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
        self.crearPantallaModificacion(datos)
        
        
   def crearPantallaModificacion(self,datos):
       campoEstilo = """
           QLineEdit, QComboBox {
               background-color: white;
               border: 2px solid #dce4ec;
               border-radius: 8px;
               padding: 8px;
               font-size: 14px;
               selection-background-color: #3498db;
           }
           QLineEdit:focus, QComboBox:focus {
               border: 2px solid #3498db;
               background-color: #f7f9fc;
           }
           QComboBox::drop-down {
               border: none;
               width: 20px;
           }
           QComboBox::down-arrow {
               image: none;
               border-left: 5px solid transparent;
               border-right: 5px solid transparent;
               border-top: 5px solid #2c3e50;
               width: 0px;
               height: 0px;
           }
       """     
       editEstilo = """
           QLabel {
               font-size: 14px;
               font-weight: bold;
               color: #2c3e50;
               padding: 3px;
           }
       """
       campoEscribirEstilo = """
           QLineEdit {
               border: 2px solid #dce4ec;
               border-radius: 8px;
               padding: 8px;
               font-size: 14px;
               background-color: white;
           }
           QLineEdit:focus {
               border: 2px solid #3498db;
               background-color: #f7f9fc;
           }
       """
       layoutDatos = QVBoxLayout(self)
       titulo = QLabel("DATOS DE EMPLEADO")
       titulo.setStyleSheet("""
           QLabel {
               font-size: 22px;
               color: #2980b9;
               font-weight: bold;
               margin-bottom: 20px;
               padding: 10px;
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #e8f4ff, stop: 1 #c5e1ff);
               border-radius: 10px;
               border: 1px solid #a0c5e8;
           }
       """)
       layoutDatos.addWidget(titulo, alignment=Qt.AlignCenter)
       layoutDatos.setSpacing(10)
       layoutDatos.setContentsMargins(40,40,40,40)
       nombre = QLabel("NOMBRE")
       apellido = QLabel("APELLIDO PATERNO")
       apellido2 = QLabel("APELLIDO MATERNO")
       ci = QLabel("CI")
       numCelular = QLabel("NÚMERO DE CELULAR")
       idCargo = QLabel("CARGO")
       direccion = QLabel("DIRECCIÓN")
       correoElectronico = QLabel("CORREO ELECTRÓNICO")
       self.campoNombre = QLineEdit()
       letras_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+")
       self.campoNombre.setValidator(QRegExpValidator(letras_regex))
       self.campoNombre.setText(datos[3])
       self.campoApellido = QLineEdit()
       self.campoApellido.setValidator(QRegExpValidator(letras_regex))
       self.campoApellido.setText(datos[4])
       self.campoApellido2 = QLineEdit()
       self.campoApellido2.setValidator(QRegExpValidator(letras_regex))
       self.campoApellido2.setText(datos[5])
       self.campoCi = QLineEdit()
       self.campoCi.setValidator(QIntValidator())
       self.campoCi.setMaxLength(7)
       self.campoCi.setText(datos[2])
       self.campoNumeroCelular = QLineEdit()
       self.campoNumeroCelular.setMaxLength(8)
       self.campoNumeroCelular.setValidator(QIntValidator())
       self.campoNumeroCelular.setText(datos[6])
       self.campoCargo = QComboBox()
       self.cargarCargos(self.campoCargo)
       self.campoCargo.setCurrentText(datos[9])
       self.campoDireccion = QLineEdit()
       self.campoDireccion.setText(datos[7])
       self.campoCorreo = QLineEdit()
       regex_correo = QRegExpValidator(QRegExp(r"^[a-zA-Z][a-zA-Z0-9._-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"))
       self.campoCorreo.setValidator(regex_correo)
       self.campoCorreo.setText(datos[8])
       nombre.setStyleSheet(editEstilo)
       apellido.setStyleSheet(editEstilo)
       apellido2.setStyleSheet(editEstilo)
       ci.setStyleSheet(editEstilo)
       numCelular.setStyleSheet(editEstilo)
       idCargo.setStyleSheet(editEstilo)
       direccion.setStyleSheet(editEstilo)
       correoElectronico.setStyleSheet(editEstilo)
       self.campoNombre.setStyleSheet(campoEstilo)
       self.campoApellido.setStyleSheet(campoEstilo)
       self.campoApellido2.setStyleSheet(campoEstilo)
       self.campoCi.setStyleSheet(campoEstilo)
       self.campoNumeroCelular.setStyleSheet(campoEstilo)
       self.campoCargo.setStyleSheet(campoEstilo)
       self.campoDireccion.setStyleSheet(campoEstilo)
       self.campoCorreo.setStyleSheet(campoEstilo)
       layout1 = QHBoxLayout()
       layout2 = QHBoxLayout()
       layout3 = QHBoxLayout()
       layout4 = QHBoxLayout()
       layout5 = QHBoxLayout()
       layout6 = QHBoxLayout()
       layout7 = QHBoxLayout()
       layout8 = QHBoxLayout()
       layout1.addWidget(nombre)
       layout1.addWidget(self.campoNombre)
       layout2.addWidget(apellido)
       layout2.addWidget(self.campoApellido)
       layout3.addWidget(apellido2)
       layout3.addWidget(self.campoApellido2)
       layout4.addWidget(ci)
       layout4.addWidget(self.campoCi)
       layout5.addWidget(numCelular)
       layout5.addWidget(self.campoNumeroCelular)
       layout6.addWidget(idCargo)
       layout6.addWidget(self.campoCargo)
       layout7.addWidget(direccion)
       layout7.addWidget(self.campoDireccion)
       layout8.addWidget(correoElectronico)
       layout8.addWidget(self.campoCorreo)
       layoutDatos.addLayout(layout1)
       layoutDatos.addLayout(layout2)
       layoutDatos.addLayout(layout3)
       layoutDatos.addLayout(layout4)
       layoutDatos.addLayout(layout5)
       layoutDatos.addLayout(layout6)
       layoutDatos.addLayout(layout7)
       layoutDatos.addLayout(layout8)
       imagen = QLabel()
       imagen.setFixedSize(210,210)
       imagen.setStyleSheet("""
           QLabel {
               border: 2px dashed #95a5a6;
               border-radius: 8px;
               background-color: #f8f9fa;
           }
       """)
       pixmap = QPixmap()
       pixmap.loadFromData(datos[10].data())
       imagen.setPixmap(pixmap.scaled(210, 210,  Qt.IgnoreAspectRatio,  Qt.SmoothTransformation)) 
       layoutImagen = QHBoxLayout()
       layoutBotones = QHBoxLayout()
       cancelar = QPushButton("CANCELAR")
       modificar = QPushButton("MODIFICAR")
       cancelar.setCursor(Qt.PointingHandCursor)
       cancelar.clicked.connect(self.cerrarVentanaCancelar)
       modificar.setCursor(Qt.PointingHandCursor)
       modificar.clicked.connect(lambda:self.modificarRegistro(datos))
       botonEstilo1 = """
           QPushButton {
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #e74c3c, stop: 1 #c0392b);
               color: white;
               border: none;
               border-radius: 8px;
               padding: 12px 25px;
               font-weight: bold;
               font-size: 15px;
               min-width: 120px;
           }
           QPushButton:hover {
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #ff6b6b, stop: 1 #ee5253);
           }
           QPushButton:pressed {
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #c0392b, stop: 1 #e74c3c);
           }
       """

       botonEstilo2 = """
           QPushButton {
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #2ecc71, stop: 1 #27ae60);
               color: white;
               border: none;
               border-radius: 8px;
               padding: 12px 25px;
               font-weight: bold;
               font-size: 15px;
               min-width: 120px;
           }
           QPushButton:hover {
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #32ff7e, stop: 1 #3ae374);
           }
           QPushButton:pressed {
               background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                   stop: 0 #27ae60, stop: 1 #2ecc71);
           }
       """
       
       layoutCancelar = QVBoxLayout()
       layoutModificar = QVBoxLayout()
       cancelar.setStyleSheet(botonEstilo1)
       modificar.setStyleSheet(botonEstilo2)
       layoutCancelar.addStretch(100)
       layoutCancelar.addWidget(cancelar, alignment=Qt.AlignCenter, stretch=20) 
       layoutBotones.addStretch(1)
       layoutBotones.addLayout(layoutCancelar)       
       layoutImagen.addWidget(imagen, alignment=Qt.AlignCenter, stretch=80)
       layoutModificar.addStretch(100)
       layoutModificar.addWidget(modificar, alignment=Qt.AlignCenter, stretch=20)
       layoutBotones.addLayout(layoutModificar)  
       layoutBotones.addStretch(1)
       layoutDatos.addLayout(layoutImagen)   
       layoutBotones.setSpacing(20)
       layoutDatos.addLayout(layoutBotones)
   
       
   
   def modificarRegistro(self,datos):
       conn=sqlite3.connect(DB_PATH)
       c=conn.cursor()
       buscarIndice="""SELECT idCargo FROM Cargo WHERE nomCarg=?"""
       resultados=c.execute(buscarIndice,(datos[9],))
       indice=resultados.fetchone()[0]
       consulta="""UPDATE Empleado
                   SET nomEmp=?,
                       apellPatEmp=?,
                       apellMatEmp=?,
                       ciEmp=?,
                       numCelEmp=?,
                       direccionEmp=?,
                       correoElEmp=?,
                       idCargo=?
                   WHERE aliasEmp=?"""
       dupla=(self.campoNombre.text(),self.campoApellido.text(),self.campoApellido2.text(),self.campoCi.text(),self.campoNumeroCelular.text(),self.campoDireccion.text(),self.campoCorreo.text(),indice,datos[0])
       if self.campoNombre.text()=="" or self.campoApellido.text()=="" or self.campoApellido2.text()=="" or self.campoCi.text()=="" or self.campoNumeroCelular.text()=="":
           QMessageBox.warning(self,"Alerta","Rellene los campos necesarios")
           return 
       c.execute(consulta,dupla)
       conn.commit()
       conn.close()
       QMessageBox.information(self,"Confirmación", "¡Se modifico con exito!" )
       self.cerrarVentana()
      
        
   def cerrarVentanaCancelar(self):
       self.reject()
       self.close()
       
   def cerrarVentana(self):
       self.accept() 
       self.close()
       
   def cargarCargos(self,campoCargos):
        conn=sqlite3.connect(DB_PATH)
        c=conn.cursor()
        consulta=("""SELECT * FROM Cargo""")
        c.execute(consulta)
        resultados=c.fetchall()
        for _,cargo in resultados:
            campoCargos.addItem(cargo)
        campoCargos.setCurrentIndex(-1)
        conn.close()