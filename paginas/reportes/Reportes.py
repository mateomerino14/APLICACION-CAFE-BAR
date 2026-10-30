import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from datetime import datetime
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import tempfile
import webbrowser
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from nucleo.Rutas import get_db_path


def _fmt2(x):
    d = Decimal(str(x)) if x is not None else Decimal("0")
    return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


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
        '\u201c': '"',
        '\u201d': '"',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


class PDFReport(FPDF):
    def __init__(self, tipo_reporte, periodo=None, empleado=None, subreporte=None):
        super().__init__()
        self.tipo_reporte = tipo_reporte
        self.periodo = periodo
        self.empleado = empleado
        self.subreporte = subreporte
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'CAFE BAR - REPORTE', 0, 1, 'C')
        self.set_font('Arial', 'B', 14)
        titulo = f'Reporte de {self.tipo_reporte}'
        if self.subreporte:
            titulo = f'{titulo} - {self.subreporte}'
        self.cell(0, 10, titulo, 0, 1, 'C')
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
            elif len(headers) == 4:
                col_widths = [35, 80, 35, 40]
            elif len(headers) == 5:
                col_widths = [35, 30, 35, 35, 35]
            elif len(headers) == 6:
                col_widths = [30, 35, 20, 35, 35, 35]
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
        for row in data:
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

    def add_detalle_venta(
        self,
        num_venta,
        fecha,
        hora,
        mesero_apertura,
        cajero,
        salon,
        mesa,
        productos_detalle,
        hora_cierre=None,
        duracion=None,
    ):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, f'VENTA #{num_venta}', 0, 1, 'L')

        self.set_font('Arial', '', 9)
        self.cell(0, 6, f'Fecha: {fecha} | Hora Inicio: {hora}', 0, 1, 'L')
        texto_cierre = hora_cierre if hora_cierre else "En proceso"
        texto_duracion = duracion if duracion else "En proceso"
        self.cell(0, 6, f'Hora Cierre: {texto_cierre} | Duracion: {texto_duracion}', 0, 1, 'L')
        self.cell(0, 6, f'Mesero (Apertura): {mesero_apertura} | Cajero: {cajero}', 0, 1, 'L')
        if salon and mesa and mesa != '0':
            self.cell(0, 6, f'Ubicación: {salon} - Mesa {mesa}', 0, 1, 'L')
        else:
            self.cell(0, 6, 'Ubicación: Para Llevar', 0, 1, 'L')
        self.ln(2)

        if productos_detalle:
            self.set_font('Arial', 'B', 9)
            headers = ["Cantidad", "Producto", "Tipo", "Subtotal", "Mesero"]
            col_widths = [15, 85, 20, 25, 25]

            for i, header in enumerate(headers):
                self.cell(col_widths[i], 8, header, 1, 0, 'C')
            self.ln()

            self.set_font('Arial', '', 8)
            total_venta = 0

            for (
                cantidad,
                producto,
                tipo_consumo,
                subtotal,
                mesero_detalle,
                personalizacion,
                ids_det,
                es_promocion,
            ) in productos_detalle:
                lineas_personalizacion = []
                if personalizacion:
                    for linea_personalizacion in personalizacion.split("\n"):
                        linea_limpia = linea_personalizacion.strip()
                        if not linea_limpia:
                            continue
                        fragmentos = [linea_limpia[i : i + 75] for i in range(0, len(linea_limpia), 75)]
                        lineas_personalizacion.extend(fragmentos)

                borde_fila_producto = 'LTR' if lineas_personalizacion else 1

                self.cell(col_widths[0], 8, str(cantidad), borde_fila_producto, 0, 'C')

                prod_text = str(producto) if producto else "N/A"
                if len(prod_text) > 40:
                    prod_text = prod_text[:37] + "..."
                self.cell(col_widths[1], 8, prod_text, borde_fila_producto, 0, 'L')

                tipo_text = "Local" if str(tipo_consumo).upper() == "LOCAL" else "Llevar"
                self.cell(col_widths[2], 8, tipo_text, borde_fila_producto, 0, 'C')

                self.cell(col_widths[3], 8, f"{float(subtotal):.2f}", borde_fila_producto, 0, 'R')
                self.cell(col_widths[4], 8, mesero_detalle, borde_fila_producto, 0, 'C')
                self.ln()
                total_venta += float(subtotal)

                if lineas_personalizacion:
                    self.set_font('Arial', 'I', 7)
                    for idx_linea, fragmento in enumerate(lineas_personalizacion):
                        es_ultima = idx_linea == len(lineas_personalizacion) - 1
                        borde_linea = 'LRB' if es_ultima else 'LR'
                        self.cell(col_widths[0], 5, "", borde_linea, 0, 'C')
                        self.cell(sum(col_widths[1:]), 5, fragmento, borde_linea, 1, 'L')
                    self.set_font('Arial', '', 8)

            self.set_font('Arial', 'B', 9)
            self.cell(sum(col_widths[0:4]), 8, "TOTAL:", 1, 0, 'R')
            self.cell(col_widths[4], 8, f"{total_venta:.2f}", 1, 0, 'R')
            self.ln()

        self.ln(5)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)


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
            padding: 10px 20px; 
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
        QLabel { 
            color: #2c3e50; 
            font-size: 13px; 
            font-weight: 500; 
            margin-bottom: 3px; 
        }
        QTableWidget { 
            background-color: white; 
            border: 2px solid #e2e8f0; 
            border-radius: 8px; 
            gridline-color: #e2e8f0; 
            font-size: 14px; 
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QTableWidget::item { 
            padding: 8px; 
            border-bottom: 1px solid #e2e8f0; 
        }
        QTableWidget::item:selected {
            background-color: transparent;
            color: #2c3e50;
        }
        QTableWidget::item:focus {
            outline: none;
            border: none;
        }
        QTableWidget::item:hover {
            background-color: transparent;
        }
        QHeaderView::section { 
            background-color: #3498db; 
            color: white; 
            padding: 10px; 
            border: none; 
            font-weight: bold; 
            font-size: 14px; 
            font-family: 'Segoe UI', Arial, sans-serif;
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
        QComboBox {
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 5px 10px;
            font-size: 13px;
            min-height: 25px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QDateEdit {
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 5px 8px;
            font-size: 13px;
            min-height: 25px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QScrollArea {
            border: none;
            background: transparent;
        }
        QScrollBar:vertical {
            border: none;
            background: #f1f5f9;
            width: 10px;
            margin: 0px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #cbd5e1;
            min-height: 30px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background: #94a3b8;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        """)
        self.set_up()
        self.fecha_inicio_actual = None
        self.fecha_fin_actual = None

    def set_up(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.layoutPrincipal.setSpacing(15)
        self.tablaResultados = None
        self.canvas = None
        self.grafica_tipo = "cajero"
        QLocale.setDefault(QLocale(QLocale.Spanish, QLocale.Bolivia))
        self.iniciarInterfaz()

    def iniciarInterfaz(self):
        panelFiltros = QWidget()
        panelFiltros.setFixedWidth(310)
        panelFiltros.setStyleSheet("""
            QWidget { 
                background-color: #ffffff; 
                border-radius: 8px; 
                border: 1px solid #e2e8f0; 
            }
        """)

        scrollArea = QScrollArea()
        scrollArea.setWidget(panelFiltros)
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollArea.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
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

        grupoSubreporte = QGroupBox("Subreporte de Ventas")
        grupoSubreporte.setStyleSheet(grupoTipo.styleSheet())
        layoutSubreporte = QVBoxLayout(grupoSubreporte)
        layoutSubreporte.setSpacing(10)
        self.comboSubreporte = QComboBox()
        self.comboSubreporte.addItem("Ventas Detalladas", "detallado")
        self.comboSubreporte.addItem("Resumen por Fechas", "resumen_fechas")
        self.comboSubreporte.addItem("Resumen por Empleado", "resumen_empleado")
        self.comboSubreporte.addItem("Productos Más Vendidos", "productos_vendidos")
        self.comboSubreporte.currentIndexChanged.connect(self.actualizarOpcionesFiltro)
        self.comboSubreporte.setFixedHeight(35)
        self.comboSubreporte.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 13px;
                min-height: 25px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #e2e8f0;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #4a89dc;
                width: 0;
                height: 0;
            }
        """)
        layoutSubreporte.addWidget(QLabel("Seleccione el tipo de análisis:"))
        layoutSubreporte.addWidget(self.comboSubreporte)
        layoutFiltros.addWidget(grupoSubreporte)

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
        self.dateInicio.setLocale(QLocale(QLocale.Spanish, QLocale.Bolivia))
        self.dateInicio.setFixedHeight(35)
        self.dateInicio.setStyleSheet("""
            QDateEdit {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 5px 8px;
                font-size: 13px;
                min-height: 25px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QDateEdit::drop-down {
                width: 25px;
                border-left: 1px solid #e2e8f0;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #4a89dc;
                width: 0;
                height: 0;
            }
        """)
        layoutFechaInicio.addWidget(self.dateInicio)
        layoutFechas.addLayout(layoutFechaInicio)

        layoutFechaFin = QHBoxLayout()
        layoutFechaFin.addWidget(QLabel("Hasta:"))
        self.dateFin = QDateEdit()
        self.dateFin.setDate(hoy)
        self.dateFin.setCalendarPopup(True)
        self.dateFin.setDisplayFormat("dd-MM-yyyy")
        self.dateFin.setLocale(QLocale(QLocale.Spanish, QLocale.Bolivia))
        self.dateFin.setFixedHeight(35)
        self.dateFin.setStyleSheet("""
            QDateEdit {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 5px 8px;
                font-size: 13px;
                min-height: 25px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QDateEdit::drop-down {
                width: 25px;
                border-left: 1px solid #e2e8f0;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #4a89dc;
                width: 0;
                height: 0;
            }
        """)
        layoutFechaFin.addWidget(self.dateFin)
        layoutFechas.addLayout(layoutFechaFin)
        layoutFiltros.addWidget(grupoFechas)

        grupoEmpleado = QGroupBox("Filtro por Empleado")
        grupoEmpleado.setStyleSheet(grupoTipo.styleSheet())
        layoutEmpleado = QVBoxLayout(grupoEmpleado)
        layoutEmpleado.setSpacing(10)
        self.checkEmpleado = QCheckBox("Filtrar por empleado")
        self.checkEmpleado.toggled.connect(self.toggleFiltroEmpleado)
        self.comboEmpleado = QComboBox()
        self.comboEmpleado.setEnabled(False)
        self.comboEmpleado.setFixedHeight(35)
        self.comboEmpleado.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 13px;
                min-height: 25px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #e2e8f0;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #4a89dc;
                width: 0;
                height: 0;
            }
        """)
        layoutEmpleado.addWidget(self.checkEmpleado)
        layoutEmpleado.addWidget(QLabel("Seleccionar empleado:"))
        layoutEmpleado.addWidget(self.comboEmpleado)
        layoutFiltros.addWidget(grupoEmpleado)

        grupoInfo = QGroupBox("Información")
        grupoInfo.setStyleSheet(grupoTipo.styleSheet())
        layoutInfo = QVBoxLayout(grupoInfo)
        layoutInfo.setSpacing(8)
        self.info_text = QLabel("""
        <b>📌 ¿Cómo funciona el filtro?</b><br>
        • <b>Ventas Detalladas / Resumen por Fechas:</b><br>
          &nbsp;&nbsp;Filtran por CAJERO<br>
        • <b>Resumen por Empleado:</b><br>
          &nbsp;&nbsp;Sin filtro: Gráfica de ventas por empleado<br>
          &nbsp;&nbsp;Con filtro: Tabla de ventas del empleado<br>
        • <b>Productos Más Vendidos:</b><br>
          &nbsp;&nbsp;No tiene filtro
        """)
        self.info_text.setWordWrap(True)
        self.info_text.setTextFormat(Qt.RichText)
        self.info_text.setStyleSheet("font-size: 11px; color: #2c3e50; padding: 5px;")
        layoutInfo.addWidget(self.info_text)
        layoutFiltros.addWidget(grupoInfo)

        btnMostrarInfo = QPushButton("Mostrar Información")
        btnMostrarInfo.setStyleSheet("""
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                border-radius: 8px; 
                padding: 10px 20px; 
                font-size: 14px; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #2980b9; 
            }
        """)
        btnMostrarInfo.setFixedHeight(45)
        btnMostrarInfo.clicked.connect(self.mostrarInformacion)
        layoutFiltros.addWidget(btnMostrarInfo)

        btnGenerar = QPushButton("Generar y Abrir PDF")
        btnGenerar.setStyleSheet("""
            QPushButton { 
                background-color: #2ecc71; 
                color: white; 
                border-radius: 8px; 
                padding: 10px 20px; 
                font-size: 14px; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #27ae60; 
            }
        """)
        btnGenerar.setFixedHeight(45)
        btnGenerar.clicked.connect(self.generarYMostrarPDF)
        layoutFiltros.addWidget(btnGenerar)

        btnGenerarCorreo = QPushButton("Generar y Enviar por Correo")
        btnGenerarCorreo.setStyleSheet("""
            QPushButton { 
                background-color: #f39c12; 
                color: white; 
                border-radius: 8px; 
                padding: 10px 20px; 
                font-size: 14px; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #e67e22; 
            }
        """)
        btnGenerarCorreo.setFixedHeight(45)
        btnGenerarCorreo.clicked.connect(self.generarReporte)
        layoutFiltros.addWidget(btnGenerarCorreo)

        btnLimpiar = QPushButton("Limpiar Filtros")
        btnLimpiar.setStyleSheet("""
            QPushButton { 
                background-color: #95a5a6; 
                color: white; 
                border-radius: 8px; 
                padding: 10px 20px; 
                font-size: 14px; 
                font-weight: bold; 
            }
            QPushButton:hover { 
                background-color: #7f8c8d; 
            }
        """)
        btnLimpiar.setFixedHeight(45)
        btnLimpiar.clicked.connect(self.limpiarFiltros)
        layoutFiltros.addWidget(btnLimpiar)
        layoutFiltros.addStretch()

        panelResultados = QWidget()
        layoutResultados = QVBoxLayout(panelResultados)
        layoutResultados.setContentsMargins(0, 0, 0, 0)
        layoutResultados.setSpacing(0)

        self.stackedWidget = QStackedWidget()
        self.tablaResultados = QTableWidget()
        self.tablaResultados.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tablaResultados.setSelectionMode(QTableWidget.NoSelection)
        self.tablaResultados.setFocusPolicy(Qt.NoFocus)
        self.tablaResultados.verticalHeader().setVisible(False)
        self.tablaResultados.setAlternatingRowColors(True)
        self.tablaResultados.cellDoubleClicked.connect(self.onCellDoubleClicked)

        self.lblTotalResumen = QLabel("")
        self.lblTotalResumen.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #2c3e50;
                background-color: #eafaf1;
                border: 2px solid #a9dfbf;
                border-radius: 8px;
                padding: 10px 15px;
            }
        """)
        self.lblTotalResumen.setVisible(False)

        self.contenedorTabla = QWidget()
        layoutContenedorTabla = QVBoxLayout(self.contenedorTabla)
        layoutContenedorTabla.setContentsMargins(0, 0, 0, 0)
        layoutContenedorTabla.setSpacing(10)
        layoutContenedorTabla.addWidget(self.tablaResultados)
        layoutContenedorTabla.addWidget(self.lblTotalResumen)

        self.graficaContainer = QWidget()
        graficaLayout = QVBoxLayout(self.graficaContainer)

        self.botonera = QHBoxLayout()
        self.btnCajeros = QPushButton("Ver Ventas como Cajero")
        self.btnCajeros.setStyleSheet("background-color: #3498db; color: white; padding: 8px; border-radius: 6px;")
        self.btnCajeros.clicked.connect(lambda: self.cambiarGrafica("cajero"))
        self.btnMeseros = QPushButton("Ver Ventas como Mesero")
        self.btnMeseros.setStyleSheet("background-color: #2ecc71; color: white; padding: 8px; border-radius: 6px;")
        self.btnMeseros.clicked.connect(lambda: self.cambiarGrafica("mesero"))
        self.botonera.addWidget(self.btnCajeros)
        self.botonera.addWidget(self.btnMeseros)
        graficaLayout.addLayout(self.botonera)

        self.canvas = MplCanvas(self, width=8, height=5, dpi=100)
        graficaLayout.addWidget(self.canvas)

        self.stackedWidget.addWidget(self.contenedorTabla)
        self.stackedWidget.addWidget(self.graficaContainer)

        layoutResultados.addWidget(self.stackedWidget)

        layoutContenedor = QHBoxLayout()
        layoutContenedor.setSpacing(20)
        layoutContenedor.setContentsMargins(0, 0, 0, 0)
        layoutContenedor.addWidget(scrollArea)
        layoutContenedor.addWidget(panelResultados, 1)
        self.layoutPrincipal.addLayout(layoutContenedor)
        self.limpiarTabla()
        self.showMaximized()

    def cambiarGrafica(self, tipo):
        self.grafica_tipo = tipo
        if self.fecha_inicio_actual and self.fecha_fin_actual:
            self.mostrarGraficaEmpleados(
                self.fecha_inicio_actual, self.fecha_fin_actual, solo_mostrar=True, abrir_pdf=False
            )

    def cargarEmpleados(self):
        self.comboEmpleado.clear()
        self.comboEmpleado.addItem("Todos los empleados", None)
        self.cursor.execute("SELECT codEmp, aliasEmp FROM Empleado WHERE disponibleEmp = 1 ORDER BY aliasEmp")
        empleados = self.cursor.fetchall()
        for codigo, alias in empleados:
            self.comboEmpleado.addItem(alias, codigo)
        self.comboEmpleado.addItem("DIRECTORIO", -1)

    def actualizarOpcionesFiltro(self):
        subreporte_tipo = self.comboSubreporte.currentData()

        if subreporte_tipo == "productos_vendidos":
            self.checkEmpleado.setEnabled(False)
            self.checkEmpleado.setChecked(False)
            self.comboEmpleado.setEnabled(False)
            self.info_text.setText("""
            <b>📌 ¿Cómo funciona el filtro?</b><br>
            • <b>Productos Más Vendidos:</b><br>
              &nbsp;&nbsp;No tiene filtro, muestra todos los productos del período
            """)
        elif subreporte_tipo == "resumen_empleado":
            self.checkEmpleado.setEnabled(True)
            self.comboEmpleado.setEnabled(self.checkEmpleado.isChecked())
            self.info_text.setText("""
            <b>📌 ¿Cómo funciona el filtro?</b><br>
            • <b>Resumen por Empleado:</b><br>
              &nbsp;&nbsp;Sin filtro: Gráfica de ventas por empleado<br>
              &nbsp;&nbsp;Con filtro: Tabla de ventas del empleado
            """)
        else:
            self.checkEmpleado.setEnabled(True)
            self.comboEmpleado.setEnabled(self.checkEmpleado.isChecked())
            self.info_text.setText("""
            <b>📌 ¿Cómo funciona el filtro?</b><br>
            • <b>Ventas Detalladas / Resumen por Fechas:</b><br>
              &nbsp;&nbsp;Filtran por CAJERO
            """)

        if self.checkEmpleado.isChecked():
            self.cargarEmpleados()

    def toggleFiltroEmpleado(self, activado):
        subreporte_tipo = self.comboSubreporte.currentData()

        if subreporte_tipo == "productos_vendidos":
            self.comboEmpleado.setEnabled(False)
            return

        self.comboEmpleado.setEnabled(activado)
        if activado and self.comboEmpleado.currentData() is not None:
            self.cargarEmpleados()

    def cambiarTipoReporte(self):
        es_reporte_ventas = self.radioVentas.isChecked()
        self.dateInicio.setEnabled(es_reporte_ventas)
        self.dateFin.setEnabled(es_reporte_ventas)

        if es_reporte_ventas:
            self.comboSubreporte.setEnabled(True)
            self.actualizarOpcionesFiltro()
        else:
            self.checkEmpleado.setEnabled(False)
            self.checkEmpleado.setChecked(False)
            self.comboEmpleado.setEnabled(False)
            self.comboSubreporte.setEnabled(False)

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
            porcentajes = [0.1, 0.09, 0.11, 0.11, 0.09, 0.06, 0.09, 0.09, 0.07, 0.09, 0.14]
            for i in range(1, 12):
                ancho = int(espacio_restante * porcentajes[i - 1])
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
        self.stackedWidget.setCurrentWidget(self.contenedorTabla)
        self.lblTotalResumen.setVisible(False)
        self.tablaResultados.setRowCount(0)
        self.tablaResultados.setColumnCount(1)
        self.tablaResultados.setHorizontalHeaderLabels(["Información"])
        item = QTableWidgetItem("Seleccione los filtros y haga clic en 'Mostrar Información'")
        item.setTextAlignment(Qt.AlignCenter)
        item.setFont(QFont("Segoe UI", 12))
        self.tablaResultados.setRowCount(1)
        self.tablaResultados.setItem(0, 0, item)
        self.tablaResultados.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    def mostrarInformacion(self):
        if self.radioVentas.isChecked():
            self.generarReporteVentas(solo_mostrar=True)
        else:
            self.generarReporteStock(solo_mostrar=True)

    def generarYMostrarPDF(self):
        if self.radioVentas.isChecked():
            self.generarReporteVentas(solo_mostrar=False, abrir_pdf=True)
        else:
            self.generarReporteStock(solo_mostrar=False, abrir_pdf=True)

    def generarReporte(self):
        if self.radioVentas.isChecked():
            self.generarReporteVentas(solo_mostrar=False, abrir_pdf=False)
        else:
            self.generarReporteStock(solo_mostrar=False, abrir_pdf=False)

    def generarReporteVentas(self, solo_mostrar=True, abrir_pdf=False):
        fecha_inicio = self.dateInicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.dateFin.date().toString("yyyy-MM-dd")
        empleado_id = None

        self.fecha_inicio_actual = fecha_inicio
        self.fecha_fin_actual = fecha_fin

        subreporte_tipo = self.comboSubreporte.currentData()

        if subreporte_tipo == "productos_vendidos":
            if solo_mostrar:
                self.mostrarProductosVendidosEnTabla(fecha_inicio, fecha_fin)
            else:
                self.generarPDFProductosVendidos(fecha_inicio, fecha_fin, abrir_pdf)
        elif subreporte_tipo == "resumen_empleado":
            if self.checkEmpleado.isChecked():
                empleado_id = self.comboEmpleado.currentData()
                if empleado_id is None:
                    self.mostrarGraficaEmpleados(fecha_inicio, fecha_fin, solo_mostrar, abrir_pdf)
                else:
                    self.mostrarVentasEmpleadoEnTabla(fecha_inicio, fecha_fin, empleado_id, solo_mostrar, abrir_pdf)
            else:
                self.mostrarGraficaEmpleados(fecha_inicio, fecha_fin, solo_mostrar, abrir_pdf)
        else:
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
                     END AS estado_venta,
                    v.horaCierre
                FROM Venta v
                JOIN Empleado e1 ON v.codEmp = e1.codEmp
                LEFT JOIN Empleado e2 ON v.codEmp2 = e2.codEmp
                JOIN Seccion s ON v.idSeccion = s.idSeccion
                JOIN Mesa m ON v.idMesa = m.idMesa AND v.idSeccion = m.idSeccion
                LEFT JOIN Pago p ON v.numVenta = p.numVenta AND p.fechaRegVenta = v.fechaReg
                WHERE DATE(v.fechaReg) BETWEEN ? AND ?
            """
            params = [fecha_inicio, fecha_fin]

            if self.checkEmpleado.isChecked():
                empleado_id = self.comboEmpleado.currentData()
                if empleado_id is not None:
                    if empleado_id == -1:
                        query += " AND v.codEmp2 = -1"
                    else:
                        query += " AND v.codEmp2 = ?"
                        params.append(empleado_id)

            query += " GROUP BY v.numVenta, v.fechaReg, v.horaReg, e1.aliasEmp, e2.aliasEmp, v.codEmp2, s.nombSeccion, m.idMesa, v.totalVenta"
            query += " ORDER BY v.fechaReg, v.horaReg"
            self.cursor.execute(query, params)
            ventas = self.cursor.fetchall()

            if solo_mostrar:
                if subreporte_tipo == "detallado":
                    self.mostrarVentasDetalladasEnTabla(ventas)
                elif subreporte_tipo == "resumen_fechas":
                    self.mostrarResumenFechasEnTabla(ventas)
            else:
                self.generarPDFVentasCompleto(ventas, fecha_inicio, fecha_fin, empleado_id, subreporte_tipo, abrir_pdf)

    def mostrarGraficaEmpleados(self, fecha_inicio, fecha_fin, solo_mostrar=True, abrir_pdf=False):
        if self.grafica_tipo == "cajero":
            query = """
                SELECT 
                    CASE WHEN v.codEmp2 = -1 THEN 'DIRECTORIO' ELSE e.aliasEmp END as empleado,
                    COUNT(DISTINCT v.numVenta) as total_ventas
                FROM Venta v
                LEFT JOIN Empleado e ON v.codEmp2 = e.codEmp
                WHERE DATE(v.fechaReg) BETWEEN ? AND ?
                GROUP BY v.codEmp2
                ORDER BY total_ventas DESC
            """
        else:
            query = """
                SELECT 
                    e.aliasEmp as empleado,
                    COUNT(DISTINCT v.numVenta) as total_ventas
                FROM Venta v
                JOIN Empleado e ON v.codEmp = e.codEmp
                WHERE DATE(v.fechaReg) BETWEEN ? AND ?
                GROUP BY v.codEmp
                ORDER BY total_ventas DESC
            """

        params = [fecha_inicio, fecha_fin]
        self.cursor.execute(query, params)
        datos = self.cursor.fetchall()

        if solo_mostrar:
            self.stackedWidget.setCurrentWidget(self.graficaContainer)
            self.canvas.axes.clear()

            nombres = [row[0] for row in datos]
            ventas = [row[1] for row in datos]

            x = range(len(nombres))
            color = '#2980b9' if self.grafica_tipo == "cajero" else '#27ae60'
            titulo = "Ventas por Cajero" if self.grafica_tipo == "cajero" else "Ventas por Mesero"

            bars = self.canvas.axes.bar(x, ventas, color=color, alpha=0.9)
            self.canvas.axes.set_xlabel('Empleados', fontsize=12)
            self.canvas.axes.set_ylabel('Número de Ventas', fontsize=12)
            self.canvas.axes.set_title(f'{titulo}\nPeríodo: {fecha_inicio} al {fecha_fin}', fontsize=14)
            self.canvas.axes.set_xticks(x)
            self.canvas.axes.set_xticklabels(nombres, rotation=45, ha='right', fontsize=10)

            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    self.canvas.axes.text(
                        bar.get_x() + bar.get_width() / 2,
                        height / 2,
                        f'{int(height)}',
                        ha='center',
                        va='center',
                        fontsize=11,
                        fontweight='bold',
                        color='white',
                    )

            self.canvas.fig.tight_layout()
            self.canvas.draw()
        else:
            self.generarPDFGraficaEmpleados(datos, fecha_inicio, fecha_fin, self.grafica_tipo, abrir_pdf)

    def generarPDFGraficaEmpleados(self, datos, fecha_inicio, fecha_fin, tipo, abrir_pdf):
        fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
        periodo = f"{fecha_inicio_obj.strftime('%d/%m/%Y')} a {fecha_fin_obj.strftime('%d/%m/%Y')}"
        titulo = "Ventas por Cajero" if tipo == "cajero" else "Ventas por Mesero"

        pdf = PDFReport(tipo_reporte="Ventas", periodo=periodo, empleado=None, subreporte=titulo)
        pdf.add_page()
        pdf.chapter_title(titulo)

        plt.figure(figsize=(10, 6))

        nombres = [row[0] for row in datos]
        ventas = [row[1] for row in datos]

        x = range(len(nombres))
        color = '#1a5d8f' if tipo == "cajero" else '#1e7a5c'

        bars = plt.bar(x, ventas, color=color, alpha=0.9)
        plt.xlabel('Empleados', fontsize=12)
        plt.ylabel('Número de Ventas', fontsize=12)
        plt.title(f'{titulo}\nPeríodo: {periodo}', fontsize=14)
        plt.xticks(x, nombres, rotation=45, ha='right', fontsize=10)

        for bar in bars:
            height = bar.get_height()
            if height > 0:
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    height / 2,
                    f'{int(height)}',
                    ha='center',
                    va='center',
                    fontsize=11,
                    fontweight='bold',
                    color='white',
                )

        plt.tight_layout()

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False, mode='wb') as temp_img:
            img_path = temp_img.name
        plt.savefig(img_path, dpi=150, bbox_inches='tight')
        plt.close()

        pdf.image(img_path, x=10, y=pdf.get_y(), w=190)

        os.unlink(img_path)

        self.enviarYMostrarPDF(pdf, "Reporte de Ventas", abrir_pdf)

    def mostrarVentasEmpleadoEnTabla(self, fecha_inicio, fecha_fin, empleado_id, solo_mostrar, abrir_pdf):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        tipo_layout = QHBoxLayout()
        self.chkCajero = QCheckBox("Como Cajero (cobró)")
        self.chkCajero.setChecked(True)
        self.chkMesero = QCheckBox("Como Mesero (atendió)")
        self.chkMesero.setChecked(True)
        tipo_layout.addWidget(self.chkCajero)
        tipo_layout.addWidget(self.chkMesero)

        btnFiltrar = QPushButton("Aplicar Filtro")
        btnFiltrar.setStyleSheet("background-color: #3498db; color: white; padding: 5px 15px; border-radius: 5px;")
        btnFiltrar.clicked.connect(lambda: self.cargarVentasEmpleado(fecha_inicio, fecha_fin, empleado_id))
        tipo_layout.addWidget(btnFiltrar)
        tipo_layout.addStretch()
        layout.addLayout(tipo_layout)

        self.tablaEmpleado = QTableWidget()
        self.tablaEmpleado.setColumnCount(5)
        self.tablaEmpleado.setHorizontalHeaderLabels(["N° Venta", "Fecha", "Hora", "Rol", "Total"])
        self.tablaEmpleado.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablaEmpleado.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tablaEmpleado.setSelectionMode(QTableWidget.NoSelection)
        self.tablaEmpleado.setFocusPolicy(Qt.NoFocus)
        self.tablaEmpleado.verticalHeader().setVisible(False)
        self.tablaEmpleado.setAlternatingRowColors(True)
        layout.addWidget(self.tablaEmpleado)

        self.lblTotalEmpleado = QLabel("")
        self.lblTotalEmpleado.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #2c3e50;
                background-color: #eafaf1;
                border: 2px solid #a9dfbf;
                border-radius: 8px;
                padding: 10px 15px;
            }
        """)
        layout.addWidget(self.lblTotalEmpleado)

        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)

        dialog = QDialog(self)
        dialog.setWindowTitle("Ventas del Empleado")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(500)
        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.addWidget(scroll)

        btnCerrar = QPushButton("Cerrar")
        btnCerrar.setStyleSheet(
            "background-color: #95a5a6; color: white; padding: 8px 20px; border-radius: 5px; font-weight: bold;"
        )
        btnCerrar.clicked.connect(dialog.accept)
        dlg_layout.addWidget(btnCerrar, alignment=Qt.AlignCenter)

        self.cargarVentasEmpleado(fecha_inicio, fecha_fin, empleado_id)

        if solo_mostrar:
            dialog.exec_()
        else:
            self.generarPDFVentasEmpleado(fecha_inicio, fecha_fin, empleado_id, abrir_pdf)

    def cargarVentasEmpleado(self, fecha_inicio, fecha_fin, empleado_id):
        self.tablaEmpleado.setRowCount(0)
        ventas_dict = {}

        if self.chkCajero.isChecked():
            query = """
                SELECT v.numVenta, DATE(v.fechaReg), v.horaReg, 'Cajero', v.totalVenta
                FROM Venta v
                WHERE DATE(v.fechaReg) BETWEEN ? AND ?
                AND v.codEmp2 = ?
                ORDER BY v.fechaReg, v.horaReg
            """
            params = [fecha_inicio, fecha_fin, empleado_id]
            self.cursor.execute(query, params)
            for row in self.cursor.fetchall():
                clave = f"{row[0]}_{row[1]}"
                if clave not in ventas_dict:
                    ventas_dict[clave] = row

        if self.chkMesero.isChecked():
            query = """
                SELECT v.numVenta, DATE(v.fechaReg), v.horaReg, 'Mesero', v.totalVenta
                FROM Venta v
                WHERE DATE(v.fechaReg) BETWEEN ? AND ?
                AND v.codEmp = ?
                ORDER BY v.fechaReg, v.horaReg
            """
            params = [fecha_inicio, fecha_fin, empleado_id]
            self.cursor.execute(query, params)
            for row in self.cursor.fetchall():
                clave = f"{row[0]}_{row[1]}"
                if clave not in ventas_dict:
                    ventas_dict[clave] = row

        ventas = sorted(ventas_dict.values(), key=lambda x: (x[1], x[2]))

        self.tablaEmpleado.setRowCount(len(ventas))
        total_general = 0.0
        for row, venta in enumerate(ventas):
            fecha_obj = datetime.strptime(venta[1], "%Y-%m-%d")
            fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
            self.tablaEmpleado.setItem(row, 0, QTableWidgetItem(str(venta[0])))
            self.tablaEmpleado.setItem(row, 1, QTableWidgetItem(fecha_formateada))
            self.tablaEmpleado.setItem(row, 2, QTableWidgetItem(venta[2]))
            self.tablaEmpleado.setItem(row, 3, QTableWidgetItem(venta[3]))
            self.tablaEmpleado.setItem(row, 4, QTableWidgetItem(f"{float(venta[4]):.2f}"))
            for col in range(5):
                self.tablaEmpleado.item(row, col).setTextAlignment(Qt.AlignCenter)
            total_general += float(venta[4])
        if hasattr(self, 'lblTotalEmpleado'):
            self.lblTotalEmpleado.setText(
                f"💰 Total del período mostrado: {total_general:.2f} Bs   |   Registros: {len(ventas)}"
            )

    def generarPDFVentasEmpleado(self, fecha_inicio, fecha_fin, empleado_id, abrir_pdf):
        self.cargarVentasEmpleado(fecha_inicio, fecha_fin, empleado_id)

        fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
        periodo = f"{fecha_inicio_obj.strftime('%d/%m/%Y')} a {fecha_fin_obj.strftime('%d/%m/%Y')}"

        nombre_empleado = self.comboEmpleado.currentText()

        pdf = PDFReport(
            tipo_reporte="Ventas", periodo=periodo, empleado=nombre_empleado, subreporte="Ventas del Empleado"
        )
        pdf.add_page()
        pdf.chapter_title(f"VENTAS DEL EMPLEADO: {nombre_empleado}")

        roles = []
        if self.chkCajero.isChecked():
            roles.append("Cajero")
        if self.chkMesero.isChecked():
            roles.append("Mesero")
        resumen_texto = f"""
        Periodo: {periodo}
        Roles incluidos: {', '.join(roles)}
        Total de ventas: {self.tablaEmpleado.rowCount()}
        """
        pdf.chapter_body(resumen_texto)

        if self.tablaEmpleado.rowCount() > 0:
            headers = ["N° Venta", "Fecha", "Hora", "Rol", "Total"]
            table_data = []
            for row in range(self.tablaEmpleado.rowCount()):
                table_data.append(
                    [
                        self.tablaEmpleado.item(row, 0).text(),
                        self.tablaEmpleado.item(row, 1).text(),
                        self.tablaEmpleado.item(row, 2).text(),
                        self.tablaEmpleado.item(row, 3).text(),
                        self.tablaEmpleado.item(row, 4).text(),
                    ]
                )
            pdf.add_table(headers, table_data)

        self.enviarYMostrarPDF(pdf, "Reporte de Ventas", abrir_pdf)

    def generarPDFProductosVendidos(self, fecha_inicio, fecha_fin, abrir_pdf):
        query_productos = """
            SELECT 
                COALESCE(p.nomProd, pr.nomProm) as producto,
                SUM(dv.cantidadProdDet) as cantidad_vendida,
                SUM(dv.subtotal) as total_venta
            FROM DetallesVenta dv
            LEFT JOIN Producto p ON dv.idProd = p.idProd
            LEFT JOIN Promocion pr ON dv.idProm = pr.idProm
            WHERE DATE(dv.fechaRegVenta) BETWEEN ? AND ?
            AND dv.estadoDetalleVenta = 'Finalizado'
            GROUP BY COALESCE(p.nomProd, pr.nomProm)
            ORDER BY cantidad_vendida DESC LIMIT 50
        """
        params_prod = [fecha_inicio, fecha_fin]

        self.cursor.execute(query_productos, params_prod)
        productos = self.cursor.fetchall()

        fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
        periodo = f"{fecha_inicio_obj.strftime('%d/%m/%Y')} a {fecha_fin_obj.strftime('%d/%m/%Y')}"

        pdf = PDFReport(tipo_reporte="Ventas", periodo=periodo, empleado=None, subreporte="Productos Más Vendidos")
        pdf.add_page()
        pdf.chapter_title("PRODUCTOS MÁS VENDIDOS")

        resumen_texto = f"""
        Periodo: {periodo}
        Total de productos diferentes: {len(productos)}
        """
        pdf.chapter_body(resumen_texto)

        if productos:
            headers = ["Producto", "Cantidad Vendida", "Total Ventas"]
            table_data = []
            for producto, cantidad, total in productos:
                table_data.append([str(producto) if producto else "N/A", str(int(cantidad)), f"{float(total):.2f}"])
            pdf.add_table(headers, table_data)

        self.enviarYMostrarPDF(pdf, "Reporte de Ventas", abrir_pdf)

    def mostrarVentasDetalladasEnTabla(self, ventas):
        self.stackedWidget.setCurrentWidget(self.contenedorTabla)
        self.tablaResultados.setColumnCount(12)
        headers = [
            "N° Venta",
            "Fecha",
            "Hora",
            "Mesero (Aper)",
            "Cajero",
            "Salón",
            "Mesa",
            "Total Venta",
            "Efectivo",
            "QR",
            "Total Pagado",
            "Estado",
        ]
        self.tablaResultados.setHorizontalHeaderLabels(headers)
        self.tablaResultados.setRowCount(len(ventas))

        font_normal = QFont("Segoe UI", 11)

        suma_total_venta = 0.0
        for row, venta in enumerate(ventas):
            (
                num_venta,
                fecha,
                hora,
                mesero_apertura,
                cajero,
                salon,
                mesa,
                total_venta,
                efectivo,
                qr,
                total_pagado,
                estado_venta,
                hora_cierre,
            ) = venta
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
            if estado_venta != 'Cancelada':
                suma_total_venta += float(total_venta)
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
                estado_venta,
            ]
            for col, valor in enumerate(datos):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(font_normal)
                if col == 11:
                    item.setForeground(color_estado)
                    item.setFont(QFont("Segoe UI", 11, QFont.Bold))
                    if estado_venta == "Cancelada":
                        for c in range(12):
                            bg_item = QTableWidgetItem(str(datos[c]) if c < len(datos) else "")
                            bg_item.setTextAlignment(Qt.AlignCenter)
                            bg_item.setFont(font_normal)
                            bg_item.setBackground(QColor(255, 230, 230))
                            bg_item.setForeground(QColor(220, 50, 50) if c == 11 else QColor(0, 0, 0))
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
        self.lblTotalResumen.setText(
            f"💰 Total del período (sin canceladas): {suma_total_venta:.2f} Bs   |   Ventas: {len(ventas)}"
        )
        self.lblTotalResumen.setVisible(True)

    def mostrarResumenFechasEnTabla(self, ventas):
        self.stackedWidget.setCurrentWidget(self.contenedorTabla)
        resumen_fechas = {}
        for venta in ventas:
            fecha = venta[1]
            cajero = venta[4]
            if fecha not in resumen_fechas:
                resumen_fechas[fecha] = {}
            if cajero not in resumen_fechas[fecha]:
                resumen_fechas[fecha][cajero] = {'total_ventas': 0, 'total_monto': 0, 'efectivo': 0, 'qr': 0}
            resumen_fechas[fecha][cajero]['total_ventas'] += 1
            if venta[11] != 'Cancelada':
                resumen_fechas[fecha][cajero]['total_monto'] += float(venta[7])
            resumen_fechas[fecha][cajero]['efectivo'] += float(venta[8])
            resumen_fechas[fecha][cajero]['qr'] += float(venta[9])

        self.tablaResultados.setColumnCount(6)
        headers = ["Fecha", "Cajero", "N° Ventas", "Total Monto", "Efectivo", "QR"]
        self.tablaResultados.setHorizontalHeaderLabels(headers)

        total_filas = 0
        for fecha, cajeros in resumen_fechas.items():
            total_filas += len(cajeros)

        self.tablaResultados.setRowCount(total_filas)

        font_normal = QFont("Segoe UI", 11)

        row = 0
        gran_total = 0.0
        for fecha, cajeros in sorted(resumen_fechas.items()):
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
            fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
            for cajero, datos in sorted(cajeros.items()):
                self.tablaResultados.setItem(row, 0, QTableWidgetItem(fecha_formateada))
                self.tablaResultados.setItem(row, 1, QTableWidgetItem(cajero))
                self.tablaResultados.setItem(row, 2, QTableWidgetItem(str(datos['total_ventas'])))
                self.tablaResultados.setItem(row, 3, QTableWidgetItem(f"{datos['total_monto']:.2f}"))
                self.tablaResultados.setItem(row, 4, QTableWidgetItem(f"{datos['efectivo']:.2f}"))
                self.tablaResultados.setItem(row, 5, QTableWidgetItem(f"{datos['qr']:.2f}"))
                for col in range(6):
                    self.tablaResultados.item(row, col).setTextAlignment(Qt.AlignCenter)
                    self.tablaResultados.item(row, col).setFont(font_normal)
                gran_total += datos['total_monto']
                row += 1
        QTimer.singleShot(50, self.ajustarTamanos)
        self.lblTotalResumen.setText(f"💰 Total general del período (sin canceladas): {gran_total:.2f} Bs")
        self.lblTotalResumen.setVisible(True)

    def mostrarProductosVendidosEnTabla(self, fecha_inicio, fecha_fin):
        self.stackedWidget.setCurrentWidget(self.contenedorTabla)
        query_productos = """
            SELECT 
                COALESCE(p.nomProd, pr.nomProm) as producto,
                SUM(dv.cantidadProdDet) as cantidad_vendida,
                SUM(dv.subtotal) as total_venta
            FROM DetallesVenta dv
            LEFT JOIN Producto p ON dv.idProd = p.idProd
            LEFT JOIN Promocion pr ON dv.idProm = pr.idProm
            WHERE DATE(dv.fechaRegVenta) BETWEEN ? AND ?
            AND dv.estadoDetalleVenta = 'Finalizado'
            GROUP BY COALESCE(p.nomProd, pr.nomProm)
            ORDER BY cantidad_vendida DESC LIMIT 50
        """
        params_prod = [fecha_inicio, fecha_fin]

        self.cursor.execute(query_productos, params_prod)
        productos = self.cursor.fetchall()

        self.tablaResultados.setColumnCount(3)
        headers = ["Producto", "Cantidad Vendida", "Total Ventas"]
        self.tablaResultados.setHorizontalHeaderLabels(headers)
        self.tablaResultados.setRowCount(len(productos))

        font_normal = QFont("Segoe UI", 11)

        suma_total = 0.0
        for row, (producto, cantidad, total) in enumerate(productos):
            item0 = QTableWidgetItem(str(producto) if producto else "N/A")
            item0.setTextAlignment(Qt.AlignCenter)
            item0.setFont(font_normal)
            self.tablaResultados.setItem(row, 0, item0)

            item1 = QTableWidgetItem(str(int(cantidad)))
            item1.setTextAlignment(Qt.AlignCenter)
            item1.setFont(font_normal)
            self.tablaResultados.setItem(row, 1, item1)

            item2 = QTableWidgetItem(f"{float(total):.2f}")
            item2.setTextAlignment(Qt.AlignCenter)
            item2.setFont(font_normal)
            self.tablaResultados.setItem(row, 2, item2)
            suma_total += float(total)
        QTimer.singleShot(50, self.ajustarTamanos)
        self.lblTotalResumen.setText(f"💰 Total vendido en el período: {suma_total:.2f} Bs")
        self.lblTotalResumen.setVisible(True)

    def obtenerDetallesProductosVenta(self, num_venta, fecha):
        query = """
            SELECT 
                dv.cantidadProdDet,
                COALESCE(p.nomProd, pr.nomProm) as producto,
                dv.tipoConsumo,
                dv.subtotal,
                e.aliasEmp as mesero_detalle,
                COALESCE(dv.idProd, dv.idProm) as id_item,
                dv.idDetalleVenta,
                dv.idProd,
                dv.idProm
            FROM DetallesVenta dv
            LEFT JOIN Producto p ON dv.idProd = p.idProd
            LEFT JOIN Promocion pr ON dv.idProm = pr.idProm
            JOIN Empleado e ON dv.idMeseroActual = e.codEmp
            WHERE dv.numVenta = ? AND DATE(dv.fechaRegVenta) = ?
            ORDER BY dv.idDetalleVenta
        """
        self.cursor.execute(query, (num_venta, fecha))
        productos_raw_base = self.cursor.fetchall()
        productos_raw = []
        for cant, nombre, tipo, subtotal, mesero, id_item, id_det, id_prod, id_prom in productos_raw_base:
            personalizacion = self._obtenerPersonalizacionDetalle(id_det, id_prod, id_prom, cant)
            productos_raw.append(
                (cant, nombre, tipo, subtotal, mesero, id_item, personalizacion, id_det, id_prod, id_prom)
            )
        return self.agrupar_productos_detalle(productos_raw)

    def _obtenerPersonalizacionDetalle(self, id_det, id_prod, id_prom, cantidad_combo=1):
        if id_prod:
            self.cursor.execute("SELECT nomIng FROM DetallesVentaExclusiones WHERE idDetalleVenta=?", (id_det,))
            excl = self.cursor.fetchall()
            self.cursor.execute(
                """
                SELECT nomIng, cantidadExtra FROM DetallesVentaExtras
                WHERE idDetalleVenta=? AND idProd IS NULL
            """,
                (id_det,),
            )
            extra = self.cursor.fetchall()
            partes = []
            if excl:
                partes.append("Sin: " + ", ".join(sorted(r[0] for r in excl)))
            if extra:
                partes.append("Extra: " + ", ".join(f"+{c} {n}" for n, c in extra))
            return " | ".join(partes)
        elif id_prom:
            self.cursor.execute(
                """
                SELECT p.idProd, p.nomProd, pp.cantidadProdProm FROM PromocionProd pp
                JOIN Producto p ON pp.idProd = p.idProd WHERE pp.idProm=?
            """,
                (id_prom,),
            )
            info_productos = self.cursor.fetchall()
            nombres_por_id = {pid: pnom for pid, pnom, _ in info_productos}
            cant_por_combo = {pid: cant for pid, _, cant in info_productos}

            self.cursor.execute(
                "SELECT idProd, numUnidad, nomIng FROM DetallesVentaExclusionesPromo WHERE idDetalleVenta=?", (id_det,)
            )
            excl_por_producto_unidad = {}
            for id_p, num_unidad, nom_ing in self.cursor.fetchall():
                excl_por_producto_unidad.setdefault(id_p, {}).setdefault(num_unidad, []).append(nom_ing)

            self.cursor.execute(
                """
                SELECT idProd, numUnidad, nomIng, cantidadExtra FROM DetallesVentaExtras
                WHERE idDetalleVenta=? AND idProd IS NOT NULL
            """,
                (id_det,),
            )
            extra_por_producto_unidad = {}
            for id_p, num_unidad, nom_ing, cant_extra in self.cursor.fetchall():
                extra_por_producto_unidad.setdefault(id_p, {}).setdefault(num_unidad, []).append((nom_ing, cant_extra))

            ids_con_personalizacion = sorted(
                set(excl_por_producto_unidad.keys()) | set(extra_por_producto_unidad.keys()),
                key=lambda x: nombres_por_id.get(x, str(x)),
            )
            if not ids_con_personalizacion:
                return ""

            lineas = []
            for id_p in ids_con_personalizacion:
                nombre_prod = nombres_por_id.get(id_p, f"Producto {id_p}")
                unidades_excl = excl_por_producto_unidad.get(id_p, {})
                unidades_extra = extra_por_producto_unidad.get(id_p, {})
                todas_unidades_idx = set(unidades_excl.keys()) | set(unidades_extra.keys())

                conteo_combos = {}
                for num_unidad in todas_unidades_idx:
                    sin_texto = (
                        ", ".join(sorted(unidades_excl.get(num_unidad, []))) if unidades_excl.get(num_unidad) else ""
                    )
                    extra_texto = (
                        ", ".join(f"+{c} {n}" for n, c in unidades_extra.get(num_unidad, []))
                        if unidades_extra.get(num_unidad)
                        else ""
                    )
                    clave_combo = (sin_texto, extra_texto)
                    conteo_combos[clave_combo] = conteo_combos.get(clave_combo, 0) + 1

                lineas.append(f"{nombre_prod}:")
                for (sin_texto, extra_texto), cant in sorted(conteo_combos.items(), key=lambda kv: -kv[1]):
                    partes_linea = []
                    if sin_texto:
                        partes_linea.append(f"Sin: {sin_texto}")
                    if extra_texto:
                        partes_linea.append(f"Extra: {extra_texto}")
                    lineas.append(f"  {cant} x " + "  |  ".join(partes_linea))

                total_prod = cant_por_combo.get(id_p, 0) * cantidad_combo
                normales = total_prod - len(todas_unidades_idx)
                if normales > 0:
                    lineas.append(f"  {normales} x normal (sin cambios)")
            return "\n".join(lineas)
        return ""

    def agrupar_productos_detalle(self, productos_raw):
        productos_agrupados = []
        productos_dict = defaultdict(list)
        for cant, nombre, tipo, subtotal, mesero, id_item, personalizacion, id_det, id_prod, id_prom in productos_raw:
            key = (nombre, tipo, id_item, mesero, personalizacion)
            productos_dict[key].append(
                (cant, nombre, tipo, subtotal, mesero, id_item, personalizacion, id_det, id_prod, id_prom)
            )

        for key, items in productos_dict.items():
            es_promocion = items[0][9] is not None
            total_cant = sum(item[0] for item in items)
            nombre = items[0][1]
            tipo = items[0][2]
            total_subtotal = sum(item[3] for item in items)
            meseros = ", ".join(sorted(set(item[4] for item in items)))
            personalizacion = items[0][6]
            ids_det = [item[7] for item in items]
            productos_agrupados.append(
                (total_cant, nombre, tipo, total_subtotal, meseros, personalizacion, ids_det, es_promocion)
            )
        return productos_agrupados

    def _calcularDuracion(self, hora_inicio_str, fecha, hora_cierre_str):
        if not hora_cierre_str:
            return None
        inicio = None
        for formato in ("%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                inicio = datetime.strptime(f"{fecha} {hora_inicio_str}", formato)
                break
            except ValueError:
                continue
        if inicio is None:
            return None
        try:
            cierre = datetime.strptime(hora_cierre_str[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
        diferencia = cierre - inicio
        segundos = int(diferencia.total_seconds())
        if segundos < 0:
            return None
        minutos = segundos // 60
        horas = minutos // 60
        minutos_restantes = minutos % 60
        if horas > 0:
            return f"{horas}h {minutos_restantes}min"
        return f"{minutos_restantes}min"

    def generarPDFVentasCompleto(self, ventas, fecha_inicio, fecha_fin, empleado_id, subreporte_tipo, abrir_pdf):
        fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
        periodo = f"{fecha_inicio_obj.strftime('%d/%m/%Y')} a {fecha_fin_obj.strftime('%d/%m/%Y')}"

        nombre_empleado = self.comboEmpleado.currentText() if empleado_id else "Todos los empleados"
        subreporte_nombre = {
            "detallado": "Ventas Detalladas",
            "resumen_fechas": "Resumen por Fechas",
        }.get(subreporte_tipo, "Ventas Detalladas")

        pdf = PDFReport(tipo_reporte="Ventas", periodo=periodo, empleado=nombre_empleado, subreporte=subreporte_nombre)
        pdf.add_page()
        pdf.chapter_title(f"REPORTE DE VENTAS - {subreporte_nombre}")

        if subreporte_tipo == "detallado":
            total_ventas = len(ventas)
            estados = {'Finalizada': 0, 'En Preparación': 0, 'Por Cobrar': 0, 'Cancelada': 0, 'Mixto': 0}
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
                headers = [
                    "N°",
                    "Fecha",
                    "Hora",
                    "Mesero(Aper)",
                    "Cajero",
                    "Salón",
                    "Mesa",
                    "Total",
                    "Efectivo",
                    "QR",
                    "Pagado",
                    "Estado",
                ]
                col_widths = [8, 22, 15, 25, 25, 20, 15, 20, 20, 15, 20, 25]
                table_data = []
                for venta in ventas:
                    (
                        num_venta,
                        fecha,
                        hora,
                        mesero_apertura,
                        cajero,
                        salon,
                        mesa,
                        total_venta,
                        efectivo,
                        qr,
                        total_pagado,
                        estado_venta,
                        hora_cierre,
                    ) = venta
                    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
                    fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                    table_data.append(
                        [
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
                            estado_venta,
                        ]
                    )
                pdf.add_table(headers, table_data, col_widths)
                if len(ventas) > 0:
                    pdf.add_page()
                    pdf.chapter_title("DETALLE DE CADA VENTA")
                    for venta in ventas:
                        (
                            num_venta,
                            fecha,
                            hora,
                            mesero_apertura,
                            cajero,
                            salon,
                            mesa,
                            total_venta,
                            efectivo,
                            qr,
                            total_pagado,
                            estado_venta,
                            hora_cierre,
                        ) = venta
                        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
                        fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                        productos_detalle = self.obtenerDetallesProductosVenta(num_venta, fecha)
                        if productos_detalle:
                            if estado_venta == 'Cancelada':
                                hora_cierre_fmt = "N/A (cancelada)"
                                duracion = "N/A (cancelada)"
                            else:
                                hora_cierre_fmt = None
                                if hora_cierre:
                                    try:
                                        hora_cierre_fmt = datetime.strptime(
                                            hora_cierre[:19], "%Y-%m-%d %H:%M:%S"
                                        ).strftime("%H:%M:%S")
                                    except ValueError:
                                        hora_cierre_fmt = hora_cierre
                                duracion = self._calcularDuracion(hora, fecha, hora_cierre)
                            pdf.add_detalle_venta(
                                num_venta=num_venta,
                                fecha=fecha_formateada,
                                hora=hora,
                                mesero_apertura=mesero_apertura,
                                cajero=cajero,
                                salon=salon,
                                mesa=mesa,
                                productos_detalle=productos_detalle,
                                hora_cierre=hora_cierre_fmt,
                                duracion=duracion,
                            )
                            if pdf.get_y() > 250:
                                pdf.add_page()

        elif subreporte_tipo == "resumen_fechas":
            resumen_fechas = {}
            for venta in ventas:
                fecha = venta[1]
                cajero = venta[4]
                if fecha not in resumen_fechas:
                    resumen_fechas[fecha] = {}
                if cajero not in resumen_fechas[fecha]:
                    resumen_fechas[fecha][cajero] = {'total_ventas': 0, 'total_monto': 0, 'efectivo': 0, 'qr': 0}
                resumen_fechas[fecha][cajero]['total_ventas'] += 1
                if venta[11] != 'Cancelada':
                    resumen_fechas[fecha][cajero]['total_monto'] += float(venta[7])
                resumen_fechas[fecha][cajero]['efectivo'] += float(venta[8])
                resumen_fechas[fecha][cajero]['qr'] += float(venta[9])

            pdf.chapter_title("RESUMEN DE VENTAS POR FECHA")
            headers = ["Fecha", "Cajero", "N° Ventas", "Total Monto", "Efectivo", "QR"]
            table_data = []
            for fecha, cajeros in sorted(resumen_fechas.items()):
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                for cajero, datos in sorted(cajeros.items()):
                    table_data.append(
                        [
                            fecha_formateada,
                            cajero,
                            str(datos['total_ventas']),
                            f"{datos['total_monto']:.2f}",
                            f"{datos['efectivo']:.2f}",
                            f"{datos['qr']:.2f}",
                        ]
                    )
            pdf.add_table(headers, table_data)

        self.enviarYMostrarPDF(pdf, "Reporte de Ventas", abrir_pdf)

    def generarReporteStock(self, solo_mostrar=True, abrir_pdf=False):
        query = """
            SELECT s.nomIng, s.descripcion, s.cantidadStock, s.unidadMedida
            FROM Stock s
            ORDER BY s.nomIng
        """
        self.cursor.execute(query)
        stock = self.cursor.fetchall()
        self.stackedWidget.setCurrentWidget(self.contenedorTabla)
        self.lblTotalResumen.setVisible(False)
        self.tablaResultados.setColumnCount(4)
        headers = ["Ingrediente", "Descripción", "Cantidad", "Unidad"]
        self.tablaResultados.setHorizontalHeaderLabels(headers)
        self.tablaResultados.setRowCount(len(stock))

        font_normal = QFont("Segoe UI", 11)

        for row, (nomIng, descripcion, cantidadStock, unidadMedida) in enumerate(stock):
            it0 = QTableWidgetItem(str(nomIng))
            it0.setTextAlignment(Qt.AlignCenter)
            it0.setFont(font_normal)
            self.tablaResultados.setItem(row, 0, it0)
            it1 = QTableWidgetItem(str(descripcion) if descripcion else "")
            it1.setTextAlignment(Qt.AlignCenter)
            it1.setFont(font_normal)
            self.tablaResultados.setItem(row, 1, it1)
            it2 = QTableWidgetItem(_fmt2(cantidadStock))
            it2.setTextAlignment(Qt.AlignCenter)
            it2.setFont(font_normal)
            self.tablaResultados.setItem(row, 2, it2)
            it3 = QTableWidgetItem(str(unidadMedida))
            it3.setTextAlignment(Qt.AlignCenter)
            it3.setFont(font_normal)
            self.tablaResultados.setItem(row, 3, it3)

        self.tablaResultados.setColumnWidth(0, 120)
        self.tablaResultados.setColumnWidth(1, 180)
        self.tablaResultados.setColumnWidth(2, 80)
        self.tablaResultados.setColumnWidth(3, 80)

        QTimer.singleShot(50, self.ajustarTamanos)
        if not solo_mostrar:
            total_ingredientes = len(stock)
            self.generarPDFStock(stock, total_ingredientes, abrir_pdf)

    def generarPDFStock(self, stock, total_ingredientes, abrir_pdf):
        pdf = PDFReport(tipo_reporte="Stock")
        pdf.add_page()
        pdf.chapter_title("RESUMEN DE STOCK")
        resumen_texto = f"Total de ingredientes: {total_ingredientes}"
        pdf.chapter_body(resumen_texto)
        if stock:
            pdf.chapter_title("DETALLE DE STOCK")
            headers = ["Ingrediente", "Descripción", "Cantidad", "Unidad"]
            table_data = []
            for nomIng, descripcion, cantidadStock, unidadMedida in stock:
                table_data.append(
                    [str(nomIng), str(descripcion) if descripcion else "", _fmt2(cantidadStock), str(unidadMedida)]
                )
            pdf.add_table(headers, table_data)
        self.enviarYMostrarPDF(pdf, "Reporte de Stock", abrir_pdf)

    def enviarYMostrarPDF(self, pdf, asunto, abrir_pdf):
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False, mode='wb') as temp_file:
                temp_path = temp_file.name
            pdf.output(temp_path)

            if abrir_pdf:
                webbrowser.open(temp_path)
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"El {asunto.lower()} se ha generado correctamente.\nSe abrirá automáticamente en tu visor de PDF.",
                )
            else:
                self.enviarPorCorreoConArchivo(temp_path, asunto)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar el PDF: {str(e)}")
            import traceback

            print(traceback.format_exc())

    def enviarPorCorreoConArchivo(self, pdf_path, asunto):
        try:
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
                    "https://myaccount.google.com/apppasswords",
                )
                return
            from_email, password = row
            to_email = from_email
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = f"{asunto} - {datetime.now().strftime('%d/%m/%Y')}"
            cuerpo = f"""Se ha generado el {asunto.lower()} con fecha {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}. 
            \n Este es un mensaje automático, por favor no responder.
            """
            msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
            with open(pdf_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{asunto.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"',
                )
                msg.attach(part)
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(from_email, password)
                server.send_message(msg)
                server.quit()
                QMessageBox.information(
                    self, "Éxito", f"El {asunto.lower()} ha sido generado y enviado por correo electrónico a {to_email}"
                )
            except smtplib.SMTPAuthenticationError as e:
                QMessageBox.warning(
                    self,
                    "Error de Autenticación",
                    f"No se pudo autenticar con el servidor de correo:\n\n"
                    f"Error: {str(e)}\n\n"
                    f"Para Gmail, necesitas usar una 'Contraseña de aplicación' en lugar de tu contraseña normal.\n"
                    f"Puedes generar una en: https://myaccount.google.com/apppasswords",
                )
            except Exception as e:
                QMessageBox.warning(self, "Error al Enviar Correo", f"No se pudo enviar el correo: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")
            import traceback

            print(traceback.format_exc())
        finally:
            try:
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)
            except Exception:
                pass

    def limpiarFiltros(self):
        hoy = QDate.currentDate()
        hace30Dias = hoy.addDays(-30)
        self.dateInicio.setDate(hace30Dias)
        self.dateFin.setDate(hoy)
        self.checkEmpleado.setChecked(False)
        self.comboEmpleado.setCurrentIndex(0)
        self.comboSubreporte.setCurrentIndex(0)
        self.limpiarTabla()

    def onCellDoubleClicked(self, row, column):
        if row < self.tablaResultados.rowCount():
            num_venta_item = self.tablaResultados.item(row, 0)
            fecha_item = self.tablaResultados.item(row, 1)
            if num_venta_item and fecha_item and self.tablaResultados.columnCount() == 12:
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
             END AS estado_venta,
             v.horaCierre
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
            def resizeEvent(self, event):
                QTableWidget.resizeEvent(self, event)
                ancho_tabla = self.viewport().width()
                if ancho_tabla > 0:
                    self.setColumnWidth(0, int(ancho_tabla * 0.10))
                    self.setColumnWidth(1, int(ancho_tabla * 0.45))
                    self.setColumnWidth(2, int(ancho_tabla * 0.12))
                    self.setColumnWidth(3, int(ancho_tabla * 0.15))
                    self.setColumnWidth(4, int(ancho_tabla * 0.18))

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalle Venta #{num_venta}")
        dialog.setMinimumWidth(900)
        dialog.setMinimumHeight(600)
        layout = QVBoxLayout(dialog)
        (
            num_venta_db,
            fecha_db,
            hora,
            mesero_apertura,
            cajero,
            salon,
            mesa,
            total_venta,
            efectivo,
            qr,
            total_pagado,
            estado_venta,
            hora_cierre,
        ) = info_venta
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
        hora_cierre_fmt = "En proceso"
        duracion_texto = "En proceso"
        if estado_venta == 'Cancelada':
            hora_cierre_fmt = "N/A (venta cancelada)"
            duracion_texto = "N/A (venta cancelada)"
        elif hora_cierre:
            try:
                hora_cierre_fmt = datetime.strptime(hora_cierre[:19], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
            except ValueError:
                hora_cierre_fmt = hora_cierre
            duracion_calc = self._calcularDuracion(hora, fecha_db, hora_cierre)
            duracion_texto = duracion_calc if duracion_calc else "—"
        info_text = f"""
            <div style='font-size: 14px; padding: 10px;'>
            <h3 style='color: #2c3e50;'>VENTA #{num_venta_db}</h3>
            <table style='font-size: 13px; border-spacing: 8px;'>
            <tr><td style='font-weight:bold;'>Fecha:</td><td>{fecha_formateada}</td>
                <td style='font-weight:bold; padding-left:20px;'>Hora Inicio:</td><td>{hora}</td></tr>
            <tr><td style='font-weight:bold;'>Mesero (Apertura):</td><td>{mesero_apertura}</td>
                <td style='font-weight:bold; padding-left:20px;'>Cajero:</td><td>{cajero}</td></tr>
            <tr><td style='font-weight:bold;'>Ubicación:</td><td>{ubicacion}</td>
                <td style='font-weight:bold; padding-left:20px;'>Estado:</td>
                <td style='color:{color_estado}; font-weight:bold;'>{estado_venta}</td></tr>
            <tr><td style='font-weight:bold;'>Hora Cierre:</td><td>{hora_cierre_fmt}</td>
                <td style='font-weight:bold; padding-left:20px;'>Duración:</td><td>{duracion_texto}</td></tr>
            <tr><td style='font-weight:bold;'>Total Venta:</td>
                <td style='color:#e74c3c; font-weight:bold;'>{float(total_venta):.2f} Bs.</td>
                <td style='font-weight:bold; padding-left:20px;'>Efectivo:</td>
                <td style='color:#27ae60;'>{float(efectivo):.2f} Bs.</td></tr>
            <tr><td style='font-weight:bold;'>QR:</td>
                <td style='color:#2980b9;'>{float(qr):.2f} Bs.</td>
                <td style='font-weight:bold; padding-left:20px;'>Total Pagado:</td>
                <td style='color:#9b59b6; font-weight:bold;'>{float(total_pagado):.2f} Bs.</td></tr>
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
            tabla.setSelectionMode(QTableWidget.NoSelection)
            tabla.setFocusPolicy(Qt.NoFocus)
            tabla.verticalHeader().setVisible(False)
            tabla.horizontalHeader().setStretchLastSection(True)
            total_productos = 0

            font_normal = QFont("Segoe UI", 11)
            font_bold = QFont("Segoe UI", 11, QFont.Bold)

            datos_por_fila_reporte = {}
            for row, (
                cantidad,
                producto,
                tipo_consumo,
                subtotal,
                mesero_detalle,
                personalizacion,
                ids_det,
                es_promocion,
            ) in enumerate(productos_detalle):
                datos_por_fila_reporte[row] = {
                    'nombre': producto,
                    'tipo': tipo_consumo,
                    'es_promocion': es_promocion,
                    'personalizacion': personalizacion,
                    'ids_det': ids_det,
                    'cantidad': cantidad,
                }
                item1 = QTableWidgetItem(str(cantidad))
                item1.setTextAlignment(Qt.AlignCenter)
                item1.setFont(font_normal)
                tabla.setItem(row, 0, item1)
                texto_producto = producto if producto else "N/A"
                item2 = QTableWidgetItem(texto_producto)
                item2.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                if personalizacion:
                    fuente_link = QFont("Segoe UI", 11)
                    fuente_link.setUnderline(True)
                    item2.setFont(fuente_link)
                    item2.setForeground(QColor("#2980b9"))
                    item2.setToolTip("🖱 Haga clic para ver el detalle de la personalización")
                else:
                    item2.setFont(font_normal)
                tabla.setItem(row, 1, item2)
                tabla.setRowHeight(row, 30)
                tipo_text = "Local" if str(tipo_consumo).upper() == "LOCAL" else "Llevar"
                item3 = QTableWidgetItem(tipo_text)
                item3.setTextAlignment(Qt.AlignCenter)
                item3.setFont(font_normal)
                tabla.setItem(row, 2, item3)
                item4 = QTableWidgetItem(f"{float(subtotal):.2f} Bs.")
                item4.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item4.setFont(font_bold)
                tabla.setItem(row, 3, item4)
                item5 = QTableWidgetItem(mesero_detalle)
                item5.setTextAlignment(Qt.AlignCenter)
                item5.setFont(font_normal)
                tabla.setItem(row, 4, item5)
                total_productos += float(subtotal)

            def al_hacer_clic_detalle(fila, columna):
                if columna != 1:
                    return
                datos = datos_por_fila_reporte.get(fila)
                if not datos or not datos['personalizacion']:
                    return
                self.mostrarDetallePersonalizacionReporte(
                    datos['nombre'], datos['tipo'], datos['es_promocion'], datos['ids_det'], datos['cantidad']
                )

            tabla.cellClicked.connect(al_hacer_clic_detalle)
            tabla.setRowCount(len(productos_detalle) + 1)
            item_total1 = QTableWidgetItem("TOTAL")
            item_total1.setFont(font_bold)
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
            item_total4.setFont(font_bold)
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
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_cerrar.setFixedHeight(40)
        btn_cerrar.clicked.connect(dialog.close)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowMaximizeButtonHint)
        dialog.exec_()

    def mostrarDetallePersonalizacionReporte(self, nombre, tipo, es_promocion, ids_det, cantidad_total=0):
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
        header.setStyleSheet(
            "QWidget { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2980b9); }"
        )
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 20)
        titulo = QLabel(nombre)
        titulo.setStyleSheet("QLabel { color: white; font-size: 19px; font-weight: bold; background: transparent; }")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setWordWrap(True)
        header_layout.addWidget(titulo)
        subtitulo = QLabel("Promoción" if es_promocion else "Producto")
        subtitulo.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.9); font-size: 13px; font-weight: 500; background: transparent; }"
        )
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
            self.cursor.execute("SELECT idProm FROM Promocion WHERE nomProm=?", (nombre,))
            fila_prom = self.cursor.fetchone()
            id_prom = fila_prom[0] if fila_prom else None
            self.cursor.execute(
                """
                SELECT p.idProd, p.nomProd, pp.cantidadProdProm FROM PromocionProd pp
                JOIN Producto p ON pp.idProd = p.idProd WHERE pp.idProm=?
            """,
                (id_prom,),
            )
            info_productos = self.cursor.fetchall()
            nombres_por_id = {pid: pnom for pid, pnom, _ in info_productos}
            cant_por_combo = {pid: cant for pid, _, cant in info_productos}

            excl_por_producto_unidad = {}
            extra_por_producto_unidad = {}
            for id_det in ids_det:
                self.cursor.execute(
                    "SELECT idProd, numUnidad, nomIng FROM DetallesVentaExclusionesPromo WHERE idDetalleVenta=?",
                    (id_det,),
                )
                for id_prod, num_unidad, nom_ing in self.cursor.fetchall():
                    excl_por_producto_unidad.setdefault(id_prod, {}).setdefault(num_unidad, []).append(nom_ing)
                self.cursor.execute(
                    "SELECT idProd, numUnidad, nomIng, cantidadExtra FROM DetallesVentaExtras WHERE idDetalleVenta=? AND idProd IS NOT NULL",
                    (id_det,),
                )
                for id_prod, num_unidad, nom_ing, cant_extra in self.cursor.fetchall():
                    extra_por_producto_unidad.setdefault(id_prod, {}).setdefault(num_unidad, []).append(
                        (nom_ing, cant_extra)
                    )

            ids_con_personalizacion = sorted(
                set(excl_por_producto_unidad.keys()) | set(extra_por_producto_unidad.keys()),
                key=lambda x: nombres_por_id.get(x, str(x)),
            )

            if not ids_con_personalizacion:
                lbl_vacio = QLabel(
                    "Sin personalización — todos los productos de la promoción están con sus ingredientes originales"
                )
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
                        sin_texto = (
                            ", ".join(sorted(unidades_excl.get(num_unidad, [])))
                            if unidades_excl.get(num_unidad)
                            else ""
                        )
                        extra_texto = (
                            ", ".join(f"+{c} {n}" for n, c in unidades_extra.get(num_unidad, []))
                            if unidades_extra.get(num_unidad)
                            else ""
                        )
                        clave_combo = (sin_texto, extra_texto)
                        conteo_combos[clave_combo] = conteo_combos.get(clave_combo, 0) + 1

                    total_prod = cant_por_combo.get(id_prod, 0) * cantidad_total
                    con_personalizacion = len(todas_unidades_idx)
                    sin_personalizacion = total_prod - con_personalizacion

                    prod_frame = QFrame()
                    prod_frame.setStyleSheet(
                        "QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; }"
                    )
                    prod_layout = QVBoxLayout(prod_frame)
                    prod_layout.setContentsMargins(12, 10, 12, 10)
                    prod_layout.setSpacing(6)
                    prod_titulo = QLabel(f"🍔 {nombre_prod}")
                    prod_titulo.setStyleSheet(
                        "font-weight: bold; font-size: 15px; color: #2c3e50; background: transparent; border: none;"
                    )
                    prod_layout.addWidget(prod_titulo)

                    for (sin_texto, extra_texto), cant in sorted(conteo_combos.items(), key=lambda kv: -kv[1]):
                        partes_linea = []
                        if sin_texto:
                            partes_linea.append(f"Sin: {sin_texto}")
                        if extra_texto:
                            partes_linea.append(f"Extra: {extra_texto}")
                        texto_linea = f"{cant} unidad(es) — " + "  |  ".join(partes_linea)
                        color_txt = (
                            "#c0392b"
                            if sin_texto and not extra_texto
                            else ("#27ae60" if extra_texto and not sin_texto else "#8e44ad")
                        )
                        lbl = QLabel(texto_linea)
                        lbl.setWordWrap(True)
                        lbl.setStyleSheet(
                            f"color: {color_txt}; font-size: 14px; font-weight: 600; background: transparent; border: none; padding-left: 12px;"
                        )
                        prod_layout.addWidget(lbl)

                    if sin_personalizacion > 0:
                        lbl_resto = QLabel(f"{sin_personalizacion} unidad(es) — sin ninguna personalización")
                        lbl_resto.setWordWrap(True)
                        lbl_resto.setStyleSheet(
                            "color: #7f8c8d; font-size: 13px; font-style: italic; background: transparent; border: none; padding-left: 12px;"
                        )
                        prod_layout.addWidget(lbl_resto)

                    cuerpo_layout.addWidget(prod_frame)
        else:
            excl_por_unidad = {}
            extra_por_unidad = {}
            for i, id_det in enumerate(ids_det):
                self.cursor.execute("SELECT nomIng FROM DetallesVentaExclusiones WHERE idDetalleVenta=?", (id_det,))
                excl_nombres = sorted(r[0] for r in self.cursor.fetchall())
                self.cursor.execute(
                    "SELECT nomIng, cantidadExtra FROM DetallesVentaExtras WHERE idDetalleVenta=?", (id_det,)
                )
                extra_lista = self.cursor.fetchall()
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
                        bloque_personalizacion(
                            f"{cant} unidad(es) — Extra:", extra_texto, "#eafaf1", "#27ae60", "#2ecc71"
                        )

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

        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = Reportes()
    pagina.show()
    sys.exit(app.exec_())
