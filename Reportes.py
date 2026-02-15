import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from datetime import datetime, timedelta
from fpdf import FPDF
import smtplib
import unicodedata
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import tempfile
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

def _fmt2(x):
    d = Decimal(str(x)) if x is not None else Decimal("0")
    return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'database', 'cafebar.db')

DB_PATH = get_db_path()

def normalize_text(text):
    if text is None:
        return ""
    text = str(text)
    replacements = {
        '\u2022': '•',
        '\u2013': '-',
        '\u2014': '-',
        '\u2018': "'",
        '\u2019': "'",
        '\u201C': '"',
        '\u201D': '"',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text

class PDFReport(FPDF):
    def __init__(self, tipo_reporte, periodo=None, empleado=None):
        super().__init__()
        self.tipo_reporte = tipo_reporte
        self.periodo = periodo
        self.empleado = empleado
        self.set_auto_page_break(auto=True, margin=15)


    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'CAFE BAR - REPORTE', 0, 1, 'C')
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, f'Reporte de {self.tipo_reporte}', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        if self.periodo:
            self.cell(0, 8, f'Período: {self.periodo}', 0, 1, 'C')
        if self.empleado:
            self.cell(0, 8, f'Empleado: {self.empleado}', 0, 1, 'C')
        fecha_actual = datetime.now()
        fecha_formateada = fecha_actual.strftime("%d/%m/%Y %H:%M")
        self.cell(0, 8, f'Fecha de generación: {fecha_formateada}', 0, 1, 'C')
        self.ln(5)
    

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
    

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, normalize_text(title), 0, 1, 'L')
        self.ln(2)
    

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 8, normalize_text(body))
        self.ln()
    
    
    def cell(self, w, h=0, txt='', border=0, ln=0, align='', fill=False, link=''):
        super().cell(w, h, normalize_text(txt), border, ln, align, fill, link)
    

    def multi_cell(self, w, h=0, txt='', border=0, align='J', fill=False):
        super().multi_cell(w, h, normalize_text(txt), border, align, fill)
    

    def add_table(self, headers, data, col_widths=None, max_rows_per_page=30):
        self.set_font('Arial', 'B', 9)
        headers = [normalize_text(h) for h in headers]
        if not col_widths:
            if len(headers) == 12:
                col_widths = [12, 20, 15, 25, 25, 20, 15, 20, 20, 15, 20, 25]
            elif len(headers) == 3:
                col_widths = [80, 40, 30]
            else:
                col_widths = [self.get_string_width(str(h)) + 12 for h in headers]
        page_width = self.w - 2 * self.l_margin
        total_width = sum(col_widths)
        if total_width > page_width:
            ratio = page_width / total_width
            col_widths = [w * ratio for w in col_widths]
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, 1, 0, 'C')
        self.ln()
        self.set_font('Arial', '', 8)
        row_count = 0
        for row_idx, row in enumerate(data):
            if row_count >= max_rows_per_page:
                self.add_page()
                self.set_font('Arial', 'B', 9)
                for i, header in enumerate(headers):
                    self.cell(col_widths[i], 10, header, 1, 0, 'C')
                self.ln()
                self.set_font('Arial', '', 8)
                row_count = 0
            
            row = [normalize_text(item) for item in row]
            
            for i, item in enumerate(row):
                text = str(item)
                if len(text) > 25:
                    text = text[:22] + "..."
                self.cell(col_widths[i], 8, text, 1, 0, 'C')
            self.ln()
            row_count += 1
        self.ln(5)
    

    def add_detalle_venta(self, num_venta, fecha, hora, mesero_apertura, cajero, salon, mesa, productos_detalle):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, f'VENTA #{num_venta}', 0, 1, 'L')
        
        self.set_font('Arial', '', 9)
        self.cell(0, 6, f'Fecha: {fecha} | Hora: {hora}', 0, 1, 'L')
        self.cell(0, 6, f'Mesero (Apertura): {mesero_apertura} | Cajero: {cajero}', 0, 1, 'L')
        if salon and mesa and mesa != '0':
            self.cell(0, 6, f'Ubicación: {salon} - Mesa {mesa}', 0, 1, 'L')
        else:
            self.cell(0, 6, f'Ubicación: Para Llevar', 0, 1, 'L')
        self.ln(2)
        
        if productos_detalle:
            self.set_font('Arial', 'B', 9)
            headers = ["Cantidad", "Producto", "Tipo", "Subtotal", "Mesero"]
            col_widths = [15, 70, 20, 25, 40]
            
            for i, header in enumerate(headers):
                self.cell(col_widths[i], 8, header, 1, 0, 'C')
            self.ln()
            
            self.set_font('Arial', '', 8)
            total_venta = 0
            
            for cantidad, producto, tipo_consumo, subtotal, mesero_detalle in productos_detalle:
                self.cell(col_widths[0], 8, str(cantidad), 1, 0, 'C')
                
                prod_text = str(producto) if producto else "N/A"
                if len(prod_text) > 25:
                    prod_text = prod_text[:22] + "..."
                self.cell(col_widths[1], 8, prod_text, 1, 0, 'L')
                
                tipo_text = "Local" if str(tipo_consumo).upper() == "LOCAL" else "Llevar"
                self.cell(col_widths[2], 8, tipo_text, 1, 0, 'C')
                
                self.cell(col_widths[3], 8, f"{float(subtotal):.2f}", 1, 0, 'R')
                self.cell(col_widths[4], 8, mesero_detalle, 1, 0, 'C')
                self.ln()
                total_venta += float(subtotal)
            
            self.set_font('Arial', 'B', 9)
            self.cell(sum(col_widths[0:4]), 8, "TOTAL:", 1, 0, 'R')
            self.cell(col_widths[4], 8, f"{total_venta:.2f}", 1, 0, 'R')
            self.ln()
        
        self.ln(5)

