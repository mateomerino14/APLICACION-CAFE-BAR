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

class RegistroIngredientes(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            self{background-color: #e6f2ff;
            font-family: 'Segoe UI', Arial, sans-serif;}
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
            QMessageBox QPushButton:hover { 
                background-color: #2980b9; 
            }
        """)
        self.set_up()
        
    def set_up(self):
        self.layoutDatos = QHBoxLayout()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20,20,20,20)
        self.anadirAreaRegistro()
        self.showMaximized()
        self.layoutPrincipal.addStretch(1)
    
    def anadirAreaRegistro(self):
        labelEstilo = """
            font-size: 16px;
            font-family: Verdana;
            color: #2c3e50;
            font-weight: bold;
            margin-bottom: 5px;
        """
                       
        camposEstilo = """
            background-color: white;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 0px;
            margin:0px;
            font-size: 15px;
        """
        
     
        botonesEstilo = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        widgetRegistro = QWidget()
        widgetRegistro.setStyleSheet("""
            background-color: white;
            margin-bottom: 30px;
            border-radius: 10px;
            border: 1px solid #d6d6d6;
        """)
        widgetRegistro.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        widgetRegistro.setLayout(self.layoutDatos)
        layoutCampos = QVBoxLayout()
        layoutCampos.setSpacing(15)
        layoutCampos.setContentsMargins(20, 20, 20, 20)
        layoutH1 = QHBoxLayout()
        layoutH1.setSpacing(10)
        letras_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+")
        nombre = QLabel("NOMBRE")
        nombre.setStyleSheet(labelEstilo)
        self.campo1 = QLineEdit()
        self.campo1.setStyleSheet(camposEstilo)
        self.campo1.setValidator(QRegExpValidator(letras_regex))
        unidadMedida = QLabel("UNIDAD DE MEDIDA")
        unidadMedida.setStyleSheet(labelEstilo)
        self.campo2 = QComboBox()
        self.campo2.addItems(["Kilogramos","Litros","Onzas","Gramos","Mililitros","Unidades"])
        self.campo2.setStyleSheet(camposEstilo)
        self.campo2.setCurrentIndex(-1)
        cantidad = QLabel("CANTIDAD DE STOCK")
        cantidad.setStyleSheet(labelEstilo)
        self.campo3 = QLineEdit()
        self.campo3.setPlaceholderText("0.00")
        self.campo3.setStyleSheet(camposEstilo)
        self.campo3.setValidator(QRegExpValidator(QRegExp("[0-9]+\\.?[0-9]*")))
    
        def crear_grupo_campo(label, campo):
            grupo = QVBoxLayout()
            grupo.addWidget(label, alignment=Qt.AlignLeft)
            grupo.addWidget(campo)
            return grupo
        
        layoutH1.addLayout(crear_grupo_campo(nombre, self.campo1))
        layoutH1.addLayout(crear_grupo_campo(unidadMedida, self.campo2))
        layoutH1.addLayout(crear_grupo_campo(cantidad, self.campo3))
        layoutCampos.addLayout(layoutH1)
        layoutH2 = QHBoxLayout()
        layoutH2.setSpacing(10)
        descripcion = QLabel("DESCRIPCION")
        descripcion.setStyleSheet(labelEstilo)
        self.campo4 = QTextEdit()
        self.campo4.setFixedHeight(200)
        self.campo4.setStyleSheet(camposEstilo)
        layoutH2.addLayout(crear_grupo_campo(descripcion, self.campo4))
        layoutCampos.addLayout(layoutH2)
        layoutBotones = QHBoxLayout()
        layoutBotones.setSpacing(20)
        layoutBotones.setContentsMargins(0, 20, 0, 0)
        confirmar = QPushButton("CONFIRMAR")
        confirmar.setStyleSheet(botonesEstilo)
        confirmar.setCursor(Qt.PointingHandCursor)
        confirmar.clicked.connect(self.confirmarRegistro)
        rechazar = QPushButton("CANCELAR")
        rechazar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        rechazar.setCursor(Qt.PointingHandCursor)
        rechazar.clicked.connect(self.limpiarTodo)
        layoutBotones.addWidget(confirmar)
        layoutBotones.addWidget(rechazar)
        layoutBotones.setAlignment(Qt.AlignCenter)
        layoutCampos.addLayout(layoutBotones)
        self.layoutDatos.addLayout(layoutCampos)
        self.layoutPrincipal.addWidget(widgetRegistro)
 
    def confirmarRegistro(self):
        conn=sqlite3.connect(DB_PATH)
        c=conn.cursor()
        lista=[self.campo1.text(),self.campo2.currentText(),self.campo3.text()]
        for elem in lista:
            if elem=="":
                QMessageBox.information(self,"Advertencia","Llene los campos obligatorios porfavor")
                return
        consulta="""SELECT * FROM Stock WHERE nomIng=? AND descripcion=?"""
        registros=c.execute(consulta,(self.campo1.text(),self.campo4.toPlainText()))
        resultados=registros.fetchone()
        if resultados is not None:
            QMessageBox.information(self,"Advertencia","Este ingrediente ya ha sido registrado")
            return
        consulta="""INSERT INTO Stock(nomIng,descripcion,cantidadStock,unidadMedida) VALUES (?,?,?,?)"""
        c.execute(consulta,(
            self.campo1.text(),      
            self.campo4.toPlainText(),       
            float(self.campo3.text()),     
            self.campo2.currentText()      
        ))
        QMessageBox.information(self,"Confirmacion","Se ha registrado con exito") 
        self.limpiarTodo()
        conn.commit()
        conn.close()
   
   
    def limpiarTodo(self):
        self.campo1.clear()
        self.campo2.setCurrentIndex(-1)
        self.campo3.clear()
        self.campo4.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = RegistroIngredientes()
    pagina.show()
    sys.exit(app.exec_())