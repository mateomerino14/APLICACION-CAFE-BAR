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

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

DB_PATH = get_db_path()

class Pop_up_RegistroProductos(QDialog):
    def __init__(self, datos, tabla, parent=None):
        super().__init__(parent)
        self.setWindowTitle("REGISTRO DE PRODUCTO")
        self.setFixedSize(500, 650)
        self.setStyleSheet("""
            QDialog {
                background-color: #aed6f1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
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
        layoutPrincipal = QVBoxLayout()
        self.setLayout(layoutPrincipal)
        titulo = QLabel("INGRESE LA IMAGEN DEL PRODUCTO")
        titulo.setStyleSheet("""font-size: 15px;
                            font-weight: bold;
                            color: black;""")
        layoutPrincipal.addWidget(titulo, stretch=20, alignment=Qt.AlignCenter)
        imagen = QPushButton()
        imagen.setFixedSize(300, 300)
        imagen.setStyleSheet("""border:5px dashed black;
                             padding:10px;
                             background:white;
                             border-radius:7px;""")
        default_image_path = get_resource_path("Imagenes/camara.png")
        icono = QIcon(default_image_path)
        imagen.setIconSize(QSize(287, 287))
        imagen.setIcon(icono)
        imagen.setCursor(Qt.PointingHandCursor)
        imagen.clicked.connect(lambda: self.actualizarFoto(imagen))
        layoutPrincipal.addWidget(imagen, stretch=50, alignment=Qt.AlignCenter)
        layoutPrincipal.addStretch(20)
        layoutBotones = QHBoxLayout()
        botonConfirmar = QPushButton("Confirmar")
        botonConfirmar.setStyleSheet("""color:white;
                                        background:green;
                                        font-size:16px;
                                        font-weigth:500;
                                        padding:10px;
                                        border-radius:8px;""")
        botonConfirmar.clicked.connect(lambda: self.subirInformacion(datos, tabla, imagen.icon()))
        botonCancelar = QPushButton("Cancelar")
        botonCancelar.setStyleSheet("""color:white;
                                        background:red;
                                        font-size:16px;
                                        font-weigth:500;
                                        padding:10px;
                                        border-radius:8px;""")
        layoutBotones.addWidget(botonConfirmar)
        layoutBotones.addWidget(botonCancelar)
        botonCancelar.clicked.connect(self.cerrarVentana)
        layoutPrincipal.addLayout(layoutBotones)
        layoutPrincipal.addStretch(10)
        layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        layoutPrincipal.setSpacing(20)
    
    def subirInformacion(self, datos, tabla, icono):
        pixmap = icono.pixmap(287, 287)
        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        pixmap.save(buffer, "PNG")
        imagen_bytes = buffer.data()
        buffer.close()
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        consulta = """SELECT idSubcategoria FROM Subcategoria WHERE nombre=?"""
        c.execute(consulta, (datos[4],))
        resultados = c.fetchone()
        
        if not resultados:
            QMessageBox.critical(self, "Error", f"No se encontró la subcategoría: {datos[4]}")
            conn.close()
            return
            
        indiceSub = resultados[0]
        
        consulta = """INSERT INTO Producto(nomProd,descripcion,precioVenta,costoFabricacion,imgProd,idSubcategoria) VALUES(?,?,?,?,?,?)"""
        c.execute(consulta, (datos[0], datos[1], datos[2], datos[3], imagen_bytes, indiceSub))
        indiceProducto = c.lastrowid
        
        numFilas = tabla.rowCount()
        for i in range(numFilas):
            item_nombre = tabla.item(i, 0)
            indiceIng = item_nombre.data(Qt.UserRole + 1) if item_nombre else None

            if indiceIng is None:
                consulta = """SELECT idIng FROM Stock WHERE nomIng=?"""
                c.execute(consulta, (tabla.item(i, 0).text(),))
                resultados = c.fetchone()
                if not resultados:
                    QMessageBox.critical(self, "Error", f"No se encontró el ingrediente: {tabla.item(i, 0).text()}")
                    conn.rollback()
                    conn.close()
                    return
                indiceIng = resultados[0]
            else:
                c.execute("SELECT 1 FROM Stock WHERE idIng=?", (indiceIng,))
                if not c.fetchone():
                    QMessageBox.critical(self, "Error", f"El ingrediente '{tabla.item(i, 0).text()}' ya no existe. Quítelo de la tabla y vuelva a agregarlo.")
                    conn.rollback()
                    conn.close()
                    return

            consulta = """INSERT INTO ProductosIngredientes VALUES(?,?,?)"""
            c.execute(consulta, (indiceProducto, indiceIng, float(tabla.item(i, 2).text())))
        
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Confirmacion", "Se ha registrado con exito el producto")
        self.cerrarVentana(True)
    
    def actualizarFoto(self, imagen):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar una imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                icono = QIcon(pixmap)
            else:
                default_image_path = get_resource_path("Imagenes/camara.png")
                icono = QIcon(default_image_path)
            imagen.setIcon(icono)
            imagen.setIconSize(QSize(287, 287))
    
    def cerrarVentana(self, bandera=False):
        if bandera:
            self.accept()
        else:
            self.reject()

if __name__ == "__main__":
    aplicacion = QApplication(sys.argv)
    sys.exit(aplicacion.exec_())