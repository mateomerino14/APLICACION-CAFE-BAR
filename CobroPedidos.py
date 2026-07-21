import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from collections import defaultdict
import smtplib
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from PyQt5.QtWidgets import QMessageBox
from Impresion import ManejadorImpresion
import webbrowser

try:
    from escpos.printer import Usb
    USB_IMPRESORA_DISPONIBLE = True
except ImportError:
    USB_IMPRESORA_DISPONIBLE = False

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'database', 'cafebar.db')

def get_images_dir():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'Imagenes')

DB_PATH = get_db_path()
DIRECCION_LUPA = get_images_dir()

class CobroPedidos(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QTableWidget {
                background-color: white;
                padding:10px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #e2e8f0;
                font-size: 14px;
                alternate-background-color: #f8fafc;
            }
            
            QTableWidget::item {
                padding: 3px;
                border-bottom: 1px solid #e2e8f0;
            }
            
            QTableWidget::item:selected {
                background-color: #e6f2ff;
                color: #2c3e50;
            }
            
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton {
                padding: 5px 0px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                border: none;
            }
            
            QPushButton:hover {
                opacity: 0.9;
            }
            
            QPushButton:pressed {
                opacity: 0.8;
            }
            
            QLineEdit {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                min-height: 40px;
                selection-background-color: #4a89dc;
            }
            
            QLineEdit:focus {
                border: 2px solid #4a89dc;
                background-color: #f0f7ff;
            }
            
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 5px;
            }
            
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 12px;
                margin: 0;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                min-height: 30px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
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
            
            QRadioButton {
                font-size: 14px;
                color: #2c3e50;
                padding: 8px;
                spacing: 8px;
            }
            
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #4a89dc;
            }
            
            QRadioButton::indicator:checked {
                background-color: #4a89dc;
                border: 2px solid #4a89dc;
            }
            
            QRadioButton::indicator:unchecked {
                background-color: white;
            }
            
            QComboBox {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                min-height: 40px;
            }
            
            QComboBox:focus {
                border: 2px solid #4a89dc;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: #e2e8f0;
                border-left-style: solid;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #4a89dc;
                width: 0px;
                height: 0px;
            }
            
            QComboBox QAbstractItemView {
                background-color: white;
                selection-background-color: #02505e;
                border: 1px solid #e2e8f0;
                outline: 0;
                border-radius: 6px;
            }
            
            QTextEdit {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                min-height: 100px;
            }
            
            QTextEdit:focus {
                border: 2px solid #4a89dc;
                background-color: #f0f7ff;
            }
            
            QDialog {
                background-color: white;
                border-radius: 8px;
            }
            
            QPushButton#cobrar {
                background-color: #2ecc71;
                color: white;
            }
            
            QPushButton#cobrar:hover {
                background-color: #27ae60;
            }
            
            QPushButton#imprimir {
                background-color: #3498db;
                color: white;
            }
            
            QPushButton#imprimir:hover {
                background-color: #2980b9;
            }
            
            QPushButton#notificar {
                background-color: #9b59b6;
                color: white;
            }
            
            QPushButton#notificar:hover {
                background-color: #8e44ad;
            }
            
            QPushButton#confirmar {
                background-color: #2ecc71;
                color: white;
            }
            
            QPushButton#confirmar:hover {
                background-color: #27ae60;
            }
            
            QPushButton#cancelar {
                background-color: #95a5a6;
                color: white;
            }
            
            QPushButton#cancelar:hover {
                background-color: #7f8c8d;
            }
            
            QPushButton#buscar {
                background-color: #f39c12;
                color: white;
            }
            
            QPushButton#buscar:hover {
                background-color: #e67e22;
            }
            
            QPushButton#registrar {
                background-color: #3498db;
                color: white;
            }
            
            QPushButton#registrar:hover {
                background-color: #2980b9;
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
             QMessageBox QPushButton:hover { background-color: #2980b9; }
        """)
        self.pago = None
        self.rbEfectivo = None
        self.rbQR = None
        self.rbMixto = None
        self.txtEfectivo = None
        self.txtQR = None
        self.set_up()

    def set_up(self):
        self.layoutDatos = QHBoxLayout()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.iniciarPagina()
        self.showMaximized()
        
    def iniciarPagina(self):
        self.tablaVentasCobrar = QTableWidget()
        self.tablaVentasCobrar.verticalHeader().setVisible(False)
        self.tablaVentasCobrar.setColumnCount(4)
        self.tablaVentasCobrar.setHorizontalHeaderLabels(["FECHA REGISTRO", "MESA", "SECCIÓN", "ACCION"])
        self.tablaVentasCobrar.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablaVentasCobrar.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablaVentasCobrar.setSelectionMode(QAbstractItemView.NoSelection)
        self.tablaVentasCobrar.setFocusPolicy(Qt.NoFocus)
        self.tablaVentasCobrar.setAlternatingRowColors(True)
        self.cargarDatosTabla()
        self.layoutPrincipal.addWidget(self.tablaVentasCobrar)
       
    def cargarDatosTabla(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT 
                                V.numVenta,
                                DATE(V.fechaReg) AS fecha,
                                MAX(V.idMesa)    AS idMesa,
                                MAX(V.idSeccion) AS idSeccion
                             FROM Venta V
                             LEFT JOIN DetallesVenta Dt 
                                   ON Dt.numVenta = V.numVenta 
                                  AND Dt.fechaRegVenta = V.fechaReg
                             GROUP BY V.numVenta, V.fechaReg
                             HAVING SUM(CASE WHEN Dt.estadoDetalleVenta = 'Preparacion' THEN 1 ELSE 0 END) = 0
                                    AND SUM(CASE WHEN Dt.estadoDetalleVenta = 'Cobrar'      THEN 1 ELSE 0 END) > 0;
                            """)
                           
            resultados = cursor.fetchall()
            self.tablaVentasCobrar.setRowCount(0)
            for venta in resultados:
                fila = self.tablaVentasCobrar.rowCount()
                self.tablaVentasCobrar.insertRow(fila)
                numVenta=venta[0]
                fechaReg = venta[1]
                numMesa = venta[2]
                idSeccion = venta[3]
                cursor.execute("""SELECT nombSeccion FROM Seccion WHERE idSeccion=?""",(idSeccion,))
                nombSeccion = cursor.fetchone()[0]
                boton_cobrar = QPushButton("Cobrar")
                boton_cobrar.setFixedHeight(23)
                boton_cobrar.setObjectName("cobrar")
                boton_cobrar.clicked.connect(lambda checked, f=fila, fecha=fechaReg,nv=numVenta, nM=numMesa, idSec=idSeccion: self.cobrar(f, fecha,nv, nM, idSec))
                boton_cobrar.setCursor(QCursor(Qt.PointingHandCursor))
                fecha_obj = datetime.strptime(fechaReg, "%Y-%m-%d")
                item = QTableWidgetItem(fecha_obj.strftime("%d/%m/%Y"))
                item.setTextAlignment(Qt.AlignCenter)
                self.tablaVentasCobrar.setItem(fila, 0, item)
                item = QTableWidgetItem(f"{numMesa}")
                item.setTextAlignment(Qt.AlignCenter)
                self.tablaVentasCobrar.setItem(fila, 1, item)
                item = QTableWidgetItem(f"{nombSeccion}")
                item.setTextAlignment(Qt.AlignCenter)
                self.tablaVentasCobrar.setItem(fila, 2, item)
                self.tablaVentasCobrar.setCellWidget(fila, 3, boton_cobrar)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar datos: {str(e)}")
        finally:
            conn.close()

    
    def imprimir(self, fecha, numVenta):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""SELECT numVenta, idMesa, nombSeccion, E1.nomEmp AS empleado, E2.nomEmp AS cajero 
                            FROM Venta V
                            INNER JOIN Empleado E1 ON V.codEmp = E1.codEmp
                            INNER JOIN Empleado E2 ON V.codEmp2 = E2.codEmp
                            INNER JOIN Seccion S ON S.idSeccion = V.idSeccion
                            WHERE DATE(V.fechaReg) = ? AND V.numVenta = ?""", (fecha, numVenta))
        resultadosVenta = self.cursor.fetchone()
        
        self.cursor.execute("""
            SELECT cantidadProdDet, tipoConsumo, 
                CASE 
                    WHEN idProd IS NOT NULL THEN (SELECT nomProd FROM Producto WHERE idProd = D.idProd)
                    ELSE (SELECT nomProm FROM Promocion WHERE idProm = D.idProm)
                END as nombre,
                CASE 
                    WHEN idProd IS NOT NULL THEN (SELECT precioVenta FROM Producto WHERE idProd = D.idProd)
                    ELSE (SELECT precioProm FROM Promocion WHERE idProm = D.idProm)
                END as precio
            FROM DetallesVenta D
            WHERE D.numVenta = ? AND DATE(D.fechaRegVenta) = ?
        """, (numVenta, fecha))
        
        detallesVenta = self.cursor.fetchall()
        self.cursor.close()
        self.conn.close()
        
        items_agrupados = {}
        for cantidad, tipo, nombre, precio in detallesVenta:
            if nombre is None:
                continue
            cantidad = int(cantidad) if cantidad else 0
            precio = float(precio) if precio else 0.0
            
            clave = (nombre, tipo)
            if clave in items_agrupados:
                items_agrupados[clave]['cantidad'] += cantidad
                items_agrupados[clave]['subtotal'] += cantidad * precio
            else:
                items_agrupados[clave] = {
                    'cantidad': cantidad,
                    'producto': nombre,
                    'tipo': tipo,
                    'precio': precio,
                    'subtotal': cantidad * precio
                }
        
        items = list(items_agrupados.values())
        
        impresion = ManejadorImpresion()
        datosVenta = {
            'num_venta': str(resultadosVenta[0]),
            'mesa': str(resultadosVenta[1]),
            'seccion': str(resultadosVenta[2]),
            'empleado': str(resultadosVenta[3]),
            'cajero': str(resultadosVenta[4])
        }
        exito, mensaje = impresion.imprimir_ticket(datosVenta, items)
        print(mensaje)



    def cobrar(self, f, fecha,numVenta, numMesa, idSec):
        self.paginaCobrarVenta = QDialog(self)
        self.paginaCobrarVenta.setFixedSize(1600,900)
        self.paginaCobrarVenta.setWindowTitle("CAJA")
        self.paginaCobrarVenta.setStyleSheet("""QDialog{
            background-color:white; border-radius: 8px;}
            QWidget{
                padding:0px;
            };""")
        
        layoutPagina = QVBoxLayout()
        layoutPagina.setContentsMargins(20, 20, 20, 20)
        layoutPagina.setSpacing(15)
        self.paginaCobrarVenta.setLayout(layoutPagina)
        titulo = QLabel("ÁREA DE COBRO")
        titulo.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #3498db;
                color: white;
                border-radius: 8px;
            }
        """)
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setMinimumHeight(40)
        layoutPagina.addWidget(titulo)
        layoutIntermedio = QHBoxLayout()
        layoutBotones = QHBoxLayout()
        layoutPagina.addLayout(layoutIntermedio)
        layoutPagina.addLayout(layoutBotones)
        layoutPreview = QVBoxLayout()
        tituloPreview = QLabel("📄 PREVISUALIZACIÓN DE FACTURA")
        tituloPreview.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 6px;
                text-align: center;
            }
        """)
        layoutPreview.addWidget(tituloPreview)
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setMinimumHeight(500)
        scrollArea.setStyleSheet("""
            QScrollArea {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
            }
        """)
        previewWidget = QWidget()
        self.previewLayout = QVBoxLayout(previewWidget)
        self.previewLayout.setSpacing(8)
        self.previewLayout.setContentsMargins(15, 15, 15, 15)
        self.cargarPrevisualizacionFactura(fecha, numVenta, numMesa, idSec)
        scrollArea.setWidget(previewWidget)
        layoutPreview.addWidget(scrollArea)
        layoutIntermedio.addLayout(layoutPreview, stretch=6)
        layoutMetodosPago = QVBoxLayout()
        grupoMetodosPago = QButtonGroup()
        lblMetodoPago = QLabel("MÉTODO DE PAGO:")
        lblMetodoPago.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; margin-bottom: 10px;")
        layoutMetodosPago.addWidget(lblMetodoPago)
        self.rbEfectivo = QRadioButton("Efectivo")
        self.rbQR = QRadioButton("QR")
        self.rbMixto = QRadioButton("Mixto")
        for rb in [self.rbEfectivo, self.rbQR, self.rbMixto]:
            rb.setStyleSheet("font-size: 15px; padding: 10px;")
        grupoMetodosPago.addButton(self.rbEfectivo)
        grupoMetodosPago.addButton(self.rbQR)
        grupoMetodosPago.addButton(self.rbMixto)
        layoutMetodosPago.addWidget(self.rbEfectivo)
        layoutMetodosPago.addWidget(self.rbQR)
        layoutMetodosPago.addWidget(self.rbMixto)
        self.lblEfectivo = QLabel("Monto en Efectivo:")
        self.lblEfectivo.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 15px;")
        self.txtEfectivo = QLineEdit("")
        self.txtEfectivo.setPlaceholderText("0.00")
        self.txtEfectivo.setValidator(QRegExpValidator(QRegExp("[0-9]+\.?[0-9]{0,2}")))
        self.txtEfectivo.setEnabled(False)
        self.txtEfectivo.setStyleSheet("font-size: 15px; padding: 8px;")
        self.lblQR = QLabel("Monto con QR:")
        self.lblQR.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        self.txtQR = QLineEdit("")
        self.txtQR.setPlaceholderText("0.00")
        self.txtQR.setValidator(QRegExpValidator(QRegExp("[0-9]+\.?[0-9]{0,2}")))
        self.txtQR.setEnabled(False)
        self.txtQR.setStyleSheet("font-size: 15px; padding: 8px;")
        layoutMetodosPago.addWidget(self.lblEfectivo)
        layoutMetodosPago.addWidget(self.txtEfectivo)
        layoutMetodosPago.addWidget(self.lblQR)
        layoutMetodosPago.addWidget(self.txtQR)
        self.rbEfectivo.toggled.connect(self.actualizarCamposPago)
        self.rbQR.toggled.connect(self.actualizarCamposPago)
        self.rbMixto.toggled.connect(self.actualizarCamposPago)
        self.rbEfectivo.setChecked(True)
        layoutCobro = QVBoxLayout()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            self.total = 0.00
            cursor.execute("""SELECT totalVenta FROM Venta WHERE DATE(fechaReg)=? AND numVenta=?""",(fecha,numVenta))
            resultados = cursor.fetchall()
            for elemento in resultados:
                self.total += float(elemento[0])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al calcular total: {str(e)}")
        finally:
            conn.close()
        etiquetaTotal = QLabel("Total:")
        etiquetaTotal.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; margin-top: 10px;")
        total = QLabel(f"{self.total:.2f} Bs.")
        total.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c; margin-bottom: 15px;")
        etiquetaPago = QLabel("Pago:")
        etiquetaPago.setStyleSheet("font-weight: bold; font-size: 15px; color: #2c3e50; margin-top: 10px;")
        self.pago = QLineEdit()
        self.pago.setPlaceholderText((f"{self.total:.2f} Bs."))
        self.pago.setValidator(QRegExpValidator(QRegExp("[0-9]+\.?[0-9]{0,2}")))
        self.pago.textChanged.connect(self.actualizarCambio)
        self.pago.setStyleSheet("font-size: 15px; padding: 8px;")
        etiquetaCambio = QLabel("Cambio:")
        etiquetaCambio.setStyleSheet("font-weight: bold; font-size: 15px; color: #2c3e50; margin-top: 10px;")
        self.cambio = QLabel("0.00 Bs.")
        self.cambio.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
        layoutCobro.addWidget(etiquetaTotal)
        layoutCobro.addWidget(total)
        layoutCobro.addWidget(etiquetaPago)
        layoutCobro.addWidget(self.pago)
        layoutCobro.addWidget(etiquetaCambio)
        layoutCobro.addWidget(self.cambio)
        layoutCobro.addLayout(layoutMetodosPago)
        layoutCobro.addStretch(1)
        layoutIntermedio.addLayout(layoutCobro, stretch=2)
        impuestos = QPushButton("IMPUESTOS")
        impuestos.setStyleSheet("""background-color:purple;
                                   color:white;""")
        impuestos.setObjectName("impuestos")
        impuestos.setFixedHeight(35)
        impuestos.setCursor(QCursor(Qt.PointingHandCursor))
        impuestos.clicked.connect(self.abrirPaginaImpuestos)
        confirmar = QPushButton("CONFIRMAR")
        confirmar.setObjectName("confirmar")
        confirmar.setFixedHeight(35)
        confirmar.setCursor(QCursor(Qt.PointingHandCursor))
        confirmar.clicked.connect(lambda checked, f=fecha, idMesa=numMesa, idSeccion=idSec,total=round(self.total,2): self.confirmar(f,numVenta,idMesa, idSeccion,total))
        cancelar = QPushButton("CANCELAR")
        cancelar.setObjectName("cancelar")
        cancelar.setFixedHeight(35)
        cancelar.setCursor(QCursor(Qt.PointingHandCursor))
        cancelar.clicked.connect(self.paginaCobrarVenta.close)
        imprimir=QPushButton("IMPRIMIR")
        imprimir.setObjectName("imprimir")
        imprimir.setFixedHeight(35)
        imprimir.setCursor(QCursor(Qt.PointingHandCursor))
        imprimir.clicked.connect(lambda _,fecha=fecha,nVenta=numVenta:self.imprimir(fecha,nVenta))
        layoutBotones.addWidget(imprimir)
        layoutBotones.addWidget(impuestos) 
        layoutBotones.addWidget(confirmar)
        layoutBotones.addWidget(cancelar)
        self.actualizarCamposPago()
        self.paginaCobrarVenta.exec_()
    
    def cargarPrevisualizacionFactura(self, fecha, numVenta, numMesa, idSeccion):
        while self.previewLayout.count():
            item = self.previewLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT nombSeccion FROM Seccion WHERE idSeccion=?""", (idSeccion,))
            nombre_seccion = cursor.fetchone()[0]
            cursor.execute("""
                SELECT DV.cantidadProdDet, P.nomProd, P.precioVenta, DV.subtotal, DV.tipoConsumo, DV.idProd
                FROM DetallesVenta DV
                INNER JOIN Producto P ON DV.idProd = P.idProd
                WHERE strftime('%Y-%m-%d', DV.fechaRegVenta)=? 
                  AND DV.numVenta=?
                  AND DV.estadoDetalleVenta='Cobrar'
                  AND DV.idProd IS NOT NULL
                ORDER BY DV.tipoConsumo, P.nomProd
            """, (fecha, numVenta))
            productos_sin_procesar = cursor.fetchall()
            cursor.execute("""
                SELECT DV.cantidadProdDet, PR.nomProm, PR.precioProm, DV.subtotal, DV.tipoConsumo, DV.idProm
                FROM DetallesVenta DV
                INNER JOIN Promocion PR ON DV.idProm = PR.idProm
                WHERE strftime('%Y-%m-%d', DV.fechaRegVenta)=? 
                  AND DV.numVenta=?
                  AND DV.estadoDetalleVenta='Cobrar'
                  AND DV.idProm IS NOT NULL
                ORDER BY DV.tipoConsumo, PR.nomProm
            """, (fecha, numVenta))
            promociones_sin_procesar = cursor.fetchall()
            def agrupar_items(items_sin_procesar, es_promocion=False):
                if not items_sin_procesar:
                    return []
                items_agrupados = {}
                for cantidad, nombre, precio, subtotal, tipo, id_item in items_sin_procesar:
                    if nombre is None:
                        continue
                        
                    cantidad = cantidad if cantidad is not None else 0
                    precio = precio if precio is not None else 0.0
                    subtotal = subtotal if subtotal is not None else 0.0
                    
                    clave = (nombre, precio, tipo, id_item, es_promocion)
                    if clave in items_agrupados:
                        items_agrupados[clave] = (
                            items_agrupados[clave][0] + cantidad,
                            nombre,
                            precio,
                            items_agrupados[clave][3] + subtotal,
                            tipo,
                            id_item,
                            es_promocion
                        )
                    else:
                        items_agrupados[clave] = (cantidad, nombre, precio, subtotal, tipo, id_item, es_promocion)
                return list(items_agrupados.values())
            productos = agrupar_items(productos_sin_procesar, es_promocion=False)
            promociones = agrupar_items(promociones_sin_procesar, es_promocion=True)
            productos_local = [p for p in productos if p[4] == 'Local']
            productos_llevar = [p for p in productos if p[4] == 'Para llevar']
            promociones_local = [p for p in promociones if p[4] == 'Local']
            promociones_llevar = [p for p in promociones if p[4] == 'Para llevar']
            cursor.execute("""SELECT MAX(fechaRegDetalleVenta) FROM DetallesVenta 
                           WHERE strftime('%Y-%m-%d', fechaRegVenta)=? AND numVenta=?""", (fecha, numVenta))
            fecha_hora = cursor.fetchone()[0]
            if fecha_hora:
                try:
                    hora_registro = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S.%f").strftime("%I:%M %p")
                except:
                    hora_registro = "Hora no disponible"
            else:
                hora_registro = "No disponible"
            
            fecha_objeto = datetime.strptime(fecha, "%Y-%m-%d")
            fecha_formateada = fecha_objeto.strftime("%d/%m/%Y")
            encabezadoFrame = QFrame()
            encabezadoFrame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3498db, stop:1 #2980b9);
                    border-radius: 12px;
                    padding: 25px;
                }
            """)
            layoutEncabezado = QVBoxLayout(encabezadoFrame)
            layoutEncabezado.setSpacing(5)
            etiquetaInfoVenta = QLabel(f"<div style='font-size: 24px; font-weight: 700; text-align: center;'>FACTURA #{numVenta}</div>")
            etiquetaInfoVenta.setStyleSheet("QLabel { font-family: 'Segoe UI', Arial, sans-serif; color: white; }")
            layoutEncabezado.addWidget(etiquetaInfoVenta)
            def crear_etiqueta_info(texto, valor, icono=""):
                marco = QFrame()
                marco.setStyleSheet("""
                    QFrame {
                        background-color: rgba(255, 255, 255, 0.15);
                        border-radius: 8px;
                        padding: 10px;
                        font-size: 16px;
                    }
                """)
                layout_marco = QHBoxLayout(marco)
                layout_marco.setContentsMargins(10, 8, 10, 8)
                if icono:
                    etiqueta_icono = QLabel(icono)
                    etiqueta_icono.setStyleSheet("font-size: 18px; margin-right: 8px;")
                    layout_marco.addWidget(etiqueta_icono)
                etiqueta_texto = QLabel(f"<b>{texto}: <span>{valor}</span>")
                etiqueta_texto.setStyleSheet("color: white; font-family: 'Segoe UI';")
                etiqueta_texto.setAlignment(Qt.AlignLeft)
                layout_marco.addWidget(etiqueta_texto)
                layout_marco.addStretch()
                return marco
            cuadriculaInfo = QGridLayout()
            cuadriculaInfo.setSpacing(5)
            cuadriculaInfo.setContentsMargins(5, 5, 5, 5)
            cuadriculaInfo.addWidget(crear_etiqueta_info("📅 FECHA", fecha_formateada), 0, 0)
            cuadriculaInfo.addWidget(crear_etiqueta_info("🕐 HORA", hora_registro), 0, 1)
            cuadriculaInfo.addWidget(crear_etiqueta_info("📍 MESA", str(numMesa)), 1, 0)
            cuadriculaInfo.addWidget(crear_etiqueta_info("🏢 SECCIÓN", nombre_seccion), 1, 1)
            layoutEncabezado.addLayout(cuadriculaInfo)
            self.previewLayout.addWidget(encabezadoFrame)
            separador = QFrame()
            separador.setFixedHeight(2)
            separador.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 transparent, stop:0.5 #3498db, stop:1 transparent);
                    margin: 20px 0;
                }
            """)
            self.previewLayout.addWidget(separador)

            def crear_seccion_producto(titulo, productos_lista, color, icono, tipo=None, es_promocion=False):
                if not productos_lista:
                    return None
                widget_seccion = QWidget()
                layout_seccion = QVBoxLayout(widget_seccion)
                layout_seccion.setSpacing(10)
                if tipo:
                    texto_titulo = f"{icono} {titulo} ({tipo})"
                else:
                    texto_titulo = f"{icono} {titulo}"
                etiqueta_titulo = QLabel(texto_titulo)
                etiqueta_titulo.setStyleSheet(f"""
                    QLabel {{
                        font-family: 'Segoe UI', Arial, sans-serif;
                        font-size: 18px;
                        font-weight: 600;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 10px 5px;
                        background-color: {color};
                        color: white;
                    }}
                """)
                layout_seccion.addWidget(etiqueta_titulo)
                tabla = QTableWidget()
                tabla.setColumnCount(4)
                tabla.setHorizontalHeaderLabels(["CANTIDAD", "DESCRIPCIÓN", "PRECIO UNIT.", "SUBTOTAL"])
                tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
                tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
                tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
                tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
                tabla.setColumnWidth(0, 80)
                tabla.setColumnWidth(2, 140)
                tabla.setColumnWidth(3, 140)
                tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
                tabla.setAlternatingRowColors(True)
                tabla.verticalHeader().setVisible(False)
                tabla.setFixedHeight(min(250, len(productos_lista) * 50 + 60))
                tabla.setStyleSheet("""
                    QTableWidget {
                        background-color: white;
                        border: 2px solid #e0e6ed;
                        border-radius: 10px;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        font-size: 14px;
                        gridline-color: #e8edf5;
                    }
                    QTableWidget::item {
                        padding: 10px 5px;
                        border-bottom: 1px solid #f1f5f9;
                    }
                    QTableWidget::item:selected {
                        background-color: #e3f2fd;
                    }
                    QHeaderView::section {
                        background-color: #4a6fa5;
                        color: white;
                        padding: 12px 5px;
                        border: none;
                        font-size: 14px;
                        font-weight: 600;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        text-align: center;
                    }
                    QTableWidget QScrollBar:vertical {
                        width: 12px;
                        background: #f8fafc;
                        border-radius: 6px;
                    }
                    QTableWidget QScrollBar::handle:vertical {
                        background: #cbd5e1;
                        border-radius: 6px;
                        min-height: 30px;
                    }
                    QTableWidget QScrollBar::handle:vertical:hover {
                        background: #94a3b8;
                    }
                """)
                
                for columna in range(4):
                    item_encabezado = tabla.horizontalHeaderItem(columna)
                    if item_encabezado:
                        item_encabezado.setTextAlignment(Qt.AlignCenter)
                tabla.setRowCount(len(productos_lista))
                subtotal_seccion = 0
                for i, (cantidad, nombre, precio, subtotal, tipo_consumo, id_item, es_promocion_flag) in enumerate(productos_lista):
                    cantidad = cantidad if cantidad is not None else 0
                    precio = precio if precio is not None else 0.0
                    subtotal = subtotal if subtotal is not None else 0.0
                    item_cantidad = QTableWidgetItem(str(cantidad))
                    item_cantidad.setTextAlignment(Qt.AlignCenter)
                    item_cantidad.setFont(QFont("Segoe UI", 12))
                    tabla.setItem(i, 0, item_cantidad)
                    item_nombre = QTableWidgetItem(str(nombre))
                    item_nombre.setTextAlignment(Qt.AlignCenter)
                    item_nombre.setFont(QFont("Segoe UI", 12))
                    tabla.setItem(i, 1, item_nombre)
                    texto_precio = f"{precio:.2f} Bs" if precio is not None else "0.00 Bs"
                    item_precio = QTableWidgetItem(texto_precio)
                    item_precio.setTextAlignment(Qt.AlignCenter)
                    item_precio.setFont(QFont("Segoe UI", 12))
                    tabla.setItem(i, 2, item_precio)
                    texto_subtotal = f"{subtotal:.2f} Bs" if subtotal is not None else "0.00 Bs"
                    item_subtotal = QTableWidgetItem(texto_subtotal)
                    item_subtotal.setTextAlignment(Qt.AlignCenter)
                    item_subtotal.setFont(QFont("Segoe UI", 12, QFont.Bold))
                    item_subtotal.setForeground(QColor("#2c3e50"))
                    tabla.setItem(i, 3, item_subtotal)
                    subtotal_seccion += subtotal if subtotal is not None else 0
                for fila in range(tabla.rowCount()):
                    tabla.setRowHeight(fila, 40)
                layout_seccion.addWidget(tabla)
                marco_subtotal = QFrame()
                marco_subtotal.setStyleSheet(f"""
                    QFrame {{
                        background-color: {color}20;
                        border-left: 4px solid {color};
                        border-radius: 6px;
                        padding: 8px;
                    }}
                """)
                layout_subtotal = QHBoxLayout(marco_subtotal)
                if tipo:
                    titulo_seccion = f"{titulo.split()[0]} {tipo}"
                else:
                    titulo_seccion = titulo.split()[-1]
                etiqueta_subtotal = QLabel(f"<b>Subtotal {titulo_seccion}:</b>")
                etiqueta_subtotal.setStyleSheet("font-family: 'Segoe UI'; font-size: 16px; color: #2c3e50;")
                valor_subtotal = QLabel(f"<b>{subtotal_seccion:.2f} Bs</b>")
                valor_subtotal.setStyleSheet("font-family: 'Segoe UI'; font-size: 16px; font-weight: 600; color: #2c3e50;")
                layout_subtotal.addWidget(etiqueta_subtotal)
                layout_subtotal.addStretch()
                layout_subtotal.addWidget(valor_subtotal)
                layout_seccion.addWidget(marco_subtotal)
                return widget_seccion
            secciones_agregadas = False
            if productos_local:
                seccion_local = crear_seccion_producto("PRODUCTOS", productos_local, "#27ae60", "🏠", "Local", False)
                if seccion_local:
                    self.previewLayout.addWidget(seccion_local)
                    self.previewLayout.addSpacing(15)
                    secciones_agregadas = True
            if productos_llevar:
                seccion_llevar = crear_seccion_producto("PRODUCTOS", productos_llevar, "#27ae60", "🥡", "Para llevar", False)
                if seccion_llevar:
                    self.previewLayout.addWidget(seccion_llevar)
                    self.previewLayout.addSpacing(15)
                    secciones_agregadas = True
            if promociones_local:
                seccion_promociones_local = crear_seccion_producto("PROMOCIONES", promociones_local, "#27ae60", "🎁", "Local", True)
                if seccion_promociones_local:
                    self.previewLayout.addWidget(seccion_promociones_local)
                    self.previewLayout.addSpacing(15)
                    secciones_agregadas = True
            if promociones_llevar:
                seccion_promociones_llevar = crear_seccion_producto("PROMOCIONES", promociones_llevar, "#27ae60", "🎁", "Para llevar", True)
                if seccion_promociones_llevar:
                    self.previewLayout.addWidget(seccion_promociones_llevar)
                    self.previewLayout.addSpacing(15)
                    secciones_agregadas = True
            if not secciones_agregadas:
                etiqueta_vacia = QLabel("""
                    <div style='padding: 40px; text-align: center; background-color: #f8f9fa; border-radius: 10px; border: 2px dashed #dee2e6;'>
                        <span style='color: #6c757d; font-size: 18px; font-weight: 600;'>📋 No hay productos o promociones en esta venta</span><br><br>
                        <span style='color: #adb5bd; font-size: 14px;'>Esta venta no contiene elementos para mostrar.</span>
                    </div>
                """)
                etiqueta_vacia.setStyleSheet("font-family: 'Segoe UI';")
                self.previewLayout.addWidget(etiqueta_vacia)
                self.previewLayout.addSpacing(15)
            separador2 = QFrame()
            separador2.setFixedHeight(3)
            separador2.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #e74c3c, stop:0.5 #c0392b, stop:1 #e74c3c);
                    border-radius: 1.5px;
                    margin: 20px 0;
                }
            """)
            self.previewLayout.addWidget(separador2)
            cursor.execute("""SELECT totalVenta FROM Venta WHERE strftime('%Y-%m-%d', fechaReg)=? AND numVenta=?""",(fecha,numVenta))
            resultado = cursor.fetchone()
            total_venta = resultado[0] if resultado else 0.0
            marcoTotal = QFrame()
            marcoTotal.setStyleSheet("""
              QFrame {
                  background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                      stop:0 #ffffff, stop:0.5 #f8f9fa, stop:1 #ffffff);
                  border: 3px solid #2c3e50;
                  border-radius: 12px;
                  padding: 10px;
                  }
              """)
            layoutTotal = QVBoxLayout(marcoTotal)
            layoutTotal.setSpacing(10)
            layoutFilaTotal = QHBoxLayout()
            etiquetaTotalTitulo = QLabel("TOTAL A PAGAR:")
            etiquetaTotalTitulo.setStyleSheet("""
              QLabel {
                  font-family: 'Segoe UI', Arial, sans-serif;
                  font-size: 18px;
                  font-weight: 600;
                  color: #2c3e50;
                  border:none;
              }
          """)
            layoutFilaTotal.addWidget(etiquetaTotalTitulo)
            etiquetaTotalValor = QLabel(f"<div style='font-size: 18px; font-weight: 700; color: #e74c3c;'>{total_venta:.2f} Bs</div>")
            etiquetaTotalValor.setStyleSheet("font-family: 'Segoe UI', Arial, sans-serif; border:none;")
            layoutFilaTotal.addWidget(etiquetaTotalValor)
            layoutFilaTotal.addStretch()
            layoutTotal.addLayout(layoutFilaTotal)
            self.etiquetaMetodo = QLabel(f"<span style='color: #7f8c8d; font-size: 14px;'>Método: </span><b>Efectivo</b>")
            self.etiquetaMetodo.setStyleSheet("font-family: 'Segoe UI'; font-size: 14px; text-align: center;")
            self.etiquetaMetodo.setAlignment(Qt.AlignCenter)
            layoutTotal.addWidget(self.etiquetaMetodo)
            self.previewLayout.addWidget(marcoTotal)
            etiquetaPie = QLabel("<div style='text-align: center; padding: 15px; color: #7f8c8d; font-size: 13px;'>"
                               "¡Gracias por su preferencia!<br>"
                               "CAFEBAR SYSTEM © 2026</div>")
            etiquetaPie.setStyleSheet("font-family: 'Segoe UI';")
            self.previewLayout.addWidget(etiquetaPie)
            self.previewLayout.addStretch()
        except Exception as e:
            import traceback
            detalles_error = traceback.format_exc()
            etiquetaError = QLabel(f"""
                <div style='padding: 30px; text-align: center; background-color: #fee; border-radius: 10px;'>
                    <span style='color: #e74c3c; font-size: 18px; font-weight: 600;'>⚠️ Error al cargar la previsualización</span><br><br>
                    <span style='color: #7f8c8d; font-size: 14px;'>Error: {str(e)}</span><br>
                    <pre style='color: #95a5a6; font-size: 12px; text-align: left;'>{detalles_error}</pre>
                </div>
            """)
            etiquetaError.setStyleSheet("font-family: 'Segoe UI';")
            self.previewLayout.addWidget(etiquetaError)
        finally:
            conn.close()
            
    def abrirPaginaImpuestos(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT enlace FROM Enlace WHERE idEnlace=1""")
            resultado = cursor.fetchone()
            if resultado:
                enlace = resultado[0]
                webbrowser.open(enlace)
            else:
                QMessageBox.information(self, "Información", "No se encontró un enlace configurado")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo acceder al enlace: {str(e)}")
        finally:
            conn.close()
            
    def actualizarCamposPago(self):
        if (self.rbEfectivo is None or self.rbQR is None or 
            self.rbMixto is None or self.txtEfectivo is None or 
            self.txtQR is None):
            return
        try:
            monto_total = float(getattr(self, "total", 0.0))
        except (ValueError, TypeError):
            monto_total = 0.0
    
        if self.rbEfectivo.isChecked():
            self.txtEfectivo.setEnabled(True)
            self.txtQR.setEnabled(False)
            self.txtEfectivo.setText("")
            self.txtQR.setText("0.00")
            self.actualizarMetodoPagoLabel("Efectivo")
    
        elif self.rbQR.isChecked():
            self.txtEfectivo.setEnabled(False)
            self.txtQR.setEnabled(True)
            self.txtEfectivo.setText("0.00")
            self.txtQR.setText("")
            self.actualizarMetodoPagoLabel("QR")
    
        elif self.rbMixto.isChecked():
            self.txtEfectivo.setEnabled(True)
            self.txtQR.setEnabled(True)
            self.txtEfectivo.setText("")
            self.txtQR.setText("")
            self.actualizarMetodoPagoLabel("Mixto (Efectivo + QR)")
    
    def actualizarMetodoPagoLabel(self, metodo):
        if hasattr(self, 'metodoLabel'):
            self.metodoLabel.setText(f"<span style='color: #7f8c8d; font-size: 14px;'>Método: </span><b>{metodo}</b>")
        
    def confirmar(self, fecha, numVenta, idMesa, idSeccion,total):
        if self.rbEfectivo.isChecked():
            pagoEfectivo=round(float(self.txtEfectivo.text()),2)
            if not self.txtEfectivo.text() or  pagoEfectivo!=total:
                QMessageBox.warning(self, "Advertencia", "Ingrese un monto válido para pago en efectivo")
                return
        elif self.rbQR.isChecked():
            pagoQr=round(float(self.txtQR.text()),2)
            if not self.txtQR.text() or  pagoQr!=total:
                QMessageBox.warning(self, "Advertencia", "Ingrese un monto válido para pago con QR")
                return
        elif self.rbMixto.isChecked():
            pago=round(float(self.txtEfectivo.text())+float(self.txtQR.text()),2)
            if (not self.txtEfectivo.text() or not self.txtQR.text() or pago!=total):
                QMessageBox.warning(self, "Advertencia", "Ingrese montos válidos para ambos métodos de pago")
                return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            num_venta = numVenta
            cursor.execute("""SELECT fechaReg FROM Venta WHERE DATE(fechaReg)=? AND numVenta=?""",(fecha,numVenta))
            fechaCompleta = cursor.fetchone()[0]
            
            if self.rbEfectivo.isChecked() or self.rbMixto.isChecked():
                monto_efectivo = float(self.txtEfectivo.text())
                cursor.execute("""INSERT INTO Pago (numVenta,fechaRegVenta, idMetodo, monto) 
                                 VALUES (?,?,1,?)""", (num_venta,fechaCompleta, monto_efectivo))
            
            if self.rbQR.isChecked() or self.rbMixto.isChecked():
                monto_qr = float(self.txtQR.text())
                cursor.execute("""INSERT INTO Pago (numVenta,fechaRegVenta, idMetodo, monto) 
                                 VALUES (?,?,2,?)""", (num_venta,fechaCompleta, monto_qr))
            
            cursor.execute("""UPDATE DetallesVenta 
                           SET estadoDetalleVenta='Finalizado' 
                           WHERE DATE(fechaRegVenta)=? AND numVenta=? AND estadoDetalleVenta='Cobrar'""", 
                           (fecha, num_venta))
            
            cursor.execute("""UPDATE Mesa SET disponible=TRUE WHERE idMesa=? AND idSeccion=?""", (idMesa,idSeccion))
            conn.commit()
            
            QMessageBox.information(self, "Éxito", "Pago registrado correctamente")
            self.paginaCobrarVenta.close()
            self.cargarDatosTabla()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo registrar el pago: {str(e)}")
            conn.rollback()
        finally:
            conn.close()
        
    def actualizarCambio(self):
        try:
            pago = float(self.pago.text()) if self.pago.text() else 0.0
            resto = pago - self.total
            self.cambio.setText(f"{resto:.2f} Bs." if resto >= 0 else f"{-resto:.2f} Bs. (Falta)")
        except ValueError:
            self.cambio.setText("0.00 Bs.")
            
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = CobroPedidos()
    pagina.show()
    sys.exit(app.exec_())