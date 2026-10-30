import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from Rutas import get_db_path, get_images_dir


DB_PATH = get_db_path()

DIRECCION_IMAGENES = get_images_dir()

class ModificacionSeccion(QWidget):
    def __init__(self,nombSeccion,descSec):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #e6f2ff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel#titulo_principal {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                padding: 20px 0;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                min-width: 120px;
                transition: all 0.3s ease;
            }
            
            QPushButton:hover {
                transform: translateY(-1px);
            }
            
            QPushButton#btn_cerrar {
                background-color: #e74c3c;
                color: white;
                border: none;
            }
            
            QPushButton#btn_cerrar:hover {
                background-color: #c0392b;
            }
            
            QPushButton#btn_modificar {
                background-color: #2ecc71;
                color: white;
                border: none;
            }
            
            QPushButton#btn_modificar:hover {
                background-color: #27ae60;
            }
            
            QPushButton#btn_cancelar {
                background-color: #95a5a6;
                color: white;
                border: none;
            }
            
            QPushButton#btn_cancelar:hover {
                background-color: #7f8c8d;
            }
            
            QLineEdit {
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 10px;
                font-size: 15px;
                min-height: 36px;
            }
            
            QLineEdit:focus {
                border: 2px solid #5d9cec;
            }
            
            QLabel {
                color: #34495e;
                font-size: 15px;
                font-weight: 500;
                margin-bottom: 5px;
            }

            QWidget#menu_superior {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #5d9cec, stop:1 #4a89dc);
                border-bottom: 2px solid #3a79d4;
            }
            
            QPushButton#menu_btn {
                padding: 15px 5px;
                color: white;
                font-weight: bold;
                border: none;
                border-right: 1px solid rgba(255,255,255,0.2);
            }
            
            QPushButton#menu_btn:hover {
                background-color: rgba(255,255,255,0.1);
            }
            

            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #e9ecef;
                width: 10px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background: #adb5bd;
                min-height: 20px;
                border-radius: 5px;
            }

            QLabel#mesa_numero {
                font-weight: 600;
                color: #2c3e50;
                background-color: #f8f9fa;
                border-radius: 4px;
                padding: 2px;
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
        self.set_up(nombSeccion,descSec)
        
        
    def set_up(self,nombSeccion,descSec):
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20,20,20,20)
        self.anadirAreaRegistro(nombSeccion,descSec)
        self.showMaximized()
    
    def anadirAreaRegistro(self,nombSeccion,descSec):
        self.nombSeccion=nombSeccion
        self.descSec=descSec
        conn=sqlite3.connect(DB_PATH)
        c=conn.cursor()
        consulta="""SELECT * FROM Seccion S,Mesa M WHERE S.idSeccion=M.idSeccion AND nombSeccion=? AND existe=TRUE"""
        c.execute(consulta,(nombSeccion,))
        resultados=c.fetchall()
        conn.close()
        contenedorSeccion=QWidget()
        layoutSeccion=QHBoxLayout()
        layoutAnadirSeccion=QVBoxLayout()
        self.etiqueta1=QLabel("Nombre de Seccion")
        self.campo1=QLineEdit(nombSeccion)
        self.campo1.setMaxLength(17)
        letras_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+")
        self.campo1.setValidator(QRegExpValidator(letras_regex))
        self.etiqueta2=QLabel("Descripcion")
        self.campo2=QLineEdit(descSec)
        self.campo2.setMaxLength(40)
        descripcion_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ0-9.,\\-\\s]*")
        self.campo2.setValidator(QRegExpValidator(descripcion_regex))
        self.etiqueta3=QLabel("Numero de Mesas")
        self.cantidadMesas=str(len(resultados))
        self.campo3=QLineEdit(self.cantidadMesas)
        cantidad_regex = QRegExp("[0-9]*")
        self.campo3.setValidator(QRegExpValidator(cantidad_regex))
        self.campo3.setMaxLength(4)
        layoutAnadirSeccion.addWidget(self.etiqueta1)
        layoutAnadirSeccion.addWidget(self.campo1)
        layoutAnadirSeccion.addWidget(self.etiqueta2)
        layoutAnadirSeccion.addWidget(self.campo2)
        layoutAnadirSeccion.addWidget(self.etiqueta3)
        layoutAnadirSeccion.addWidget(self.campo3)
        botonModificar=QPushButton("MODIFICAR")
        botonModificar.setStyleSheet("""background-color:green;
                                        color:white;""")
        botonModificar.clicked.connect(self.subirInformacion)
        botonCancelar=QPushButton("CANCELAR")
        botonCancelar.setStyleSheet("""background-color:red;
                                    color:white;""")
        botonCancelar.clicked.connect(self.reestablecerDatos)
        botonVolver=QPushButton("VOLVER")
        botonVolver.setStyleSheet("""background-color:gray;
                                    color:white;""")
        botonVolver.clicked.connect(self.cerrar)
        layoutAnadirSeccion.addWidget(botonModificar)
        layoutAnadirSeccion.addWidget(botonCancelar)
        layoutAnadirSeccion.addWidget(botonVolver)
        layoutAnadirSeccion.addStretch()
        layoutSeccion.addLayout(layoutAnadirSeccion,stretch=2)
        contenedorMesas=QWidget()
        contenedorMesas.setStyleSheet("""background-color:white;""")
        self.layoutMesas=QVBoxLayout()
        self.layoutMesas.setSpacing(5)
        contenedorMesas.setLayout(self.layoutMesas)
        scroll=QScrollArea()
        scroll.setWidget(contenedorMesas)
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layoutSeccion.addWidget(scroll,stretch=10)
        contenedorSeccion.setLayout(layoutSeccion)
        self.layoutPrincipal.addWidget(contenedorSeccion,stretch=8)
        self.generarMesas()
        return
   
    def cerrar(self):
         self.deleteLater()
   
    def subirInformacion(self):
        nuevoNombSeccion=self.campo1.text().strip()
        nuevaDescSeccion=self.campo2.text().strip()
        nuevaCantidadTexto=self.campo3.text().strip()
        if nuevoNombSeccion=="" or nuevaCantidadTexto=="":
           QMessageBox.information(self,"Advertencia","¡Los campos requeridos no pueden estar vacios!")
           return
        try:
            nuevaCantidad=int(nuevaCantidadTexto)
        except ValueError:
            QMessageBox.information(self,"Advertencia","La cantidad de mesas debe ser un numero valido.")
            return
        if nuevaCantidad<0:
            QMessageBox.information(self,"Advertencia","La cantidad debe ser un numero mayor o igual a 0")
            return
        conn=sqlite3.connect(DB_PATH)
        c=conn.cursor()
        try:
            consulta="""SELECT * FROM Seccion WHERE nombSeccion=?"""
            c.execute(consulta,(nuevoNombSeccion,))
            resultados=c.fetchall()
            if resultados:
                if nuevoNombSeccion!=self.nombSeccion:
                    QMessageBox.information(self,"Advertencia","¡El nombre pertenece a una seccion ya registrada!")
                    return

            consulta="""SELECT idSeccion FROM Seccion WHERE nombSeccion=?"""
            c.execute(consulta,(self.nombSeccion,))
            resultados=c.fetchone()
            if resultados is None:
                QMessageBox.critical(self,"Error","No se encontro la seccion original en la base de datos.")
                return
            idSeccion=int(resultados[0])
            consulta="""SELECT COUNT(*) FROM Mesa WHERE idSeccion=?"""
            c.execute(consulta,(idSeccion,))
            resultados=c.fetchone()
            cantidadRegistrada=resultados[0]
            consulta="""SELECT COUNT(*) FROM Mesa WHERE idSeccion=? AND existe=TRUE"""
            c.execute(consulta,(idSeccion,))
            resultados=c.fetchone()
            cantidadHabilitada=resultados[0]
            if cantidadHabilitada>=nuevaCantidad:
                diferencia=cantidadHabilitada-nuevaCantidad
                for i in range(diferencia):
                    idMesa=cantidadHabilitada-i
                    consulta="""UPDATE Mesa SET existe=FALSE WHERE idSeccion=? AND idMesa=?"""
                    c.execute(consulta,(idSeccion,idMesa))
            else:
                diferencia=cantidadRegistrada-cantidadHabilitada
                resto=nuevaCantidad-cantidadHabilitada
                if diferencia>=resto:
                    for i in range(resto):
                       idMesa=cantidadHabilitada+(i+1)
                       consulta="""UPDATE Mesa SET existe=TRUE WHERE idSeccion=? AND idMesa=?"""
                       c.execute(consulta,(idSeccion,idMesa))
                else:
                    for i in range(diferencia):
                        idMesa=cantidadHabilitada+(i+1)
                        consulta="""UPDATE Mesa SET existe=TRUE WHERE idSeccion=? AND idMesa=?"""
                        c.execute(consulta,(idSeccion,idMesa))
                    nuevaDiferencia=nuevaCantidad-cantidadRegistrada
                    if nuevaDiferencia>0:
                        for i in range(nuevaDiferencia):
                         consulta="""INSERT INTO Mesa(idMesa,idSeccion) VALUES(NULL,?)"""
                         c.execute(consulta,(idSeccion,))
            consulta="""UPDATE Seccion SET nombSeccion=?,descripcion=? WHERE idSeccion=?"""
            c.execute(consulta,(nuevoNombSeccion,nuevaDescSeccion,idSeccion))
            conn.commit()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self,"Error",f"No se pudo modificar la seccion: {str(e)}")
            return
        finally:
            conn.close()
        self.nombSeccion=nuevoNombSeccion
        self.descSec=nuevaDescSeccion
        self.cantidadMesas=str(nuevaCantidad)
        self.generarMesas()
        QMessageBox.information(self,"Confirmacion","¡Se modifico con exito el registro!")
        
        
    def reestablecerDatos(self):
        self.limpiarMesas(self.layoutMesas)
        self.campo1.setText(self.nombSeccion)
        self.campo2.setText(self.descSec)
        self.campo3.setText(self.cantidadMesas)
        self.generarMesas()
        
    def generarMesas(self):
        self.limpiarMesas(self.layoutMesas)
        layoutFilaMesas=QHBoxLayout()
        layoutFilaMesas.setSpacing(10)
        if self.cantidadMesas=="":
            cantidad=0
        else:
            try:
                cantidad=int(self.cantidadMesas)
            except ValueError:
                cantidad=0
            if cantidad<0:
                QMessageBox.information(self,"Advertencia","La cantidad debe ser un numero mayor o igual a 0")
                return
        for i in range(cantidad):
            if i%10==0 and i != 0:
                self.layoutMesas.addLayout(layoutFilaMesas)
                layoutFilaMesas=QHBoxLayout()
                layoutFilaMesas.setSpacing(10)
            contenedor_mesa=QWidget()
            layoutMesa=QVBoxLayout()
            layoutMesa.setContentsMargins(5, 5, 5, 5)
            contenedor_mesa.setLayout(layoutMesa)
            contenedor_mesa.setStyleSheet("""background-color:#E0D6D1;
                                             border:3px solid #463730;""")
            imagen=QLabel()
            pixmap=QPixmap(f"{DIRECCION_IMAGENES}\\mesa.png")
            pixmap = pixmap.scaled(90,90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            imagen.setPixmap(pixmap)
            imagen.setFixedSize(90, 90)
            numero=QLabel(str(i+1))
            numero.setAlignment(Qt.AlignCenter)
            numero.setFixedSize(90, 30)
            layoutMesa.addWidget(imagen,alignment=Qt.AlignCenter)
            layoutMesa.addWidget(numero,alignment=Qt.AlignCenter)
            layoutFilaMesas.addWidget(contenedor_mesa)
        limite=cantidad%10
        if limite!=0:
            limite=10-limite
            for i in range (limite):
                contenedor_mesa=QWidget()
                layoutMesa=QVBoxLayout()
                layoutMesa.setContentsMargins(5, 5, 5, 5)
                contenedor_mesa.setLayout(layoutMesa)
                imagen=QLabel()
                imagen.setFixedSize(90, 90)
                numero=QLabel()
                layoutMesa.addWidget(imagen,alignment=Qt.AlignCenter)
                layoutMesa.addWidget(numero,alignment=Qt.AlignCenter)
                layoutFilaMesas.addWidget(contenedor_mesa)
            self.layoutMesas.addLayout(layoutFilaMesas)
        else:
            self.layoutMesas.addLayout(layoutFilaMesas) 
        self.layoutMesas.addStretch(1)
    
    def limpiarMesas(self,layout):
        if layout is None:
         return
        while(layout.count()>0):
            hijo=layout.takeAt(0)
            if hijo.widget():
                hijo.widget().deleteLater()
            else:
                if hijo.layout():
                    self.limpiarMesas(hijo.layout())
                    hijo.layout().deleteLater()
                    
                


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = ModificacionSeccion("Terraza", "Seccion exterior")
    pagina.show()
    sys.exit(app.exec_())