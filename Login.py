from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import sqlite3
import os
from SeguridadUtils import verificar_password
from Rutas import get_db_path, get_resource_path

DB_PATH = get_db_path()

class Login(QMainWindow):
    def __init__(self):
        super().__init__()
        self.set_up()
    
    def set_up(self):
        self.setWindowTitle("LOGIN - Sistema Cafebar")
        self.showMaximized()
        self.setFixedSize(QApplication.primaryScreen().size())
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #aed6f1;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 10px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
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
        
        
        contenedorPrincipal = QWidget()
        self.setCentralWidget(contenedorPrincipal)
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        contenedorPrincipal.setLayout(layout)
        layoutListaEmpleados=QHBoxLayout()
        botonIzquierda=QPushButton("<<")
        botonIzquierda.setStyleSheet("""font-size:25px;""")
        botonIzquierda.setFixedSize(50,40)
        layoutListaEmpleados.addWidget(botonIzquierda)
        self.layoutEmpleado=QHBoxLayout()
        self.cargarEmpleados(self.layoutEmpleado,layoutListaEmpleados)
        botonDerecha=QPushButton(">>")
        botonIzquierda.clicked.connect(lambda _: self.moverIzquierda(self.layoutEmpleado))
        botonDerecha.clicked.connect(lambda _: self.moverDerecha(self.layoutEmpleado))
        botonDerecha.setStyleSheet(botonIzquierda.styleSheet())
        botonDerecha.setFixedSize(50,40)
        layoutListaEmpleados.addWidget(botonDerecha)
        layout.addLayout(layoutListaEmpleados)
        titulo = QLabel("INICIO DE SESIÓN")
        titulo.setStyleSheet("""
            font-family: 'Verdana';
            font-size: 35px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 30px;
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        logo = QLabel()
        logo_path = get_resource_path(os.path.join('Imagenes','Login-Logo.jpg'))
        logo.setFixedSize(150, 150) 
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                mask = QBitmap(150, 150)
                mask.fill(Qt.color0)
                painter = QPainter(mask)
                painter.setBrush(Qt.color1)
                painter.drawEllipse(0, 0, 150, 150)
                painter.end()
                pixmap.setMask(mask)
                logo.setPixmap(pixmap)
            else:
                print(f"Error: No se pudo cargar la imagen {logo_path}")
                logo.setText("LOGO\nNO ENCONTRADO")
                logo.setStyleSheet("""
                    background-color: #ccc; 
                    color: #666; 
                    border: 1px dashed #999;
                    border-radius: 75px;
                """)
        else:
            print(f"Error: Archivo no encontrado {logo_path}")
            logo.setText("LOGO\nNO ENCONTRADO")
            logo.setStyleSheet("""
                background-color: #ccc; 
                color: #666; 
                border: 1px dashed #999;
                border-radius: 75px;
            """)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo,alignment=Qt.AlignCenter)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        usuario_layout = QVBoxLayout()
        lbl_usuario = QLabel("USUARIO")
        lbl_usuario.setStyleSheet("""
            font-family: 'Verdana';
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
        """)
        self.text_usuario = QLineEdit()
        self.text_usuario.setPlaceholderText("Ingrese su nombre de usuario")
        self.text_usuario.setFixedWidth(400)
        usuario_layout.addWidget(lbl_usuario,alignment=Qt.AlignCenter)
        usuario_layout.addWidget(self.text_usuario,alignment=Qt.AlignCenter)
        form_layout.addLayout(usuario_layout)
        pass_layout = QVBoxLayout()
        lbl_pass = QLabel("CONTRASEÑA")
        lbl_pass.setStyleSheet("""
            font-family: 'Verdana';
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
        """)
        pass_input_layout = QHBoxLayout()
        self.text_pass = QLineEdit()
        self.text_pass.setEchoMode(QLineEdit.Password)
        self.text_pass.setPlaceholderText("Ingrese su contraseña")
        self.text_pass.setFixedWidth(400)
        self.btn_visible = QPushButton()
        self.btn_visible.setCheckable(True)
        self.btn_visible.setCursor(Qt.PointingHandCursor)
        ojo_abierto_path =get_resource_path(os.path.join('Imagenes','ojoAbierto.png'))
        ojo_cerrado_path = get_resource_path(os.path.join('Imagenes','ojoCerrado.png'))
        if os.path.exists(ojo_abierto_path):
            self.btn_visible.setIcon(QIcon(ojo_abierto_path))
        else:
            print(f"Error: No se encontró el icono {ojo_abierto_path}")
            self.btn_visible.setText("👁")
        
        self.btn_visible.setIconSize(QSize(24, 24))
        self.btn_visible.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
        """)
        self.btn_visible.clicked.connect(lambda: self.mostrarContrasena(self.text_pass, self.btn_visible, ojo_abierto_path, ojo_cerrado_path))
        pass_input_layout.addStretch(71)
        pass_input_layout.addWidget(self.text_pass,alignment=Qt.AlignCenter,stretch=100)
        pass_input_layout.addWidget(self.btn_visible,alignment=Qt.AlignLeft,stretch=0)
        pass_input_layout.addStretch(50)
        pass_layout.addWidget(lbl_pass,alignment=Qt.AlignCenter)
        pass_layout.addLayout(pass_input_layout)
        form_layout.addLayout(pass_layout)
        layout.addLayout(form_layout)
        layout.addStretch(1)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(80)
        btn_ingresar = QPushButton("INGRESAR")
        btn_ingresar.setFixedSize(200, 50)
        btn_ingresar.setStyleSheet("""
            font-family: 'Verdana';
            font-size: 18px;
            font-weight: bold;
        """)
        btn_ingresar.clicked.connect(lambda: self.verificarUsuario(self.text_usuario.text().strip(), self.text_pass.text().strip()))
        btn_directorio = QPushButton("MODO DIRECTORIO")
        btn_directorio.setFixedSize(250, 50)
        btn_directorio.setStyleSheet("""
            font-family: 'Verdana';
            font-size: 18px;
            font-weight: bold;
            background-color: #e67e22;
        """)
        btn_directorio.clicked.connect(lambda: self.rellenarCampo(self.text_usuario))
        btn_layout.addStretch(1)
        btn_layout.addWidget(btn_ingresar)
        btn_layout.addWidget(btn_directorio)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)
        layout.addStretch()
        footer = QLabel("© 2026 Sistema Cafebar - Todos los derechos reservados")
        footer.setStyleSheet("""
            font-family: 'Verdana';
            font-size: 12px;
            color: #7f8c8d;
        """)
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer,stretch=3)
        QShortcut(QKeySequence("Return"),self,lambda *_: self.verificarUsuario(self.text_usuario.text().strip(), self.text_pass.text().strip()))
        
    
    def rellenarCampo(self, campo):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""SELECT * FROM Directorio""")
            resultado = c.fetchone()
            if resultado:
                campo.setText(resultado[1])
            else:
                QMessageBox.warning(self, "Advertencia", "No se encontraron datos de directorio")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al acceder a la base de datos: {str(e)}")
        finally:
            if conn:
                conn.close()
        

    def verificarUsuario(self, nombre, contrasena):
        if not nombre or not contrasena:
            QMessageBox.information(self, "Aviso", "Rellene los campos solicitados")
            return 
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            esDirectorio = False
            if nombre == "DIRECTORIO":
                c.execute("""SELECT * FROM Directorio""")
                resultado = c.fetchone()
                if resultado and verificar_password(contrasena, resultado[2]):
                    self.iniciarPaginaPrincipal("DIRECTORIO")
                else:
                    QMessageBox.information(self, "Error", "Credenciales Incorrectas")
                esDirectorio = True
            
            if not esDirectorio:
                consulta = """SELECT contEmp FROM Empleado WHERE aliasEmp = ? AND disponibleEmp=1"""
                c.execute(consulta, (nombre,))
                resultado = c.fetchone()
                if resultado and verificar_password(contrasena, resultado[0]):
                    self.iniciarPaginaPrincipal(nombre)
                else:
                    QMessageBox.information(self, "Error", "Credenciales Incorrectas")  
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al acceder a la base de datos: {str(e)}")
        finally:
            if conn:
                conn.close()
        

    def iniciarPaginaPrincipal(self,usuario):
        from AdministradorPaginas import AdministradorPaginas
        self.pagina=AdministradorPaginas(usuario)
        self.pagina.show()
        self.close()
    
    def mostrarContrasena(self, textPass, botonVisible, ojo_abierto_path, ojo_cerrado_path):
        if botonVisible.isChecked():
            textPass.setEchoMode(QLineEdit.Normal)
            if os.path.exists(ojo_cerrado_path):
                botonVisible.setIcon(QIcon(ojo_cerrado_path))
            else:
                botonVisible.setText("👁")
        else:
            textPass.setEchoMode(QLineEdit.Password)
            if os.path.exists(ojo_abierto_path):
                botonVisible.setIcon(QIcon(ojo_abierto_path))
            else:
                botonVisible.setText("👁")
    
    
    def cargarEmpleados(self, layoutEmpleados, layout):
        self._clear_layout(layoutEmpleados)
        self.contenedor = QFrame()
        self.contenedor.setStyleSheet("""
            background-color:#fafbfd;
            border-radius:8px;
        """)
        self.contenedor.setLayout(layoutEmpleados)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT aliasEmp, imgEmp FROM Empleado WHERE disponibleEmp=1")
        self.resultados = c.fetchall()
        conn.close()
        self.actual = 0
        self.page_size = 7
        self.mostrarPagina(layoutEmpleados, 0)
        layout.addWidget(self.contenedor)

    def mostrarPagina(self, layoutEmpleados, inicio):
        self._clear_layout(layoutEmpleados)
        fin = inicio + self.page_size
        subset = self.resultados[inicio:fin]
        for alias, imagen in subset:
            empleado = QPushButton()
            empleado.setStyleSheet("background-color:#ccccce; border-radius:8px;")
            empleado.clicked.connect(lambda _, a=alias: self.text_usuario.setText(a))
            empleado.setFixedSize(120, 120)
            pixmap = QPixmap()
            pixmap.loadFromData(imagen)
            empleado.setIcon(QIcon(pixmap))
            empleado.setIconSize(QSize(90, 90))
            layoutEmpleados.addWidget(empleado)
        for _ in range(len(subset), self.page_size):
            vacio = QWidget()
            vacio.setFixedSize(120, 120)
            layoutEmpleados.addWidget(vacio)
        self.actual = inicio


    def moverIzquierda(self, layoutEmpleados):
        if self.actual==0:
            return 
        nuevo_inicio = max(0, self.actual-self.page_size)
        self.mostrarPagina(layoutEmpleados,nuevo_inicio)
    
    
    def moverDerecha(self, layoutEmpleados):
        if self.actual+self.page_size>=len(self.resultados):
            return  
        nuevo_inicio = self.actual+self.page_size
        self.mostrarPagina(layoutEmpleados, nuevo_inicio)
        
        
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = Login()
    pagina.show()
    sys.exit(app.exec_())