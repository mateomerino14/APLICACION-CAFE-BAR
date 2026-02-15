import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter, QPainterPath, QPen
import os

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)


class PaginaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("""
            background-color: #e6f2ff;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        self.showMinimized()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(0,0,0,0)
        self.layoutPrincipal.setSpacing(30)
        self.set_up()
        
    def set_up(self): 
        contenedorCentral = QWidget()
        contenedorCentral.setStyleSheet("background: transparent;")
        layoutCentral = QVBoxLayout(contenedorCentral)
        layoutCentral.setAlignment(Qt.AlignCenter)
        imagen = QLabel()
        imagen.setFixedSize(400, 400)
        try:
            icono = QPixmap(get_resource_path(os.path.join('Imagenes','logo.jpg')))
            icono = icono.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            circular_pixmap = QPixmap(400, 400)
            circular_pixmap.fill(Qt.transparent)
            painter = QPainter(circular_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, 400, 400)
            painter.setClipPath(path)
            pen = QPen(Qt.black)
            pen.setWidth(2) 
            painter.setPen(pen)
            painter.drawEllipse(1, 1, 348, 348) 
            painter.drawPixmap(0, 0, icono)
            painter.end()
            imagen.setPixmap(circular_pixmap)
        except:
            imagen.setText("Logo no encontrado")
            imagen.setAlignment(Qt.AlignCenter)

        imagen.setStyleSheet("""
            background: transparent;
            border-radius: 175px;
        """)
        layoutCentral.addWidget(imagen)
        self.layoutPrincipal.addWidget(contenedorCentral, stretch=1)
        
        
if __name__=="__main__":
    aplicacion=QApplication(sys.argv)
    pagina=PaginaPrincipal()
    pagina.show()
    sys.exit(aplicacion.exec_())