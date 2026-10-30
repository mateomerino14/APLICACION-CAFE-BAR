import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from datetime import datetime
from Impresion import ManejadorImpresion
import webbrowser
from SeguridadUtils import verificar_password
from Rutas import get_db_path

DB_PATH = get_db_path()

class DialogoCobroVenta(QDialog):
    def __init__(self, fecha, numVenta, numMesa, idSeccion, parent=None):
        super().__init__(parent)
        self.fecha = fecha
        self.numVenta = numVenta
        self.numMesa = numMesa
        self.idSeccion = idSeccion
        self.total = 0.0
        self.pago = None
        self.rbEfectivo = None
        self.rbQR = None
        self.rbMixto = None
        self.txtEfectivo = None
        self.txtQR = None
        self.cajero_actual = None
        self.mesero_actual = None
        
        if parent and hasattr(parent, 'campoCajero'):
            self.cajero_actual = parent.campoCajero.text() if parent.campoCajero else None
        if parent and hasattr(parent, 'campoEncargado'):
            self.mesero_actual = parent.campoEncargado.text() if parent.campoEncargado else None
        
        self.setWindowTitle("CAJA")
        self.setFixedSize(1600, 900)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 8px;
            }
            QWidget {
                padding:0px;
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
            QTableWidget {
                background-color: white;
                border: 2px solid #e0e6ed;
                border-radius: 10px;
                gridline-color: #e8edf5;
                font-size: 14px;
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
                text-align: center;
            }
            QPushButton#imprimir {
                background-color: #3498db;
                color: white;
            }
            QPushButton#imprimir:hover {
                background-color: #2980b9;
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
            QPushButton#impuestos {
                background-color: purple;
                color: white;
            }
            QPushButton#impuestos:hover {
                background-color: #8e44ad;
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
        
        self.initUI()
        self.cargarTotal()
        
    def initUI(self):
        layoutPagina = QVBoxLayout()
        layoutPagina.setContentsMargins(20, 20, 20, 20)
        layoutPagina.setSpacing(15)
        self.setLayout(layoutPagina)
        
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
        self.cargarPrevisualizacionFactura()
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
        self.txtEfectivo = QLineEdit("0.00")
        self.txtEfectivo.setValidator(QRegExpValidator(QRegExp("[0-9]+\\.?[0-9]{0,2}")))
        self.txtEfectivo.setEnabled(False)
        self.txtEfectivo.setStyleSheet("font-size: 15px; padding: 8px;")
        
        self.lblQR = QLabel("Monto con QR:")
        self.lblQR.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        self.txtQR = QLineEdit("0.00")
        self.txtQR.setValidator(QRegExpValidator(QRegExp("[0-9]+\\.?[0-9]{0,2}")))
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
        
        etiquetaTotal = QLabel("Total:")
        etiquetaTotal.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; margin-top: 10px;")
        self.totalLabel = QLabel(f"{self.total:.2f} Bs.")
        self.totalLabel.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c; margin-bottom: 15px;")
        
        etiquetaPago = QLabel("Pago:")
        etiquetaPago.setStyleSheet("font-weight: bold; font-size: 15px; color: #2c3e50; margin-top: 10px;")
        self.pago = QLineEdit()
        self.pago.setPlaceholderText(f"{self.total:.2f} Bs.")
        self.pago.setValidator(QRegExpValidator(QRegExp("[0-9]+\\.?[0-9]{0,2}")))
        self.pago.textChanged.connect(self.actualizarCambio)
        self.pago.setStyleSheet("font-size: 15px; padding: 8px;")
        
        etiquetaCambio = QLabel("Cambio:")
        etiquetaCambio.setStyleSheet("font-weight: bold; font-size: 15px; color: #2c3e50; margin-top: 10px;")
        self.cambio = QLabel("0.00 Bs.")
        self.cambio.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
        
        layoutCobro.addWidget(etiquetaTotal)
        layoutCobro.addWidget(self.totalLabel)
        layoutCobro.addWidget(etiquetaPago)
        layoutCobro.addWidget(self.pago)
        layoutCobro.addWidget(etiquetaCambio)
        layoutCobro.addWidget(self.cambio)
        layoutCobro.addLayout(layoutMetodosPago)
        layoutCobro.addStretch(1)
        
        layoutIntermedio.addLayout(layoutCobro, stretch=2)
        
        impuestos = QPushButton("IMPUESTOS")
        impuestos.setObjectName("impuestos")
        impuestos.setFixedHeight(35)
        impuestos.setCursor(QCursor(Qt.PointingHandCursor))
        impuestos.clicked.connect(self.abrirPaginaImpuestos)
        
        confirmar = QPushButton("CONFIRMAR")
        confirmar.setObjectName("confirmar")
        confirmar.setFixedHeight(35)
        confirmar.setCursor(QCursor(Qt.PointingHandCursor))
        confirmar.clicked.connect(self.confirmar)
        
        cancelar = QPushButton("CANCELAR")
        cancelar.setObjectName("cancelar")
        cancelar.setFixedHeight(35)
        cancelar.setCursor(QCursor(Qt.PointingHandCursor))
        cancelar.clicked.connect(self.reject)
        
        imprimir = QPushButton("IMPRIMIR")
        imprimir.setObjectName("imprimir")
        imprimir.setFixedHeight(35)
        imprimir.setCursor(QCursor(Qt.PointingHandCursor))
        imprimir.clicked.connect(lambda: self.imprimir(self.fecha, self.numVenta))
        
        layoutBotones.addWidget(imprimir)
        layoutBotones.addWidget(impuestos)
        layoutBotones.addWidget(confirmar)
        layoutBotones.addWidget(cancelar)
        
    def cargarTotal(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT totalVenta FROM Venta WHERE DATE(fechaReg)=? AND numVenta=?", 
                         (self.fecha, self.numVenta))
            resultados = cursor.fetchall()
            for elemento in resultados:
                self.total += float(elemento[0])
            self.totalLabel.setText(f"{self.total:.2f} Bs.")
            self.pago.setPlaceholderText(f"{self.total:.2f} Bs.")
            self.actualizarCamposPago()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al calcular total: {str(e)}")
        finally:
            conn.close()
            
    def actualizarCamposPago(self):
        if self.rbEfectivo.isChecked():
            self.txtEfectivo.setEnabled(True)
            self.txtQR.setEnabled(False)
            self.txtEfectivo.setText(f"{self.total:.2f}")
            self.txtQR.setText("0.00")
        elif self.rbQR.isChecked():
            self.txtEfectivo.setEnabled(False)
            self.txtQR.setEnabled(True)
            self.txtEfectivo.setText("0.00")
            self.txtQR.setText(f"{self.total:.2f}")
        elif self.rbMixto.isChecked():
            self.txtEfectivo.setEnabled(True)
            self.txtQR.setEnabled(True)
            self.txtEfectivo.clear()
            self.txtQR.clear()
            self.txtEfectivo.setPlaceholderText(f"Sugerido: {self.total/2:.2f}")
            self.txtQR.setPlaceholderText(f"Sugerido: {self.total/2:.2f}")
            
    def actualizarCambio(self):
        try:
            pago = float(self.pago.text()) if self.pago.text() else 0.0
            resto = pago - self.total
            if resto >= 0:
                self.cambio.setText(f"{resto:.2f} Bs.")
            else:
                self.cambio.setText(f"{-resto:.2f} Bs. (Falta)")
        except ValueError:
            self.cambio.setText("0.00 Bs.")
            
    def cargarPrevisualizacionFactura(self):
        while self.previewLayout.count():
            item = self.previewLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT nombSeccion FROM Seccion WHERE idSeccion=?", (self.idSeccion,))
            nombre_seccion = cursor.fetchone()[0]

            cursor.execute("""
                SELECT DV.cantidadProdDet, P.nomProd, P.precioVenta, DV.subtotal, DV.tipoConsumo, DV.idProd, DV.idDetalleVenta
                FROM DetallesVenta DV
                INNER JOIN Producto P ON DV.idProd = P.idProd
                WHERE strftime('%Y-%m-%d', DV.fechaRegVenta)=?
                  AND DV.numVenta=?
                  AND DV.idProd IS NOT NULL
                ORDER BY DV.tipoConsumo, P.nomProd
            """, (self.fecha, self.numVenta))
            productos_sin_procesar_raw = cursor.fetchall()

            productos_sin_procesar = []
            for cantidad, nombre, precio, subtotal, tipo, id_prod, id_det in productos_sin_procesar_raw:
                cursor.execute("SELECT nomIng FROM DetallesVentaExclusiones WHERE idDetalleVenta=?", (id_det,))
                excl_rows = cursor.fetchall()
                excl_texto = ("sin " + ", ".join(sorted(r[0] for r in excl_rows))) if excl_rows else ""
                cursor.execute("SELECT nomIng, cantidadExtra FROM DetallesVentaExtras WHERE idDetalleVenta=?", (id_det,))
                extra_rows = cursor.fetchall()
                extra_texto = ("extra " + ", ".join(f"+{c} {n}" for n, c in extra_rows)) if extra_rows else ""
                personalizacion = " | ".join(t for t in [excl_texto, extra_texto] if t)
                productos_sin_procesar.append((cantidad, nombre, precio, subtotal, tipo, id_prod, personalizacion, id_det))

            cursor.execute("""
                SELECT DV.cantidadProdDet, PR.nomProm, PR.precioProm, DV.subtotal, DV.tipoConsumo, DV.idProm, DV.idDetalleVenta
                FROM DetallesVenta DV
                INNER JOIN Promocion PR ON DV.idProm = PR.idProm
                WHERE strftime('%Y-%m-%d', DV.fechaRegVenta)=?
                  AND DV.numVenta=?
                  AND DV.idProm IS NOT NULL
                ORDER BY DV.tipoConsumo, PR.nomProm
            """, (self.fecha, self.numVenta))
            promociones_sin_procesar_raw = cursor.fetchall()

            promociones_sin_procesar = []
            for cantidad, nombre, precio, subtotal, tipo, id_prom, id_det in promociones_sin_procesar_raw:
                cursor.execute("SELECT nomIng FROM DetallesVentaExclusionesPromo WHERE idDetalleVenta=?", (id_det,))
                excl_rows = cursor.fetchall()
                cursor.execute("SELECT nomIng, cantidadExtra FROM DetallesVentaExtras WHERE idDetalleVenta=? AND idProd IS NOT NULL", (id_det,))
                extra_rows = cursor.fetchall()
                partes = []
                if excl_rows:
                    nombres_excl = sorted(set(r[0] for r in excl_rows))
                    partes.append("sin " + ", ".join(nombres_excl))
                if extra_rows:
                    textos_extra = [f"+{c} {n}" for n, c in extra_rows]
                    partes.append("extra " + ", ".join(textos_extra))
                personalizacion_promo = " | ".join(partes)
                promociones_sin_procesar.append((cantidad, nombre, precio, subtotal, tipo, id_prom, personalizacion_promo, id_det))

            def agrupar_items(items_sin_procesar, es_promocion=False):
                if not items_sin_procesar:
                    return []
                items_agrupados = {}
                for cantidad, nombre, precio, subtotal, tipo, id_item, personalizacion, id_det in items_sin_procesar:
                    if nombre is None:
                        continue
                    cantidad = cantidad if cantidad is not None else 0
                    precio = precio if precio is not None else 0.0
                    subtotal = subtotal if subtotal is not None else 0.0
                    clave = (nombre, precio, tipo, es_promocion, personalizacion)
                    if clave in items_agrupados:
                        items_agrupados[clave]['cantidad'] += cantidad
                        items_agrupados[clave]['subtotal'] += subtotal
                        items_agrupados[clave]['ids_det'].append(id_det)
                    else:
                        items_agrupados[clave] = {
                            'cantidad': cantidad,
                            'nombre': nombre,
                            'precio': precio,
                            'subtotal': subtotal,
                            'tipo': tipo,
                            'id_item': id_item,
                            'es_promocion': es_promocion,
                            'personalizacion': personalizacion,
                            'ids_det': [id_det]
                        }
                return [
                    (g['cantidad'], g['nombre'], g['precio'], g['subtotal'], g['tipo'], g['id_item'], g['es_promocion'], g['personalizacion'], g['ids_det'])
                    for g in items_agrupados.values()
                ]

            productos = agrupar_items(productos_sin_procesar, es_promocion=False)
            promociones = agrupar_items(promociones_sin_procesar, es_promocion=True)

            productos_local = [p for p in productos if p[4] == 'Local']
            productos_llevar = [p for p in productos if p[4] == 'Para llevar']
            promociones_local = [p for p in promociones if p[4] == 'Local']
            promociones_llevar = [p for p in promociones if p[4] == 'Para llevar']

            cursor.execute("""SELECT MAX(fechaRegDetalleVenta) FROM DetallesVenta
                           WHERE strftime('%Y-%m-%d', fechaRegVenta)=? AND numVenta=?""", (self.fecha, self.numVenta))
            fecha_hora = cursor.fetchone()[0]
            if fecha_hora:
                try:
                    hora_registro = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S.%f").strftime("%I:%M %p")
                except Exception:
                    hora_registro = "Hora no disponible"
            else:
                hora_registro = "No disponible"

            fecha_objeto = datetime.strptime(self.fecha, "%Y-%m-%d")
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

            etiquetaInfoVenta = QLabel(f"<div style='font-size: 24px; font-weight: 700; text-align: center;'>FACTURA #{self.numVenta}</div>")
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
            cuadriculaInfo.addWidget(crear_etiqueta_info("📍 MESA", str(self.numMesa)), 1, 0)
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

            secciones_agregadas = False

            if productos_local:
                widget = self._crearSeccionProducto("PRODUCTOS", productos_local, "#27ae60", "🏠", "Local", False)
                if widget:
                    self.previewLayout.addWidget(widget)
                    self.previewLayout.addSpacing(15)
                    secciones_agregadas = True

            if productos_llevar:
                widget = self._crearSeccionProducto("PRODUCTOS", productos_llevar, "#27ae60", "🥡", "Para llevar", False)
                if widget:
                    self.previewLayout.addWidget(widget)
                    self.previewLayout.addSpacing(15)
                    secciones_agregadas = True

            if promociones_local:
                widget = self._crearSeccionProducto("PROMOCIONES", promociones_local, "#27ae60", "🎁", "Local", True)
                if widget:
                    self.previewLayout.addWidget(widget)
                    self.previewLayout.addSpacing(15)
                    secciones_agregadas = True

            if promociones_llevar:
                widget = self._crearSeccionProducto("PROMOCIONES", promociones_llevar, "#27ae60", "🎁", "Para llevar", True)
                if widget:
                    self.previewLayout.addWidget(widget)
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

            cursor.execute("SELECT totalVenta FROM Venta WHERE strftime('%Y-%m-%d', fechaReg)=? AND numVenta=?", (self.fecha, self.numVenta))
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

            self.etiquetaMetodo = QLabel("<span style='color: #7f8c8d; font-size: 14px;'>Método: </span><b>Efectivo</b>")
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
            
    def _crearSeccionProducto(self, titulo, productos_lista, color, icono, tipo=None, es_promocion=False):
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
        
        for columna in range(4):
            item_encabezado = tabla.horizontalHeaderItem(columna)
            if item_encabezado:
                item_encabezado.setTextAlignment(Qt.AlignCenter)
                
        tabla.setRowCount(len(productos_lista))
        subtotal_seccion = 0
        datos_por_fila = {}

        for i, (cantidad, nombre, precio, subtotal, tipo_consumo, id_item, es_promocion_flag, personalizacion, ids_det) in enumerate(productos_lista):
            cantidad = cantidad if cantidad is not None else 0
            precio = precio if precio is not None else 0.0
            subtotal = subtotal if subtotal is not None else 0.0
            datos_por_fila[i] = {
                'nombre': nombre,
                'tipo': tipo_consumo,
                'es_promocion': es_promocion_flag,
                'personalizacion': personalizacion,
                'ids_det': ids_det,
                'cantidad': cantidad
            }
            
            item_cantidad = QTableWidgetItem(str(cantidad))
            item_cantidad.setTextAlignment(Qt.AlignCenter)
            item_cantidad.setFont(QFont("Segoe UI", 12))
            tabla.setItem(i, 0, item_cantidad)
            
            item_nombre = QTableWidgetItem(str(nombre))
            item_nombre.setTextAlignment(Qt.AlignCenter)
            if personalizacion:
                fuente_nombre = QFont("Segoe UI", 12)
                fuente_nombre.setUnderline(True)
                item_nombre.setFont(fuente_nombre)
                item_nombre.setForeground(QColor("#2980b9"))
                item_nombre.setToolTip("🖱 Haga clic para ver el detalle de la personalización")
            else:
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

        def al_hacer_clic(fila, columna):
            if columna != 1:
                return
            datos = datos_por_fila.get(fila)
            if not datos or not datos['personalizacion']:
                return
            self.mostrarDetallePersonalizacionCobro(
                datos['nombre'], datos['tipo'], datos['es_promocion'], datos['ids_det'], datos['cantidad']
            )

        tabla.cellClicked.connect(al_hacer_clic)
            
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

    def mostrarDetallePersonalizacionCobro(self, nombre, tipo, es_promocion, ids_det, cantidad_total=0):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        dialog = QDialog(self)
        dialog.setWindowTitle("Detalle de personalización")
        dialog.setMinimumWidth(440)
        dialog.setMaximumWidth(560)
        dialog.setStyleSheet("""
            QDialog { background-color: white; font-family: 'Segoe UI', Arial, sans-serif; }
            QLabel { color: #2c3e50; font-size: 14px; background: transparent; }
        """)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setStyleSheet("QWidget { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2980b9); }")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 20)
        titulo = QLabel(nombre)
        titulo.setStyleSheet("QLabel { color: white; font-size: 19px; font-weight: bold; background: transparent; }")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setWordWrap(True)
        header_layout.addWidget(titulo)
        subtitulo = QLabel("Promoción" if es_promocion else "Producto")
        subtitulo.setStyleSheet("QLabel { color: rgba(255,255,255,0.9); font-size: 13px; font-weight: 500; background: transparent; }")
        subtitulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitulo)
        layout.addWidget(header)

        cuerpo = QWidget()
        cuerpo_layout = QVBoxLayout(cuerpo)
        cuerpo_layout.setContentsMargins(24, 20, 24, 20)
        cuerpo_layout.setSpacing(10)

        def bloque_personalizacion(titulo_texto, texto, color_fondo, color_texto, color_borde):
            titulo_lbl = QLabel(titulo_texto)
            titulo_lbl.setStyleSheet(f"font-weight: bold; color: {color_texto}; font-size: 14px; margin-top: 4px;")
            cuerpo_layout.addWidget(titulo_lbl)
            contenido_lbl = QLabel(texto)
            contenido_lbl.setWordWrap(True)
            contenido_lbl.setStyleSheet(f"""
                color: {color_texto}; font-size: 14px; font-weight: 500;
                padding: 8px 12px; background-color: {color_fondo};
                border-radius: 6px; border-left: 4px solid {color_borde};
            """)
            cuerpo_layout.addWidget(contenido_lbl)

        if es_promocion:
            cursor.execute("SELECT idProm FROM Promocion WHERE nomProm=?", (nombre,))
            fila_prom = cursor.fetchone()
            id_prom = fila_prom[0] if fila_prom else None
            cursor.execute("""
                SELECT p.idProd, p.nomProd, pp.cantidadProdProm FROM PromocionProd pp
                JOIN Producto p ON pp.idProd = p.idProd WHERE pp.idProm=?
            """, (id_prom,))
            info_productos = cursor.fetchall()
            nombres_por_id = {pid: pnom for pid, pnom, _ in info_productos}
            cant_por_combo = {pid: cant for pid, _, cant in info_productos}

            excl_por_producto_unidad = {}
            extra_por_producto_unidad = {}
            for id_det in ids_det:
                cursor.execute("SELECT idProd, numUnidad, nomIng FROM DetallesVentaExclusionesPromo WHERE idDetalleVenta=?", (id_det,))
                for id_prod, num_unidad, nom_ing in cursor.fetchall():
                    excl_por_producto_unidad.setdefault(id_prod, {}).setdefault(num_unidad, []).append(nom_ing)
                cursor.execute("SELECT idProd, numUnidad, nomIng, cantidadExtra FROM DetallesVentaExtras WHERE idDetalleVenta=? AND idProd IS NOT NULL", (id_det,))
                for id_prod, num_unidad, nom_ing, cant_extra in cursor.fetchall():
                    extra_por_producto_unidad.setdefault(id_prod, {}).setdefault(num_unidad, []).append((nom_ing, cant_extra))

            ids_con_personalizacion = sorted(
                set(excl_por_producto_unidad.keys()) | set(extra_por_producto_unidad.keys()),
                key=lambda x: nombres_por_id.get(x, str(x))
            )

            if not ids_con_personalizacion:
                lbl_vacio = QLabel("Sin personalización — todos los productos de la promoción están con sus ingredientes originales")
                lbl_vacio.setWordWrap(True)
                lbl_vacio.setStyleSheet("""
                    color: #27ae60; font-size: 14px; font-weight: 500; padding: 8px 12px;
                    background-color: #eafaf1; border-radius: 6px; border-left: 4px solid #2ecc71;
                """)
                cuerpo_layout.addWidget(lbl_vacio)
            else:
                titulo_seccion = QLabel("Detalle por producto:")
                titulo_seccion.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50; margin-top: 4px;")
                cuerpo_layout.addWidget(titulo_seccion)
                for id_prod in ids_con_personalizacion:
                    nombre_prod = nombres_por_id.get(id_prod, f"Producto {id_prod}")
                    unidades_excl = excl_por_producto_unidad.get(id_prod, {})
                    unidades_extra = extra_por_producto_unidad.get(id_prod, {})
                    todas_unidades_idx = set(unidades_excl.keys()) | set(unidades_extra.keys())

                    conteo_combos = {}
                    for num_unidad in todas_unidades_idx:
                        sin_texto = ", ".join(sorted(unidades_excl.get(num_unidad, []))) if unidades_excl.get(num_unidad) else ""
                        extra_texto = ", ".join(f"+{c} {n}" for n, c in unidades_extra.get(num_unidad, [])) if unidades_extra.get(num_unidad) else ""
                        clave_combo = (sin_texto, extra_texto)
                        conteo_combos[clave_combo] = conteo_combos.get(clave_combo, 0) + 1

                    total_prod = cant_por_combo.get(id_prod, 0) * cantidad_total
                    con_personalizacion = len(todas_unidades_idx)
                    sin_personalizacion = total_prod - con_personalizacion

                    prod_frame = QFrame()
                    prod_frame.setStyleSheet("QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; }")
                    prod_layout = QVBoxLayout(prod_frame)
                    prod_layout.setContentsMargins(12, 10, 12, 10)
                    prod_layout.setSpacing(6)
                    prod_titulo = QLabel(f"🍔 {nombre_prod}")
                    prod_titulo.setStyleSheet("font-weight: bold; font-size: 15px; color: #2c3e50; background: transparent; border: none;")
                    prod_layout.addWidget(prod_titulo)

                    for (sin_texto, extra_texto), cant in sorted(conteo_combos.items(), key=lambda kv: -kv[1]):
                        partes_linea = []
                        if sin_texto:
                            partes_linea.append(f"Sin: {sin_texto}")
                        if extra_texto:
                            partes_linea.append(f"Extra: {extra_texto}")
                        texto_linea = f"{cant} unidad(es) — " + "  |  ".join(partes_linea)
                        color_txt = "#c0392b" if sin_texto and not extra_texto else ("#27ae60" if extra_texto and not sin_texto else "#8e44ad")
                        lbl = QLabel(texto_linea)
                        lbl.setWordWrap(True)
                        lbl.setStyleSheet(f"color: {color_txt}; font-size: 14px; font-weight: 600; background: transparent; border: none; padding-left: 12px;")
                        prod_layout.addWidget(lbl)

                    if sin_personalizacion > 0:
                        lbl_resto = QLabel(f"{sin_personalizacion} unidad(es) — sin ninguna personalización")
                        lbl_resto.setWordWrap(True)
                        lbl_resto.setStyleSheet("color: #7f8c8d; font-size: 13px; font-style: italic; background: transparent; border: none; padding-left: 12px;")
                        prod_layout.addWidget(lbl_resto)

                    cuerpo_layout.addWidget(prod_frame)
        else:
            excl_por_unidad = {}
            extra_por_unidad = {}
            for i, id_det in enumerate(ids_det):
                cursor.execute("SELECT nomIng FROM DetallesVentaExclusiones WHERE idDetalleVenta=?", (id_det,))
                excl_nombres = sorted(r[0] for r in cursor.fetchall())
                cursor.execute("SELECT nomIng, cantidadExtra FROM DetallesVentaExtras WHERE idDetalleVenta=?", (id_det,))
                extra_lista = cursor.fetchall()
                excl_por_unidad[i] = ", ".join(excl_nombres)
                extra_por_unidad[i] = ", ".join(f"+{c} {n}" for n, c in extra_lista)

            conteo_combos = {}
            for i in range(len(ids_det)):
                clave_combo = (excl_por_unidad[i], extra_por_unidad[i])
                conteo_combos[clave_combo] = conteo_combos.get(clave_combo, 0) + 1

            hay_personalizacion = any(sin or extra for sin, extra in conteo_combos.keys())
            if not hay_personalizacion:
                lbl_vacio = QLabel("Sin personalización — todos los ingredientes originales")
                lbl_vacio.setWordWrap(True)
                lbl_vacio.setStyleSheet("""
                    color: #27ae60; font-size: 14px; font-weight: 500; padding: 8px 12px;
                    background-color: #eafaf1; border-radius: 6px; border-left: 4px solid #2ecc71;
                """)
                cuerpo_layout.addWidget(lbl_vacio)
            else:
                for (sin_texto, extra_texto), cant in sorted(conteo_combos.items(), key=lambda kv: -kv[1]):
                    if not sin_texto and not extra_texto:
                        continue
                    if sin_texto:
                        bloque_personalizacion(f"{cant} unidad(es) — Sin:", sin_texto, "#fdecea", "#c0392b", "#e74c3c")
                    if extra_texto:
                        bloque_personalizacion(f"{cant} unidad(es) — Extra:", extra_texto, "#eafaf1", "#27ae60", "#2ecc71")

        scroll_cuerpo = QScrollArea()
        scroll_cuerpo.setWidgetResizable(True)
        scroll_cuerpo.setMaximumHeight(420)
        scroll_cuerpo.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_cuerpo.setWidget(cuerpo)
        layout.addWidget(scroll_cuerpo)

        footer = QWidget()
        footer.setStyleSheet("QWidget { background-color: #f8f9fa; border-top: 1px solid #e2e8f0; }")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 14, 20, 14)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setCursor(Qt.PointingHandCursor)
        btn_cerrar.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border: none; border-radius: 8px;
                font-size: 14px; font-weight: bold; padding: 10px 20px; min-width: 100px; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        btn_cerrar.clicked.connect(dialog.accept)
        footer_layout.addStretch()
        footer_layout.addWidget(btn_cerrar)
        layout.addWidget(footer)

        conn.close()
        dialog.exec_()

    def verificar_contraseña_usuario(self, usuario):
        dialog = QDialog(self)
        dialog.setWindowTitle("Autorizacion requerida")
        dialog.setFixedWidth(480)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        lock_icon = QLabel("🔒")
        lock_icon.setStyleSheet("""
            QLabel {
                font-size: 48px;
                color: #f39c12;
                background: transparent;
                padding: 5px;
            }
        """)
        lock_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(lock_icon)
        
        label = QLabel(f"Se ha excedido el limite de 2 impresiones.\nIngrese la contrasena de {usuario}:")
        label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        password_container = QWidget()
        password_container.setStyleSheet("background: transparent;")
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(4)
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setMinimumHeight(40)
        password_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 2px 10px;
                font-size: 14px;
                selection-background-color: #4a89dc;
            }
            QLineEdit:focus {
                border: 2px solid #4a89dc;
                background-color: #f8fafc;
            }
        """)
        password_layout.addWidget(password_input)
        
        toggle_password_btn = QPushButton()
        toggle_password_btn.setFixedHeight(45)
        toggle_password_btn.setFixedWidth(29)
        toggle_password_btn.setCheckable(True)
        toggle_password_btn.setCursor(Qt.PointingHandCursor)
        toggle_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin: 0px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #e6f2ff;
                border: 2px solid #4a89dc;
            }
            QPushButton:checked {
                background-color: #e6f2ff;
                border: 2px solid #4a89dc;
            }
        """)
        toggle_password_btn.setText("👁")
        toggle_password_btn.setFont(QFont("Segoe UI", 15))

        def toggle_password_visibility(checked):
            if checked:
                password_input.setEchoMode(QLineEdit.Normal)
                toggle_password_btn.setText("🙈")
            else:
                password_input.setEchoMode(QLineEdit.Password)
                toggle_password_btn.setText("👁")

        toggle_password_btn.toggled.connect(toggle_password_visibility)
        password_layout.addWidget(toggle_password_btn)
        layout.addWidget(password_container)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        for button in button_box.buttons():
            text = button.text().lower()
            if 'ok' in text or 'aceptar' in text:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border-radius: 6px;
                        padding: 10px 24px;
                        font-weight: 600;
                        font-size: 14px;
                        min-width: 100px;
                        margin-right: 10px;
                    }
                    QPushButton:hover { background-color: #27ae60; }
                """)
            elif 'cancelar' in text or 'cancel' in text:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border-radius: 6px;
                        padding: 10px 24px;
                        font-weight: 600;
                        font-size: 14px;
                        min-width: 100px;
                        margin-left: 10px;
                    }
                    QPushButton:hover { background-color: #c0392b; }
                """)
        layout.addWidget(button_box, alignment=Qt.AlignCenter)
        password_input.setFocus()
        password_input.returnPressed.connect(dialog.accept)
        if dialog.exec_() == QDialog.Accepted:
            clave = password_input.text()
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            if usuario == "DIRECTORIO":
                cur.execute("SELECT contrasenaAdmin FROM Directorio")
                resultado = cur.fetchone()
                existe = resultado and verificar_password(clave, resultado[0])
            else:
                cur.execute("SELECT contEmp FROM Empleado WHERE aliasEmp = ?", (usuario,))
                resultado = cur.fetchone()
                existe = resultado and verificar_password(clave, resultado[0])
            conn.close()
            if existe:
                return True
            else:
                QMessageBox.warning(self, "Error", "Contrasena incorrecta.")
                return False
        return False
        
    def _obtenerPersonalizacionParaTicket(self, cursor, id_det, id_prod, id_prom):
        if id_prod:
            cursor.execute("SELECT nomIng FROM DetallesVentaExclusiones WHERE idDetalleVenta=?", (id_det,))
            excl = cursor.fetchall()
            cursor.execute("""
                SELECT nomIng, cantidadExtra FROM DetallesVentaExtras
                WHERE idDetalleVenta=? AND idProd IS NULL
            """, (id_det,))
            extra = cursor.fetchall()
            partes = []
            if excl:
                partes.append("sin: " + ", ".join(sorted(r[0] for r in excl)))
            if extra:
                partes.append("extra: " + ", ".join(f"+{c} {n}" for n, c in extra))
            return " | ".join(partes)
        elif id_prom:
            cursor.execute("SELECT idProd, numUnidad, nomIng FROM DetallesVentaExclusionesPromo WHERE idDetalleVenta=?", (id_det,))
            excl_por_producto_unidad = {}
            for id_p, num_unidad, nom_ing in cursor.fetchall():
                excl_por_producto_unidad.setdefault(id_p, {}).setdefault(num_unidad, []).append(nom_ing)

            cursor.execute("""
                SELECT idProd, numUnidad, nomIng, cantidadExtra FROM DetallesVentaExtras
                WHERE idDetalleVenta=? AND idProd IS NOT NULL
            """, (id_det,))
            extra_por_producto_unidad = {}
            for id_p, num_unidad, nom_ing, cant_extra in cursor.fetchall():
                extra_por_producto_unidad.setdefault(id_p, {}).setdefault(num_unidad, []).append((nom_ing, cant_extra))

            ids_con_personalizacion = set(excl_por_producto_unidad.keys()) | set(extra_por_producto_unidad.keys())
            if not ids_con_personalizacion:
                return ""

            nombres_por_id = {}
            for id_p in ids_con_personalizacion:
                cursor.execute("SELECT nomProd FROM Producto WHERE idProd=?", (id_p,))
                fila = cursor.fetchone()
                nombres_por_id[id_p] = fila[0] if fila else str(id_p)

            partes = []
            for id_p in ids_con_personalizacion:
                nombre_prod = nombres_por_id[id_p]
                unidades_excl = excl_por_producto_unidad.get(id_p, {})
                unidades_extra = extra_por_producto_unidad.get(id_p, {})
                todas_unidades_idx = set(unidades_excl.keys()) | set(unidades_extra.keys())
                for num_unidad in todas_unidades_idx:
                    if num_unidad in unidades_excl:
                        nombres_excl = ", ".join(unidades_excl[num_unidad])
                        partes.append(f"U{num_unidad + 1} {nombre_prod}: sin {nombres_excl}")
                    if num_unidad in unidades_extra:
                        nombres_extra = ", ".join(f"+{c} {n}" for n, c in unidades_extra[num_unidad])
                        partes.append(f"U{num_unidad + 1} {nombre_prod}: extra {nombres_extra}")
            return " | ".join(partes)
        return ""

    def imprimir(self, fecha, numVenta):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""SELECT V.numVenta, V.idMesa, S.nombSeccion, E1.nomEmp AS empleado, E2.nomEmp AS cajero 
                            FROM Venta V
                            INNER JOIN Empleado E1 ON V.codEmp = E1.codEmp
                            INNER JOIN Empleado E2 ON V.codEmp2 = E2.codEmp
                            INNER JOIN Seccion S ON S.idSeccion = V.idSeccion
                            WHERE DATE(V.fechaReg) = DATE(?) AND V.numVenta = ?""", (fecha, numVenta))
        resultadosVenta = self.cursor.fetchone()
        
        if not resultadosVenta:
            self.cursor.execute("""SELECT V.numVenta, V.idMesa, S.nombSeccion, E1.nomEmp AS empleado, 'Sin Cajero' AS cajero 
                                FROM Venta V
                                INNER JOIN Empleado E1 ON V.codEmp = E1.codEmp
                                INNER JOIN Seccion S ON S.idSeccion = V.idSeccion
                                WHERE DATE(V.fechaReg) = DATE(?) AND V.numVenta = ?""", (fecha, numVenta))
            resultadosVenta = self.cursor.fetchone()

        if not resultadosVenta:
            self.cursor.close()
            self.conn.close()
            return

        self.cursor.execute("""
            SELECT idDetalleVenta, cantidadProdDet, tipoConsumo, subtotal,
                CASE 
                    WHEN idProd IS NOT NULL THEN (SELECT nomProd FROM Producto WHERE idProd = D.idProd)
                    ELSE (SELECT nomProm FROM Promocion WHERE idProm = D.idProm)
                END as nombre
            FROM DetallesVenta D
            WHERE D.numVenta = ? AND DATE(D.fechaRegVenta) = DATE(?)
        """, (numVenta, fecha))
        
        detallesVenta = self.cursor.fetchall()
        
        items_agrupados = {}
        for id_detalle, cantidad, tipo, subtotal_real, nombre in detallesVenta:
            if nombre is None:
                continue
            cantidad = int(cantidad) if cantidad else 0
            subtotal_real = float(subtotal_real) if subtotal_real else 0.0
            
            precio_unitario = subtotal_real / cantidad if cantidad > 0 else 0.0
            
            clave = (nombre, tipo)
            if clave in items_agrupados:
                items_agrupados[clave]['cantidad'] += cantidad
                items_agrupados[clave]['subtotal'] += subtotal_real
                total_cant = items_agrupados[clave]['cantidad']
                items_agrupados[clave]['precio'] = items_agrupados[clave]['subtotal'] / total_cant if total_cant > 0 else 0.0
            else:
                items_agrupados[clave] = {
                    'cantidad': cantidad,
                    'producto': nombre,
                    'tipo': tipo,
                    'precio': precio_unitario,
                    'subtotal': subtotal_real
                }
        
        self.cursor.close()
        self.conn.close()
        
        items = list(items_agrupados.values())
        
        impresion = ManejadorImpresion()
        datosVenta = {
            'num_venta': str(resultadosVenta[0]),
            'mesa': str(resultadosVenta[1]),
            'seccion': str(resultadosVenta[2]),
            'empleado': str(resultadosVenta[3]),
            'cajero': str(resultadosVenta[4])
        }
        impresion.imprimir_ticket(datosVenta, items)
        
    def abrirPaginaImpuestos(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT enlace FROM Enlace WHERE idEnlace=1")
            resultado = cursor.fetchone()
            if resultado:
                webbrowser.open(resultado[0])
            else:
                QMessageBox.information(self, "Información", "No se encontró un enlace configurado")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo acceder al enlace: {str(e)}")
        finally:
            conn.close()
            
    def confirmar(self):
        if self.rbMixto.isChecked():
            efectivo_text = self.txtEfectivo.text().strip()
            qr_text = self.txtQR.text().strip()
            
            if not efectivo_text or not qr_text:
                QMessageBox.warning(self, "Advertencia", "Complete ambos montos para pago mixto")
                return
                
            try:
                pagoEfectivo = round(float(efectivo_text), 2)
                pagoQr = round(float(qr_text), 2)
                pagoTotal = pagoEfectivo + pagoQr
                
                if abs(pagoTotal - self.total) > 0.01:
                    QMessageBox.warning(self, "Advertencia", 
                                       f"La suma de los montos ({pagoTotal:.2f}) no coincide con el total ({self.total:.2f})")
                    return
            except ValueError:
                QMessageBox.warning(self, "Advertencia", "Ingrese montos válidos")
                return
                
        elif self.rbEfectivo.isChecked():
            try:
                pagoEfectivo = round(float(self.txtEfectivo.text()), 2)
                if abs(pagoEfectivo - self.total) > 0.01:
                    QMessageBox.warning(self, "Advertencia", "El monto en efectivo debe ser igual al total")
                    return
            except ValueError:
                QMessageBox.warning(self, "Advertencia", "Ingrese un monto válido")
                return
                
        elif self.rbQR.isChecked():
            try:
                pagoQr = round(float(self.txtQR.text()), 2)
                if abs(pagoQr - self.total) > 0.01:
                    QMessageBox.warning(self, "Advertencia", "El monto con QR debe ser igual al total")
                    return
            except ValueError:
                QMessageBox.warning(self, "Advertencia", "Ingrese un monto válido")
                return
                
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT fechaReg FROM Venta WHERE DATE(fechaReg)=? AND numVenta=?", (self.fecha, self.numVenta))
            fechaCompleta = cursor.fetchone()[0]
            
            if self.rbEfectivo.isChecked() or self.rbMixto.isChecked():
                monto_efectivo = float(self.txtEfectivo.text())
                cursor.execute("INSERT INTO Pago (numVenta, fechaRegVenta, idMetodo, monto) VALUES (?,?,1,?)",
                             (self.numVenta, fechaCompleta, monto_efectivo))
            
            if self.rbQR.isChecked() or self.rbMixto.isChecked():
                monto_qr = float(self.txtQR.text())
                cursor.execute("INSERT INTO Pago (numVenta, fechaRegVenta, idMetodo, monto) VALUES (?,?,2,?)",
                             (self.numVenta, fechaCompleta, monto_qr))
            
            cursor.execute("UPDATE DetallesVenta SET estadoDetalleVenta='Finalizado' WHERE DATE(fechaRegVenta)=? AND numVenta=? AND estadoDetalleVenta='Cobrar'", 
                         (self.fecha, self.numVenta))
            
            cursor.execute("UPDATE Mesa SET disponible=TRUE WHERE idMesa=? AND idSeccion=?", 
                         (self.numMesa, self.idSeccion))

            cursor.execute("""
                UPDATE Venta SET horaCierre = DATETIME('now','localtime')
                WHERE numVenta=? AND fechaReg=?
            """, (self.numVenta, fechaCompleta))
                         
            conn.commit()
            QMessageBox.information(self, "Éxito", "Pago registrado correctamente")
            self.accept()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo registrar el pago: {str(e)}")
        finally:
            conn.close()
    
    def _imprimir_en_consola_ticket(self, datos_venta, items):
        from datetime import datetime
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%I:%M %p")
        lineas = []
        lineas.append("=" * 44)
        lineas.append(f"{'CAFEBAR RESTAURANTE':^44}")
        lineas.append("=" * 44)
        lineas.append(f"Fecha: {fecha}  Hora: {hora}")
        lineas.append(f"Nro. Venta: {datos_venta.get('num_venta', '')}")
        lineas.append(f"Mesa: {datos_venta.get('mesa', '')} - {datos_venta.get('seccion', '')}")
        lineas.append(f"Mesero: {datos_venta.get('empleado', '')}")
        lineas.append(f"Cajero: {datos_venta.get('cajero', '')}")
        lineas.append("-" * 44)
        grupos = {}
        for item in items:
            producto = str(item.get('producto', ''))
            tipo = item.get('tipo', 'Local')
            precio = float(item.get('precio', 0))
            cantidad = int(item.get('cantidad', 1))
            subtotal = float(item.get('subtotal', cantidad * precio))
            personalizacion = str(item.get('exclusiones', '') or '')
            clave = (producto, tipo, personalizacion)
            if clave in grupos:
                grupos[clave]['cantidad'] += cantidad
                grupos[clave]['subtotal'] += subtotal
            else:
                grupos[clave] = {
                    'producto': producto,
                    'tipo': tipo,
                    'precio': precio,
                    'cantidad': cantidad,
                    'subtotal': subtotal,
                    'personalizacion': personalizacion
                }
        total_general = 0
        lineas.append(f"{'CANT':<5}{'DESCRIPCION':<22}{'T':<3}{'SUBTOTAL':>14}")
        lineas.append("-" * 44)
        for g in grupos.values():
            prod = g['producto']
            if len(prod) > 19:
                prod = prod[:16] + "..."
            tipo_cod = "L" if g['tipo'] == 'Local' else "LL"
            total_general += g['subtotal']
            lineas.append(f"{g['cantidad']:<5}{prod:<22}{tipo_cod:<3}{g['subtotal']:>14.2f}")
            if g['personalizacion']:
                for parte in g['personalizacion'].split('|'):
                    parte = parte.strip()
                    if parte:
                        lineas.append(f"     {parte}")
        lineas.append("=" * 44)
        lineas.append(f"{'TOTAL:':>30}{total_general:>14.2f} Bs")
        lineas.append("=" * 44)
        print("\n".join(lineas))