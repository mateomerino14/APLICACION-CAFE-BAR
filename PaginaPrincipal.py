import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QColor
import os
import shutil
import math
from datetime import datetime

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

def get_writable_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(__file__)

def get_banner_path():
    base = get_writable_base_path()
    carpeta = os.path.join(base, 'database')
    os.makedirs(carpeta, exist_ok=True)
    return os.path.join(carpeta, 'banner_custom.png')

BANNER_PATH = get_banner_path()


class FormaDecorativa(QWidget):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color)
        painter.drawEllipse(self.rect())
        painter.end()


class PaginaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget#fondoPrincipal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #eaf4fd, stop: 0.5 #dceefc, stop: 1 #cfe6fb);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMessageBox {
                background: #ffffff;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 15px;
                font-weight: 500;
                background: transparent;
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
        self.setObjectName("fondoPrincipal")
        self.formasDecorativas = []
        self.showMinimized()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(0,0,0,0)
        self.layoutPrincipal.setSpacing(24)

        self._crearFormasDecorativas()

        self.set_up()

        self._glowPhase = 0.0
        self._glowTimer = QTimer(self)
        self._glowTimer.timeout.connect(self._pulsarBrillo)
        self._glowTimer.start(40)

        self._relojTimer = QTimer(self)
        self._relojTimer.timeout.connect(self._actualizarReloj)
        self._relojTimer.start(1000)

        QTimer.singleShot(50, self._animarAparicion)

    def _crearFormasDecorativas(self):
        especificaciones = [
            (QColor(52, 152, 219, 35), 260),
            (QColor(41, 128, 185, 28), 180),
            (QColor(93, 173, 226, 30), 140),
        ]
        for color, tamano in especificaciones:
            forma = FormaDecorativa(color, self)
            forma.resize(tamano, tamano)
            forma.lower()
            self.formasDecorativas.append(forma)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, "formasDecorativas") or len(self.formasDecorativas) != 3:
            return
        ancho = self.width()
        alto = self.height()
        self.formasDecorativas[0].move(ancho - 220, -80)
        self.formasDecorativas[1].move(-90, alto - 200)
        self.formasDecorativas[2].move(int(ancho * 0.08), int(alto * 0.62))

    def set_up(self): 
        self.contenedorCentral = QWidget()
        self.contenedorCentral.setStyleSheet("background: transparent;")
        layoutCentral = QVBoxLayout(self.contenedorCentral)
        layoutCentral.setAlignment(Qt.AlignCenter)
        layoutCentral.setSpacing(45)

        self._crearEncabezadoBienvenida(layoutCentral)

        self.imagen = QLabel()
        self.imagen.setFixedSize(440, 440)
        self.imagen.setStyleSheet("""
            background: transparent;
            border-radius: 220px;
        """)
        self.cargarImagenActual()

        self.brillo = QGraphicsDropShadowEffect(self.imagen)
        self.brillo.setColor(QColor(52, 152, 219, 160))
        self.brillo.setOffset(0, 0)
        self.brillo.setBlurRadius(35)
        self.imagen.setGraphicsEffect(self.brillo)

        layoutCentral.addWidget(self.imagen, alignment=Qt.AlignCenter)

        self.botonCambiar = QPushButton("Cambiar portada")
        self.botonCambiar.setCursor(Qt.PointingHandCursor)
        self.botonCambiar.setFixedSize(200, 44)
        self.botonCambiar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #16a085, stop: 1 #138d75);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 14px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1abc9c, stop: 1 #159d84);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #138d75, stop: 1 #0f7a64);
            }
        """)
        self.botonCambiar.clicked.connect(self.cambiarImagenPortada)
        layoutCentral.addWidget(self.botonCambiar, alignment=Qt.AlignCenter)

        self.layoutPrincipal.addWidget(self.contenedorCentral, stretch=1)

        self.efectoOpacidad = QGraphicsOpacityEffect(self.contenedorCentral)
        self.efectoOpacidad.setOpacity(0.0)
        self.contenedorCentral.setGraphicsEffect(self.efectoOpacidad)

    def _crearEncabezadoBienvenida(self, layoutCentral):
        encabezado = QFrame()
        encabezado.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3498db, stop: 1 #2980b9);
                border-radius: 16px;
            }
        """)
        sombraEncabezado = QGraphicsDropShadowEffect(encabezado)
        sombraEncabezado.setColor(QColor(52, 152, 219, 90))
        sombraEncabezado.setOffset(0, 6)
        sombraEncabezado.setBlurRadius(24)
        encabezado.setGraphicsEffect(sombraEncabezado)

        layoutEncabezado = QVBoxLayout(encabezado)
        layoutEncabezado.setContentsMargins(40, 22, 40, 22)
        layoutEncabezado.setSpacing(4)

        self.tituloBienvenida = QLabel("Bienvenido a Cafebar")
        self.tituloBienvenida.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.tituloBienvenida.setAlignment(Qt.AlignCenter)
        layoutEncabezado.addWidget(self.tituloBienvenida)

        self.subtituloFechaHora = QLabel("")
        self.subtituloFechaHora.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: 500;
                background: transparent;
            }
        """)
        self.subtituloFechaHora.setAlignment(Qt.AlignCenter)
        layoutEncabezado.addWidget(self.subtituloFechaHora)
        self._actualizarReloj()

        layoutCentral.addWidget(encabezado)

    def _actualizarReloj(self):
        if not hasattr(self, "subtituloFechaHora"):
            return
        locale = QLocale(QLocale.Spanish, QLocale.Bolivia)
        fecha_texto = locale.toString(QDate.currentDate(), "dddd, d 'de' MMMM")
        fecha_texto = fecha_texto[:1].upper() + fecha_texto[1:]
        hora_texto = datetime.now().strftime("%I:%M:%S %p")
        self.subtituloFechaHora.setText(f"{fecha_texto}  •  {hora_texto}")

    def _pulsarBrillo(self):
        if not hasattr(self, "brillo"):
            return
        self._glowPhase += 0.05
        valor = 35 + 18 * math.sin(self._glowPhase)
        self.brillo.setBlurRadius(valor)

    def _animarAparicion(self):
        self.animacionAparicion = QPropertyAnimation(self.efectoOpacidad, b"opacity", self)
        self.animacionAparicion.setDuration(650)
        self.animacionAparicion.setStartValue(0.0)
        self.animacionAparicion.setEndValue(1.0)
        self.animacionAparicion.setEasingCurve(QEasingCurve.OutCubic)
        self.animacionAparicion.finished.connect(self._quitarEfectoOpacidad)
        self.animacionAparicion.start()

    def _quitarEfectoOpacidad(self):
        self.contenedorCentral.setGraphicsEffect(None)
        
    def cargarImagenActual(self):
        tamano = self.imagen.width()
        if os.path.exists(BANNER_PATH):
            ruta_imagen = BANNER_PATH
        else:
            ruta_imagen = get_resource_path(os.path.join('Imagenes', 'logo.jpg'))
        try:
            icono = QPixmap(ruta_imagen)
            if icono.isNull():
                raise ValueError("No se pudo cargar la imagen")
            icono = icono.scaled(tamano, tamano, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            circular_pixmap = QPixmap(tamano, tamano)
            circular_pixmap.fill(Qt.transparent)
            painter = QPainter(circular_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, tamano, tamano)
            painter.setClipPath(path)
            pen = QPen(QColor("#ffffff"))
            pen.setWidth(6)
            painter.setPen(pen)
            x_offset = (icono.width() - tamano) // 2
            y_offset = (icono.height() - tamano) // 2
            painter.drawPixmap(-x_offset, -y_offset, icono)
            painter.drawEllipse(3, 3, tamano - 6, tamano - 6)
            painter.end()
            self.imagen.setPixmap(circular_pixmap)
        except Exception:
            self.imagen.setText("Logo no encontrado")
            self.imagen.setAlignment(Qt.AlignCenter)

    def cambiarImagenPortada(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen de portada",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if not file_path:
            return
        try:
            pixmap_prueba = QPixmap(file_path)
            if pixmap_prueba.isNull():
                QMessageBox.warning(self, "Error", "El archivo seleccionado no es una imagen válida")
                return
            os.makedirs(os.path.dirname(BANNER_PATH), exist_ok=True)
            shutil.copyfile(file_path, BANNER_PATH)
            self.cargarImagenActual()
            QMessageBox.information(self, "Confirmación", "La imagen de portada fue actualizada correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar la imagen: {str(e)}")
        
        
if __name__=="__main__":
    aplicacion=QApplication(sys.argv)
    pagina=PaginaPrincipal()
    pagina.show()
    sys.exit(aplicacion.exec_())