class Reportes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("REPORTES Y ESTADÍSTICAS")
        self.setStyleSheet("""
        QMainWindow { 
            background-color: #f8fafc; 
            font-family: 'Segoe UI', Arial, sans-serif; 
        }

        QPushButton { 
            padding: 12px 24px; 
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

        QLineEdit, QDateEdit { 
            background-color: white; 
            border: 2px solid #e2e8f0; 
            border-radius: 6px; 
            padding: 10px; 
            font-size: 14px; 
            min-height: 40px; 
        }

        QLineEdit:focus, QDateEdit:focus { 
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

        QTableWidget { 
            background-color: white; 
            border: 2px solid #e2e8f0; 
            border-radius: 8px; 
            gridline-color: #e2e8f0; 
            font-size: 14px; 
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
            font-size: 14px; 
        }

        QGroupBox { 
            font-weight: bold; 
            border: 2px solid #e2e8f0; 
            border-radius: 8px; 
            margin-top: 1ex; 
            padding-top: 10px; 
            background-color: #ffffff; 
        }

        QGroupBox::title { 
            subcontrol-origin: margin; 
            subcontrol-position: top center; 
            padding: 0 5px; 
            background-color: #3498db; 
            color: white; 
            border-radius: 4px; 
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
    QMessageBox QPushButton:hover { background-color: #2980b9; }
""")
        self.set_up()
    
    
    def set_up(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.layoutPrincipal.setSpacing(15)
        
        self.tablaResultados = None
        self.iniciarInterfaz()
    
    
    def iniciarInterfaz(self):
        panelFiltros = QWidget()
        panelFiltros.setFixedWidth(350)
        panelFiltros.setStyleSheet("""
            QWidget { 
                background-color: #ffffff; 
                border-radius: 8px; 
                border: 1px solid #e2e8f0; 
            }
        """)
        
        layoutFiltros = QVBoxLayout(panelFiltros)
        layoutFiltros.setContentsMargins(15, 15, 15, 15)
        layoutFiltros.setSpacing(15)    
        grupoTipo = QGroupBox("Tipo de Reporte")
        grupoTipo.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                border: 2px solid #e2e8f0; 
                border-radius: 8px; 
                margin-top: 1ex; 
                padding-top: 10px; 
                background-color: #ffffff; 
            } 
            QGroupBox::title { 
                subcontrol-origin: margin; 
                subcontrol-position: top center; 
                padding: 0 5px; 
                background-color: #3498db; 
                color: white; 
                border-radius: 4px; 
            }
        """)
        
        layoutTipo = QVBoxLayout(grupoTipo)
        layoutTipo.setSpacing(10)
        self.radioVentas = QRadioButton("Reporte de Ventas")
        self.radioVentas.setChecked(True)
        self.radioVentas.toggled.connect(self.cambiarTipoReporte)
        self.radioStock = QRadioButton("Reporte de Stock")
        self.radioStock.toggled.connect(self.cambiarTipoReporte)
        layoutTipo.addWidget(self.radioVentas)
        layoutTipo.addWidget(self.radioStock)
        layoutFiltros.addWidget(grupoTipo)
        grupoFechas = QGroupBox("Rango de Fechas")
        grupoFechas.setStyleSheet(grupoTipo.styleSheet())
        layoutFechas = QVBoxLayout(grupoFechas)
        layoutFechas.setSpacing(10)
        hoy = QDate.currentDate()
        hace30Dias = hoy.addDays(-30)
        layoutFechaInicio = QHBoxLayout()
        layoutFechaInicio.addWidget(QLabel("Desde:"))
        self.dateInicio = QDateEdit()
        self.dateInicio.setDate(hace30Dias)
        self.dateInicio.setCalendarPopup(True)
        self.dateInicio.setDisplayFormat("dd-MM-yyyy")
        self.dateInicio.setFixedHeight(40)
        layoutFechaInicio.addWidget(self.dateInicio)
        layoutFechas.addLayout(layoutFechaInicio)
        layoutFechaFin = QHBoxLayout()
        layoutFechaFin.addWidget(QLabel("Hasta:"))
        self.dateFin = QDateEdit()
        self.dateFin.setDate(hoy)
        self.dateFin.setCalendarPopup(True)
        self.dateFin.setDisplayFormat("dd-MM-yyyy")
        self.dateFin.setFixedHeight(40)
        layoutFechaFin.addWidget(self.dateFin)
        layoutFechas.addLayout(layoutFechaFin)
        layoutFiltros.addWidget(grupoFechas)
        grupoEmpleado = QGroupBox("Filtro por Cajero")
        grupoEmpleado.setStyleSheet(grupoTipo.styleSheet())
        layoutEmpleado = QVBoxLayout(grupoEmpleado)
        layoutEmpleado.setSpacing(10)
        self.checkEmpleado = QCheckBox("Filtrar por cajero")
        self.checkEmpleado.toggled.connect(self.toggleFiltroEmpleado)
        self.comboEmpleado = QComboBox()
        self.comboEmpleado.setEnabled(False)
        self.comboEmpleado.setFixedHeight(40)
        self.cargarEmpleados()
        layoutEmpleado.addWidget(self.checkEmpleado)
        layoutEmpleado.addWidget(self.comboEmpleado)
        layoutFiltros.addWidget(grupoEmpleado)
        btnMostrarInfo = QPushButton("Mostrar Información")
        btnMostrarInfo.setStyleSheet("""
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                border-radius: 8px; 
                padding: 12px 24px; 
                font-size: 16px; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #2980b9; 
            }
        """)
        btnMostrarInfo.setFixedHeight(50)
        btnMostrarInfo.clicked.connect(self.mostrarInformacion)
        layoutFiltros.addWidget(btnMostrarInfo)
        btnGenerar = QPushButton("Generar Reporte PDF")
        btnGenerar.setStyleSheet("""
            QPushButton { 
                background-color: #2ecc71; 
                color: white; 
                border-radius: 8px; 
                padding: 12px 24px; 
                font-size: 16px; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #27ae60; 
            }
        """)
        btnGenerar.setFixedHeight(50)
        btnGenerar.clicked.connect(self.generarReporte)
        btnLimpiar = QPushButton("Limpiar Filtros")
        btnLimpiar.setStyleSheet("""
            QPushButton { 
                background-color: #95a5a6; 
                color: white; 
                border-radius: 8px; 
                padding: 12px 24px; 
                font-size: 16px; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #7f8c8d; 
            }
        """)
        btnLimpiar.setFixedHeight(50)
        btnLimpiar.clicked.connect(self.limpiarFiltros)
        layoutFiltros.addWidget(btnGenerar)
        layoutFiltros.addWidget(btnLimpiar)
        layoutFiltros.addStretch()
        panelResultados = QWidget()
        layoutResultados = QVBoxLayout(panelResultados)
        layoutResultados.setContentsMargins(0, 0, 0, 0)
        layoutResultados.setSpacing(0)
        self.tablaResultados = QTableWidget()
        self.tablaResultados.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tablaResultados.setSelectionMode(QTableWidget.SingleSelection)
        self.tablaResultados.setFocusPolicy(Qt.StrongFocus)
        self.tablaResultados.verticalHeader().setVisible(False)
        self.tablaResultados.setAlternatingRowColors(True)
        self.tablaResultados.cellDoubleClicked.connect(self.onCellDoubleClicked)
        layoutResultados.addWidget(self.tablaResultados)
        layoutContenedor = QHBoxLayout()
        layoutContenedor.setSpacing(20)
        layoutContenedor.setContentsMargins(0, 0, 0, 0)
        layoutContenedor.addWidget(panelFiltros)
        layoutContenedor.addWidget(panelResultados, 1)
        self.layoutPrincipal.addLayout(layoutContenedor)
        self.limpiarTabla()
        self.showMaximized()
    

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'tablaResultados') and self.tablaResultados and self.tablaResultados.columnCount() > 0:
            self.ajustarTamanosColumnas()
    
    def ajustarTamanosColumnas(self):
        if not hasattr(self, 'tablaResultados') or not self.tablaResultados:
            return   
        if self.tablaResultados.columnCount() == 12:
            ancho_total = self.tablaResultados.viewport().width()
            self.tablaResultados.setColumnWidth(0, 40)
            espacio_restante = ancho_total - 40
            porcentajes = [
                0.1,  
                0.09, 
                0.11, 
                0.11, 
                0.09,  
                0.06, 
                0.09,  
                0.09,
                0.07,  
                0.09,  
                0.14   
            ]
            for i in range(1, 12):
                ancho = int(espacio_restante * porcentajes[i-1])
                self.tablaResultados.setColumnWidth(i, ancho)
            self.tablaResultados.horizontalHeader().setStretchLastSection(True)
    

    def ajustarTamanos(self):
        if not hasattr(self, 'tablaResultados') or not self.tablaResultados:
            return        
        if self.tablaResultados.columnCount() > 0:
            if self.tablaResultados.columnCount() == 12:
                self.ajustarTamanosColumnas()
            else:
                header = self.tablaResultados.horizontalHeader()
                header.setStretchLastSection(True)
                header.setSectionResizeMode(QHeaderView.Stretch)
    

    def limpiarTabla(self):
        if not hasattr(self, 'tablaResultados') or not self.tablaResultados:
            return        
        self.tablaResultados.setRowCount(0)
        self.tablaResultados.setColumnCount(1)
        self.tablaResultados.setHorizontalHeaderLabels(["Información"])
        item = QTableWidgetItem("Seleccione los filtros y haga clic en 'Mostrar Información'")
        item.setTextAlignment(Qt.AlignCenter)
        item.setFont(QFont("Arial", 12))
        self.tablaResultados.setRowCount(1)
        self.tablaResultados.setItem(0, 0, item)
        self.tablaResultados.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    

    def cargarEmpleados(self):
        self.comboEmpleado.clear()
        self.comboEmpleado.addItem("Todos los cajeros", None)
        self.cursor.execute("SELECT codEmp, aliasEmp FROM Empleado WHERE disponibleEmp = 1 ORDER BY aliasEmp")
        empleados = self.cursor.fetchall()
        for codigo, alias in empleados:
            self.comboEmpleado.addItem(alias, codigo)
    

    def toggleFiltroEmpleado(self, activado):
        self.comboEmpleado.setEnabled(activado)
        self.cargarEmpleados()
    

    def cambiarTipoReporte(self):
        es_reporte_ventas = self.radioVentas.isChecked()
        self.dateInicio.setEnabled(es_reporte_ventas)
        self.dateFin.setEnabled(es_reporte_ventas)
        self.checkEmpleado.setEnabled(es_reporte_ventas)
        self.comboEmpleado.setEnabled(es_reporte_ventas and self.checkEmpleado.isChecked())
    

    def mostrarInformacion(self):
        if self.radioVentas.isChecked():
            self.generarReporteVentas(solo_mostrar=True)
        else:
            self.generarReporteStock(solo_mostrar=True)
    

    def generarReporte(self):
        if self.radioVentas.isChecked():
            self.generarReporteVentas(solo_mostrar=False)
        else:
            self.generarReporteStock(solo_mostrar=False)
    

    def generarReporteVentas(self, solo_mostrar=True):
        fecha_inicio = self.dateInicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.dateFin.date().toString("yyyy-MM-dd")    
        empleado_id = None
        if self.checkEmpleado.isChecked():
            empleado_id = self.comboEmpleado.currentData()
        query = """
            SELECT 
                v.numVenta, 
                DATE(v.fechaReg) as fecha,
                v.horaReg, 
                e1.aliasEmp as mesero_apertura,
                CASE 
                    WHEN v.codEmp2 = -1 THEN 'DIRECTORIO'
                    ELSE e2.aliasEmp 
                END as cajero,
                s.nombSeccion, 
                m.idMesa, 
                v.totalVenta,
                COALESCE(SUM(CASE WHEN p.idMetodo = 1 THEN p.monto ELSE 0 END), 0) as efectivo,
                COALESCE(SUM(CASE WHEN p.idMetodo = 2 THEN p.monto ELSE 0 END), 0) as qr,
                COALESCE(SUM(p.monto), 0) as total_pagado,
                CASE 
                     WHEN NOT EXISTS (
                         SELECT 1 FROM DetallesVenta d 
                         WHERE d.numVenta = v.numVenta 
                         AND d.fechaRegVenta = v.fechaReg
                         AND d.estadoDetalleVenta != 'Cancelada'
                     ) THEN 'Cancelada'
                     
                     WHEN EXISTS (
                         SELECT 1 FROM DetallesVenta d 
                         WHERE d.numVenta = v.numVenta 
                         AND d.fechaRegVenta = v.fechaReg
                         AND d.estadoDetalleVenta = 'Preparacion'
                     ) THEN 'En Preparación'
                     
                     WHEN NOT EXISTS (
                         SELECT 1 FROM DetallesVenta d 
                         WHERE d.numVenta = v.numVenta 
                         AND d.fechaRegVenta = v.fechaReg
                         AND d.estadoDetalleVenta != 'Finalizado'
                     ) THEN 'Finalizada'
                     
                     WHEN NOT EXISTS (
                         SELECT 1 FROM DetallesVenta d 
                         WHERE d.numVenta = v.numVenta 
                         AND d.fechaRegVenta = v.fechaReg
                         AND d.estadoDetalleVenta != 'Cobrar'
                     ) THEN 'Por Cobrar'
                     
                     ELSE 'Mixto'
                 END AS estado_venta
            FROM Venta v
            JOIN Empleado e1 ON v.codEmp = e1.codEmp
            LEFT JOIN Empleado e2 ON v.codEmp2 = e2.codEmp
            JOIN Seccion s ON v.idSeccion = s.idSeccion
            JOIN Mesa m ON v.idMesa = m.idMesa AND v.idSeccion = m.idSeccion
            LEFT JOIN Pago p ON v.numVenta = p.numVenta AND p.fechaRegVenta = v.fechaReg
            WHERE DATE(v.fechaReg) BETWEEN ? AND ?
        """
        params = [fecha_inicio, fecha_fin]
        if empleado_id:
            query += " AND v.codEmp2 = ?"
            params.append(empleado_id)
        query += " GROUP BY v.numVenta, v.fechaReg, v.horaReg, e1.aliasEmp, e2.aliasEmp, v.codEmp2, s.nombSeccion, m.idMesa, v.totalVenta"
        query += " ORDER BY v.fechaReg, v.horaReg"
        self.cursor.execute(query, params)
        ventas = self.cursor.fetchall()
        self.tablaResultados.setColumnCount(12)
        headers = [
            "N° Venta", "Fecha", "Hora", "Mesero (Apertura)", "Cajero", "Salón", "Mesa", 
            "Total Venta", "Efectivo", "QR", "Total Pagado", "Estado"
        ]
        self.tablaResultados.setHorizontalHeaderLabels(headers)
        self.tablaResultados.setRowCount(len(ventas))
        for row, venta in enumerate(ventas):
            num_venta, fecha, hora, mesero_apertura, cajero, salon, mesa, total_venta, efectivo, qr, total_pagado, estado_venta = venta
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
            fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
            if estado_venta == 'Finalizada':
                color_estado = QColor(39, 174, 96)
            elif estado_venta == 'En Preparación':
                color_estado = QColor(241, 196, 15)
            elif estado_venta == 'Por Cobrar':
                color_estado = QColor(52, 152, 219)
            elif estado_venta == 'Cancelada':
                color_estado = QColor(231, 76, 60)
            elif estado_venta == 'Mixto':
                color_estado = QColor(155, 89, 182) 
            else:
                color_estado = QColor(149, 165, 166)
            datos = [
                num_venta, 
                fecha_formateada, 
                hora, 
                mesero_apertura, 
                cajero, 
                salon, 
                mesa, 
                f"{float(total_venta):.2f}",
                f"{float(efectivo):.2f}",
                f"{float(qr):.2f}",
                f"{float(total_pagado):.2f}",
                estado_venta
            ]
            for col, valor in enumerate(datos):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(QFont("Arial", 11))   
                if col == 11:
                    item.setForeground(color_estado)
                    item.setFont(QFont("Arial", 11, QFont.Bold))
                    if estado_venta == "Cancelada":
                        for c in range(12):
                            bg_item = QTableWidgetItem(str(datos[c]) if c < len(datos) else "")
                            bg_item.setBackground(QColor(255, 230, 230))
                            bg_item.setForeground(QColor(220, 50, 50) if c == 11 else QColor(0, 0, 0))
                            bg_item.setTextAlignment(Qt.AlignCenter)
                            bg_item.setFont(QFont("Arial", 11))
                            self.tablaResultados.setItem(row, c, bg_item)
                        continue
                    elif estado_venta == "En Preparación":
                        item.setBackground(QColor(255, 255, 230))
                    elif estado_venta == "Por Cobrar":
                        item.setBackground(QColor(230, 255, 230))
                    elif estado_venta == "Finalizada":
                        item.setBackground(QColor(240, 248, 255))
                    elif estado_venta == "Mixto":
                        item.setBackground(QColor(235, 220, 250))
                self.tablaResultados.setItem(row, col, item)
        self.ajustarTamanosColumnas()
        QTimer.singleShot(50, self.ajustarTamanos)
        if not solo_mostrar:
            self.generarPDFVentasCompleto(ventas, fecha_inicio, fecha_fin, empleado_id)
    

    def obtenerDetallesProductosVenta(self, num_venta, fecha):
        query = """
            SELECT 
                dv.cantidadProdDet,
                COALESCE(p.nomProd, pr.nomProm) as producto,
                dv.tipoConsumo,
                dv.subtotal,
                e.aliasEmp as mesero_detalle,
                COALESCE(dv.idProd, dv.idProm) as id_item
            FROM DetallesVenta dv
            LEFT JOIN Producto p ON dv.idProd = p.idProd
            LEFT JOIN Promocion pr ON dv.idProm = pr.idProm
            JOIN Empleado e ON dv.idMeseroActual = e.codEmp
            WHERE dv.numVenta = ? AND DATE(dv.fechaRegVenta) = ?
            ORDER BY dv.idDetalleVenta
        """
        self.cursor.execute(query, (num_venta, fecha))
        productos_raw = self.cursor.fetchall()
        return self.agrupar_productos_detalle(productos_raw)
    

    def obtenerProductosAgrupadosVenta(self, num_venta, fecha):
        query = """
            SELECT 
                SUM(dv.cantidadProdDet) as cantidad_total,
                COALESCE(p.nomProd, pr.nomProm) as producto,
                dv.tipoConsumo,
                SUM(dv.subtotal) as subtotal_total,
                COALESCE(dv.idProd, dv.idProm) as id_item
            FROM DetallesVenta dv
            LEFT JOIN Producto p ON dv.idProd = p.idProd
            LEFT JOIN Promocion pr ON dv.idProm = pr.idProm
            WHERE dv.numVenta = ? AND DATE(dv.fechaRegVenta) = ?
            GROUP BY COALESCE(p.nomProd, pr.nomProm), dv.tipoConsumo, COALESCE(dv.idProd, dv.idProm)
            ORDER BY dv.idDetalleVenta
        """
        self.cursor.execute(query, (num_venta, fecha))
        productos_raw = self.cursor.fetchall()
        return productos_raw
    

    def agrupar_productos_detalle(self, productos_raw):
        productos_agrupados = []
        productos_dict = defaultdict(list)
        for cant, nombre, tipo, subtotal, mesero, id_item in productos_raw:
            key = (nombre, tipo, id_item, mesero)
            productos_dict[key].append((cant, nombre, tipo, subtotal, mesero, id_item))
        
        for key, items in productos_dict.items():
            if len(items) == 1:
                cant, nombre, tipo, subtotal, mesero, id_item = items[0]
                productos_agrupados.append((cant, nombre, tipo, subtotal, mesero))
            else:
                total_cant = sum(item[0] for item in items)
                nombre = items[0][1]
                tipo = items[0][2]
                total_subtotal = sum(item[3] for item in items)
                meseros = ", ".join(sorted(set(item[4] for item in items)))
                productos_agrupados.append((total_cant, nombre, tipo, total_subtotal, meseros))
        return productos_agrupados
    

    def generarPDFVentasCompleto(self, ventas, fecha_inicio, fecha_fin, empleado_id):
        fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
        periodo = f"{fecha_inicio_obj.strftime('%d/%m/%Y')} a {fecha_fin_obj.strftime('%d/%m/%Y')}"
        pdf = PDFReport(
            tipo_reporte="Ventas",
            periodo=periodo,
            empleado=self.comboEmpleado.currentText() if empleado_id else "Todos los cajeros"
        )
        pdf.add_page()
        pdf.chapter_title("REPORTE COMPLETO DE VENTAS")
        total_ventas = len(ventas)
        estados = {
           'Finalizada': 0,
           'En Preparación': 0,
           'Por Cobrar': 0,
           'Cancelada': 0,
           'Mixto': 0
       }
        suma_total_venta = 0
        suma_efectivo = 0
        suma_qr = 0
        suma_total_pagado = 0
        for venta in ventas:
            estado = venta[11]
            if estado in estados:
                estados[estado] += 1
            if estado != 'Cancelada':
                suma_total_venta += float(venta[7])
            suma_efectivo += float(venta[8])
            suma_qr += float(venta[9])
            suma_total_pagado += float(venta[10])
        resumen_texto = f"""
            Periodo: {periodo}
            Total de ventas: {total_ventas}
            Distribución por estado:
            - Finalizadas: {estados['Finalizada']}
            - En Preparación: {estados['En Preparación']}
            - Por Cobrar: {estados['Por Cobrar']}
            - Canceladas: {estados['Cancelada']}
            - Mixto: {estados['Mixto']} 
            
            Suma total de ventas (excluyendo canceladas): {suma_total_venta:.2f} Bs.
            Suma en efectivo: {suma_efectivo:.2f} Bs.
            Suma en QR: {suma_qr:.2f} Bs.
            Suma total pagado: {suma_total_pagado:.2f} Bs.
            """
        pdf.chapter_body(resumen_texto)
        if ventas:
            pdf.chapter_title("RESUMEN DE VENTAS")
            headers = ["N°", "Fecha", "Hora", "Mesero (Apertura)", "Cajero", "Salón", "Mesa", "Total", "Efectivo", "QR", "Pagado", "Estado"]
            col_widths = [8, 22, 15, 25, 25, 20, 15, 20, 20, 15, 20, 25]
            table_data = []
            for venta in ventas:
                num_venta, fecha, hora, mesero_apertura, cajero, salon, mesa, total_venta, efectivo, qr, total_pagado, estado_venta = venta
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                table_data.append([
                    num_venta,
                    fecha_formateada,
                    hora,
                    mesero_apertura,
                    cajero,
                    salon,
                    mesa,
                    f"{float(total_venta):.2f}",
                    f"{float(efectivo):.2f}",
                    f"{float(qr):.2f}",
                    f"{float(total_pagado):.2f}",
                    estado_venta
                ])
            pdf.add_table(headers, table_data, col_widths)
            if len(ventas) > 0:
                pdf.add_page()
                pdf.chapter_title("DETALLE DE CADA VENTA")
                for venta in ventas:
                    num_venta, fecha, hora, mesero_apertura, cajero, salon, mesa, total_venta, efectivo, qr, total_pagado, estado_venta = venta
                    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
                    fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                    productos_detalle = self.obtenerDetallesProductosVenta(num_venta, fecha)
                    if productos_detalle:
                        pdf.add_detalle_venta(
                            num_venta=num_venta,
                            fecha=fecha_formateada,
                            hora=hora,
                            mesero_apertura=mesero_apertura,
                            cajero=cajero,
                            salon=salon,
                            mesa=mesa,
                            productos_detalle=productos_detalle
                        )
                        if pdf.get_y() > 250:
                            pdf.add_page()
        self.enviarPorCorreo(pdf, "Reporte Completo de Ventas")
    

    def generarReporteStock(self, solo_mostrar=True):
        query = """
            SELECT s.nomIng, s.cantidadStock, s.unidadMedida
            FROM Stock s
            ORDER BY s.nomIng
        """
        self.cursor.execute(query)
        stock = self.cursor.fetchall()
        self.tablaResultados.setColumnCount(3)
        headers = ["Ingrediente", "Cantidad", "Unidad"]
        self.tablaResultados.setHorizontalHeaderLabels(headers)
        self.tablaResultados.setRowCount(len(stock))
        for row, (nomIng, cantidadStock, unidadMedida) in enumerate(stock):
            it0 = QTableWidgetItem(str(nomIng))
            it0.setTextAlignment(Qt.AlignCenter)
            it0.setFont(QFont("Arial", 11))
            self.tablaResultados.setItem(row, 0, it0)
            it1 = QTableWidgetItem(_fmt2(cantidadStock))
            it1.setTextAlignment(Qt.AlignCenter)
            it1.setFont(QFont("Arial", 11))
            self.tablaResultados.setItem(row, 1, it1)
            it2 = QTableWidgetItem(str(unidadMedida))
            it2.setTextAlignment(Qt.AlignCenter)
            it2.setFont(QFont("Arial", 11))
            self.tablaResultados.setItem(row, 2, it2)
        QTimer.singleShot(50, self.ajustarTamanos)
        if not solo_mostrar:
            total_ingredientes = len(stock)
            self.generarPDFStock(stock, total_ingredientes)
    

    def generarPDFStock(self, stock, total_ingredientes):
        pdf = PDFReport(tipo_reporte="Stock")
        pdf.add_page()
        pdf.chapter_title("RESUMEN DE STOCK")
        resumen_texto = f"Total de ingredientes: {total_ingredientes}"
        pdf.chapter_body(resumen_texto)
        if stock:
            pdf.chapter_title("DETALLE DE STOCK")
            headers = ["Ingrediente", "Cantidad", "Unidad"]
            table_data = []
            for nomIng, cantidadStock, unidadMedida in stock:
                table_data.append([
                    str(nomIng),
                    _fmt2(cantidadStock),
                    str(unidadMedida)
                ])
            pdf.add_table(headers, table_data)
        self.enviarPorCorreo(pdf, "Reporte de Stock")
    

    def enviarPorCorreo(self, pdf, asunto, es_detalle_venta=False, info_adicional=None):
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False, mode='wb') as temp_file:
                temp_path = temp_file.name
            pdf.output(temp_path)
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                QMessageBox.warning(self, "Advertencia", f"No se pudo generar el archivo PDF de {asunto.lower()}")
                return
            conn_cfg = sqlite3.connect(DB_PATH)
            cur_cfg = conn_cfg.cursor()
            cur_cfg.execute("""
                SELECT correoCuenta, contCuenta
                FROM Cuenta
                WHERE activaCuenta = 1
                LIMIT 1
            """)
            row = cur_cfg.fetchone()
            conn_cfg.close()
            if not row:
                QMessageBox.information(
                    self,
                    "Información",
                    "No existe una cuenta de correo activa para enviar reportes.\n"
                    "Configure una en el módulo de cuentas.\n\n"
                    "IMPORTANTE: Para Gmail, necesitas usar una 'Contraseña de aplicación' \n"
                    "en lugar de tu contraseña normal. Puedes generar una en:\n"
                    "https://myaccount.google.com/apppasswords"
                )
                return
            from_email, password = row
            to_email = from_email
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = f"{asunto} - {datetime.now().strftime('%d/%m/%Y')}"
            if es_detalle_venta and info_adicional:
                cuerpo = f"""Se ha generado el detalle de venta #{info_adicional['num_venta']} con fecha {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}.
                Fecha de venta: {info_adicional['fecha_venta']}
                Hora de venta: {info_adicional['hora_venta']}
                Empleado: {info_adicional['empleado']}
                Total: {info_adicional['total']} Bs.
                Este es un mensaje automático, por favor no responder.
                """
            else:
                cuerpo = f"""Se ha generado el {asunto.lower()} con fecha {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}.
                    Este es un mensaje automático, por favor no responder.
                    """
            msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
            with open(temp_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 
                               f'attachment; filename="{asunto.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"')
                msg.attach(part)
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(from_email, password)
                server.send_message(msg)
                server.quit()
                if es_detalle_venta:
                    QMessageBox.information(self, "Éxito", 
                        f"El detalle de venta #{info_adicional['num_venta']} ha sido enviado por correo electrónico a {to_email}")
                else:
                    QMessageBox.information(self, "Éxito", 
                        f"El {asunto.lower()} ha sido generado y enviado por correo electrónico a {to_email}")
            except smtplib.SMTPAuthenticationError as e:
                QMessageBox.warning(self, "Error de Autenticación",
                    f"No se pudo autenticar con el servidor de correo:\n\n"
                    f"Error: {str(e)}\n\n"
                    f"Para Gmail, necesitas usar una 'Contraseña de aplicación' en lugar de tu contraseña normal.\n"
                    f"Puedes generar una en: https://myaccount.google.com/apppasswords")
            except Exception as e:
                QMessageBox.warning(self, "Error al Enviar Correo",
                    f"No se pudo enviar el correo: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")
            import traceback
            print(traceback.format_exc())
        finally:
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except:
                pass
    

    def limpiarFiltros(self):
        hoy = QDate.currentDate()
        hace30Dias = hoy.addDays(-30)
        self.dateInicio.setDate(hace30Dias)
        self.dateFin.setDate(hoy)
        self.checkEmpleado.setChecked(False)
        self.comboEmpleado.setCurrentIndex(0)
        self.limpiarTabla()
    

    def onCellDoubleClicked(self, row, column):
        if row < self.tablaResultados.rowCount():
            num_venta_item = self.tablaResultados.item(row, 0)
            fecha_item = self.tablaResultados.item(row, 1)        
            if num_venta_item and fecha_item:
                num_venta = num_venta_item.text()
                fecha_str = fecha_item.text()
                try:
                    fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
                    fecha_db = fecha_obj.strftime("%Y-%m-%d")
                    self.mostrarDetalleVentaSimple(num_venta, fecha_db)
                except ValueError:
                    QMessageBox.warning(self, "Error", "Formato de fecha inválido")
    

    def mostrarDetalleVentaSimple(self, num_venta, fecha):
        query_venta = """
            SELECT 
                v.numVenta,
                DATE(v.fechaReg) as fecha,
                v.horaReg,
                e1.aliasEmp as mesero_apertura,
                CASE 
                    WHEN v.codEmp2 = -1 THEN 'DIRECTORIO'
                    ELSE e2.aliasEmp 
                END as cajero,
                s.nombSeccion,
                m.idMesa,
                v.totalVenta,
                COALESCE(SUM(CASE WHEN p.idMetodo = 1 THEN p.monto ELSE 0 END), 0) as efectivo,
                COALESCE(SUM(CASE WHEN p.idMetodo = 2 THEN p.monto ELSE 0 END), 0) as qr,
                COALESCE(SUM(p.monto), 0) as total_pagado,
                CASE 
                 WHEN NOT EXISTS (
                     SELECT 1 FROM DetallesVenta d 
                     WHERE d.numVenta = v.numVenta 
                     AND d.fechaRegVenta = v.fechaReg
                     AND d.estadoDetalleVenta != 'Cancelada'
                 ) THEN 'Cancelada'
                 
                 WHEN EXISTS (
                     SELECT 1 FROM DetallesVenta d 
                     WHERE d.numVenta = v.numVenta 
                     AND d.fechaRegVenta = v.fechaReg
                     AND d.estadoDetalleVenta = 'Preparacion'
                 ) THEN 'En Preparación'
                 
                 WHEN NOT EXISTS (
                     SELECT 1 FROM DetallesVenta d 
                     WHERE d.numVenta = v.numVenta 
                     AND d.fechaRegVenta = v.fechaReg
                     AND d.estadoDetalleVenta != 'Finalizado'
                 ) THEN 'Finalizada'
                 
                 WHEN NOT EXISTS (
                     SELECT 1 FROM DetallesVenta d 
                     WHERE d.numVenta = v.numVenta 
                     AND d.fechaRegVenta = v.fechaReg
                     AND d.estadoDetalleVenta != 'Cobrar'
                 ) THEN 'Por Cobrar'
                 
                 ELSE 'Mixto'
             END AS estado_venta
            FROM Venta v
            JOIN Empleado e1 ON v.codEmp = e1.codEmp
            LEFT JOIN Empleado e2 ON v.codEmp2 = e2.codEmp
            JOIN Seccion s ON v.idSeccion = s.idSeccion
            JOIN Mesa m ON v.idMesa = m.idMesa AND v.idSeccion = m.idSeccion
            LEFT JOIN Pago p ON v.numVenta = p.numVenta AND p.fechaRegVenta = v.fechaReg
            WHERE v.numVenta = ? AND DATE(v.fechaReg) = ?
            GROUP BY v.numVenta, v.fechaReg, v.horaReg, e1.aliasEmp, e2.aliasEmp, v.codEmp2, s.nombSeccion, m.idMesa, v.totalVenta
        """    
        self.cursor.execute(query_venta, (num_venta, fecha))
        info_venta = self.cursor.fetchone()
        if not info_venta:
            QMessageBox.warning(self, "Error", f"No se encontró la venta #{num_venta}")
            return
        productos_detalle = self.obtenerDetallesProductosVenta(num_venta, fecha)
        

        class CustomTableWidget(QTableWidget):
            def resizeEvent(inner_self, event):
                QTableWidget.resizeEvent(inner_self, event)
                ancho_tabla = inner_self.viewport().width()
                if ancho_tabla > 0:
                    inner_self.setColumnWidth(0, int(ancho_tabla * 0.10))
                    inner_self.setColumnWidth(1, int(ancho_tabla * 0.45))
                    inner_self.setColumnWidth(2, int(ancho_tabla * 0.12))
                    inner_self.setColumnWidth(3, int(ancho_tabla * 0.15))
                    inner_self.setColumnWidth(4, int(ancho_tabla * 0.18))
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalle Venta #{num_venta}")
        dialog.setMinimumWidth(900)
        dialog.setMinimumHeight(600)
        layout = QVBoxLayout(dialog)
        num_venta_db, fecha_db, hora, mesero_apertura, cajero, salon, mesa, total_venta, efectivo, qr, total_pagado, estado_venta = info_venta
        if estado_venta == 'Finalizada':
            color_estado = "#27ae60"
        elif estado_venta == 'En Preparación':
            color_estado = "#f39c12"
        elif estado_venta == 'Por Cobrar':
            color_estado = "#3498db"
        elif estado_venta == 'Cancelada':
            color_estado = "#e74c3c"
        elif estado_venta == 'Mixto':
            color_estado = "#9b59b6" 
        else:
            color_estado = "#95a5a6"
        fecha_obj = datetime.strptime(fecha_db, "%Y-%m-%d")
        fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
        ubicacion = f"{salon} - Mesa {mesa}" if salon and mesa and mesa != '0' else "Para Llevar"
        info_text = f"""
        <div style='font-size: 14px;'>
        <h3 style='color: #2c3e50; font-size: 16px;'>VENTA #{num_venta_db}</h3>
        <table style='width: 100%; font-size: 13px;'>
            <tr>
                <td style='width: 120px; font-weight: bold;'>Fecha:</td>
                <td>{fecha_formateada}</td>
            </tr>
            <tr>
                <td style='font-weight: bold;'>Hora:</td>
                <td>{hora}</td>
            </tr>
            <tr>
                <td style='font-weight: bold;'>Mesero (Apertura):</td>
                <td>{mesero_apertura}</td>
            </tr>
            <tr>
                <td style='font-weight: bold;'>Cajero:</td>
                <td>{cajero}</td>
            </tr>
            <tr>
                <td style='font-weight: bold;'>Ubicación:</td>
                <td>{ubicacion}</td>
            </tr>
            <tr>
                <td style='font-weight: bold;'>Estado:</td>
                <td style='color: {color_estado}; font-weight: bold;'>{estado_venta}</td>
            </tr>
            <tr>
                <td style='font-weight: bold;'>Total Venta:</td>
                <td style='color: #e74c3c; font-weight: bold;'>{float(total_venta):.2f} Bs.</td>
            </tr>
            <tr>
                <td style='font-weight: bold;'>Efectivo:</td>
                <td style='color: #27ae60;'>{float(efectivo):.2f} Bs.</td>
            </tr>
            <tr>
                <td style='font-weight: bold;'>QR:</td>
                <td style='color: #2980b9;'>{float(qr):.2f} Bs.</td>
            </tr>
            <tr>
                <td style='font-weight: bold;'>Total Pagado:</td>
                <td style='color: #9b59b6; font-weight: bold;'>{float(total_pagado):.2f} Bs.</td>
            </tr>
        </table>
        </div>
        """
        label_info = QLabel(info_text)
        label_info.setTextFormat(Qt.RichText)
        layout.addWidget(label_info)
        layout.addSpacing(20)
        if productos_detalle:
            grupo_tabla = QGroupBox("Productos de la Venta (Detallados por mesero)")
            grupo_tabla.setStyleSheet("""
                QGroupBox { 
                    font-weight: bold; 
                    border: 2px solid #e2e8f0; 
                    border-radius: 8px; 
                    margin-top: 1ex; 
                    padding-top: 10px; 
                    background-color: #ffffff; 
                } 
                QGroupBox::title { 
                    subcontrol-origin: margin; 
                    subcontrol-position: top center; 
                    padding: 0 5px; 
                    background-color: #3498db; 
                    color: white; 
                    border-radius: 4px; 
                }
            """)
            layout_tabla = QVBoxLayout(grupo_tabla)
            tabla = CustomTableWidget()
            tabla.setColumnCount(5)
            tabla.setHorizontalHeaderLabels(["Cantidad", "Producto", "Tipo", "Subtotal", "Mesero"])
            tabla.setRowCount(len(productos_detalle))
            tabla.setAlternatingRowColors(True)
            tabla.setEditTriggers(QTableWidget.NoEditTriggers)
            tabla.setSelectionMode(QTableWidget.SingleSelection)
            tabla.verticalHeader().setVisible(False)
            tabla.horizontalHeader().setStretchLastSection(True)
            total_productos = 0
            for row, (cantidad, producto, tipo_consumo, subtotal, mesero_detalle) in enumerate(productos_detalle):
                item1 = QTableWidgetItem(str(cantidad))
                item1.setTextAlignment(Qt.AlignCenter)
                item1.setFont(QFont("Arial", 11))
                tabla.setItem(row, 0, item1)
                item2 = QTableWidgetItem(producto if producto else "N/A")
                item2.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item2.setFont(QFont("Arial", 11))
                tabla.setItem(row, 1, item2)
                tipo_text = "Local" if str(tipo_consumo).upper() == "LOCAL" else "Llevar"
                item3 = QTableWidgetItem(tipo_text)
                item3.setTextAlignment(Qt.AlignCenter)
                item3.setFont(QFont("Arial", 11))
                tabla.setItem(row, 2, item3)
                item4 = QTableWidgetItem(f"{float(subtotal):.2f} Bs.")
                item4.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item4.setFont(QFont("Arial", 11))
                tabla.setItem(row, 3, item4)
                item5 = QTableWidgetItem(mesero_detalle)
                item5.setTextAlignment(Qt.AlignCenter)
                item5.setFont(QFont("Arial", 11))
                tabla.setItem(row, 4, item5)
                total_productos += float(subtotal)
            tabla.setRowCount(len(productos_detalle) + 1)
            item_total1 = QTableWidgetItem("TOTAL")
            item_total1.setFont(QFont("Arial", 11, QFont.Bold))
            item_total1.setTextAlignment(Qt.AlignCenter)
            item_total1.setBackground(QColor(240, 248, 255))
            tabla.setItem(len(productos_detalle), 0, item_total1)
            item_total2 = QTableWidgetItem("")
            item_total2.setBackground(QColor(240, 248, 255))
            tabla.setItem(len(productos_detalle), 1, item_total2)
            item_total3 = QTableWidgetItem("")
            item_total3.setBackground(QColor(240, 248, 255))
            tabla.setItem(len(productos_detalle), 2, item_total3)
            item_total4 = QTableWidgetItem(f"{total_productos:.2f} Bs.")
            item_total4.setFont(QFont("Arial", 11, QFont.Bold))
            item_total4.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_total4.setForeground(QColor(0, 100, 0))
            item_total4.setBackground(QColor(240, 248, 255))
            tabla.setItem(len(productos_detalle), 3, item_total4)
            item_total5 = QTableWidgetItem("")
            item_total5.setBackground(QColor(240, 248, 255))
            tabla.setItem(len(productos_detalle), 4, item_total5)
            layout_tabla.addWidget(tabla)
            layout.addWidget(grupo_tabla, 1)
            
            def ajustar_columnas_inicial():
                ancho_tabla = tabla.viewport().width()
                if ancho_tabla > 0:
                    tabla.setColumnWidth(0, int(ancho_tabla * 0.10))
                    tabla.setColumnWidth(1, int(ancho_tabla * 0.45))
                    tabla.setColumnWidth(2, int(ancho_tabla * 0.12))
                    tabla.setColumnWidth(3, int(ancho_tabla * 0.15))
                    tabla.setColumnWidth(4, int(ancho_tabla * 0.18))
                    for i in range(tabla.rowCount()):
                        tabla.setRowHeight(i, 40)
    
            QTimer.singleShot(50, ajustar_columnas_inicial)
    
        layout.addSpacing(20)    
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 120px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_cerrar.setFixedHeight(45)
        btn_cerrar.clicked.connect(dialog.close)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMaximizeButtonHint)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = Reportes()
    pagina.show()
    sys.exit(app.exec_())