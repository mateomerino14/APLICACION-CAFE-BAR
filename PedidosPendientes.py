import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from datetime import datetime, timedelta

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'database', 'cafebar.db')

DB_PATH = get_db_path()

class PedidosPendientes(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QMainWindow {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
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
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                background-color: #f8fafc;
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
        self.dialog_activo = None
        self.set_up()
        
    def set_up(self):
        self.layoutDatos = QHBoxLayout()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20,20,20,20)
        self.iniciarPagina()
        self.temporizador=QTimer()
        self.temporizador.timeout.connect(self.actualizarTiempos)
        self.temporizador.start(500)
        self.showMaximized()
        
    def iniciarPagina(self):
        self.tablaVentas = QTableWidget()
        self.tablaVentas.verticalHeader().setDefaultSectionSize(50)
        self.tablaVentas.setColumnCount(10)
        columnas = ["N° Venta", "Fecha", "Hora", "Mesa", "Sección", "Mesero","Cajero","Tiempo", "Acción","Informacion"]
        self.tablaVentas.setHorizontalHeaderLabels(columnas)
        self.tablaVentas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablaVentas.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tablaVentas.setSelectionMode(QTableWidget.NoSelection)
        self.tablaVentas.setFocusPolicy(Qt.NoFocus)
        self.tablaVentas.setStyleSheet("""
            QTableWidget {
                background-color: white;
                padding:10px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #e2e8f0;
                font-size: 16px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e2e8f0;
            }
            QTableWidget::item:selected {
                background-color: #e6f2ff;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        self.layoutPrincipal.addWidget(self.tablaVentas)
        self.cargarVentasPreparacion()
        
    def cargarVentasPreparacion(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute("""
            SELECT numVenta, fechaRegVenta, fechaRegDetalleVenta
            FROM DetallesVenta
            WHERE estadoDetalleVenta='Preparacion'
            GROUP BY numVenta, fechaRegVenta, fechaRegDetalleVenta
            ORDER BY fechaRegDetalleVenta DESC
        """)
        
        ventas = self.cursor.fetchall()
        self.tablaVentas.setRowCount(0)
        for venta in ventas:
            numVenta, fechaRegVenta, fechaRegDetalleVenta = venta
            row = self.tablaVentas.rowCount()
            self.tablaVentas.insertRow(row)
            
            item=QTableWidgetItem(str(numVenta))
            item.setTextAlignment(Qt.AlignCenter)
            self.tablaVentas.setItem(row, 0, item)
            
            item=QTableWidgetItem(self._fmt_fecha_mdy(fechaRegDetalleVenta))
            item.setTextAlignment(Qt.AlignCenter)
            self.tablaVentas.setItem(row, 1, item)
            
            fechaRegDetalleVentaConvertida = datetime.strptime(fechaRegDetalleVenta, "%Y-%m-%d %H:%M:%S.%f")
            horaReg=fechaRegDetalleVentaConvertida.strftime("%I:%M %p").lstrip("0")
            item=QTableWidgetItem(horaReg)
            item.setTextAlignment(Qt.AlignCenter)
            self.tablaVentas.setItem(row, 2, item)
            
            self.cursor.execute("""
                SELECT V.idMesa, 
                       S.nombSeccion,
                       CASE 
                           WHEN Dt.idMeseroActual= -1 THEN 'DIRECTORIO' 
                           ELSE E1.aliasEmp 
                       END as mesero,
                       CASE 
                           WHEN V.codEmp2 = -1 THEN 'DIRECTORIO' 
                           ELSE E2.aliasEmp 
                       END as cajero
                FROM Venta V 
                JOIN DetallesVenta Dt ON V.numVenta = Dt.numVenta AND V.fechaReg = Dt.fechaRegVenta
                JOIN Mesa M ON M.idMesa = V.idMesa
                JOIN Seccion S ON S.idSeccion = V.idSeccion
                LEFT JOIN Empleado E1 ON Dt.idMeseroActual = E1.codEmp
                LEFT JOIN Empleado E2 ON V.codEmp2 = E2.codEmp
                WHERE V.fechaReg = ? AND Dt.fechaRegDetalleVenta=?
            """, (fechaRegVenta,fechaRegDetalleVenta))
            datosRestantes=self.cursor.fetchone()
            if datosRestantes:
                idMesa=datosRestantes[0]
                item=QTableWidgetItem(str(idMesa))
                item.setTextAlignment(Qt.AlignCenter)
                self.tablaVentas.setItem(row, 3, item)
                
                nombSeccion=datosRestantes[1]
                item=QTableWidgetItem(nombSeccion)
                item.setTextAlignment(Qt.AlignCenter)
                self.tablaVentas.setItem(row, 4, item)
                
                aliasEmp=datosRestantes[2]
                item=QTableWidgetItem(aliasEmp)
                item.setTextAlignment(Qt.AlignCenter)
                self.tablaVentas.setItem(row, 5, item)
                
                aliasEmp2=datosRestantes[3]
                item=QTableWidgetItem(aliasEmp2)
                item.setTextAlignment(Qt.AlignCenter)
                self.tablaVentas.setItem(row,6, item)
            else:
                for col in range(3, 7):
                    item=QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tablaVentas.setItem(row, col, item)
            boton=QPushButton("")
            self.tablaVentas.setCellWidget(row,7,boton)
            
            btn_preparado = QPushButton("Preparado")
            btn_preparado.setFixedHeight(30)
            btn_preparado.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
            btn_preparado.clicked.connect(lambda _, nv=numVenta, f=fechaRegDetalleVenta: self.marcarComoPreparado(nv, f))
            self.tablaVentas.setCellWidget(row, 8, btn_preparado)
            btn_informacion=QPushButton("Ver Detalles")
            btn_informacion.setFixedHeight(30)
            btn_informacion.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn_informacion.clicked.connect(lambda _,fd=fechaRegDetalleVenta:self.mostrarInformacionAgrupada(fd))
            self.tablaVentas.setCellWidget(row,9, btn_informacion)
        self.actualizarTiempos()
        self.conn.close()
    
    def mostrarInformacionAgrupada(self, fecha_registro_detalle_venta):
        self.fecha_actual_dialogo = fecha_registro_detalle_venta
        self.dialog_activo = QDialog(self)
        self.dialog_activo.setWindowTitle("Detalles de Preparación")
        self.dialog_activo.setFixedSize(1600, 800)
        main_layout = QVBoxLayout()
        self.dialog_activo.setLayout(main_layout)
        header = QLabel("📊 ESTADO DE PREPARACIÓN")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background-color: #ffffff;
                border-radius: 10px;
                border: 3px solid #3498db;
                text-align: center;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(header)
        contenido_principal = QWidget()
        main_layout.addWidget(contenido_principal, 1)
        grid_layout = QHBoxLayout(contenido_principal)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        col_local_container = QWidget()
        col_local_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        col_local_layout = QVBoxLayout(col_local_container)
        col_local_layout.setContentsMargins(0, 0, 0, 0)
        col_local_layout.setSpacing(0)
        titulo_local = QLabel("🏠 LOCAL")
        titulo_local.setFixedHeight(50)
        titulo_local.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: #3498db;
                padding: 12px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                text-align: center;
            }
        """)
        col_local_layout.addWidget(titulo_local)
        self.scroll_local = QScrollArea()
        self.scroll_local.setWidgetResizable(True)
        self.scroll_local.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_local.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_local.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f8fafc;
                width: 12px;
                border-radius: 6px;
                margin: 2px 2px 2px 0;
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
        """)
        self.widget_local = QWidget()
        self.widget_local.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.layout_local = QVBoxLayout(self.widget_local)
        self.layout_local.setSpacing(10)
        self.layout_local.setContentsMargins(10, 10, 15, 10)
        self.layout_local.addStretch()
        self.scroll_local.setWidget(self.widget_local)
        col_local_layout.addWidget(self.scroll_local, 1)
        grid_layout.addWidget(col_local_container)
        col_llevar_container = QWidget()
        col_llevar_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        col_llevar_layout = QVBoxLayout(col_llevar_container)
        col_llevar_layout.setContentsMargins(0, 0, 0, 0)
        col_llevar_layout.setSpacing(0)
        titulo_llevar = QLabel("🥡 PARA LLEVAR")
        titulo_llevar.setFixedHeight(50)
        titulo_llevar.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: #e67e22;
                padding: 12px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                text-align: center;
            }
        """)
        col_llevar_layout.addWidget(titulo_llevar)
        self.scroll_llevar = QScrollArea()
        self.scroll_llevar.setWidgetResizable(True)
        self.scroll_llevar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_llevar.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_llevar.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f8fafc;
                width: 12px;
                border-radius: 6px;
                margin: 2px 2px 2px 0;
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
        """)
        self.widget_llevar = QWidget()
        self.widget_llevar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.layout_llevar = QVBoxLayout(self.widget_llevar)
        self.layout_llevar.setSpacing(10)
        self.layout_llevar.setContentsMargins(10, 10, 15, 10)
        self.layout_llevar.addStretch()
        self.scroll_llevar.setWidget(self.widget_llevar)
        col_llevar_layout.addWidget(self.scroll_llevar, 1)
        grid_layout.addWidget(col_llevar_container)
        col_resumen_container = QWidget()
        col_resumen_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        col_resumen_layout = QVBoxLayout(col_resumen_container)
        col_resumen_layout.setContentsMargins(0, 0, 0, 0)
        col_resumen_layout.setSpacing(0)
        titulo_resumen = QLabel("📋 RESUMEN DE FALTANTES")
        titulo_resumen.setFixedHeight(50)
        titulo_resumen.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: #2ecc71;
                padding: 12px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                text-align: center;
            }
        """)
        col_resumen_layout.addWidget(titulo_resumen)
        self.scroll_resumen = QScrollArea()
        self.scroll_resumen.setWidgetResizable(True)
        self.scroll_resumen.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_resumen.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_resumen.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f8fafc;
                width: 12px;
                border-radius: 6px;
                margin: 2px 2px 2px 0;
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
        """)
        self.widget_resumen = QWidget()
        self.widget_resumen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.layout_resumen = QVBoxLayout(self.widget_resumen)
        self.layout_resumen.setSpacing(10)
        self.layout_resumen.setContentsMargins(10, 10, 15, 10)
        self.layout_resumen.addStretch()
        self.scroll_resumen.setWidget(self.widget_resumen)
        col_resumen_layout.addWidget(self.scroll_resumen, 1)
        grid_layout.addWidget(col_resumen_container)
        main_layout.addWidget(contenido_principal)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 12px 40px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_cerrar.clicked.connect(self.dialog_activo.accept)
        main_layout.addWidget(btn_cerrar, alignment=Qt.AlignCenter)
        self.actualizarContenidoTresColumnas()
        self.dialog_activo.exec_()
        self.dialog_activo = None
    
    def actualizarContenidoTresColumnas(self):
        while self.layout_local.count():
            item = self.layout_local.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        while self.layout_llevar.count():
            item = self.layout_llevar.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        while self.layout_resumen.count():
            item = self.layout_resumen.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        productos_por_tipo = {'Local': [], 'Llevar': []}
        total_faltantes_local = 0
        total_faltantes_llevar = 0
        productos_faltantes_local = []
        productos_faltantes_llevar = []
        
        self.cursor.execute("""
            SELECT 
                COALESCE(P.nomProd, Prom.nomProm) as nombre_producto,
                SUM(Dt.cantidadProdDet) as cantidad_total,
                SUM(Dt.cantidadMarcado) as preparados,
                SUM(Dt.cantidadProdDet) - SUM(Dt.cantidadMarcado) as por_preparar,
                GROUP_CONCAT(Dt.idDetalleVenta) as ids_detalles,
                Dt.tipoConsumo,
                CASE 
                    WHEN Dt.idProd IS NOT NULL THEN 'producto'
                    ELSE 'promocion'
                END as tipo_producto
            FROM DetallesVenta Dt
            LEFT JOIN Producto P ON P.idProd = Dt.idProd
            LEFT JOIN Promocion Prom ON Prom.idProm = Dt.idProm
            WHERE Dt.fechaRegDetalleVenta = ?
            GROUP BY COALESCE(Dt.idProd, Dt.idProm), COALESCE(P.nomProd, Prom.nomProm), Dt.tipoConsumo
            HAVING por_preparar > 0
            ORDER BY Dt.tipoConsumo DESC, por_preparar DESC, nombre_producto
        """, (self.fecha_actual_dialogo,))
        productos_agrupados = self.cursor.fetchall()
        for nombre_producto, cantidad_total, preparados, por_preparar, ids_detalles, tipo_consumo, tipo_producto in productos_agrupados:
            tipo_key = 'Local' if tipo_consumo == 'Local' else 'Llevar'
            productos_por_tipo[tipo_key].append((
                nombre_producto, cantidad_total, preparados, por_preparar, 
                ids_detalles, tipo_producto, tipo_consumo
            ))
            if por_preparar > 0:
                if tipo_consumo == 'Local':
                    total_faltantes_local += por_preparar
                    productos_faltantes_local.append(f"• {nombre_producto}: {por_preparar} faltantes")
                else:
                    total_faltantes_llevar += por_preparar
                    productos_faltantes_llevar.append(f"• {nombre_producto}: {por_preparar} faltantes")
        
        if productos_por_tipo['Local']:
            for producto in productos_por_tipo['Local']:
                nombre_producto, cantidad_total, preparados, por_preparar, ids_detalles, tipo_producto, tipo_consumo = producto
                card = QFrame()
                card.setMinimumHeight(200)
                card.setStyleSheet("""
                    QFrame {
                        background-color: #e8f4fc;
                        border: 2px solid #3498db;
                        border-radius: 8px;
                        padding: 12px;
                        margin-bottom: 10px;
                    }
                """)
                card_layout = QVBoxLayout(card)
                card_layout.setSpacing(8)
                card_layout.setContentsMargins(10, 10, 10, 10)
                titulo = QLabel(f"<b>{nombre_producto}</b> ({tipo_producto})")
                titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
                titulo.setWordWrap(True)
                card_layout.addWidget(titulo)
                info = QHBoxLayout()
                info.setSpacing(15)
                info.addWidget(QLabel(f"<b>Total:</b> {cantidad_total}"))
                info.addWidget(QLabel(f"<b>Listos:</b> {preparados}"))
                info.addWidget(QLabel(f"<b>Faltan:</b> {por_preparar}"))
                info.addStretch()
                card_layout.addLayout(info)
                progreso = QProgressBar()
                progreso.setMaximum(cantidad_total)
                progreso.setValue(preparados)
                progreso.setFormat(f"{preparados}/{cantidad_total}")
                progreso.setFixedHeight(25)
                progreso.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        text-align: center;
                        font-weight: bold;
                    }
                    QProgressBar::chunk {
                        background-color: #2ecc71;
                        border-radius: 6px;
                    }
                """)
                card_layout.addWidget(progreso)
                botones = QHBoxLayout()
                botones.setSpacing(10)
                btn_mas = QPushButton("+1")
                btn_mas.setFixedSize(60, 40)
                btn_mas.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                btn_mas.clicked.connect(lambda _, ids=ids_detalles, nom=nombre_producto, tipo='Local': 
                                      self.marcarProductoAgrupadoColumnas(ids, 1, nom, tipo))
                btn_menos = QPushButton("-1")
                btn_menos.setFixedSize(60, 40)
                btn_menos.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                btn_menos.clicked.connect(lambda _, ids=ids_detalles, nom=nombre_producto, tipo='Local': 
                                        self.marcarProductoAgrupadoColumnas(ids, -1, nom, tipo))
                btn_todos = QPushButton("Todos")
                btn_todos.setFixedSize(80, 40)
                btn_todos.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #27ae60;
                    }
                """)
                btn_todos.clicked.connect(lambda _, ids=ids_detalles, total=cantidad_total, nom=nombre_producto, tipo='Local': 
                                        self.marcarProductoAgrupadoColumnas(ids, total, nom, tipo, True))
                botones.addWidget(btn_mas)
                botones.addWidget(btn_menos)
                botones.addWidget(btn_todos)
                botones.addStretch()
                card_layout.addLayout(botones)
                self.layout_local.addWidget(card)
        else:
            label = QLabel("✅ Todos los productos para Local están listos")
            label.setFixedHeight(180)
            label.setStyleSheet("""
                font-size: 16px; 
                color: #27ae60; 
                font-weight: bold; 
                padding: 20px; 
                text-align: center;
                background-color: #eafaf1;
                border: 2px solid #27ae60;
                border-radius: 8px;
            """)
            label.setAlignment(Qt.AlignCenter)
            self.layout_local.addWidget(label)
        if productos_por_tipo['Llevar']:
            for producto in productos_por_tipo['Llevar']:
                nombre_producto, cantidad_total, preparados, por_preparar, ids_detalles, tipo_producto, tipo_consumo = producto
                card = QFrame()
                card.setMinimumHeight(200)
                card.setStyleSheet("""
                    QFrame {
                        background-color: #fef5e7;
                        border: 2px solid #e67e22;
                        border-radius: 8px;
                        padding: 12px;
                        margin-bottom: 10px;
                    }
                """)
                card_layout = QVBoxLayout(card)
                card_layout.setSpacing(8)
                card_layout.setContentsMargins(10, 10, 10, 10)
                titulo = QLabel(f"<b>{nombre_producto}</b> ({tipo_producto})")
                titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
                titulo.setWordWrap(True)
                card_layout.addWidget(titulo)
                info = QHBoxLayout()
                info.setSpacing(15)
                info.addWidget(QLabel(f"<b>Total:</b> {cantidad_total}"))
                info.addWidget(QLabel(f"<b>Listos:</b> {preparados}"))
                info.addWidget(QLabel(f"<b>Faltan:</b> {por_preparar}"))
                info.addStretch()
                card_layout.addLayout(info)
                progreso = QProgressBar()
                progreso.setMaximum(cantidad_total)
                progreso.setValue(preparados)
                progreso.setFormat(f"{preparados}/{cantidad_total}")
                progreso.setFixedHeight(25)
                progreso.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #ddd;
                        border-radius: 6px;
                        text-align: center;
                        font-weight: bold;
                    }
                    QProgressBar::chunk {
                        background-color: #e67e22;
                        border-radius: 6px;
                    }
                """)
                card_layout.addWidget(progreso)
                botones = QHBoxLayout()
                botones.setSpacing(10)
                btn_mas = QPushButton("+1")
                btn_mas.setFixedSize(60, 50)
                btn_mas.setStyleSheet("""
                    QPushButton {
                        background-color: #e67e22;
                        color: white;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #d35400;
                    }
                """)
                btn_mas.clicked.connect(lambda _, ids=ids_detalles, nom=nombre_producto, tipo='Llevar': self.marcarProductoAgrupadoColumnas(ids, 1, nom, tipo))
                btn_menos = QPushButton("-1")
                btn_menos.setFixedSize(60, 50)
                btn_menos.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                btn_menos.clicked.connect(lambda _, ids=ids_detalles, nom=nombre_producto, tipo='Llevar': self.marcarProductoAgrupadoColumnas(ids, -1, nom, tipo))
                btn_todos = QPushButton("Todos")
                btn_todos.setFixedSize(80, 50)
                btn_todos.setStyleSheet("""
                    QPushButton {
                        background-color: #2ecc71;
                        color: white;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #27ae60;
                    }
                """)
                btn_todos.clicked.connect(lambda _, ids=ids_detalles, total=cantidad_total, nom=nombre_producto, tipo='Llevar':self.marcarProductoAgrupadoColumnas(ids, total, nom, tipo, True))
                botones.addWidget(btn_mas)
                botones.addWidget(btn_menos)
                botones.addWidget(btn_todos)
                botones.addStretch()
                card_layout.addLayout(botones)
                self.layout_llevar.addWidget(card)
        else:
            label = QLabel("✅ Todos los productos para Llevar están listos")
            label.setFixedHeight(180)
            label.setStyleSheet("""
                font-size: 16px; 
                color: #27ae60; 
                font-weight: bold; 
                padding: 20px; 
                text-align: center;
                background-color: #eafaf1;
                border: 2px solid #27ae60;
                border-radius: 8px;
            """)
            label.setAlignment(Qt.AlignCenter)
            self.layout_llevar.addWidget(label)
        self.layout_local.addStretch()
        self.layout_llevar.addStretch()
        resumen_titulo = QLabel("📊 RESUMEN DE FALTANTES")
        resumen_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; text-align: center; margin-bottom: 15px;")
        self.layout_resumen.addWidget(resumen_titulo)
        local_resumen = QLabel("🏠 LOCAL")
        local_resumen.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db; margin-top: 10px;")
        self.layout_resumen.addWidget(local_resumen)
        local_total = QLabel(f"<b>Total faltantes:</b> {total_faltantes_local}")
        local_total.setStyleSheet("font-size: 14px; color: #2c3e50; margin-bottom: 5px;")
        self.layout_resumen.addWidget(local_total)
        if productos_faltantes_local:
            for item in productos_faltantes_local:
                label_item = QLabel(item)
                label_item.setStyleSheet("font-size: 13px; color: #7f8c8d; padding-left: 10px;")
                self.layout_resumen.addWidget(label_item)
        else:
            label_completo = QLabel("✅ Todo completo")
            label_completo.setStyleSheet("font-size: 13px; color: #27ae60; padding-left: 10px;")
            self.layout_resumen.addWidget(label_completo)
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setStyleSheet("background-color: #ddd; margin: 10px 0;")
        self.layout_resumen.addWidget(separador)
        llevar_resumen = QLabel("🥡 PARA LLEVAR")
        llevar_resumen.setStyleSheet("font-size: 16px; font-weight: bold; color: #e67e22; margin-top: 10px;")
        self.layout_resumen.addWidget(llevar_resumen)
        llevar_total = QLabel(f"<b>Total faltantes:</b> {total_faltantes_llevar}")
        llevar_total.setStyleSheet("font-size: 14px; color: #2c3e50; margin-bottom: 5px;")
        self.layout_resumen.addWidget(llevar_total)
        if productos_faltantes_llevar:
            for item in productos_faltantes_llevar:
                label_item = QLabel(item)
                label_item.setStyleSheet("font-size: 13px; color: #7f8c8d; padding-left: 10px;")
                self.layout_resumen.addWidget(label_item)
        else:
            label_completo = QLabel("✅ Todo completo")
            label_completo.setStyleSheet("font-size: 13px; color: #27ae60; padding-left: 10px;")
            self.layout_resumen.addWidget(label_completo)
        total_general = total_faltantes_local + total_faltantes_llevar
        if total_general == 0:
            estado = QLabel("🎉 ¡TODO PREPARADO!")
            estado.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #27ae60;
                    padding: 15px;
                    background-color: #eafaf1;
                    border-radius: 8px;
                    border: 2px solid #27ae60;
                    text-align: center;
                    margin-top: 15px;
                }
            """)
            self.layout_resumen.addWidget(estado)
        else:
            estado = QLabel(f"⚠️ <b>Total general faltante:</b> {total_general} productos")
            estado.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #e74c3c;
                    padding: 12px;
                    background-color: #fdedec;
                    border-radius: 8px;
                    border: 2px solid #e74c3c;
                    text-align: center;
                    margin-top: 15px;
                }
            """)
            self.layout_resumen.addWidget(estado)
        
        self.layout_resumen.addStretch()
        self.conn.close()

    def marcarProductoAgrupadoColumnas(self, ids_detalles, cantidad, nombre_producto, tipo_consumo, marcar_todos=False):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        try:
            ids_lista = ids_detalles.split(',')
            
            for id_detalle in ids_lista:
                if not id_detalle:
                    continue
                    
                self.cursor.execute("""
                    SELECT cantidadProdDet, cantidadMarcado 
                    FROM DetallesVenta 
                    WHERE idDetalleVenta = ?
                """, (int(id_detalle),))
                
                resultado = self.cursor.fetchone()
                if resultado:
                    cantidad_total, cantidad_actual = resultado
                    
                    if marcar_todos:
                        nueva_cantidad = cantidad_total
                    else:
                        nueva_cantidad = cantidad_actual + cantidad
                        nueva_cantidad = max(0, min(nueva_cantidad, cantidad_total))
                    
                    marcado = nueva_cantidad > 0
                    
                    self.cursor.execute("""
                        UPDATE DetallesVenta 
                        SET marcado = ?, cantidadMarcado = ? 
                        WHERE idDetalleVenta = ?
                    """, (marcado, nueva_cantidad, int(id_detalle)))
            self.conn.commit()
            self.actualizarContenidoTresColumnas()
        except Exception as e:
            self.conn.rollback()
            print(f"Error al actualizar marcado: {e}")
        self.conn.close()
    

    def _fmt_fecha_mdy(self, fecha_sql) -> str:
        try:
            if isinstance(fecha_sql, str):
                dt = datetime.fromisoformat(fecha_sql)
            else:
                dt = datetime.strptime(str(fecha_sql), "%Y-%m-%d")
            return dt.strftime("%m-%d-%Y")  
        except Exception:
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    dt = datetime.strptime(str(fecha_sql), fmt)
                    return dt.strftime("%m-%d-%Y")
                except Exception:
                    pass
        return str(fecha_sql)
    

    def actualizarTiempos(self):
        for i in range(self.tablaVentas.rowCount()):
            item=self.tablaVentas.item(i,2)
            hora_registro=item.text()
            hora_registro = datetime.strptime(hora_registro, "%I:%M %p")
            horaActual=datetime.now()
            hora_registro_completo=horaActual.replace(
                hour=hora_registro.hour,
                minute=hora_registro.minute,
                second=0,
                microsecond=0)
            diferencia=abs(horaActual-hora_registro_completo)
            diferenciaMinutos=diferencia.total_seconds()/60
            celda=self.tablaVentas.cellWidget(i,7)
            if diferenciaMinutos<10:
                celda.setStyleSheet("background-color:green")
            else:
                if diferenciaMinutos>=10 and diferenciaMinutos<20:
                    celda.setStyleSheet("background-color:yellow")
                else:
                    celda.setStyleSheet("background-color:red")
    
    def marcarComoPreparado(self,numVenta,fecha_registro_detalle_venta):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("""
                UPDATE DetallesVenta 
                SET estadoDetalleVenta = 'Cobrar' 
                WHERE fechaRegDetalleVenta=? 
            """, (fecha_registro_detalle_venta,))
            self.conn.commit()
            self.cargarVentasPreparacion()
            if self.dialog_activo:
                self.dialog_activo.accept()
        except Exception as e:
            print(f"Error al actualizar la venta: {str(e)}")
        self.conn.close()
        
if __name__=="__main__":
    aplicacion=QApplication(sys.argv)
    pagina=PedidosPendientes()
    pagina.show()
    sys.exit(aplicacion.exec_())