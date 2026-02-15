import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
import usb.core
import escpos.printer
from datetime import datetime, time
from Impresion import ManejadorImpresion
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from decimal import Decimal, ROUND_HALF_UP

def q2(x) -> float:
    return float(Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

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
MESAS_DIRECCION = get_resource_path('Imagenes')

class ImpresionSignals(QObject):
    resultado_ticket = pyqtSignal(bool, str, dict, list)
    resultado_cocina = pyqtSignal(bool, str, dict, list)

class RegistrarPedidos(QWidget):
    def __init__(self, cajero):
        super().__init__()
        self.cajero = cajero
        self.banderaCocina = False
        self.modificacion = False
        self.validar_stock = False
        self.banderaTicket = False
        self.enviada = False
        self.ticket_print_count = 0    
        self.cocina_print_count = 0
        self.manejador_impresion = ManejadorImpresion()
        self.signals = ImpresionSignals()
        self.signals.resultado_ticket.connect(self._procesar_resultado_ticket)
        self.signals.resultado_cocina.connect(self._procesar_resultado_cocina)
        self.setStyleSheet("""
            QWidget {
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
            QPushButton:hover { opacity: 0.9; }
            QPushButton:pressed { opacity: 0.8; }
            
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
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                border: none; background: #f1f5f9; width: 12px; margin: 0; border-radius: 6px;
            }
            QScrollBar::handle:vertical { background: #cbd5e1; min-height: 30px; border-radius: 6px; }
            QScrollBar::handle:vertical:hover { background: #94a3b8; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QMessageBox { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; }
            QMessageBox QLabel { color: #2c3e50; font-size: 14px; }
            QMessageBox QPushButton { min-width: 80px; padding: 8px 16px; border-radius: 6px; font-weight: bold; }
            QRadioButton { font-size: 14px; color: #2c3e50; padding: 8px; spacing: 8px; }
            QRadioButton::indicator { width: 18px; height: 18px; border-radius: 9px; border: 2px solid #4a89dc; }
            QRadioButton::indicator:checked { background-color: #4a89dc; border: 2px solid #4a89dc; }
            QRadioButton::indicator:unchecked { background-color: white; }
            QComboBox {
                background-color: white; border: 2px solid #e2e8f0; border-radius: 6px;
                padding: 10px; font-size: 14px; min-height: 40px;
            }
            QComboBox:focus { border: 2px solid #4a89dc; }
            QComboBox::drop-down {
                subcontrol-origin: padding; subcontrol-position: top right; width: 30px;
                border-left: 1px solid #e2e8f0; border-top-right-radius: 6px; border-bottom-right-radius: 6px;
            }
            QComboBox::down-arrow {
                image: none; border-left: 5px solid transparent; border-right: 5px solid transparent;
                border-top: 6px solid #4a89dc; width: 0; height: 0;
            }
            QComboBox QAbstractItemView {
                background-color: white; selection-background-color: #02505e;
                border: 1px solid #e2e8f0; outline: 0; border-radius: 6px;
            }
            QTextEdit {
                background-color: white; border: 2px solid #e2e8f0; border-radius: 6px;
                padding: 10px; font-size: 14px; min-height: 100px;
            }
            QTextEdit:focus { border: 2px solid #4a89dc; background-color: #f0f7ff; }
            QMessageBox {
                background: #ffffff;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                background:transparent;
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
        self.set_up()
        

    def set_up(self):
        self.layoutDatos = QHBoxLayout()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20,20,20,20)
        self.conn = None
        self.cursor = None
        self.iniciarPagina()
        self.nuevaVenta = False
        self.showMaximized()


    def iniciarPagina(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        layoutCampo = QHBoxLayout()
        layoutIzq = QVBoxLayout()
        layoutDer = QVBoxLayout()
        layoutCampo.addLayout(layoutIzq, stretch=38)
        layoutCampo.addLayout(layoutDer, stretch=65)
        layoutCampo1 = QHBoxLayout()
        layoutElemento = QVBoxLayout()
        self.campoSeccion = QLabel("")
        self.campoSeccion.setStyleSheet("""
            QLabel { background-color: white; border: 2px solid #e2e8f0; border-radius: 6px;
            padding: 10px; font-size: 14px; min-height: 40px; color: #2c3e50; }
        """)
        self.etiquetaSeccion = QLabel("Seccion")
        self.etiquetaSeccion.setStyleSheet("""
            QLabel { color: #2c3e50; font-size: 16px; font-weight: bold; margin-bottom: 5px; }
        """)
        layoutElemento.addWidget(self.etiquetaSeccion, alignment=Qt.AlignCenter)
        layoutElemento.addWidget(self.campoSeccion, alignment=Qt.AlignCenter)
        layoutCampo1.addLayout(layoutElemento)
        
        layoutElemento = QVBoxLayout()
        self.campoMesa = QLabel("")
        self.campoMesa.setStyleSheet("""
            QLabel { background-color: white; border: 2px solid #e2e8f0; border-radius: 6px;
            padding: 10px; font-size: 14px; min-height: 40px; color: #2c3e50; }
        """)
        self.etiquetaMesa = QLabel("Mesa")
        self.etiquetaMesa.setStyleSheet("""
            QLabel { color: #2c3e50; font-size: 16px; font-weight: bold; margin-bottom: 5px; }
        """)
        layoutElemento.addWidget(self.etiquetaMesa, alignment=Qt.AlignCenter)
        layoutElemento.addWidget(self.campoMesa, alignment=Qt.AlignCenter)
        layoutCampo1.addLayout(layoutElemento)
        
        layoutElemento = QVBoxLayout()
        self.campoEncargado = QLabel("")
        self.campoEncargado.setStyleSheet("""
            QLabel { background-color: white; border: 2px solid #e2e8f0; border-radius: 6px;
            padding: 10px; font-size: 14px; min-height: 40px; color: #2c3e50; }
        """)
        self.etiquetaEncargado = QLabel("Apertura Mesero")
        self.etiquetaEncargado.setStyleSheet("""
            QLabel { color: #2c3e50; font-size: 16px; font-weight: bold; margin-bottom: 5px; }
        """)
        layoutElemento.addWidget(self.etiquetaEncargado, alignment=Qt.AlignCenter)
        layoutElemento.addWidget(self.campoEncargado, alignment=Qt.AlignCenter)
        layoutCampo1.addLayout(layoutElemento)
        layoutElemento = QVBoxLayout()
        self.campoCajero = QLabel(self.cajero)
        self.campoCajero.setStyleSheet("""
            QLabel { background-color: white; border: 2px solid #e2e8f0; border-radius: 6px;
            padding: 10px; font-size: 14px; min-height: 40px; color: #2c3e50; }
        """)
        self.etiquetaCajero = QLabel("Cajero")
        self.etiquetaCajero.setStyleSheet("""
            QLabel { color: #2c3e50; font-size: 16px; font-weight: bold; margin-bottom: 5px; }
        """)
        layoutElemento.addWidget(self.etiquetaCajero, alignment=Qt.AlignCenter)
        layoutElemento.addWidget(self.campoCajero, alignment=Qt.AlignCenter)
        layoutCampo1.addLayout(layoutElemento)
        layoutElemento = QVBoxLayout()
        self.etiquetaHora = QLabel("Hora")
        self.etiquetaHora.setStyleSheet("""
            QLabel { color: #2c3e50; font-size: 16px; font-weight: bold; margin-bottom: 5px; }
        """)
        self.campoTiempo = QLabel(datetime.now().strftime("%I:%M %p"))
        self.campoTiempo.setStyleSheet("""
            QLabel { background-color: white; border: 2px solid #e2e8f0; border-radius: 6px;
            padding: 10px; font-size: 14px; min-height: 40px; color: #2c3e50; }
        """)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizarHora)
        self.timer.start(1000)
        layoutElemento.addWidget(self.etiquetaHora, alignment=Qt.AlignCenter)
        layoutElemento.addWidget(self.campoTiempo, alignment=Qt.AlignCenter)
        layoutCampo1.addLayout(layoutElemento)
        layoutElemento = QVBoxLayout()
        fecha = datetime.now().date()
        self.cursor.execute("""SELECT COUNT(*) FROM Venta WHERE DATE(fechaReg)=?""", (fecha,))
        resultados = self.cursor.fetchone()
        cantidad = resultados[0]
        numVenta = 1 if cantidad == 0 else cantidad + 1
        self.campoNumeroVenta = QLabel(str(numVenta))
        self.campoNumeroVenta.setStyleSheet("""
            QLabel { background-color: white; border: 2px solid #e2e8f0; border-radius: 6px;
            padding: 10px; font-size: 14px; min-height: 40px; color: #2c3e50; }
        """)
        self.etiquetaNumeroVenta = QLabel("N° Venta")
        self.etiquetaNumeroVenta.setStyleSheet("""
            QLabel { color: #2c3e50; font-size: 16px; font-weight: bold; margin-bottom: 5px; }
        """)
        layoutElemento.addWidget(self.etiquetaNumeroVenta, alignment=Qt.AlignCenter)
        layoutElemento.addWidget(self.campoNumeroVenta, alignment=Qt.AlignCenter)
        layoutCampo1.addLayout(layoutElemento)
        layoutIzq.addLayout(layoutCampo1)
        layoutCampo2 = QHBoxLayout()
        self.botonEmpleados = QPushButton("Empleados")
        self.botonEmpleados.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border-radius: 8px; padding: 12px 24px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.botonEmpleados.clicked.connect(self.mostrarEmpleados)
        
        self.botonMesas = QPushButton("Salones/Mesas")
        self.botonMesas.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border-radius: 8px; padding: 12px 24px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.botonMesas.clicked.connect(self.mostrarMesas)
        
        self.botonProductos = QPushButton("Productos")
        self.botonProductos.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border-radius: 8px; padding: 12px 24px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.botonProductos.clicked.connect(self.cargarCategorias)
        
        layoutCampo2.addWidget(self.botonEmpleados)
        layoutCampo2.addWidget(self.botonMesas)
        layoutCampo2.addWidget(self.botonProductos)
        layoutDer.addLayout(layoutCampo2)
       
        campoTabla = QWidget()
        layoutTabla = QVBoxLayout()
        campoTabla.setLayout(layoutTabla)
        scroll = QScrollArea()
        self.tabla = QTableWidget()
        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: white; border: 2px solid #e2e8f0; border-radius: 8px;
                gridline-color: #e2e8f0; font-size: 14px;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #e2e8f0; }
            QTableWidget::item:selected { background-color: #e6f2ff; color: #2c3e50; }
            QHeaderView::section { background-color: #3498db; color: white; padding: 10px; border: none; font-weight: bold; font-size: 14px; }
        """)
        scroll.setWidget(self.tabla)
        layoutTabla.addWidget(scroll)
        scroll.setWidgetResizable(True)
        self.tabla.setColumnCount(6)
        columnas = ["Cant.", "Tipo", "Producto", "P.Unitario", "Subtotal", "Accion"]
        self.tabla.setHorizontalHeaderLabels(columnas)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setFocusPolicy(Qt.NoFocus)
        self.tabla.setSelectionMode(QTableWidget.NoSelection)
        layoutIzq.addWidget(campoTabla)
        
        layoutTotal = QHBoxLayout()
        self.totalVentaEtiqueta = QLabel("Total:")
        self.totalVentaEtiqueta.setStyleSheet("""
            QLabel { color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 5px; }
        """)
        self.totalVenta = QLabel("0.00 Bs")
        self.totalVenta.setStyleSheet("""
            QLabel { background-color: white; border: 2px solid #e2e8f0; border-radius: 6px;
            padding: 10px; font-size: 18px; font-weight: bold; min-height: 40px; color: #2c3e50; }
        """)
        layoutTotal.addWidget(self.totalVentaEtiqueta, alignment=Qt.AlignCenter)
        layoutTotal.addWidget(self.totalVenta, alignment=Qt.AlignCenter)
        layoutIzq.addLayout(layoutTotal)
        

        layoutCampo4 = QVBoxLayout()
        self.construirSeccionProductos(layoutCampo4)
        layoutDer.addLayout(layoutCampo4)
        
  
        self.layoutPrincipal.addLayout(layoutCampo)
        
        layoutParteInferior = QHBoxLayout()
        botonEnviarCocina = QPushButton("Enviar Cocina/Barra")
        botonEnviarCocina.setStyleSheet("""
            QPushButton { background-color: #2ecc71; color: white; border-radius: 8px; padding: 12px 24px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #27ae60; }
        """)
        botonEnviarCocina.clicked.connect(self.enviarVentaCocina)
        botonEnviarCocina.setCursor(Qt.PointingHandCursor)
        
        botonImprimirTicket = QPushButton("Imprimir Ticket")
        botonImprimirTicket.setStyleSheet("""
            QPushButton { background-color: #f39c12; color: white; border-radius: 8px; padding: 12px 24px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #e67e22; }
        """)
        botonImprimirTicket.clicked.connect(self.imprimirTicket)
        botonImprimirTicket.setCursor(Qt.PointingHandCursor)
        
        layoutParteInferior.addWidget(botonEnviarCocina)
        layoutParteInferior.addWidget(botonImprimirTicket)
        
        self.layoutPrincipal.addLayout(layoutParteInferior)
        self.conn.close()
    

    def verificarBloqueo(self, accion):
        if (self.banderaCocina or self.banderaTicket) and not self.enviada:
            QMessageBox.warning(self, "Venta Bloqueada", 
                               f"No es posible {accion}. Debe completar el registro de la venta actual.")
            return True
        return False


    def verificarImpresoraConfigurada(self, tipo):
        impresora = self.manejador_impresion.obtener_impresora(tipo)
        if not impresora:
            if tipo == "Barra":
                mensaje = "No hay una impresora configurada para Barra/Ticket.\nPor favor, configure una impresora en la sección de configuración."
            else:
                mensaje = "No hay una impresora configurada para Cocina.\nPor favor, configure una impresora en la sección de configuración."
            return False, mensaje
        return True, "Impresora configurada correctamente"
    

    def imprimirTicket(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        
        configurada, mensaje = self.verificarImpresoraConfigurada("Barra")
        if not configurada:
            QMessageBox.warning(self, "Impresora no configurada", mensaje)
            self.conn.close()
            return
        
        if self.banderaCocina and not self.enviada:
            if self.ticket_print_count >= 2:
                if not self.solicitar_clave_admin():
                    self.conn.close()
                    return
        elif self.banderaTicket and not self.banderaCocina and self.ticket_print_count >= 2:
            if not self.solicitar_clave_admin():
                self.conn.close()
                return
        elif self.ticket_print_count >= 2:
            if not self.solicitar_clave_admin():
                self.conn.close()
                return
    
        if self.campoEncargado.text() == "" or self.campoMesa.text() == "" or self.campoSeccion.text() == "":
            QMessageBox.information(self, "Advertencia", "Rellene los campos necesarios por favor")
            self.conn.close()
            return
        
        if self.tabla.rowCount() == 0:
            QMessageBox.information(self, "Advertencia", "Debe contener por lo menos un producto la venta")
            self.conn.close()
            return

        try:
            datos_venta = {
                'num_venta': self.campoNumeroVenta.text(),
                'fecha': datetime.now().strftime("%d-%m-%Y"),
                'hora': self.campoTiempo.text(),
                'empleado': self.campoEncargado.text(),
                'mesa': self.campoMesa.text(),
                'seccion': self.campoSeccion.text(),
                'cajero': self.campoCajero.text(),
                'total': self.totalVenta.text().replace(" Bs", "").strip()
            }
            
            items = []
            for i in range(self.tabla.rowCount()):
                items.append({
                    'cantidad': int(self.tabla.item(i, 0).text()),
                    'tipo': self.tabla.item(i, 1).text(),
                    'producto': self.tabla.item(i, 2).text(),
                    'precio': float(self.tabla.item(i, 3).text()),
                    'subtotal': float(self.tabla.item(i, 4).text())
                })
            
            exito, mensaje = self.manejador_impresion.imprimir_ticket(datos_venta, items)
            
            if exito:
                self.signals.resultado_ticket.emit(True, mensaje, datos_venta, items)
            else:
                self.signals.resultado_ticket.emit(False, mensaje, {}, [])
        except Exception as e:
            self.signals.resultado_ticket.emit(False, f"Error al imprimir: {str(e)}", {}, [])
        finally:
            self.conn.close()


    def enviarVentaCocina(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        configurada, mensaje = self.verificarImpresoraConfigurada("Cocina")
        if not configurada:
            QMessageBox.warning(self, "Impresora no configurada", mensaje)
            self.conn.close()
            return
        if self.banderaTicket and not self.enviada:
            if self.cocina_print_count >= 2:
                if not self.solicitar_clave_admin():
                    self.conn.close()
                    return
        elif self.banderaCocina and not self.banderaTicket and self.cocina_print_count >= 2:
            if not self.solicitar_clave_admin():
                self.conn.close()
                return
        elif self.cocina_print_count >= 2:
            if not self.solicitar_clave_admin():
                self.conn.close()
                return
        if self.campoEncargado.text() == "" or self.campoMesa.text() == "" or self.campoSeccion.text() == "":
            QMessageBox.information(self, "Advertencia", "Rellene los campos necesarios por favor")
            self.conn.close()
            return
        if self.tabla.rowCount() == 0:
            QMessageBox.information(self, "Advertencia", "Debe contener por lo menos un producto la venta")
            self.conn.close()
            return
        try:
            datos_venta = {
                'num_venta': self.campoNumeroVenta.text(),
                'fecha': datetime.now().strftime("%d-%m-%Y"),
                'hora': self.campoTiempo.text(),
                'empleado': self.campoEncargado.text(),
                'mesa': self.campoMesa.text(),
                'seccion': self.campoSeccion.text(),
                'cajero': self.campoCajero.text()
            }
            items = []
            for i in range(self.tabla.rowCount()):
                items.append({
                    'cantidad': int(self.tabla.item(i, 0).text()),
                    'tipo': self.tabla.item(i, 1).text(),
                    'producto': self.tabla.item(i, 2).text()
                })
            
            exito, mensaje = self.manejador_impresion.imprimir_cocina(datos_venta, items)
            if exito:
                self.signals.resultado_cocina.emit(True, mensaje, datos_venta, items)
            else:
                self.signals.resultado_cocina.emit(False, mensaje, {}, [])
        except Exception as e:
            self.signals.resultado_cocina.emit(False, f"Error al enviar pedido: {str(e)}", {}, [])
        finally:
            self.conn.close()
    

    @pyqtSlot(bool, str, dict, list)
    def _procesar_resultado_ticket(self, exito, mensaje, datos_venta, items):
        if exito:
            QMessageBox.information(self, "Éxito", f"Ticket impreso correctamente\n{mensaje}")
            if not self.banderaTicket and not self.banderaCocina:
                self.subirInformacion()
            self.banderaTicket = True
            self.enviada = True if self.banderaCocina else False
            self.ticket_print_count += 1
            if self.banderaTicket and self.banderaCocina:
                self.limpiarCampos()
                self._clear_grid(self.layoutProductos)
        else:
            QMessageBox.warning(self, "Advertencia", f"No se pudo imprimir el ticket\n{mensaje}")
    

    @pyqtSlot(bool, str, dict, list)
    def _procesar_resultado_cocina(self, exito, mensaje, datos_venta, items):
        if exito:
            QMessageBox.information(self, "Éxito", f"Pedido cocina enviado correctamente\n{mensaje}")
            if not self.banderaTicket and not self.banderaCocina:
                self.subirInformacion()
            self.banderaCocina = True
            self.enviada = True if self.banderaTicket else False
            self.cocina_print_count += 1
            if self.banderaTicket and self.banderaCocina:
                self.limpiarCampos()
                self._clear_grid(self.layoutProductos)
        else:
            QMessageBox.warning(self, "Advertencia", f"No se pudo enviar pedido a cocina\n{mensaje}")
    

    def subirInformacion(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        if self.campoEncargado.text() == "" or self.campoMesa.text() == "" or self.campoSeccion.text() == "":
            QMessageBox.information(self, "Advertencia", "Rellene los campos necesarios porfavor")
            self.conn.close()
            return
        if self.tabla.rowCount() == 0:
            QMessageBox.information(self, "Advertencia", "Debe contener por lo menos un producto la venta")
            self.conn.close()
            return
        try:
            horaRegistro = self.campoTiempo.text()
            aliasCajero = self.campoCajero.text()
            if aliasCajero == "DIRECTORIO":
                idCajero = -1
            else:
                self.cursor.execute("""SELECT codEmp FROM Empleado WHERE aliasEmp=?""", (aliasCajero,))
                resultado = self.cursor.fetchone()
                idCajero = resultado[0]
            aliasEmpleado = self.campoEncargado.text()
            self.cursor.execute("""SELECT codEmp FROM Empleado WHERE aliasEmp=?""", (aliasEmpleado,))
            resultados = self.cursor.fetchone()
            idEmpleado = resultados[0]
            totalVenta = self.totalVenta.text().replace(" Bs", "").strip()
            estadoVenta = "Preparacion"
            idMesa = int(self.campoMesa.text())
            nombSeccion = self.campoSeccion.text()
            self.cursor.execute("""SELECT idSeccion FROM Seccion WHERE nombSeccion=?""", (nombSeccion,))
            resultados = self.cursor.fetchone()
            idSeccion = resultados[0]
            fechaRegistro = datetime.now()
            self.cursor.execute("""SELECT disponible FROM Mesa WHERE idMesa=? AND idSeccion=?""", (idMesa,int(idSeccion)))
            resultado = self.cursor.fetchone()
            estado = resultado[0]
            if not estado:
                self.cursor.execute("""SELECT numVenta, fechaReg FROM Venta WHERE idMesa=? AND idSeccion=? ORDER BY fechaReg DESC LIMIT 1""", 
                   (idMesa, idSeccion))
                resultados = self.cursor.fetchone()
                nVenta, fVenta = resultados[0], resultados[1]
                for i in range(self.tabla.rowCount()):
                    cantidad = self.tabla.item(i, 0).text()
                    nombre = self.tabla.item(i, 2).text()
                    subtotal = self.tabla.item(i, 4).text()
                    tipoConsumo = self.tabla.item(i, 1).text()
                    self.cursor.execute("""SELECT * FROM Promocion WHERE nomProm=?""", (nombre,))
                    resultados = self.cursor.fetchall()
                    if resultados:
                        self.cursor.execute("""SELECT idProm FROM Promocion WHERE nomProm=?""", (nombre,))
                        idPromocion = self.cursor.fetchone()[0]
                        self.cursor.execute("""INSERT INTO DetallesVenta 
                            (numVenta, fechaRegVenta, fechaRegDetalleVenta, idProm, subtotal, cantidadProdDet, tipoConsumo, estadoDetalleVenta,idMeseroActual) 
                            VALUES(?,?,?,?,?,?,?,?,?)""",
                            (nVenta, fVenta, fechaRegistro, idPromocion, float(subtotal), int(cantidad), tipoConsumo, estadoVenta,idEmpleado))
                    else:
                        self.cursor.execute("""SELECT idProd FROM Producto WHERE nomProd=?""", (nombre,))
                        idProducto = self.cursor.fetchone()[0]
                        self.cursor.execute("""INSERT INTO DetallesVenta 
                             (numVenta, fechaRegVenta, fechaRegDetalleVenta, idProd, subtotal, cantidadProdDet, tipoConsumo, estadoDetalleVenta,idMeseroActual)
                            VALUES(?,?,?,?,?,?,?,?,?)""",
                            (nVenta, fVenta, fechaRegistro, idProducto, float(subtotal), int(cantidad), tipoConsumo, estadoVenta,idEmpleado))
                
                self.cursor.execute("""SELECT totalVenta FROM Venta WHERE numVenta=? AND fechaReg=?""", (nVenta, fVenta))
                totalAnterior = self.cursor.fetchone()[0]
                nuevoTotal = float(totalAnterior) + float(totalVenta)
                self.cursor.execute("""UPDATE Venta SET totalVenta=? WHERE numVenta=? AND fechaReg=?""", (nuevoTotal, nVenta, fVenta))
            else:
                numVenta = self.campoNumeroVenta.text()
                self.cursor.execute("""INSERT INTO Venta(
                    numVenta, fechaReg, horaReg, codEmp, codEmp2, totalVenta, 
                    idMesa, idSeccion
                ) VALUES (?,?,?,?,?,?,?,?)""",
                    (int(numVenta), fechaRegistro, horaRegistro, int(idEmpleado), int(idCajero), 
                     float(totalVenta), idMesa, int(idSeccion)))
                
                self.cursor.execute("""UPDATE Mesa SET disponible=FALSE WHERE idMesa=? AND idSeccion=?""", (idMesa,int(idSeccion)))
                self.cursor.execute("""SELECT MAX(numVenta) FROM Venta WHERE fechaReg = ?""", (fechaRegistro,))
                resultado = self.cursor.fetchone()
                numVenta = resultado[0]
                for i in range(self.tabla.rowCount()):
                    cantidad = self.tabla.item(i, 0).text()
                    nombre = self.tabla.item(i, 2).text()
                    subtotal = self.tabla.item(i, 4).text()
                    tipoConsumo = self.tabla.item(i, 1).text()
                    
                    self.cursor.execute("""SELECT * FROM Promocion WHERE nomProm=?""", (nombre,))
                    resultados = self.cursor.fetchall()
                    if resultados:
                        self.cursor.execute("""SELECT idProm FROM Promocion WHERE nomProm=?""", (nombre,))
                        idPromocion = self.cursor.fetchone()[0]
                        self.cursor.execute("""INSERT INTO DetallesVenta 
                             (numVenta, fechaRegVenta, fechaRegDetalleVenta, idProm, subtotal, cantidadProdDet, tipoConsumo, estadoDetalleVenta,idMeseroActual)
                            VALUES(?,?,?,?,?,?,?,?,?)""",
                            (int(numVenta), fechaRegistro, fechaRegistro, idPromocion, float(subtotal), int(cantidad), tipoConsumo, estadoVenta,idEmpleado))
                    else:
                        self.cursor.execute("""SELECT idProd FROM Producto WHERE nomProd=?""", (nombre,))
                        idProducto = self.cursor.fetchone()[0]
                        self.cursor.execute("""INSERT INTO DetallesVenta 
                             (numVenta, fechaRegVenta, fechaRegDetalleVenta, idProd, subtotal, cantidadProdDet, tipoConsumo, estadoDetalleVenta,idMeseroActual)
                            VALUES(?,?,?,?,?,?,?,?,?)""",
                            (int(numVenta), fechaRegistro, fechaRegistro, idProducto, float(subtotal), int(cantidad), tipoConsumo, estadoVenta,idEmpleado))
                
                self.nuevaVenta = True
            self.enviada = True
            self.actualizarStock('restar', conn=self.conn)
            self.conn.commit()
        except Exception as e:
            print(f"Error al subir información: {str(e)}")
            import traceback
            traceback.print_exc()
            try:
                self.conn.rollback()
            except Exception:
                pass
        finally:
            try:
                self.conn.close()
            except Exception:
                pass
    

    def cancelarVenta(self):
        if self.banderaTicket or self.banderaCocina:
            QMessageBox.warning(self, "Venta Bloqueada", 
                               "No se puede limpiar los campos porque ya se ha enviado a impresión/cocina.")
            return
        if self.tabla.rowCount() == 0:
            self.limpiarCampos()
            return
        respuesta = QMessageBox.question(
            self,
            "Confirmar limpieza",
            "¿Está seguro de que desea limpiar todos los campos?\n\n" +
            "Se perderán todos los productos agregados.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if respuesta == QMessageBox.No:
            return
        self.limpiarCampos()
    

    def limpiarCampos(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.tabla.setRowCount(0)
        self.campoEncargado.setText("")
        self.campoMesa.setText("")
        self.campoSeccion.setText("")
        self.totalVenta.setText("0.00 Bs")
        self.banderaCocina = False
        self.banderaTicket = False
        self.enviada = False
        self.ticket_print_count = 0
        self.modificacion = False
        self.cocina_print_count = 0
        fecha = datetime.now().date()
        if self.nuevaVenta == True:
            self.cursor.execute("""SELECT COUNT(*) FROM Venta WHERE DATE(fechaReg)=?""", (fecha,))
            resultados = self.cursor.fetchone()
            cantidad = resultados[0]
            numVenta = 1 if cantidad == 0 else cantidad + 1
            self.campoNumeroVenta.setText(str(numVenta))
            self.nuevaVenta = False
        self.conn.close()
    
    
    def actualizarNumeroVenta(self,fecha):
        self.conn=sqlite3.connect(DB_PATH)
        self.cursor=self.conn.cursor()
        self.cursor.execute("""SELECT COUNT(*) FROM Venta WHERE DATE(fechaReg)=?""", (fecha,))
        resultados = self.cursor.fetchone()
        cantidad = resultados[0]
        numVenta = 1 if cantidad == 0 else cantidad + 1
        self.campoNumeroVenta.setText(str(numVenta))
        self.conn.close()
        
        
    def solicitar_clave_admin(self) -> bool:
        dialog = QDialog(self)
        dialog.setWindowTitle("Autorización requerida")
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
        
        label = QLabel("Ingrese la contraseña de administrador:")
        label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        layout.addWidget(label)
        password_container = QWidget()
        password_container.setStyleSheet("background: transparent;")
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(4)
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setMinimumHeight(5)
        password_input.setStyleSheet("""
            QLineEdit {
                background-color: white; 
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 5px 14px;
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
        toggle_password_btn.setFixedHeight(48)
        toggle_password_btn.setFixedWidth(34)
        toggle_password_btn.setCheckable(True)
        toggle_password_btn.setCursor(Qt.PointingHandCursor)
        toggle_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin: 0px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e6f2ff;
                border: 2px solid #4a89dc;
            }
            QPushButton:pressed {
                background-color: #d0e7ff;
            }
            QPushButton:checked {
                background-color: #e6f2ff;
                border: 2px solid #4a89dc;
            }
        """)
        toggle_password_btn.setText("🔒")
        toggle_password_btn.setFont(QFont("Segoe UI Emoji", 12))
        def toggle_password_visibility(checked):
            if checked:
                password_input.setEchoMode(QLineEdit.Normal)
                toggle_password_btn.setText("🔓")
            else:
                password_input.setEchoMode(QLineEdit.Password)
                toggle_password_btn.setText("🔒")
        toggle_password_btn.toggled.connect(toggle_password_visibility)
        password_layout.addWidget(toggle_password_btn)
        layout.addWidget(password_container)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        for button in button_box.buttons():
            text = button.text().lower()
            if 'ok' in text or 'aceptar' in text or 'entrar' in text:
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
                    QPushButton:hover {
                        background-color: #27ae60;
                    }
                    QPushButton:pressed {
                        background-color: #229954;
                        padding-top: 11px;
                        padding-bottom: 9px;
                    }
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
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                    QPushButton:pressed {
                        background-color: #a93226;
                        padding-top: 11px;
                        padding-bottom: 9px;
                    }
                """)
        layout.addWidget(button_box, alignment=Qt.AlignCenter)
        password_input.setFocus()
        password_input.returnPressed.connect(dialog.accept)
        if dialog.exec_() == QDialog.Accepted:
            clave = password_input.text()
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""SELECT 1 FROM Directorio WHERE contrasenaAdmin = ?""", (clave,))
            existe = cur.fetchone()
            conn.close()
            if existe:
                return True
            else:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setWindowTitle("Error")
                msg_box.setText("Contraseña incorrecta.")
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #ffffff;
                        border: 2px solid #e2e8f0;
                        border-radius: 10px;
                    }
                    QMessageBox QLabel {
                        color: #2c3e50;
                        font-size: 14px;
                        font-weight: 500;
                        padding: 10px;
                    }
                    QMessageBox QPushButton {
                        background-color: #3498db; 
                        color: white; 
                        border-radius: 6px; 
                        padding: 8px 20px; 
                        font-weight: 600;
                        font-size: 14px;
                        min-width: 90px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                msg_box.exec_()
                return False
        else:
            return False


    def construirSeccionProductos(self, layoutCampo4):
        contCat = QHBoxLayout()
        self.btnPrevCat1 = QPushButton("◀")
        self.btnPrevCat1.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btnNextCat1 = QPushButton("▶")
        self.btnNextCat1.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.scrollCat = QScrollArea()
        self.scrollCat.setWidgetResizable(True)
        self.scrollCat.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollCat.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollCat.setFixedHeight(140)
        self.widgetCat = QWidget()
        self.widgetCat.setMinimumHeight(120)
        self.layoutCategorias = QHBoxLayout(self.widgetCat)
        self.layoutCategorias.setContentsMargins(8, 8, 8, 8)
        self.layoutCategorias.setSpacing(12)
        self.layoutCategorias.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.scrollCat.setWidget(self.widgetCat)
        contCat.addWidget(self.btnPrevCat1)
        contCat.addWidget(self.scrollCat, 1)
        contCat.addWidget(self.btnNextCat1)
        layoutCampo4.addLayout(contCat)
        self.btnPrevCat1.clicked.connect(lambda: self.scrollCat.horizontalScrollBar().setValue(
            self.scrollCat.horizontalScrollBar().value() - 200))
        self.btnNextCat1.clicked.connect(lambda: self.scrollCat.horizontalScrollBar().setValue(
            self.scrollCat.horizontalScrollBar().value() + 200))
        contSub = QHBoxLayout()
        self.btnPrevSub = QPushButton("◀")
        self.btnPrevSub.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btnNextSub = QPushButton("▶")
        self.btnNextSub.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.scrollSub = QScrollArea()
        self.scrollSub.setWidgetResizable(True)
        self.scrollSub.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollSub.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollSub.setFixedHeight(140)
        self.widgetSub = QWidget()
        self.widgetSub.setMinimumHeight(120)
        self.layoutSubcategorias = QHBoxLayout(self.widgetSub)
        self.layoutSubcategorias.setContentsMargins(8, 8, 8, 8)
        self.layoutSubcategorias.setSpacing(12)
        self.layoutSubcategorias.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.scrollSub.setWidget(self.widgetSub)
        contSub.addWidget(self.btnPrevSub)
        contSub.addWidget(self.scrollSub, 1)
        contSub.addWidget(self.btnNextSub)
        layoutCampo4.addLayout(contSub)
        self.btnPrevSub.clicked.connect(lambda: self.scrollSub.horizontalScrollBar().setValue(
            self.scrollSub.horizontalScrollBar().value() - 200))
        self.btnNextSub.clicked.connect(lambda: self.scrollSub.horizontalScrollBar().setValue(
            self.scrollSub.horizontalScrollBar().value() + 200))
        self.scrollProductos = QScrollArea()
        self.scrollProductos.setStyleSheet("""
        QScrollArea {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 2px;
        }
        QScrollArea > QWidget > QWidget { 
        background-color: transparent; 
        }

        QScrollBar:vertical { 
            border: none; 
            background: #f8f9fa; 
            width: 14px; 
            margin: 0px; 
            border-radius: 7px; 
        }

        QScrollBar::handle:vertical { 
            background: #c0c7d4; 
            min-height: 40px; 
            border-radius: 7px; 
            margin: 3px; 
        }

        QScrollBar::handle:vertical:hover { 
            background: #a0b0c4; 
        }

        QScrollBar::handle:vertical:pressed { 
            background: #8090b0; 
        }

        QScrollBar::sub-line:vertical, 
        QScrollBar::add-line:vertical { 
            height: 0px; 
        }

        QScrollBar:horizontal { 
            border: none; 
            background: #f8f9fa; 
            height: 14px; 
            margin: 0px; 
            border-radius: 7px; 
        }

        QScrollBar::handle:horizontal { 
            background: #c0c7d4; 
            min-width: 40px; 
            border-radius: 7px; 
            margin: 3px; 
        }

        QScrollBar::handle:horizontal:hover { 
            background: #a0b0c4; 
        }

        QScrollBar::handle:horizontal:pressed { 
            background: #8090b0; 
        }

        QScrollBar::sub-line:horizontal, 
        QScrollBar::add-line:horizontal { 
            width: 0px; 
        }
    """)
        self.scrollProductos.setWidgetResizable(True)
        self.widgetProductos = QWidget()
        self.widgetProductos.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.layoutProductos = QGridLayout(self.widgetProductos)
        self.layoutProductos.setContentsMargins(12, 12, 12, 12)
        self.layoutProductos.setHorizontalSpacing(12)
        self.layoutProductos.setVerticalSpacing(12)
        self.scrollProductos.setWidget(self.widgetProductos)
        layoutCampo4.addWidget(self.scrollProductos, 1)
        self.cargarCategorias()
        

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
    

    def _clear_grid(self, grid):
        while grid.count():
            item = grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
    

    def cargarCategorias(self):
            self.conn = sqlite3.connect(DB_PATH)
            self.cursor = self.conn.cursor()
            self.scrollCat.setVisible(True)
            self.scrollSub.setVisible(True)
            self.btnPrevSub.setVisible(True)
            self.btnNextSub.setVisible(True)
            self.btnPrevCat1.setVisible(True)
            self.btnNextCat1.setVisible(True)
            self._clear_layout(self.layoutCategorias)
            btn_prom = self.crearBotonCategoria("PROMOCIONES", "#9b59b6")
            btn_prom.setMinimumSize(160, 120)
            btn_prom.setMaximumSize(160, 120)
            btn_prom.clicked.connect(self.mostrarPromociones)
            self.layoutCategorias.addWidget(btn_prom)
            self.cursor.execute("SELECT idCategoria, nomCategoria, imagenCategoria FROM Categoria WHERE activa=1 ORDER BY nomCategoria")
            for idCat, nombre, imagen in self.cursor.fetchall():
                btn = self.crearBotonCategoria(nombre, "#3498db", imagen)
                btn.setMinimumSize(160, 120)
                btn.setMaximumSize(160, 120)
                btn.clicked.connect(lambda checked, idCat=idCat: self.cargarSubcategorias(idCat))
                self.layoutCategorias.addWidget(btn)
            self.layoutCategorias.addStretch()
            self._clear_layout(self.layoutSubcategorias)
            self._clear_grid(self.layoutProductos)
            self.conn.close()


    def crearBotonCategoria(self, texto, color_base, imagen_blob=None):
        btn = QPushButton()
        btn.setFixedSize(160,120)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("QPushButton{background:transparent;border:none;}")
        layout = QVBoxLayout(btn)
        layout.setContentsMargins(0,0,0,0)
        lbl_bg = QLabel()
        lbl_bg.setFixedSize(160,120)
        lbl_bg.setAlignment(Qt.AlignCenter)
        lbl_bg.setStyleSheet("background:transparent;")
        if imagen_blob:
            pix = QPixmap.fromImage(QImage.fromData(imagen_blob))
        else:
            pix = QPixmap(get_resource_path("Imagenes/camara.png"))
        pix = pix.scaled(160,120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        rounded = QPixmap(160,120)
        rounded.fill(Qt.transparent)
        p = QPainter(rounded)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0,0,160,120,12,12)
        p.setClipPath(path)
        x = (160 - pix.width())//2
        y = (120 - pix.height())//2
        p.drawPixmap(x,y,pix)
        grad = QLinearGradient(0,0,0,120)
        grad.setColorAt(0, QColor(0,0,0,30))
        grad.setColorAt(1, QColor(0,0,0,140))
        p.fillPath(path, grad)
        p.end()
        lbl_bg.setPixmap(rounded)
        layout.addWidget(lbl_bg)
        lbl_text = QLabel(texto.upper(), lbl_bg)
        lbl_text.setGeometry(0,0,160,120)
        lbl_text.setAlignment(Qt.AlignCenter)
        lbl_text.setWordWrap(True)
        lbl_text.setStyleSheet("""
            QLabel{
                color:white;
                font-weight:800;
                font-size:13px;
                background:transparent;
                text-shadow:0 0 6px black;
            }
        """)
        return btn
        

    def cargarSubcategorias(self, idCategoria):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._clear_layout(self.layoutSubcategorias)
        self._clear_grid(self.layoutProductos)
        self.cursor.execute(
            "SELECT idSubcategoria, nombre, imagenSubcategoria FROM Subcategoria WHERE activa=1 AND idCategoria=? ORDER BY nombre",
            (idCategoria,)
        )
        subcats = self.cursor.fetchall()
        if subcats:
            for idSub, nombre, imagen in subcats:
                btn = self.crearBotonCategoria(nombre, "#34495e", imagen)
                btn.setMinimumSize(160, 120)
                btn.setMaximumSize(160, 120)
                btn.clicked.connect(lambda checked, idSub=idSub: self.mostrarProductos(idSub))
                self.layoutSubcategorias.addWidget(btn)
            self.layoutSubcategorias.addStretch()
        else:
            self.mostrarProductosDeCategoria(idCategoria)
        self.conn.close()
        

    def mostrarProductos(self, idSubcategoria):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._clear_grid(self.layoutProductos)
        self.cursor.execute(
            "SELECT nomProd, imgProd FROM Producto WHERE activo=1 AND idSubcategoria=? ORDER BY nomProd",
            (idSubcategoria,)
        )
        productos = self.cursor.fetchall()
        row, col = 0, 0
        max_cols = 6
        for nom, img in productos:
            caja = self.crearItem(nom, img, True)
            caja.setFixedSize(150, 160)
            self.layoutProductos.addWidget(caja, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        if self.layoutProductos.count() == 0:
            self.layoutProductos.addWidget(QLabel("No hay productos disponibles"), 0, 0, 1, max_cols)
        self.layoutProductos.setRowStretch(row + 1, 1)
        self.conn.close()


    def mostrarProductosDeCategoria(self, idCategoria):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._clear_grid(self.layoutProductos)
        self.cursor.execute("""
            SELECT p.nomProd, p.imgProd
            FROM Producto p
            JOIN Subcategoria s ON p.idSubcategoria = s.idSubcategoria
            WHERE p.activo=1 AND s.idCategoria=?
            ORDER BY p.nomProd
        """, (idCategoria,))
        productos = self.cursor.fetchall()
        row, col = 0, 0
        max_cols = 6
        for nom, img in productos:
            caja = self.crearItem(nom, img, True)
            caja.setFixedSize(150, 160)
            self.layoutProductos.addWidget(caja, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        if self.layoutProductos.count() == 0:
            self.layoutProductos.addWidget(QLabel("No hay productos disponibles"), 0, 0, 1, max_cols)
        self.layoutProductos.setRowStretch(row + 1, 1)
        self.conn.close()
        

    def mostrarPromociones(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._clear_layout(self.layoutSubcategorias)
        self._clear_grid(self.layoutProductos)
        now = datetime.now()
        current_date = now.date()
        current_time = now.time()
        current_weekday = now.weekday()
        try:
            self.cursor.execute("""
                SELECT idProm, nomProm, imgProm, fechaEspecifica, 
                       fechaInicio, fechaFin, horaInicio, horaFin
                FROM Promocion 
                WHERE activo=1
                ORDER BY nomProm
            """)
            todas_promos = self.cursor.fetchall()
            promos_filtradas = []
            for idProm, nomProm, imgProm, fechaEspecifica, fechaInicio, fechaFin, horaInicio, horaFin in todas_promos:
                if fechaEspecifica:
                    try:
                        fecha_especifica = datetime.strptime(fechaEspecifica, "%Y-%m-%d").date()
                        if fecha_especifica != current_date:
                            continue
                        hora_valida = True
                        if horaInicio and horaFin:
                            try:
                                hora_ini = datetime.strptime(horaInicio, "%H:%M:%S").time()
                                hora_fin = datetime.strptime(horaFin, "%H:%M:%S").time()
                                if not (hora_ini <= current_time <= hora_fin):
                                    hora_valida = False
                            except:
                                pass
                        if hora_valida:
                            promos_filtradas.append((nomProm, imgProm))
                            continue  
                    except:
                        pass
                fecha_valida = False
                if fechaInicio and fechaFin:
                    try:
                        fecha_ini = datetime.strptime(fechaInicio, "%Y-%m-%d").date()
                        fecha_fin = datetime.strptime(fechaFin, "%Y-%m-%d").date()
                        if fecha_ini <= current_date <= fecha_fin:
                            fecha_valida = True
                    except:
                        pass
                else:
                    fecha_valida = True
                hora_valida = False
                if horaInicio and horaFin:
                    try:
                        hora_ini = datetime.strptime(horaInicio, "%H:%M:%S").time()
                        hora_fin = datetime.strptime(horaFin, "%H:%M:%S").time()
                        if hora_ini <= current_time <= hora_fin:
                            hora_valida = True
                    except:
                        pass
                else:
                    hora_valida = True
                self.cursor.execute("""
                    SELECT COUNT(*) FROM PromocionDias 
                    WHERE idProm = ? AND diaSemana = ?
                """, (idProm, current_weekday))
                tiene_dia = self.cursor.fetchone()[0] > 0
                self.cursor.execute("""
                    SELECT COUNT(*) FROM PromocionDias 
                    WHERE idProm = ?
                """, (idProm,))
                total_dias = self.cursor.fetchone()[0]
                dias_valido = (total_dias == 0) or tiene_dia
                if fecha_valida and hora_valida and dias_valido:
                    promos_filtradas.append((nomProm, imgProm))
            row, col = 0, 0
            max_cols = 6
            for nom, img in promos_filtradas:
                caja = self.crearItem(nom, img, False)
                caja.setFixedSize(150, 160)
                self.layoutProductos.addWidget(caja, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            if self.layoutProductos.count() == 0:
                self.layoutProductos.addWidget(QLabel("No hay promociones disponibles"), 0, 0, 1, max_cols)
            self.layoutProductos.setRowStretch(row + 1, 1)
        except Exception as e:
            print(f"Error en mostrarPromociones: {e}")
            import traceback
            traceback.print_exc()
            self.cursor.execute("SELECT nomProm, imgProm FROM Promocion WHERE activo=1 ORDER BY nomProm")
            promos = self.cursor.fetchall()
            row, col = 0, 0
            max_cols = 6
            for nom, img in promos:
                caja = self.crearItem(nom, img, False)
                caja.setFixedSize(150, 160)
                self.layoutProductos.addWidget(caja, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            if self.layoutProductos.count() == 0:
                self.layoutProductos.addWidget(QLabel("No hay promociones disponibles"), 0, 0, 1, max_cols)
            self.layoutProductos.setRowStretch(row + 1, 1)
        finally:
            self.conn.close()
    

    def crearItem(self, nombre, imgBlob, bandera):
        contenedor = QPushButton() 
        contenedor.setFixedSize(150, 160)
        contenedor.setCursor(Qt.PointingHandCursor)
        contenedor.setStyleSheet("""
            QPushButton {
                background: #ffffff; 
                border: 1px solid #e2e8f0; 
                border-radius: 10px;
                text-align: center;
            }
            QPushButton:hover { 
                border: 1px solid #cbd5e1;
                background: #f8fafc; 
            }
        """)
        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        labelImg = QLabel()
        labelImg.setFixedSize(100, 100)
        labelImg.setAlignment(Qt.AlignCenter)
        if imgBlob:
            try:
                image = QImage.fromData(imgBlob)
                pix = QPixmap.fromImage(image).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                labelImg.setPixmap(pix)
            except:
                ph = QPixmap(100, 100)
                ph.fill(QColor("#f1f5f9"))
                labelImg.setPixmap(ph)
        else:
            ph = QPixmap(100, 100)
            ph.fill(QColor("#f1f5f9"))
            labelImg.setPixmap(ph)
        layout.addWidget(labelImg, alignment=Qt.AlignCenter)
        labelNom = QLabel(nombre)
        labelNom.setAlignment(Qt.AlignCenter)
        labelNom.setWordWrap(True)
        labelNom.setStyleSheet("QLabel { color: #2c3e50; font-size: 14px; font-weight: 500; }")
        layout.addWidget(labelNom)
        contenedor.clicked.connect(lambda: self.dialogProducto(nombre, bandera))
        return contenedor


    def dialogProducto(self, nombre, bandera):
        if self.verificarBloqueo("agregar productos"):
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Añadir producto")
        dialog.setStyleSheet("""
             QDialog { 
                background-color: #f8fafc; 
                border-radius: 10px; 
                font-family: 'Segoe UI', Arial, sans-serif; 
            }

            QLabel { 
                color: #2c3e50; 
                font-size: 14px; 
                font-weight: 500; 
                margin-bottom: 6px; 
            }

            QLabel[hint="true"] { 
                color: #475569; 
                font-size: 12px; 
                font-weight: 400; 
                margin-top: -2px; 
                margin-bottom: 10px; 
            }

            QSpinBox { 
                background-color: #ffffff; 
                border: 2px solid #e2e8f0; 
                border-radius: 6px; 
                padding: 6px 10px; 
                font-size: 14px; 
                min-height: 40px; 
            }

            QSpinBox:focus { 
                border: 2px solid #4a89dc; 
                background-color: #f0f7ff; 
            }

            QSpinBox::up-button, 
            QSpinBox::down-button { 
                width: 24px; 
                border: none; 
                background: transparent; 
                padding: 0px; 
                margin: 0px; 
                border-top-right-radius: 6px; 
                border-bottom-right-radius: 6px; 
            }

            QSpinBox::up-button:hover, 
            QSpinBox::down-button:hover { 
                background: #eef2f7; 
            }

            QSpinBox::up-arrow, 
            QSpinBox::down-arrow { 
                width: 0; 
                height: 0; 
                border-left: 5px solid transparent; 
                border-right: 5px solid transparent; 
            }

            QSpinBox::up-arrow { 
                border-bottom: 7px solid #4a89dc; 
                margin-right: 6px; 
            }

            QSpinBox::down-arrow { 
                border-top: 7px solid #4a89dc; 
                margin-right: 6px; 
            }

            QRadioButton { 
                font-size: 14px; 
                color: #2c3e50; 
                padding: 6px 2px; 
                spacing: 8px; 
            }

            QRadioButton::indicator { 
                width: 18px; 
                height: 18px; 
                border-radius: 9px; 
                border: 2px solid #4a89dc; 
                background: #ffffff; 
                margin-right: 6px; 
            }

            QRadioButton::indicator:hover { 
                background: #f0f7ff; 
            }

            QRadioButton::indicator:checked { 
                background-color: #4a89dc; 
                border: 2px solid #4a89dc; 
            }

            QDialogButtonBox { 
                background: #f5f7fa; 
                border-top: 1px solid #e2e8f0; 
                padding: 12px 16px; 
                border-bottom-left-radius: 10px; 
                border-bottom-right-radius: 10px; 
            }

            QDialogButtonBox QPushButton { 
                background-color: #3498db; 
                color: #ffffff; 
                border: none; 
                border-radius: 8px; 
                padding: 10px 18px; 
                min-width: 110px; 
                font-weight: bold; 
            }

            QDialogButtonBox QPushButton:hover { 
                background-color: #2980b9; 
            }

            QDialogButtonBox QPushButton:disabled { 
                background-color: #bdc3c7; 
                color: #ffffff; 
            }
        """)
        layout = QVBoxLayout(dialog)
        if not getattr(self, "validar_stock", False):
            max_disponible = 9999
            info_texto = "Sin validar stock (entrada libre)"
        else:
            max_disponible = self.verificarStockDisponible(nombre, bandera)
            info_texto = f"Máximo disponible: {max_disponible} unidades"
    
        spin = QSpinBox()
        spin.setRange(1, max_disponible if max_disponible > 0 else 1)
        spin.setValue(1)
        info_label = QLabel(info_texto)
        info_label.setProperty("hint", True)
        layout.addWidget(QLabel(f"Producto: {nombre}"))
        layout.addWidget(info_label)
        layout.addWidget(QLabel("Cantidad:"))
        layout.addWidget(spin)
        tipoLocal = QRadioButton("Local")
        tipoLlevar = QRadioButton("Para llevar")
        tipoLocal.setChecked(True)
        layout.addWidget(tipoLocal)
        layout.addWidget(tipoLlevar)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(btns)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        if dialog.exec_() == QDialog.Accepted:
            tipo = "Local" if tipoLocal.isChecked() else "Para llevar"
            self.agregarProductoTabla(nombre, spin.value(), tipo, bandera)
    

    def verificarStockDisponible(self, nombre, bandera):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        try:
            if bandera:
                self.cursor.execute("SELECT idProd FROM Producto WHERE nomProd=?", (nombre,))
                row = self.cursor.fetchone()
                if not row:
                    return 0
                id_producto = row[0]
                self.cursor.execute("""
                    SELECT pi.idIng, pi.cantidadIngNecesitada, s.cantidadStock, s.unidadMedida
                    FROM ProductosIngredientes pi
                    JOIN Stock s ON pi.idIng = s.idIng
                    WHERE pi.idProd = ?
                """, (id_producto,))
                ingredientes = self.cursor.fetchall()
            else:
                self.cursor.execute("SELECT idProm FROM Promocion WHERE nomProm=?", (nombre,))
                row = self.cursor.fetchone()
                if not row:
                    return 0
                id_promocion = row[0]
                self.cursor.execute("""
                    SELECT pp.idProd, pp.cantidadProdProm
                    FROM PromocionProd pp
                    WHERE pp.idProm = ?
                """, (id_promocion,))
                productos_promocion = self.cursor.fetchall()

                dicc = {}
                for id_prod, cant_prod in productos_promocion:
                    self.cursor.execute("""
                        SELECT pi.idIng, (pi.cantidadIngNecesitada * ?) AS cantidad_necesaria, 
                               s.cantidadStock, s.unidadMedida
                        FROM ProductosIngredientes pi
                        JOIN Stock s ON pi.idIng = s.idIng
                        WHERE pi.idProd = ?
                    """, (cant_prod, id_prod))
                    for id_ing, cant_nec, stock, unidad in self.cursor.fetchall():
                        if id_ing not in dicc:
                            dicc[id_ing] = {'cantidad_necesaria': float(cant_nec or 0), 'stock': float(stock or 0), 'unidad': unidad}
                        else:
                            dicc[id_ing]['cantidad_necesaria'] += float(cant_nec or 0)
                ingredientes = [(k, v['cantidad_necesaria'], v['stock'], v['unidad']) for k, v in dicc.items()]
            if not ingredientes:
                return 0
            max_unidades = float('inf')
            for id_ing, cantidad_necesaria, stock_disponible, _ in ingredientes:
                if cantidad_necesaria is None or cantidad_necesaria <= 0:
                    continue
                stock_disponible = float(stock_disponible or 0)
                cantidad_reservada = self.calcularIngredientesReservados(id_ing)
                stock_real = stock_disponible - float(cantidad_reservada or 0)
                if stock_real <= 0:
                    return 0
                unidades_posibles = stock_real / cantidad_necesaria
                if unidades_posibles < max_unidades:
                    max_unidades = unidades_posibles
            if max_unidades == float('inf'):
                return 0
            return max(0, int(max_unidades))
        except Exception as e:
            print(f"Error al verificar stock: {e}")
            return 0
        finally:
            self.conn.close()
    

    def calcularIngredientesReservados(self, id_ingrediente):
        cantidad_reservada = 0
        try:
            for fila in range(self.tabla.rowCount()):
                nombre_producto = self.tabla.item(fila, 2).text()
                cantidad = int(self.tabla.item(fila, 0).text())
                self.conn = sqlite3.connect(DB_PATH)
                self.cursor = self.conn.cursor()
                self.cursor.execute("SELECT idProm FROM Promocion WHERE nomProm=?", (nombre_producto,))
                es_promocion = self.cursor.fetchone() is not None
                if es_promocion:
                    self.cursor.execute("SELECT idProm FROM Promocion WHERE nomProm=?", (nombre_producto,))
                    id_promocion = self.cursor.fetchone()[0]
                    self.cursor.execute("""
                        SELECT pp.idProd, pp.cantidadProdProm 
                        FROM PromocionProd pp 
                        WHERE pp.idProm = ?
                    """, (id_promocion,))
                    productos_promocion = self.cursor.fetchall()
                    for id_prod, cant_prod in productos_promocion:
                        self.cursor.execute("""
                            SELECT cantidadIngNecesitada 
                            FROM ProductosIngredientes 
                            WHERE idProd = ? AND idIng = ?
                        """, (id_prod, id_ingrediente))
                        resultado = self.cursor.fetchone()
                        if resultado:
                            cantidad_reservada += float(resultado[0] or 0) * cant_prod * cantidad
                else:
                    self.cursor.execute("SELECT idProd FROM Producto WHERE nomProd=?", (nombre_producto,))
                    id_producto = self.cursor.fetchone()[0]
                    self.cursor.execute("""
                        SELECT cantidadIngNecesitada 
                        FROM ProductosIngredientes 
                        WHERE idProd = ? AND idIng = ?
                    """, (id_producto, id_ingrediente))
                    resultado = self.cursor.fetchone()
                    if resultado:
                        cantidad_reservada += float(resultado[0] or 0) * cantidad
                self.conn.close()
        except Exception as e:
            print(f"Error al calcular ingredientes reservados: {e}")
            if self.conn:
                self.conn.close()
        return cantidad_reservada
    

    def actualizarStock(self, operacion='restar', conn=None):
        if not self.enviada:
            return
        local_conn = None
        try:
            if conn is None:
                local_conn = sqlite3.connect(DB_PATH)
                cur = local_conn.cursor()
            else:
                cur = conn.cursor()
            signo = -1 if operacion == 'restar' else 1
            for fila in range(self.tabla.rowCount()):
                nombre_producto = self.tabla.item(fila, 2).text()
                cantidad_linea = int(self.tabla.item(fila, 0).text())
                cur.execute("SELECT idProm FROM Promocion WHERE nomProm=?", (nombre_producto,))
                prom = cur.fetchone()
                if prom:
                    id_prom = prom[0]
                    cur.execute("""
                        SELECT pp.idProd, pp.cantidadProdProm 
                        FROM PromocionProd pp 
                        WHERE pp.idProm = ?
                    """, (id_prom,))
                    for id_prod, cant_prod in cur.fetchall():
                        cur.execute("""
                            SELECT idIng, cantidadIngNecesitada 
                            FROM ProductosIngredientes 
                            WHERE idProd = ?
                        """, (id_prod,))
                        for id_ing, cant_ing in cur.fetchall():
                            cant_ing_valor = float(cant_ing or 0)
                            if cant_ing_valor > 0:
                                delta = q2(cant_ing_valor * cant_prod * cantidad_linea * signo)
                                cur.execute("""
                                    UPDATE Stock
                                       SET cantidadStock = MAX(0, ROUND(cantidadStock + ?, 2))
                                     WHERE idIng = ?
                                """, (delta, id_ing))
                else:
                    cur.execute("SELECT idProd FROM Producto WHERE nomProd=?", (nombre_producto,))
                    id_prod = cur.fetchone()[0]
                    cur.execute("""
                        SELECT idIng, cantidadIngNecesitada 
                        FROM ProductosIngredientes 
                        WHERE idProd = ?
                    """, (id_prod,))
                    for id_ing, cant_ing in cur.fetchall():
                        cant_ing_valor = float(cant_ing or 0)
                        if cant_ing_valor > 0:
                            delta = q2(cant_ing_valor * cantidad_linea * signo)
                            cur.execute("""
                                UPDATE Stock
                                   SET cantidadStock = MAX(0, ROUND(cantidadStock + ?, 2))
                                 WHERE idIng = ?
                            """, (delta, id_ing))
    
            if local_conn is not None:
                local_conn.commit()
        except Exception as e:
            print(f"Error al actualizar stock: {e}")
            if local_conn is not None:
                local_conn.rollback()
            raise
        finally:
            if local_conn is not None:
                local_conn.close()
    

    def agregarProductoTabla(self, nombre, cantidad, tipo, bandera):
        if self.verificarBloqueo("agregar productos"):
            return
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        if bandera:
            self.cursor.execute("""SELECT precioVenta FROM Producto WHERE nomProd=?""",(nombre,))
            resultados = self.cursor.fetchone()
        else:
            self.cursor.execute("""SELECT precioProm FROM Promocion WHERE nomProm=?""",(nombre,))
            resultados = self.cursor.fetchone()
        precio_unitario = float(resultados[0])
        for row in range(self.tabla.rowCount()):
            if self.tabla.item(row, 1).text() == tipo and self.tabla.item(row, 2).text() == nombre:
                cant_actual = int(self.tabla.item(row, 0).text()) + cantidad
                self.tabla.item(row, 0).setText(str(cant_actual))
                self.tabla.item(row, 4).setText(f"{cant_actual * precio_unitario:.2f}")
                self.recalcularTotal()
                self.conn.close()
                return
        row = self.tabla.rowCount()
        self.tabla.insertRow(row)
        item_cantidad = QTableWidgetItem(str(cantidad))
        item_cantidad.setTextAlignment(Qt.AlignCenter)
        self.tabla.setItem(row, 0, item_cantidad)
        item_tipo = QTableWidgetItem(tipo)
        item_tipo.setTextAlignment(Qt.AlignCenter)
        self.tabla.setItem(row, 1, item_tipo)
        item_nombre = QTableWidgetItem(nombre)
        item_nombre.setTextAlignment(Qt.AlignCenter)
        self.tabla.setItem(row, 2, item_nombre)
        item_precio = QTableWidgetItem(f"{precio_unitario:.2f}")
        item_precio.setTextAlignment(Qt.AlignCenter)
        self.tabla.setItem(row, 3, item_precio)
        total = cantidad * precio_unitario
        item_total = QTableWidgetItem(f"{total:.2f}")
        item_total.setTextAlignment(Qt.AlignCenter)
        self.tabla.setItem(row, 4, item_total)
        btn = QPushButton("🗑️")
        btn.setFixedSize(30, 30) 
        btn.setStyleSheet("border: none; padding: 0px; margin-left: -20px; background-color: transparent; font-size: 16px; margin-top:-10px;")
        btn.clicked.connect(lambda _, r=row: self.eliminarFila(r))
        self.tabla.setCellWidget(row, 5, btn)
        self.recalcularTotal()
        self.conn.close()
    

    def recalcularTotal(self):
        totalVenta = 0.0
        for i in range(self.tabla.rowCount()):
            totalVenta += float(self.tabla.item(i,4).text())
        self.totalVenta.setText(f"{totalVenta:.2f} Bs")
    

    def eliminarFila(self, row):
        if self.verificarBloqueo("eliminar productos"):
            return
        self.tabla.removeRow(row)
        for i in range(self.tabla.rowCount()):
            btn = self.tabla.cellWidget(i, 5)
            if btn is None:
                continue
            try:
                btn.clicked.disconnect()
            except Exception:
                pass
            btn.clicked.connect(lambda _, r=i: self.eliminarFila(r))
        self.recalcularTotal()
    

    def mostrarEmpleados(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.scrollCat.setVisible(False)
        self.scrollSub.setVisible(False)
        self.btnPrevSub.setVisible(False)
        self.btnNextSub.setVisible(False)
        self.btnPrevCat1.setVisible(False)
        self.btnNextCat1.setVisible(False)
        self._clear_grid(self.layoutProductos)
        self._clear_layout(self.layoutSubcategorias)
        self.cursor.execute("SELECT aliasEmp, imgEmp FROM Empleado WHERE disponibleEmp=1")
        empleados = self.cursor.fetchall()
        row, col = 0, 0
        max_cols = 6
        for alias, img in empleados:
            caja = self.crearItem(alias, img, True)
            caja.setFixedSize(150, 160)
            caja.clicked.disconnect()
            caja.clicked.connect(lambda _, n=alias: self.seleccionarEmpleado(n))
            self.layoutProductos.addWidget(caja, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        if self.layoutProductos.count() == 0:
            self.layoutProductos.addWidget(QLabel("No hay empleados disponibles"), 0, 0, 1, max_cols)
        self.layoutProductos.setRowStretch(row + 1, 1)
        self.conn.close()
    

    def seleccionarEmpleado(self, alias):
        if self.verificarBloqueo("cambiar empleado"):
            return
        self.campoEncargado.setText(alias)


    def mostrarMesas(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.scrollCat.setVisible(True)
        self.btnPrevCat1.setVisible(True)
        self.btnNextCat1.setVisible(True)
        self.scrollSub.setVisible(False)
        self.btnPrevSub.setVisible(False)
        self.btnNextSub.setVisible(False)
        self._clear_layout(self.layoutCategorias)
        self.cursor.execute("SELECT idSeccion, nombSeccion FROM Seccion")
        secciones = self.cursor.fetchall()
        colores = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6", "#1abc9c", "#34495e", "#d35400"]
        for idx, (idSec, nombre) in enumerate(secciones):
            color = colores[idx % len(colores)]
            btn = QPushButton(nombre.upper())
            btn.setMinimumSize(180, 80) 
            btn.setMaximumSize(180, 80)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 15px;
                    font-weight: 900;
                    font-size: 15px;
                    text-align: center;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: {self._darken_color(color, 0.2)};
                    transform: scale(1.02);
                }}
                QPushButton:pressed {{
                    background-color: {self._darken_color(color, 0.3)};
                    padding-top: 12px;
                    padding-bottom: 8px;
                }}
            """)
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setXOffset(0)
            shadow.setYOffset(4)
            shadow.setColor(QColor(0, 0, 0, 80))
            btn.setGraphicsEffect(shadow)
            btn.clicked.connect(lambda checked, idSecc=idSec: self.cargarSecciones(idSecc))
            self.layoutCategorias.addWidget(btn)
        self.layoutCategorias.addStretch()
        self._clear_grid(self.layoutProductos)
        self._clear_layout(self.layoutSubcategorias)
        self.conn.close()


    def _darken_color(self, hex_color, factor):
        from PyQt5.QtGui import QColor
        color = QColor(hex_color)
        return color.darker(int(100 + factor * 100)).name()


    def cargarSecciones(self, idSeccion):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._clear_grid(self.layoutProductos)
        self.cursor.execute("SELECT idMesa, disponible FROM Mesa WHERE idSeccion=? AND existe=TRUE", (idSeccion,))
        mesas = self.cursor.fetchall()
        row, col = 0, 0
        max_cols = 6
        for idMesa, disponible in mesas:
            if disponible:
                img_path = get_resource_path(os.path.join('Imagenes', 'mesasDesocupadas.png'))
            else:
                img_path = get_resource_path(os.path.join('Imagenes', 'mesasOcupadas.png'))
            if not os.path.exists(img_path):
                pix = QPixmap(100, 100)
                pix.fill(QColor("#3498db" if disponible else "#e74c3c"))
            else:
                pix = QPixmap(img_path)
            btn = QPushButton()
            btn.setFixedSize(150, 200)
            btn.setStyleSheet("""
                QPushButton { 
                        background: #ffffff; 
                        border: 1px solid #e2e8f0; 
                        border-radius: 10px; 
                        text-align: center; }
                QPushButton:hover { 
                        border: 1px solid #cbd5e1; 
                        background: #f8fafc; 
                    }
            """)
            vbox = QVBoxLayout(btn)
            labImg = QLabel()
            labImg.setPixmap(pix.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            labImg.setAlignment(Qt.AlignCenter)
            vbox.addWidget(labImg)
            label = QLabel(str(idMesa))
            label.setAlignment(Qt.AlignCenter)
            vbox.addWidget(label)
            if not disponible:
                self.cursor.execute("""SELECT E.aliasEmp 
                                    FROM DetallesVenta DV 
                                    INNER JOIN Empleado E ON DV.idMeseroActual=E.codEmp  
                                    INNER JOIN Venta V ON DV.fechaRegVenta=V.fechaReg
                                    WHERE idMesa=? AND idSeccion=? 
                                    ORDER BY DV.fechaRegDetalleVenta 
                                    DESC LIMIT 1""",(idMesa,idSeccion))
                meseroAsignado=self.cursor.fetchone()[0]
                label2=QLabel(meseroAsignado)
                label2.setStyleSheet("QLabel {color: #2c3e50; font-size: 14px; font-weight: 500; }")
                botonPedidosTiempo=QPushButton("Ver Mas")
                botonPedidosTiempo.setFixedSize(20, 30)
                botonPedidosTiempo.setStyleSheet("""QPushButton{
                    color:white;
                    background:green;
                    font-size:12px;
                    padding:0px;
                   margin:0px;
                   border-radius:15px;
                    }""")
                botonPedidosTiempo.setCursor(Qt.PointingHandCursor)
                botonPedidosTiempo.clicked.connect(lambda  checked, idSecc=idSeccion, m=idMesa:self.mostrarDetallesVentaMesa(m,idSecc))
                vbox.addWidget(label2,alignment=Qt.AlignCenter)
                vbox.addWidget(botonPedidosTiempo,alignment=Qt.AlignCenter)
            btn.clicked.connect(lambda checked, idSecc=idSeccion, m=idMesa: self.seleccionarMesa(m, idSecc))
            self.layoutProductos.addWidget(btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        if self.layoutProductos.count() == 0:
            self.layoutProductos.addWidget(QLabel("No hay mesas disponibles"), 0, 0, 1, max_cols)
        self.layoutProductos.setRowStretch(row + 1, 1)
        self.conn.close()
        
        
    def mostrarDetallesVentaMesa(self, numMesa, idSeccion):
        pantallaVentasMesa = QDialog(self)
        pantallaVentasMesa.setFixedSize(1100, 700)
        pantallaVentasMesa.setWindowTitle(f"Detalles de Pedidos - Mesa {numMesa}")
        pantallaVentasMesa.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layoutPantallaMesa = QVBoxLayout()
        layoutPantallaMesa.setContentsMargins(20, 20, 20, 20)
        layoutPantallaMesa.setSpacing(15)
        pantallaVentasMesa.setLayout(layoutPantallaMesa)
        titulo = QLabel(f"📋 Pedidos Pendientes - Mesa {numMesa}")
        titulo.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 22px;
                font-weight: bold;
                padding: 10px;
                background-color: #ffffff;
                border-radius: 8px;
                border: 2px solid #e2e8f0;
                text-align: center;
            }
        """)
        layoutPantallaMesa.addWidget(titulo)
        tablaPedidosPendientes = QTableWidget()
        tablaPedidosPendientes.setColumnCount(4)
        tablaPedidosPendientes.setHorizontalHeaderLabels(["📅 Fecha", "🕒 Hora de Registro", "⏱️ Tiempo Transcurrido", "📦 Detalles"])
        tablaPedidosPendientes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tablaPedidosPendientes.setSelectionMode(QTableWidget.NoSelection)
        tablaPedidosPendientes.setFocusPolicy(Qt.NoFocus)
        tablaPedidosPendientes.setEditTriggers(QTableWidget.NoEditTriggers)
        tablaPedidosPendientes.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                gridline-color: #e2e8f0;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:hover {
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 14px 8px;
                border: none;
                font-weight: bold;
                font-size: 15px;
                border-radius: 0px;
                margin: 0px;
            }
            QHeaderView::section:first {
                border-top-left-radius: 8px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 8px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f8fafc;
                width: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                min-height: 30px;
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        layoutPantallaMesa.addWidget(tablaPedidosPendientes)
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""SELECT fechaReg, numVenta
                               FROM Venta V
                               WHERE idMesa=? AND idSeccion=?
                               ORDER BY fechaReg DESC 
                               LIMIT 1""", (numMesa, idSeccion))
        resultados = self.cursor.fetchone()
        if not resultados:
            QMessageBox.information(self, "Información", "No hay pedidos pendientes para esta mesa.")
            self.conn.close()
            return
        fechaRegVenta, numVenta = resultados
        self.cursor.execute("""SELECT DISTINCT fechaRegDetalleVenta
                               FROM DetallesVenta
                               WHERE fechaRegVenta=? AND estadoDetalleVenta='Preparacion' """, (fechaRegVenta,))
        fechaDetallesVenta = self.cursor.fetchall()
        fechas_por_fila = {}
        for fecha in fechaDetallesVenta:
            self.cursor.execute("""SELECT nomProd, cantidadProdDet, tipoConsumo
                                   FROM DetallesVenta Dt
                                   INNER JOIN Producto P ON P.idProd=Dt.idProd
                                   WHERE Dt.fechaRegDetalleVenta=?""", (fecha[0],))
            productos = self.cursor.fetchall()
            self.cursor.execute("""SELECT nomProm, cantidadProdDet, tipoConsumo
                                   FROM DetallesVenta Dt
                                   INNER JOIN Promocion P ON P.idProm=Dt.idProm
                                   WHERE Dt.fechaRegDetalleVenta=?""", (fecha[0],))
            promociones = self.cursor.fetchall()
            detalles = ""
            for i in range(len(productos)):
                producto = productos[i]
                if producto[2] == "Local":
                    icono = "🏠"
                    etiqueta = "[Local]"
                else:
                    icono = "🥡"
                    etiqueta = "[Para llevar]"
                
                detalles += f"{icono} {producto[1]} {producto[0]} {etiqueta}"
                if i < len(productos) - 1:
                    detalles += "\n"
            if productos and promociones:
                detalles += "\n"
            for i in range(len(promociones)):
                promocion = promociones[i]
                if promocion[2] == "Local":
                    icono = "🏠🎁"
                    etiqueta = "[Local]"
                else:
                    icono = "🥡🎁"
                    etiqueta = "[Para llevar]"
                
                detalles += f"{icono} {promocion[1]} {promocion[0]} {etiqueta}"
                if i < len(promociones) - 1:
                    detalles += "\n"
            fila = tablaPedidosPendientes.rowCount()
            tablaPedidosPendientes.setRowCount(fila + 1)
            fechaCompleta = datetime.strptime(fecha[0], "%Y-%m-%d %H:%M:%S.%f")
            fechas_por_fila[fila] = fechaCompleta
            fechaMostrada = fechaCompleta.strftime("%d/%m/%Y")
            itemFecha = QTableWidgetItem(fechaMostrada)
            itemFecha.setTextAlignment(Qt.AlignCenter)
            itemFecha.setFont(QFont("Segoe UI", 11))
            itemFecha.setFlags(itemFecha.flags() & ~Qt.ItemIsSelectable)
            tablaPedidosPendientes.setItem(fila, 0, itemFecha)
            hora = fechaCompleta.strftime("%I:%M %p")
            itemHora = QTableWidgetItem(hora)
            itemHora.setTextAlignment(Qt.AlignCenter)
            itemHora.setFont(QFont("Segoe UI", 11))
            itemHora.setFlags(itemHora.flags() & ~Qt.ItemIsSelectable)
            tablaPedidosPendientes.setItem(fila, 1, itemHora)
            fechaActual = datetime.now()
            diferencia = (fechaActual - fechaCompleta).total_seconds()
            minutos = int(diferencia // 60)
            icono_tiempo = "🟢" if minutos < 10 else "🟡" if minutos < 20 else "🔴"
            itemDiferencia = QTableWidgetItem(f"{icono_tiempo} Hace {minutos} minutos")
            itemDiferencia.setTextAlignment(Qt.AlignCenter)
            itemDiferencia.setFont(QFont("Segoe UI", 11, QFont.Bold))
            itemDiferencia.setFlags(itemDiferencia.flags() & ~Qt.ItemIsSelectable)
            if minutos < 10:
                itemDiferencia.setForeground(QColor("#27ae60"))
                itemDiferencia.setBackground(QColor("#eafaf1"))
            elif minutos < 20:
                itemDiferencia.setForeground(QColor("#f39c12"))
                itemDiferencia.setBackground(QColor("#fef9e7"))
            else:
                itemDiferencia.setForeground(QColor("#e74c3c"))
                itemDiferencia.setBackground(QColor("#fdedec"))
            tablaPedidosPendientes.setItem(fila, 2, itemDiferencia)
            itemDetalles = QTableWidgetItem(detalles)
            itemDetalles.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            itemDetalles.setFlags(itemDetalles.flags() | Qt.TextWordWrap)
            itemDetalles.setFlags(itemDetalles.flags() & ~Qt.ItemIsSelectable)
            itemDetalles.setFont(QFont("Segoe UI", 11))
            if productos or promociones:
                tiene_para_llevar = any(item[2] == "Para llevar" for item in productos + promociones)
                tiene_local = any(item[2] == "Local" for item in productos + promociones)
                if tiene_para_llevar and tiene_local:
                    itemDetalles.setBackground(QColor("#fef9e7"))
                elif tiene_para_llevar:
                    itemDetalles.setBackground(QColor("#fdedec"))
                else:
                    itemDetalles.setBackground(QColor("#e6f2ff"))
            tablaPedidosPendientes.setItem(fila, 3, itemDetalles)
            tablaPedidosPendientes.resizeRowToContents(fila)
        self.conn.close()
        if tablaPedidosPendientes.rowCount() == 0:
            tablaPedidosPendientes.setRowCount(1)
            item = QTableWidgetItem("No hay pedidos pendientes para esta mesa")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(QFont("Segoe UI", 12, QFont.Bold))
            item.setForeground(QColor("#7f8c8d"))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            tablaPedidosPendientes.setSpan(0, 0, 1, 4)
            tablaPedidosPendientes.setItem(0, 0, item)
        else:
            leyenda_widget = QWidget()
            leyenda_layout = QHBoxLayout()
            leyenda_widget.setLayout(leyenda_layout)
            
            leyenda_local = QLabel("🏠 Local")
            leyenda_local.setStyleSheet("""
                QLabel {
                    background-color: #e6f2ff;
                    color: #2c3e50;
                    padding: 6px 12px;
                    border-radius: 6px;
                    border: 1px solid #3498db;
                    font-weight: bold;
                    margin-right: 10px;
                }
            """)
            
            leyenda_llevar = QLabel("🥡 Para llevar")
            leyenda_llevar.setStyleSheet("""
                QLabel {
                    background-color: #fdedec;
                    color: #2c3e50;
                    padding: 6px 12px;
                    border-radius: 6px;
                    border: 1px solid #e74c3c;
                    font-weight: bold;
                    margin-right: 10px;
                }
            """)
            
            leyenda_mixto = QLabel("🏠🥡 Mixto")
            leyenda_mixto.setStyleSheet("""
                QLabel {
                    background-color: #fef9e7;
                    color: #2c3e50;
                    padding: 6px 12px;
                    border-radius: 6px;
                    border: 1px solid #f39c12;
                    font-weight: bold;
                }
            """)
            
            leyenda_layout.addWidget(leyenda_local)
            leyenda_layout.addWidget(leyenda_llevar)
            leyenda_layout.addWidget(leyenda_mixto)
            leyenda_layout.addStretch()
            layoutPantallaMesa.insertWidget(1, leyenda_widget)
            timer_unico = QTimer(pantallaVentasMesa)

            def actualizar_todas_las_filas():
                fecha_actual = datetime.now()
                for fila, fecha_completa in fechas_por_fila.items():
                    diferencia = (fecha_actual - fecha_completa).total_seconds()
                    minutos = int(diferencia // 60)
                    icono_tiempo = "🟢" if minutos < 10 else "🟡" if minutos < 20 else "🔴"
                    item = QTableWidgetItem(f"{icono_tiempo} Hace {minutos} minutos")
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFont(QFont("Segoe UI", 11, QFont.Bold))
                    item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
                    if minutos < 10:
                        item.setForeground(QColor("#27ae60"))
                        item.setBackground(QColor("#eafaf1"))
                    elif minutos < 20:
                        item.setForeground(QColor("#f39c12"))
                        item.setBackground(QColor("#fef9e7"))
                    else:
                        item.setForeground(QColor("#e74c3c"))
                        item.setBackground(QColor("#fdedec"))
                    tablaPedidosPendientes.setItem(fila, 2, item)
            timer_unico.timeout.connect(actualizar_todas_las_filas)
            timer_unico.start(60000)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
                padding-top: 13px;
                padding-bottom: 11px;
            }
        """)
        btn_cerrar.setCursor(Qt.PointingHandCursor)
        btn_cerrar.clicked.connect(pantallaVentasMesa.accept)
        layoutPantallaMesa.addWidget(btn_cerrar, alignment=Qt.AlignCenter)
        pantallaVentasMesa.exec_()
    

    def actualizar_hora(self,fechaCompleta,fila,tablaPedidosPendientes):
        fechaActual=datetime.now()
        diferencia=(fechaActual-fechaCompleta).total_seconds()
        minutos=int(diferencia//60)
        itemDiferencia=QTableWidgetItem(f"Hace {minutos} minutos")
        itemDiferencia.setTextAlignment(Qt.AlignCenter)   
        if minutos<10:
            itemDiferencia.setForeground(QColor("green"))
        else:
            if minutos>=10 and minutos<20:
                itemDiferencia.setForeground(QColor("yellow"))
            else:
                itemDiferencia.setForeground(QColor("red"))
        tablaPedidosPendientes.setItem(fila,2,itemDiferencia)
        

    def seleccionarMesa(self, idMesa, idSeccion):
        if self.verificarBloqueo("cambiar mesa"):
            return
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.campoMesa.setText(str(idMesa))
        self.cursor.execute("""SELECT nombSeccion FROM Seccion WHERE idSeccion=?""", (idSeccion,))
        resultados = self.cursor.fetchone()
        self.campoSeccion.setText(str(resultados[0]))    
        self.conn.close()
    
    
    def actualizarHora(self):
        self.campoTiempo.setText(datetime.now().strftime("%I:%M %p"))                
        
        

if __name__=="__main__":
    aplicacion = QApplication(sys.argv)
    pagina = RegistrarPedidos("DIRECTORIO")
    pagina.show()
    sys.exit(aplicacion.exec_())