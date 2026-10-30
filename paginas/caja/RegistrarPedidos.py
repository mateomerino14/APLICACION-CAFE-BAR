import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from datetime import datetime
from servicios.Impresion import ManejadorImpresion
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from decimal import Decimal, ROUND_HALF_UP
from paginas.caja.DialogoCobroVenta import DialogoCobroVenta
from nucleo.SeguridadUtils import verificar_password
from nucleo.Rutas import get_db_path, get_resource_path


def q2(x) -> float:
    return float(Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


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
        self.dialogo_detalles = None
        self.fecha_actual_dialogo = None
        self.temporizador_dialogo = None
        self.idSeccionActual = None
        self.dialogo_cards = None
        self.numMesa_actual = None
        self.idSeccion_actual = None
        self.timer_unico = None
        self.tabla_pedidos_pendientes = None
        self.fechas_por_fila = {}
        self.productos_faltantes_global = []
        self.actualizar_al_cerrar = False
        self.exclusiones_por_fila = {}
        self.extras_por_fila = {}
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
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
                background-color: white;
            }
            QProgressBar::chunk {
                border-radius: 6px;
            }
            QSpinBox {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                min-height: 40px;
            }
            QSpinBox:focus {
                border: 2px solid #4a89dc;
                background-color: #f0f7ff;
            }
            QSpinBox::up-button {
                background-color: #3498db;
                border: none;
                border-radius: 4px;
                width: 30px;
                height: 20px;
            }
            QSpinBox::up-button:hover {
                background-color: #2980b9;
            }
            QSpinBox::down-button {
                background-color: #e74c3c;
                border: none;
                border-radius: 4px;
                width: 30px;
                height: 20px;
            }
            QSpinBox::down-button:hover {
                background-color: #c0392b;
            }
            QSpinBox::up-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 5px solid white;
                width: 0;
                height: 0;
            }
            QSpinBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                width: 0;
                height: 0;
            }
        """)
        self.set_up()

    def set_up(self):
        self.layoutDatos = QHBoxLayout()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
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
        self.etiquetaSeccion = QLabel("Sección")
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
        self.tabla.cellClicked.connect(self.mostrarDetalleFilaPedido)
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
        botonEnviarCocina = QPushButton("Enviar Cocina")
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

    def _obtenerIngredientesProducto(self, nombre_producto):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("SELECT idProd FROM Producto WHERE nomProd=?", (nombre_producto,))
            row = c.fetchone()
            if not row:
                return []
            id_prod = row[0]
            c.execute(
                """
                SELECT s.idIng, s.nomIng, pi.cantidadIngNecesitada
                FROM ProductosIngredientes pi
                JOIN Stock s ON pi.idIng = s.idIng
                WHERE pi.idProd = ?
                ORDER BY s.nomIng
            """,
                (id_prod,),
            )
            return [{"idIng": r[0], "nomIng": r[1], "cantidad": r[2]} for r in c.fetchall()]
        finally:
            conn.close()

    def _obtenerIngredientesProductoParaExtra(self, nombre_producto):
        """
        A diferencia de _obtenerIngredientesProducto (que solo trae la receta
        base), esta consulta trae ademas el precioExtra de cada ingrediente,
        y solo devuelve ingredientes que YA pertenecen al producto — para que
        al agregar "ingrediente extra" el usuario solo vea opciones que tienen
        sentido para ese producto (ej: extra queso/carne en una hamburguesa),
        no ingredientes de otros productos que no aplican.
        """
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("SELECT idProd FROM Producto WHERE nomProd=?", (nombre_producto,))
            row = c.fetchone()
            if not row:
                return []
            id_prod = row[0]
            c.execute(
                """
                SELECT s.idIng, s.nomIng, COALESCE(s.precioExtra, 0)
                FROM ProductosIngredientes pi
                JOIN Stock s ON pi.idIng = s.idIng
                WHERE pi.idProd = ?
                ORDER BY s.nomIng
            """,
                (id_prod,),
            )
            return c.fetchall()
        finally:
            conn.close()

    def _textoExtras(self, extras):
        if not extras:
            return ""
        partes = [f"+{e['cantidadExtra']} {e['nomIng']}" for e in extras]
        return "extra: " + ", ".join(partes)

    def _obtenerExtrasTextoPorDetalle(self, cursor, id_detalle):
        """
        Igual que consultar DetallesVentaExclusiones para armar el texto de
        'sin: ...', pero para DetallesVentaExtras -> 'extra: ...'. Centralizado
        aca para que todos los lugares que muestran/imprimen un detalle de
        venta (ticket, cocina, pedidos pendientes, marcar listo) reflejen los
        ingredientes extra igual que ya reflejan las exclusiones.
        """
        cursor.execute(
            """
            SELECT nomIng, cantidadExtra FROM DetallesVentaExtras WHERE idDetalleVenta=?
        """,
            (id_detalle,),
        )
        filas = cursor.fetchall()
        if not filas:
            return ""
        return "extra: " + ", ".join(f"+{cant} {nom}" for nom, cant in filas)

    def _textoExclusiones(self, exclusiones):
        if not exclusiones:
            return ""
        nombres = ", ".join(e["nomIng"] for e in exclusiones)
        return f"sin: {nombres}"

    def verificarBloqueo(self, accion):
        if self.enviada:
            QMessageBox.warning(
                self,
                "Venta Bloqueada",
                f"No es posible {accion}. La venta ya fue procesada.\nDebe completar el pago para iniciar una nueva venta.",
            )
            return True
        return False

    def verificarImpresoraConfigurada(self, tipo):
        impresora = self.manejador_impresion.obtener_impresora(tipo)
        if not impresora:
            if tipo == "Barra":
                mensaje = "No hay una impresora configurada para Barra/Ticket.\nPor favor, configure una impresora en la seccion de configuracion."
            else:
                mensaje = "No hay una impresora configurada para Cocina.\nPor favor, configure una impresora en la seccion de configuracion."
            return False, mensaje
        return True, "Impresora configurada correctamente"

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

        label = QLabel(f"Se ha excedido el límite de 2 impresiones.\nIngrese la contraseña de {usuario}:")
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

    def imprimirTicket(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        configurada, mensaje = self.verificarImpresoraConfigurada("Barra")
        if not configurada:
            QMessageBox.warning(self, "Impresora no configurada", mensaje)
            self.conn.close()
            return

        if self.ticket_print_count >= 2:
            if not self.verificar_contraseña_usuario(self.campoCajero.text()):
                self.conn.close()
                return

        if self.campoEncargado.text() == "" or self.campoMesa.text() == "" or self.campoSeccion.text() == "":
            QMessageBox.information(self, "Advertencia", "Rellene los campos necesarios por favor")
            self.conn.close()
            return

        mesa_ocupada = False
        if self.campoMesa.text() and self.campoSeccion.text():
            try:
                cursor = self.conn.cursor()
                cursor.execute("""SELECT idSeccion FROM Seccion WHERE nombSeccion=?""", (self.campoSeccion.text(),))
                res = cursor.fetchone()
                if res:
                    idSeccion = res[0]
                    cursor.execute(
                        """SELECT disponible FROM Mesa WHERE idMesa=? AND idSeccion=?""",
                        (int(self.campoMesa.text()), idSeccion),
                    )
                    disponible = cursor.fetchone()
                    if disponible and not disponible[0]:
                        mesa_ocupada = True
            except Exception as e:
                print(f"Error al verificar mesa ocupada: {e}")

        if self.tabla.rowCount() == 0 and not mesa_ocupada:
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
                'total': self.totalVenta.text().replace(" Bs", "").strip(),
            }

            if not self.enviada:
                self.conn.close()
                self.subirInformacion()
                self.enviada = True
                self.conn = sqlite3.connect(DB_PATH)
                self.cursor = self.conn.cursor()

            todos_items = self.obtener_todos_items_venta_ticket()

            self._imprimir_en_consola("TICKET DE VENTA", datos_venta, todos_items)
            exito, mensaje = self.manejador_impresion.imprimir_ticket(datos_venta, todos_items)
            if exito:
                self.signals.resultado_ticket.emit(True, mensaje, datos_venta, todos_items)
            else:
                self.signals.resultado_ticket.emit(False, mensaje, {}, [])
        except Exception as e:
            self.signals.resultado_ticket.emit(False, f"Error al imprimir: {str(e)}", {}, [])
        finally:
            self.conn.close()

    def obtener_todos_items_venta_ticket(self):
        items = []
        try:
            if self.campoMesa.text() and self.campoSeccion.text():
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""SELECT idSeccion FROM Seccion WHERE nombSeccion=?""", (self.campoSeccion.text(),))
                resultado = cursor.fetchone()
                if resultado:
                    idSeccion = resultado[0]
                    cursor.execute(
                        """SELECT numVenta, fechaReg FROM Venta
                                WHERE idMesa=? AND idSeccion=?
                                ORDER BY fechaReg DESC LIMIT 1""",
                        (int(self.campoMesa.text()), idSeccion),
                    )
                    venta = cursor.fetchone()
                    if venta:
                        numVenta, fechaReg = venta
                        cursor.execute(
                            """
                            SELECT
                                DV.idDetalleVenta,
                                COALESCE(P.nomProd, PR.nomProm) as nombre,
                                DV.cantidadProdDet,
                                DV.tipoConsumo,
                                COALESCE(P.precioVenta, PR.precioProm) as precio,
                                DV.subtotal
                            FROM DetallesVenta DV
                            LEFT JOIN Producto P ON DV.idProd = P.idProd
                            LEFT JOIN Promocion PR ON DV.idProm = PR.idProm
                            WHERE DV.numVenta=? AND DV.fechaRegVenta=?
                            ORDER BY DV.fechaRegDetalleVenta
                        """,
                            (numVenta, fechaReg),
                        )
                        items_raw = cursor.fetchall()
                        dicc_items = {}
                        for id_det, nombre, cantidad, tipo, precio, subtotal in items_raw:
                            cursor.execute(
                                """
                                SELECT nomIng FROM DetallesVentaExclusiones
                                WHERE idDetalleVenta=?
                            """,
                                (id_det,),
                            )
                            excl_rows = cursor.fetchall()
                            excl_texto = ("sin: " + ", ".join(r[0] for r in excl_rows)) if excl_rows else ""
                            extras_texto = self._obtenerExtrasTextoPorDetalle(cursor, id_det)
                            texto_personalizacion = " | ".join(t for t in [excl_texto, extras_texto] if t)
                            clave = f"{nombre}_{tipo}_{texto_personalizacion}"
                            if clave in dicc_items:
                                dicc_items[clave]['cantidad'] += int(cantidad)
                                dicc_items[clave]['subtotal'] += float(subtotal)
                            else:
                                dicc_items[clave] = {
                                    'producto': nombre,
                                    'cantidad': int(cantidad),
                                    'tipo': tipo,
                                    'precio': float(precio),
                                    'subtotal': float(subtotal),
                                    'exclusiones': texto_personalizacion,
                                }
                        items = list(dicc_items.values())
                conn.close()
        except Exception as e:
            print(f"Error al obtener items de venta: {e}")
        return items

    def enviarVentaCocina(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        configurada, mensaje = self.verificarImpresoraConfigurada("Cocina")
        if not configurada:
            QMessageBox.warning(self, "Impresora no configurada", mensaje)
            self.conn.close()
            return

        if self.cocina_print_count >= 2:
            if not self.verificar_contraseña_usuario(self.campoCajero.text()):
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
            }
            items = []
            for i in range(self.tabla.rowCount()):
                nombre_real = self._nombreRealDeFila(i)
                excl_fila = self.exclusiones_por_fila.get(i, [])
                if isinstance(excl_fila, list):
                    excl_texto = self._textoExclusiones(excl_fila)
                else:
                    excl_texto = ""
                extras_fila = self.extras_por_fila.get(i, [])
                if isinstance(extras_fila, list):
                    extras_texto_fila = self._textoExtras(extras_fila)
                else:
                    extras_texto_fila = ""
                exclusiones_promo_fila = getattr(self, 'exclusiones_promo_por_fila', {}).get(i, {})
                if isinstance(exclusiones_promo_fila, dict):
                    exclusiones_promo = exclusiones_promo_fila.get('exclusiones', {})
                    extras_promo = exclusiones_promo_fila.get('extras', {})
                else:
                    exclusiones_promo = {}
                    extras_promo = {}
                if exclusiones_promo:
                    texto_promo = self._textoExclusionesPromoParaImpresion(exclusiones_promo)
                    if excl_texto:
                        exclusiones_texto = f"{excl_texto} | {texto_promo}"
                    else:
                        exclusiones_texto = texto_promo
                else:
                    exclusiones_texto = excl_texto
                if extras_promo:
                    texto_extra_promo = self._textoExtrasPromoParaImpresion(extras_promo)
                    if extras_texto_fila:
                        extras_texto_fila = f"{extras_texto_fila} | {texto_extra_promo}"
                    else:
                        extras_texto_fila = texto_extra_promo
                texto_personalizacion_cocina = " | ".join(t for t in [exclusiones_texto, extras_texto_fila] if t)
                items.append(
                    {
                        'cantidad': int(self.tabla.item(i, 0).text()),
                        'tipo': self.tabla.item(i, 1).text(),
                        'producto': nombre_real,
                        'exclusiones': texto_personalizacion_cocina,
                    }
                )
            self._imprimir_en_consola("PEDIDO A COCINA", datos_venta, items)
            exito, mensaje = self.manejador_impresion.imprimir_cocina(datos_venta, items)
            if exito:
                self.signals.resultado_cocina.emit(True, mensaje, datos_venta, items)
            else:
                self.signals.resultado_cocina.emit(False, mensaje, {}, [])
        except Exception as e:
            self.signals.resultado_cocina.emit(False, f"Error al enviar pedido: {str(e)}", {}, [])
        finally:
            self.conn.close()

    def _textoExtrasPromoParaImpresion(self, extras_por_producto):
        if not extras_por_producto:
            return ""
        partes = []
        for id_prod_str, unidades_data in extras_por_producto.items():
            if not isinstance(unidades_data, list):
                continue
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT nomProd FROM Producto WHERE idProd=?", (int(id_prod_str),))
            prod = cursor.fetchone()
            conn.close()
            nombre_prod = prod[0] if prod else id_prod_str
            for unidad_data in unidades_data:
                if not isinstance(unidad_data, dict):
                    continue
                extras = unidad_data.get('extras', [])
                if not isinstance(extras, list):
                    continue
                nombres = []
                for e in extras:
                    if isinstance(e, dict) and 'nomIng' in e:
                        nombres.append(f"+{e['cantidadExtra']} {e['nomIng']}")
                if nombres:
                    unidad_num = unidad_data.get('unidad', 0) + 1
                    partes.append(f"U{unidad_num} {nombre_prod}: extra {', '.join(nombres)}")
        return " | ".join(partes)

    def _textoExclusionesPromoParaImpresion(self, exclusiones_por_producto):
        if not exclusiones_por_producto:
            return ""
        partes = []
        for id_prod_str, unidades_data in exclusiones_por_producto.items():
            if not isinstance(unidades_data, list):
                continue
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT nomProd FROM Producto WHERE idProd=?", (int(id_prod_str),))
            prod = cursor.fetchone()
            conn.close()
            nombre_prod = prod[0] if prod else id_prod_str
            for unidad_data in unidades_data:
                if not isinstance(unidad_data, dict):
                    continue
                excls = unidad_data.get('exclusiones', [])
                if not isinstance(excls, list):
                    continue
                nombres = []
                for e in excls:
                    if isinstance(e, dict) and 'nomIng' in e:
                        nombres.append(e['nomIng'])
                if nombres:
                    unidad_num = unidad_data.get('unidad', 0) + 1
                    partes.append(f"U{unidad_num} {nombre_prod}: sin {', '.join(nombres)}")
        return " | ".join(partes)

    @pyqtSlot(bool, str, dict, list)
    def _procesar_resultado_ticket(self, exito, mensaje, datos_venta, items):
        if exito:
            QMessageBox.information(self, "Exito", f"Ticket impreso correctamente\n{mensaje}")
            self.banderaTicket = True
            self.ticket_print_count += 1
            if self.banderaTicket and self.banderaCocina:
                self.limpiarCampos()
                self._clear_grid(self.layoutProductos)
        else:
            QMessageBox.warning(self, "Advertencia", f"No se pudo imprimir el ticket\n{mensaje}")

    @pyqtSlot(bool, str, dict, list)
    def _procesar_resultado_cocina(self, exito, mensaje, datos_venta, items):
        if exito:
            QMessageBox.information(self, "Exito", f"Pedido cocina enviado correctamente\n{mensaje}")
            if not self.enviada:
                self.subirInformacion()
                self.enviada = True
            self.banderaCocina = True
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
            self.cursor.execute(
                """SELECT disponible FROM Mesa WHERE idMesa=? AND idSeccion=?""", (idMesa, int(idSeccion))
            )
            resultado = self.cursor.fetchone()
            estado = resultado[0]
            if not estado:
                self.cursor.execute(
                    """SELECT numVenta, fechaReg FROM Venta WHERE idMesa=? AND idSeccion=? ORDER BY fechaReg DESC LIMIT 1""",
                    (idMesa, idSeccion),
                )
                resultados = self.cursor.fetchone()
                nVenta, fVenta = resultados[0], resultados[1]
                for i in range(self.tabla.rowCount()):
                    cantidad = self.tabla.item(i, 0).text()
                    nombre = self._nombreRealDeFila(i)
                    subtotal = self.tabla.item(i, 4).text()
                    tipoConsumo = self.tabla.item(i, 1).text()
                    self.cursor.execute("""SELECT * FROM Promocion WHERE nomProm=?""", (nombre,))
                    resultados = self.cursor.fetchall()
                    if resultados:
                        self.cursor.execute("""SELECT idProm FROM Promocion WHERE nomProm=?""", (nombre,))
                        idPromocion = self.cursor.fetchone()[0]
                        self.cursor.execute(
                            """INSERT INTO DetallesVenta
                            (numVenta, fechaRegVenta, fechaRegDetalleVenta, idProm, subtotal, cantidadProdDet, tipoConsumo, estadoDetalleVenta, idMeseroActual)
                            VALUES(?,?,?,?,?,?,?,?,?)""",
                            (
                                nVenta,
                                fVenta,
                                fechaRegistro,
                                idPromocion,
                                float(subtotal),
                                int(cantidad),
                                tipoConsumo,
                                estadoVenta,
                                idEmpleado,
                            ),
                        )
                        id_detalle = self.cursor.lastrowid
                        self.cursor.execute(
                            """
                            SELECT pp.idProd, pp.cantidadProdProm
                            FROM PromocionProd pp
                            WHERE pp.idProm = ?
                        """,
                            (idPromocion,),
                        )
                        productos_promo = self.cursor.fetchall()
                        unidades_creadas = 0
                        for id_prod_p, cant_prod_p in productos_promo:
                            for _ in range(cant_prod_p * int(cantidad)):
                                self.cursor.execute(
                                    """
                                    INSERT INTO DetallesVentaUnidades (idDetalleVenta, numUnidad, marcado, idProd)
                                    VALUES (?, ?, ?, ?)
                                """,
                                    (id_detalle, unidades_creadas, False, id_prod_p),
                                )
                                unidades_creadas += 1
                        exclusiones_promo_fila = getattr(self, 'exclusiones_promo_por_fila', {}).get(i, {})
                        exclusiones_promo = (
                            exclusiones_promo_fila.get('exclusiones', {})
                            if isinstance(exclusiones_promo_fila, dict)
                            else {}
                        )
                        if exclusiones_promo:
                            self._guardarExclusionesPromo(id_detalle, exclusiones_promo)
                        extras_promo = (
                            exclusiones_promo_fila.get('extras', {}) if isinstance(exclusiones_promo_fila, dict) else {}
                        )
                        if extras_promo:
                            self._guardarExtrasPromo(id_detalle, extras_promo)
                    else:
                        self.cursor.execute("""SELECT idProd FROM Producto WHERE nomProd=?""", (nombre,))
                        row = self.cursor.fetchone()
                        if row is None:
                            print(f"Producto no encontrado en BD: {nombre}")
                            continue
                        idProducto = row[0]
                        self.cursor.execute(
                            """INSERT INTO DetallesVenta
                            (numVenta, fechaRegVenta, fechaRegDetalleVenta, idProd, subtotal, cantidadProdDet, tipoConsumo, estadoDetalleVenta, idMeseroActual)
                            VALUES(?,?,?,?,?,?,?,?,?)""",
                            (
                                nVenta,
                                fVenta,
                                fechaRegistro,
                                idProducto,
                                float(subtotal),
                                int(cantidad),
                                tipoConsumo,
                                estadoVenta,
                                idEmpleado,
                            ),
                        )
                        id_detalle = self.cursor.lastrowid
                        for unidad_num in range(int(cantidad)):
                            self.cursor.execute(
                                """
                                INSERT INTO DetallesVentaUnidades (idDetalleVenta, numUnidad, marcado, idProd)
                                VALUES (?, ?, ?, ?)
                            """,
                                (id_detalle, unidad_num, False, idProducto),
                            )
                        self._guardarExclusiones(id_detalle, i)
                        self._guardarExtras(id_detalle, i)
                self.cursor.execute(
                    """SELECT totalVenta FROM Venta WHERE numVenta=? AND fechaReg=?""", (nVenta, fVenta)
                )
                totalAnterior = self.cursor.fetchone()[0]
                nuevoTotal = float(totalAnterior) + float(totalVenta)
                self.cursor.execute(
                    """UPDATE Venta SET totalVenta=? WHERE numVenta=? AND fechaReg=?""", (nuevoTotal, nVenta, fVenta)
                )
            else:
                numVenta = self.campoNumeroVenta.text()
                self.cursor.execute(
                    """INSERT INTO Venta(
                    numVenta, fechaReg, horaReg, codEmp, codEmp2, totalVenta,
                    idMesa, idSeccion
                ) VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        int(numVenta),
                        fechaRegistro,
                        horaRegistro,
                        int(idEmpleado),
                        int(idCajero),
                        float(totalVenta),
                        idMesa,
                        int(idSeccion),
                    ),
                )
                self.cursor.execute(
                    """UPDATE Mesa SET disponible=FALSE WHERE idMesa=? AND idSeccion=?""", (idMesa, int(idSeccion))
                )
                self.cursor.execute("""SELECT MAX(numVenta) FROM Venta WHERE fechaReg = ?""", (fechaRegistro,))
                resultado = self.cursor.fetchone()
                numVenta = resultado[0]
                for i in range(self.tabla.rowCount()):
                    cantidad = self.tabla.item(i, 0).text()
                    nombre = self._nombreRealDeFila(i)
                    subtotal = self.tabla.item(i, 4).text()
                    tipoConsumo = self.tabla.item(i, 1).text()
                    self.cursor.execute("""SELECT * FROM Promocion WHERE nomProm=?""", (nombre,))
                    resultados = self.cursor.fetchall()
                    if resultados:
                        self.cursor.execute("""SELECT idProm FROM Promocion WHERE nomProm=?""", (nombre,))
                        idPromocion = self.cursor.fetchone()[0]
                        self.cursor.execute(
                            """INSERT INTO DetallesVenta
                            (numVenta, fechaRegVenta, fechaRegDetalleVenta, idProm, subtotal, cantidadProdDet, tipoConsumo, estadoDetalleVenta, idMeseroActual)
                            VALUES(?,?,?,?,?,?,?,?,?)""",
                            (
                                int(numVenta),
                                fechaRegistro,
                                fechaRegistro,
                                idPromocion,
                                float(subtotal),
                                int(cantidad),
                                tipoConsumo,
                                estadoVenta,
                                idEmpleado,
                            ),
                        )
                        id_detalle = self.cursor.lastrowid
                        self.cursor.execute(
                            """
                            SELECT pp.idProd, pp.cantidadProdProm
                            FROM PromocionProd pp
                            WHERE pp.idProm = ?
                        """,
                            (idPromocion,),
                        )
                        productos_promo = self.cursor.fetchall()
                        unidades_creadas = 0
                        for id_prod_p, cant_prod_p in productos_promo:
                            for _ in range(cant_prod_p * int(cantidad)):
                                self.cursor.execute(
                                    """
                                    INSERT INTO DetallesVentaUnidades (idDetalleVenta, numUnidad, marcado, idProd)
                                    VALUES (?, ?, ?, ?)
                                """,
                                    (id_detalle, unidades_creadas, False, id_prod_p),
                                )
                                unidades_creadas += 1
                        exclusiones_promo_fila = getattr(self, 'exclusiones_promo_por_fila', {}).get(i, {})
                        exclusiones_promo = (
                            exclusiones_promo_fila.get('exclusiones', {})
                            if isinstance(exclusiones_promo_fila, dict)
                            else {}
                        )
                        if exclusiones_promo:
                            self._guardarExclusionesPromo(id_detalle, exclusiones_promo)
                        extras_promo = (
                            exclusiones_promo_fila.get('extras', {}) if isinstance(exclusiones_promo_fila, dict) else {}
                        )
                        if extras_promo:
                            self._guardarExtrasPromo(id_detalle, extras_promo)
                    else:
                        self.cursor.execute("""SELECT idProd FROM Producto WHERE nomProd=?""", (nombre,))
                        row = self.cursor.fetchone()
                        if row is None:
                            print(f"Producto no encontrado en BD: {nombre}")
                            continue
                        idProducto = row[0]
                        self.cursor.execute(
                            """INSERT INTO DetallesVenta
                            (numVenta, fechaRegVenta, fechaRegDetalleVenta, idProd, subtotal, cantidadProdDet, tipoConsumo, estadoDetalleVenta, idMeseroActual)
                            VALUES(?,?,?,?,?,?,?,?,?)""",
                            (
                                int(numVenta),
                                fechaRegistro,
                                fechaRegistro,
                                idProducto,
                                float(subtotal),
                                int(cantidad),
                                tipoConsumo,
                                estadoVenta,
                                idEmpleado,
                            ),
                        )
                        id_detalle = self.cursor.lastrowid
                        for unidad_num in range(int(cantidad)):
                            self.cursor.execute(
                                """
                                INSERT INTO DetallesVentaUnidades (idDetalleVenta, numUnidad, marcado, idProd)
                                VALUES (?, ?, ?, ?)
                            """,
                                (id_detalle, unidad_num, False, idProducto),
                            )
                        self._guardarExclusiones(id_detalle, i)
                        self._guardarExtras(id_detalle, i)
                self.nuevaVenta = True
            self.enviada = True
            self.actualizarStock('restar', conn=self.conn)
            self.conn.commit()
        except Exception as e:
            print(f"Error al subir informacion: {str(e)}")
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

    def _guardarExclusiones(self, id_detalle_venta, indice_fila):
        exclusiones = self.exclusiones_por_fila.get(indice_fila, [])
        for excl in exclusiones:
            self.cursor.execute(
                """
                INSERT INTO DetallesVentaExclusiones (idDetalleVenta, idIng, nomIng)
                VALUES (?, ?, ?)
            """,
                (id_detalle_venta, excl["idIng"], excl["nomIng"]),
            )

    def _guardarExtras(self, id_detalle_venta, indice_fila):
        extras = self.extras_por_fila.get(indice_fila, [])
        for extra in extras:
            self.cursor.execute(
                """
                INSERT INTO DetallesVentaExtras (idDetalleVenta, idIng, nomIng, cantidadExtra, precioExtra)
                VALUES (?, ?, ?, ?, ?)
            """,
                (id_detalle_venta, extra["idIng"], extra["nomIng"], extra["cantidadExtra"], extra["precioExtra"]),
            )

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
        self.exclusiones_por_fila = {}
        self.extras_por_fila = {}
        self.exclusiones_promo_por_fila = {}
        fecha = datetime.now().date()
        if self.nuevaVenta == True:
            self.cursor.execute("""SELECT COUNT(*) FROM Venta WHERE DATE(fechaReg)=?""", (fecha,))
            resultados = self.cursor.fetchone()
            cantidad = resultados[0]
            numVenta = 1 if cantidad == 0 else cantidad + 1
            self.campoNumeroVenta.setText(str(numVenta))
            self.nuevaVenta = False
        self.conn.close()

    def actualizarNumeroVenta(self, fecha):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""SELECT COUNT(*) FROM Venta WHERE DATE(fechaReg)=?""", (fecha,))
        resultados = self.cursor.fetchone()
        cantidad = resultados[0]
        numVenta = 1 if cantidad == 0 else cantidad + 1
        self.campoNumeroVenta.setText(str(numVenta))
        self.conn.close()

    def construirSeccionProductos(self, layoutCampo4):
        contCat = QHBoxLayout()
        self.btnPrevCat1 = QPushButton("◀")
        self.btnPrevCat1.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border-radius: 6px; padding: 8px 16px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.btnNextCat1 = QPushButton("▶")
        self.btnNextCat1.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border-radius: 6px; padding: 8px 16px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
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
        self.btnPrevCat1.clicked.connect(
            lambda: self.scrollCat.horizontalScrollBar().setValue(self.scrollCat.horizontalScrollBar().value() - 200)
        )
        self.btnNextCat1.clicked.connect(
            lambda: self.scrollCat.horizontalScrollBar().setValue(self.scrollCat.horizontalScrollBar().value() + 200)
        )
        contSub = QHBoxLayout()
        self.btnPrevSub = QPushButton("◀")
        self.btnPrevSub.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border-radius: 6px; padding: 8px 16px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.btnNextSub = QPushButton("▶")
        self.btnNextSub.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border-radius: 6px; padding: 8px 16px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
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
        self.btnPrevSub.clicked.connect(
            lambda: self.scrollSub.horizontalScrollBar().setValue(self.scrollSub.horizontalScrollBar().value() - 200)
        )
        self.btnNextSub.clicked.connect(
            lambda: self.scrollSub.horizontalScrollBar().setValue(self.scrollSub.horizontalScrollBar().value() + 200)
        )
        self.scrollProductos = QScrollArea()
        self.scrollProductos.setStyleSheet("""
        QScrollArea {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 2px;
        }
        QScrollArea > QWidget > QWidget { background-color: transparent; }
        QScrollBar:vertical { border: none; background: #f8f9fa; width: 14px; margin: 0px; border-radius: 7px; }
        QScrollBar::handle:vertical { background: #c0c7d4; min-height: 40px; border-radius: 7px; margin: 3px; }
        QScrollBar::handle:vertical:hover { background: #a0b0c4; }
        QScrollBar::handle:vertical:pressed { background: #8090b0; }
        QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical { height: 0px; }
        QScrollBar:horizontal { border: none; background: #f8f9fa; height: 14px; margin: 0px; border-radius: 7px; }
        QScrollBar::handle:horizontal { background: #c0c7d4; min-width: 40px; border-radius: 7px; margin: 3px; }
        QScrollBar::handle:horizontal:hover { background: #a0b0c4; }
        QScrollBar::handle:horizontal:pressed { background: #8090b0; }
        QScrollBar::sub-line:horizontal, QScrollBar::add-line:horizontal { width: 0px; }
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
        self.cursor.execute(
            "SELECT idCategoria, nomCategoria, imagenCategoria FROM Categoria WHERE activa=1 ORDER BY nomCategoria"
        )
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
        btn.setFixedSize(160, 120)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("QPushButton{background:transparent;border:none;}")
        layout = QVBoxLayout(btn)
        layout.setContentsMargins(0, 0, 0, 0)
        lbl_bg = QLabel()
        lbl_bg.setFixedSize(160, 120)
        lbl_bg.setAlignment(Qt.AlignCenter)
        lbl_bg.setStyleSheet("background:transparent;")
        if imagen_blob:
            pix = QPixmap.fromImage(QImage.fromData(imagen_blob))
        else:
            pix = QPixmap(get_resource_path("Imagenes/camara.png"))
        pix = pix.scaled(160, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        rounded = QPixmap(160, 120)
        rounded.fill(Qt.transparent)
        p = QPainter(rounded)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, 160, 120, 12, 12)
        p.setClipPath(path)
        x = (160 - pix.width()) // 2
        y = (120 - pix.height()) // 2
        p.drawPixmap(x, y, pix)
        grad = QLinearGradient(0, 0, 0, 120)
        grad.setColorAt(0, QColor(0, 0, 0, 30))
        grad.setColorAt(1, QColor(0, 0, 0, 140))
        p.fillPath(path, grad)
        p.end()
        lbl_bg.setPixmap(rounded)
        layout.addWidget(lbl_bg)
        lbl_text = QLabel(texto.upper(), lbl_bg)
        lbl_text.setGeometry(0, 0, 160, 120)
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
            (idCategoria,),
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
            (idSubcategoria,),
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
        self.cursor.execute(
            """
            SELECT p.nomProd, p.imgProd
            FROM Producto p
            JOIN Subcategoria s ON p.idSubcategoria = s.idSubcategoria
            WHERE p.activo=1 AND s.idCategoria=?
            ORDER BY p.nomProd
        """,
            (idCategoria,),
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
                            except Exception:
                                pass
                        if hora_valida:
                            promos_filtradas.append((nomProm, imgProm))
                            continue
                    except Exception:
                        pass
                fecha_valida = False
                if fechaInicio and fechaFin:
                    try:
                        fecha_ini = datetime.strptime(fechaInicio, "%Y-%m-%d").date()
                        fecha_fin = datetime.strptime(fechaFin, "%Y-%m-%d").date()
                        if fecha_ini <= current_date <= fecha_fin:
                            fecha_valida = True
                    except Exception:
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
                    except Exception:
                        pass
                else:
                    hora_valida = True
                self.cursor.execute(
                    """
                    SELECT COUNT(*) FROM PromocionDias
                    WHERE idProm = ? AND diaSemana = ?
                """,
                    (idProm, current_weekday),
                )
                tiene_dia = self.cursor.fetchone()[0] > 0
                self.cursor.execute(
                    """
                    SELECT COUNT(*) FROM PromocionDias
                    WHERE idProm = ?
                """,
                    (idProm,),
                )
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
            except Exception:
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
        if bandera:
            contenedor.clicked.connect(lambda: self.dialogProducto(nombre, bandera))
        else:
            contenedor.clicked.connect(lambda: self.dialogPromocion(nombre))
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
        QSpinBox {
            background-color: #ffffff;
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 14px;
            min-height: 40px;
            padding-right: 30px;
        }
        QSpinBox:focus {
            border: 2px solid #4a89dc;
            background-color: #f0f7ff;
        }
        QSpinBox::up-button {
            background-color: #3498db;
            border: none;
            width: 35px;
            height: 28px;
            top: 0;
            border-radius:0px 5px 0px 0px;
            right: 0;
            subcontrol-origin: border;
            subcontrol-position: top right;
        }
        QSpinBox::up-button:hover { background-color: #2980b9; }
        QSpinBox::up-button:pressed { background-color: #1f6a9a; }
        QSpinBox::down-button {
            background-color: #e74c3c;
            border: none;
            border-radius:0px 5px 0px 0px;
            width: 35px;
            height: 28px;
            bottom: 0;
            right: 0;
            subcontrol-origin: border;
            subcontrol-position: bottom right;
        }
        QSpinBox::down-button:hover { background-color: #c0392b; }
        QSpinBox::down-button:pressed { background-color: #a93226; }
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
        QRadioButton::indicator:checked {
            background-color: #4a89dc;
            border: 2px solid #4a89dc;
        }
        QDialogButtonBox {
            background: #f5f7fa;
            border-top: 1px solid #e2e8f0;
            padding: 12px 16px;
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
        QDialogButtonBox QPushButton:hover { background-color: #2980b9; }
        QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; }
        QCheckBox { spacing: 10px; font-size: 12px; font-weight: 500; color: #2c3e50; background: transparent; }
        QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 2px solid #3498db; background: white; }
        QCheckBox::indicator:checked { background-color: #3498db; border: 2px solid #3498db; }
        QCheckBox::indicator:unchecked { background-color: white; }
        """)

        layout = QVBoxLayout(dialog)
        if not getattr(self, "validar_stock", False):
            max_disponible = 9999
            info_texto = "Sin validar stock (entrada libre)"
        else:
            max_disponible = self.verificarStockDisponible(nombre, bandera)
            info_texto = f"Maximo disponible: {max_disponible} unidades"

        spin = QSpinBox()
        spin.setRange(1, max_disponible if max_disponible > 0 else 1)
        spin.setValue(1)
        info_label = QLabel(info_texto)
        layout.addWidget(QLabel(f"Producto: {nombre}"))
        layout.addWidget(info_label)
        layout.addWidget(QLabel("Cantidad:"))
        layout.addWidget(spin)

        tipoLocal = QRadioButton("Local")
        tipoLlevar = QRadioButton("Para llevar")
        tipoLocal.setChecked(True)
        layout.addWidget(tipoLocal)
        layout.addWidget(tipoLlevar)

        exclusiones_por_unidad_ref = [{}]
        cantidad_al_personalizar = [0]

        if bandera:
            ingredientes = self._obtenerIngredientesProducto(nombre)
            if ingredientes:
                btn_personalizar = QPushButton("Personalizar ingredientes")
                btn_personalizar.setStyleSheet("""
                    QPushButton {
                        background-color: #8e44ad;
                        color: white;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: bold;
                        font-size: 13px;
                        min-width: 0;
                    }
                    QPushButton:hover { background-color: #7d3c98; }
                """)

                lbl_exclusiones = QLabel("Sin exclusiones")
                lbl_exclusiones.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        color: #27ae60;
                        padding: 4px 8px;
                        background-color: #eafaf1;
                        border-radius: 4px;
                        border: 1px solid #a9dfbf;
                    }
                """)
                lbl_exclusiones.setWordWrap(True)

                def _texto_resumen_unidades(excl_por_unidad):
                    if not excl_por_unidad:
                        return ""
                    partes = []
                    for idx_u, excls in excl_por_unidad.items():
                        if excls:
                            nombres = ", ".join(e["nomIng"] for e in excls)
                            partes.append(f"#{idx_u + 1}: sin {nombres}")
                    return " | ".join(partes)

                def abrir_personalizacion():
                    cantidad_actual = spin.value()
                    cantidad_al_personalizar[0] = cantidad_actual
                    excl_previas = exclusiones_por_unidad_ref[0]

                    subdialog = QDialog(dialog)
                    subdialog.setWindowTitle(f"Personalizar ingredientes - {nombre}")
                    subdialog.setMinimumWidth(400)
                    subdialog.setMaximumWidth(500)
                    subdialog.setStyleSheet("""
                        QDialog { background-color: white; font-family: 'Segoe UI', Arial, sans-serif; }
                        QScrollArea { border: none; background: transparent; }
                        QScrollBar:vertical { border: none; background: #f1f5f9; width: 10px; border-radius: 5px; }
                        QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 5px; min-height: 30px; }
                        QScrollBar::handle:vertical:hover { background: #94a3b8; }
                        QCheckBox { spacing: 12px; font-size: 13px; color: #2c3e50; background: transparent; }
                        QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 2px solid #3498db; background: white; }
                        QCheckBox::indicator:checked { background-color: #3498db; border: 2px solid #3498db; }
                        QCheckBox::indicator:unchecked { background-color: white; }
                        QLabel { color: #2c3e50; font-size: 13px; font-weight: 500; background: transparent; }
                        QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; }
                    """)

                    sub_layout = QVBoxLayout(subdialog)
                    sub_layout.setContentsMargins(0, 0, 0, 0)
                    sub_layout.setSpacing(0)

                    sub_header = QWidget()
                    sub_header.setStyleSheet(
                        "QWidget { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2980b9); }"
                    )
                    sub_header_layout = QVBoxLayout(sub_header)
                    sub_header_layout.setContentsMargins(24, 20, 24, 20)
                    sub_titulo = QLabel("🍽️ Personalizar ingredientes")
                    sub_titulo.setStyleSheet(
                        "QLabel { color: white; font-size: 18px; font-weight: bold; background: transparent; }"
                    )
                    sub_titulo.setAlignment(Qt.AlignCenter)
                    sub_header_layout.addWidget(sub_titulo)
                    sub_subtitulo = QLabel(nombre)
                    sub_subtitulo.setStyleSheet(
                        "QLabel { color: rgba(255,255,255,0.9); font-size: 14px; font-weight: 500; background: transparent; }"
                    )
                    sub_subtitulo.setAlignment(Qt.AlignCenter)
                    sub_header_layout.addWidget(sub_subtitulo)
                    sub_layout.addWidget(sub_header)

                    ayuda_w = QWidget()
                    ayuda_w.setStyleSheet("QWidget { background-color: #fef9e7; border-bottom: 1px solid #f39c12; }")
                    ayuda_l = QHBoxLayout(ayuda_w)
                    ayuda_l.setContentsMargins(20, 10, 20, 10)
                    ayuda_lbl = QLabel(
                        "⚠️  Personaliza cada unidad individualmente — Desmarca los ingredientes que el cliente NO quiere"
                    )
                    ayuda_lbl.setStyleSheet(
                        "background: transparent; font-size: 12px; color: #e67e22; font-weight: 500;"
                    )
                    ayuda_l.addWidget(ayuda_lbl)
                    sub_layout.addWidget(ayuda_w)

                    scroll_principal = QScrollArea()
                    scroll_principal.setWidgetResizable(True)
                    scroll_principal.setStyleSheet("QScrollArea { border: none; background-color: #f8fafc; }")
                    contenedor_principal = QWidget()
                    contenedor_principal.setStyleSheet("background-color: #f8fafc;")
                    contenedor_layout = QVBoxLayout(contenedor_principal)
                    contenedor_layout.setContentsMargins(16, 16, 16, 16)
                    contenedor_layout.setSpacing(15)

                    unidades_checkboxes = []

                    for idx_u in range(cantidad_actual):
                        ids_excluidos_prev = set()
                        if idx_u in excl_previas:
                            ids_excluidos_prev = {e["idIng"] for e in excl_previas[idx_u]}

                        unidad_frame = QFrame()
                        unidad_frame.setStyleSheet(
                            "QFrame { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; margin: 2px; }"
                        )
                        unidad_frame_layout = QVBoxLayout(unidad_frame)
                        unidad_frame_layout.setSpacing(8)
                        unidad_frame_layout.setContentsMargins(12, 10, 12, 10)

                        unidad_header = QWidget()
                        unidad_header.setStyleSheet("background: transparent; border: none;")
                        unidad_header_layout = QHBoxLayout(unidad_header)
                        unidad_header_layout.setContentsMargins(0, 0, 0, 0)

                        unidad_titulo = QLabel(f"Unidad #{idx_u + 1}")
                        unidad_titulo.setStyleSheet(
                            "font-weight: bold; color: #3498db; font-size: 14px; background: transparent; border: none;"
                        )
                        unidad_header_layout.addWidget(unidad_titulo)
                        unidad_header_layout.addStretch()

                        botones_rapidos = QWidget()
                        botones_rapidos.setStyleSheet("background: transparent; border: none;")
                        botones_layout = QHBoxLayout(botones_rapidos)
                        botones_layout.setContentsMargins(0, 0, 0, 0)
                        botones_layout.setSpacing(6)

                        btn_todos_u = QPushButton("✓ Todos")
                        btn_todos_u.setStyleSheet("""
                            QPushButton { background-color: #3498db; color: white; border: none; border-radius: 6px;
                                font-size: 11px; font-weight: bold; padding: 4px 8px; min-width: 60px; }
                            QPushButton:hover { background-color: #2980b9; }
                        """)
                        btn_todos_u.setFixedSize(70, 28)

                        btn_ninguno_u = QPushButton("✗ Ninguno")
                        btn_ninguno_u.setStyleSheet("""
                            QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 6px;
                                font-size: 11px; font-weight: bold; padding: 4px 8px; min-width: 60px; }
                            QPushButton:hover { background-color: #c0392b; }
                        """)
                        btn_ninguno_u.setFixedSize(70, 28)

                        botones_layout.addWidget(btn_todos_u)
                        botones_layout.addWidget(btn_ninguno_u)
                        unidad_header_layout.addWidget(botones_rapidos)
                        unidad_frame_layout.addWidget(unidad_header)

                        separador = QWidget()
                        separador.setFixedHeight(1)
                        separador.setStyleSheet("background-color: #e2e8f0; border: none;")
                        unidad_frame_layout.addWidget(separador)

                        checkboxes = []
                        for ing in ingredientes:
                            item_w = QWidget()
                            item_w.setStyleSheet("background: transparent;")
                            item_l = QHBoxLayout(item_w)
                            item_l.setContentsMargins(8, 4, 8, 4)
                            item_l.setSpacing(10)

                            cb = QCheckBox()
                            cb.setChecked(ing["idIng"] not in ids_excluidos_prev)
                            cb.idIng = ing["idIng"]
                            cb.nomIng = ing["nomIng"]

                            ing_lbl = QLabel(ing["nomIng"])
                            ing_lbl.setStyleSheet(
                                "background: transparent; font-size: 13px; color: #2c3e50; font-weight: 500; border: none;"
                            )

                            estado_lbl = QLabel()
                            estado_lbl.setStyleSheet(
                                "background: transparent; font-size: 11px; font-weight: bold; border: none; padding: 2px 6px; border-radius: 4px;"
                            )

                            def actualizar_estado(checked, lbl=estado_lbl, widget=item_w):
                                if checked:
                                    lbl.setText("✓ Incluido")
                                    lbl.setStyleSheet(
                                        "background: #e8f5e9; font-size: 11px; color: #2ecc71; font-weight: bold; border: none; padding: 2px 6px; border-radius: 4px;"
                                    )
                                    widget.setStyleSheet("background: transparent; border-bottom: 1px solid #e2e8f0;")
                                else:
                                    lbl.setText("✗ Excluido")
                                    lbl.setStyleSheet(
                                        "background: #ffebee; font-size: 11px; color: #e74c3c; font-weight: bold; border: none; padding: 2px 6px; border-radius: 4px;"
                                    )
                                    widget.setStyleSheet("background: #fff5f5; border-bottom: 1px solid #ffcdd2;")

                            actualizar_estado(cb.isChecked())
                            cb.toggled.connect(actualizar_estado)

                            item_l.addWidget(cb)
                            item_l.addWidget(ing_lbl, 1)
                            item_l.addWidget(estado_lbl)
                            checkboxes.append(cb)
                            unidad_frame_layout.addWidget(item_w)

                        def crear_todos(cbs):
                            def fn():
                                [c.setChecked(True) for c in cbs]

                            return fn

                        def crear_ninguno(cbs):
                            def fn():
                                [c.setChecked(False) for c in cbs]

                            return fn

                        btn_todos_u.clicked.connect(crear_todos(checkboxes))
                        btn_ninguno_u.clicked.connect(crear_ninguno(checkboxes))

                        contenedor_layout.addWidget(unidad_frame)
                        unidades_checkboxes.append(checkboxes)

                    contenedor_layout.addStretch()
                    scroll_principal.setWidget(contenedor_principal)
                    sub_layout.addWidget(scroll_principal, 1)

                    sub_footer = QWidget()
                    sub_footer.setStyleSheet("QWidget { background-color: #f8f9fa; border-top: 1px solid #e2e8f0; }")
                    sub_footer_layout = QHBoxLayout(sub_footer)
                    sub_footer_layout.setContentsMargins(20, 16, 20, 16)
                    sub_footer_layout.setSpacing(12)

                    btn_cancelar_sub = QPushButton("Cancelar")
                    btn_cancelar_sub.setStyleSheet("""
                        QPushButton { background-color: #95a5a6; color: white; border: none; border-radius: 8px;
                            font-size: 14px; font-weight: bold; padding: 10px 16px; min-width: 100px; }
                        QPushButton:hover { background-color: #7f8c8d; }
                    """)
                    btn_cancelar_sub.setCursor(Qt.PointingHandCursor)

                    btn_confirmar_sub = QPushButton("Confirmar")
                    btn_confirmar_sub.setStyleSheet("""
                        QPushButton { background-color: #2ecc71; color: white; border: none; border-radius: 8px;
                            font-size: 14px; font-weight: bold; padding: 10px 16px; min-width: 120px; }
                        QPushButton:hover { background-color: #27ae60; }
                    """)
                    btn_confirmar_sub.setCursor(Qt.PointingHandCursor)

                    sub_footer_layout.addStretch()
                    sub_footer_layout.addWidget(btn_cancelar_sub)
                    sub_footer_layout.addWidget(btn_confirmar_sub)
                    sub_layout.addWidget(sub_footer)

                    btn_cancelar_sub.clicked.connect(subdialog.reject)
                    btn_confirmar_sub.clicked.connect(subdialog.accept)

                    if subdialog.exec_() == QDialog.Accepted:
                        nuevo_excl = {}
                        for idx_u, checkboxes in enumerate(unidades_checkboxes):
                            excls = [
                                {"idIng": cb.idIng, "nomIng": cb.nomIng} for cb in checkboxes if not cb.isChecked()
                            ]
                            if excls:
                                nuevo_excl[idx_u] = excls
                        exclusiones_por_unidad_ref[0] = nuevo_excl
                        texto = _texto_resumen_unidades(nuevo_excl)
                        if texto:
                            lbl_exclusiones.setText(texto)
                            lbl_exclusiones.setStyleSheet("""
                                QLabel { font-size: 12px; color: #c0392b; padding: 4px 8px;
                                    background-color: #fdecea; border-radius: 4px; border: 1px solid #f5c6cb; }
                            """)
                        else:
                            lbl_exclusiones.setText("Sin exclusiones")
                            lbl_exclusiones.setStyleSheet("""
                                QLabel { font-size: 12px; color: #27ae60; padding: 4px 8px;
                                    background-color: #eafaf1; border-radius: 4px; border: 1px solid #a9dfbf; }
                            """)

                def on_spin_changed(nuevo_valor):
                    if (
                        exclusiones_por_unidad_ref[0]
                        and cantidad_al_personalizar[0] > 0
                        and nuevo_valor != cantidad_al_personalizar[0]
                    ):
                        lbl_exclusiones.setText(
                            f"⚠ Personalizaste para {cantidad_al_personalizar[0]} unidad(es) — la cantidad cambio, personaliza de nuevo si es necesario"
                        )
                        lbl_exclusiones.setStyleSheet("""
                            QLabel { font-size: 12px; color: #e67e22; padding: 4px 8px;
                                background-color: #fef9e7; border-radius: 4px; border: 1px solid #f39c12; }
                        """)

                spin.valueChanged.connect(on_spin_changed)
                btn_personalizar.clicked.connect(abrir_personalizacion)
                layout.addWidget(btn_personalizar)
                layout.addWidget(lbl_exclusiones)

            extras_por_unidad_ref = [{}]
            cantidad_al_personalizar_extra = [0]
            ingredientes_para_extra = self._obtenerIngredientesProductoParaExtra(nombre)

            if ingredientes_para_extra:
                btn_extra = QPushButton("Agregar ingrediente extra")
                btn_extra.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 #2ecc71, stop: 1 #27ae60);
                        color: white; border: none; border-radius: 6px;
                        padding: 8px 16px; font-weight: bold; font-size: 13px; min-width: 0;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 #32ff7e, stop: 1 #3ae374);
                    }
                """)
                lbl_extras = QLabel("Sin ingredientes extra")
                lbl_extras.setStyleSheet("""
                    QLabel { font-size: 12px; color: #27ae60; padding: 4px 8px;
                        background-color: #eafaf1; border-radius: 4px; border: 1px solid #a9dfbf; }
                """)
                lbl_extras.setWordWrap(True)

                def _texto_resumen_unidades_extra(extras_por_unidad):
                    if not extras_por_unidad:
                        return ""
                    partes = []
                    for idx_u, extras_u in extras_por_unidad.items():
                        if extras_u:
                            nombres = ", ".join(f"{e['cantidadExtra']}x {e['nomIng']}" for e in extras_u)
                            partes.append(f"#{idx_u + 1}: {nombres}")
                    return " | ".join(partes)

                def abrir_personalizacion_extra():
                    cantidad_actual = spin.value()
                    cantidad_al_personalizar_extra[0] = cantidad_actual
                    extras_previas = extras_por_unidad_ref[0]

                    subdialog = QDialog(dialog)
                    subdialog.setWindowTitle(f"Ingredientes extra - {nombre}")
                    subdialog.setMinimumWidth(420)
                    subdialog.setMaximumWidth(520)
                    subdialog.setStyleSheet("""
                        QDialog { background-color: white; font-family: 'Segoe UI', Arial, sans-serif; }
                        QScrollArea { border: none; background: transparent; }
                        QScrollBar:vertical { border: none; background: #f1f5f9; width: 10px; border-radius: 5px; }
                        QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 5px; min-height: 30px; }
                        QScrollBar::handle:vertical:hover { background: #94a3b8; }
                        QLabel { color: #2c3e50; font-size: 13px; font-weight: 500; background: transparent; }
                        QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; }
                        QSpinBox {
                            background-color: white; border: 2px solid #e2e8f0; border-radius: 6px;
                            padding: 2px 6px; font-size: 13px; min-height: 30px; max-width: 70px;
                        }
                        QSpinBox:focus { border: 2px solid #27ae60; }
                        QSpinBox::up-button {
                            background-color: #3498db; border: none;
                            width: 22px; height: 19px;
                            border-radius: 0px 4px 0px 0px;
                            subcontrol-origin: border; subcontrol-position: top right;
                        }
                        QSpinBox::up-button:hover { background-color: #2980b9; }
                        QSpinBox::down-button {
                            background-color: #e74c3c; border: none;
                            width: 22px; height: 19px;
                            border-radius: 0px 0px 4px 0px;
                            subcontrol-origin: border; subcontrol-position: bottom right;
                        }
                        QSpinBox::down-button:hover { background-color: #c0392b; }
                        QSpinBox::up-arrow {
                            image: none; border-left: 3px solid transparent; border-right: 3px solid transparent;
                            border-bottom: 3px solid white; width: 0; height: 0;
                        }
                        QSpinBox::down-arrow {
                            image: none; border-left: 3px solid transparent; border-right: 3px solid transparent;
                            border-top: 3px solid white; width: 0; height: 0;
                        }
                    """)

                    sub_layout = QVBoxLayout(subdialog)
                    sub_layout.setContentsMargins(0, 0, 0, 0)
                    sub_layout.setSpacing(0)

                    sub_header = QWidget()
                    sub_header.setStyleSheet(
                        "QWidget { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ecc71, stop:1 #27ae60); }"
                    )
                    sub_header_layout = QVBoxLayout(sub_header)
                    sub_header_layout.setContentsMargins(24, 20, 24, 20)
                    sub_titulo = QLabel("➕ Ingredientes extra")
                    sub_titulo.setStyleSheet(
                        "QLabel { color: white; font-size: 18px; font-weight: bold; background: transparent; }"
                    )
                    sub_titulo.setAlignment(Qt.AlignCenter)
                    sub_header_layout.addWidget(sub_titulo)
                    sub_subtitulo = QLabel(nombre)
                    sub_subtitulo.setStyleSheet(
                        "QLabel { color: rgba(255,255,255,0.9); font-size: 14px; font-weight: 500; background: transparent; }"
                    )
                    sub_subtitulo.setAlignment(Qt.AlignCenter)
                    sub_header_layout.addWidget(sub_subtitulo)
                    sub_layout.addWidget(sub_header)

                    ayuda_w = QWidget()
                    ayuda_w.setStyleSheet("QWidget { background-color: #fef9e7; border-bottom: 1px solid #f39c12; }")
                    ayuda_l = QHBoxLayout(ayuda_w)
                    ayuda_l.setContentsMargins(20, 10, 20, 10)
                    ayuda_lbl = QLabel(
                        "⚠️  Personaliza cada unidad individualmente — indica cuánto extra quieres de cada ingrediente"
                    )
                    ayuda_lbl.setWordWrap(True)
                    ayuda_lbl.setStyleSheet(
                        "background: transparent; font-size: 12px; color: #e67e22; font-weight: 500;"
                    )
                    ayuda_l.addWidget(ayuda_lbl)
                    sub_layout.addWidget(ayuda_w)

                    scroll_principal = QScrollArea()
                    scroll_principal.setWidgetResizable(True)
                    scroll_principal.setStyleSheet("QScrollArea { border: none; background-color: #f8fafc; }")
                    contenedor_principal = QWidget()
                    contenedor_principal.setStyleSheet("background-color: #f8fafc;")
                    contenedor_layout = QVBoxLayout(contenedor_principal)
                    contenedor_layout.setContentsMargins(16, 16, 16, 16)
                    contenedor_layout.setSpacing(15)

                    unidades_spinboxes = []

                    for idx_u in range(cantidad_actual):
                        cantidades_prev = {}
                        if idx_u in extras_previas:
                            cantidades_prev = {e["idIng"]: e["cantidadExtra"] for e in extras_previas[idx_u]}

                        unidad_frame = QFrame()
                        unidad_frame.setStyleSheet(
                            "QFrame { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; margin: 2px; }"
                        )
                        unidad_frame_layout = QVBoxLayout(unidad_frame)
                        unidad_frame_layout.setSpacing(8)
                        unidad_frame_layout.setContentsMargins(12, 10, 12, 10)

                        unidad_header = QWidget()
                        unidad_header.setStyleSheet("background: transparent; border: none;")
                        unidad_header_layout = QHBoxLayout(unidad_header)
                        unidad_header_layout.setContentsMargins(0, 0, 0, 0)

                        unidad_titulo = QLabel(f"Unidad #{idx_u + 1}")
                        unidad_titulo.setStyleSheet(
                            "font-weight: bold; color: #27ae60; font-size: 14px; background: transparent; border: none;"
                        )
                        unidad_header_layout.addWidget(unidad_titulo)
                        unidad_header_layout.addStretch()

                        btn_limpiar_u = QPushButton("Limpiar")
                        btn_limpiar_u.setStyleSheet("""
                            QPushButton { background-color: #95a5a6; color: white; border: none; border-radius: 6px;
                                font-size: 11px; font-weight: bold; padding: 4px 8px; min-width: 60px; }
                            QPushButton:hover { background-color: #7f8c8d; }
                        """)
                        btn_limpiar_u.setFixedSize(70, 28)
                        unidad_header_layout.addWidget(btn_limpiar_u)
                        unidad_frame_layout.addWidget(unidad_header)

                        separador = QWidget()
                        separador.setFixedHeight(1)
                        separador.setStyleSheet("background-color: #e2e8f0; border: none;")
                        unidad_frame_layout.addWidget(separador)

                        spinboxes_unidad = []
                        for ing in ingredientes_para_extra:
                            idIng_ing, nomIng_ing, precioExtra_ing = ing
                            item_w = QWidget()
                            item_w.setStyleSheet("background: transparent;")
                            item_l = QHBoxLayout(item_w)
                            item_l.setContentsMargins(8, 4, 8, 4)
                            item_l.setSpacing(10)

                            ing_lbl = QLabel(f"{nomIng_ing}  (+{precioExtra_ing:.2f} Bs c/u)")
                            ing_lbl.setStyleSheet(
                                "background: transparent; font-size: 13px; color: #2c3e50; font-weight: 500; border: none;"
                            )

                            sp = QSpinBox()
                            sp.setRange(0, 20)
                            sp.setValue(cantidades_prev.get(idIng_ing, 0))
                            sp.idIng = idIng_ing
                            sp.nomIng = nomIng_ing
                            sp.precioExtra = precioExtra_ing

                            item_l.addWidget(ing_lbl, 1)
                            item_l.addWidget(sp)
                            spinboxes_unidad.append(sp)
                            unidad_frame_layout.addWidget(item_w)

                        def crear_limpiar(sps):
                            def fn():
                                for s in sps:
                                    s.setValue(0)

                            return fn

                        btn_limpiar_u.clicked.connect(crear_limpiar(spinboxes_unidad))

                        contenedor_layout.addWidget(unidad_frame)
                        unidades_spinboxes.append(spinboxes_unidad)

                    contenedor_layout.addStretch()
                    scroll_principal.setWidget(contenedor_principal)
                    sub_layout.addWidget(scroll_principal, 1)

                    sub_footer = QWidget()
                    sub_footer.setStyleSheet("QWidget { background-color: #f8f9fa; border-top: 1px solid #e2e8f0; }")
                    sub_footer_layout = QHBoxLayout(sub_footer)
                    sub_footer_layout.setContentsMargins(20, 16, 20, 16)
                    sub_footer_layout.setSpacing(12)

                    btn_cancelar_sub = QPushButton("Cancelar")
                    btn_cancelar_sub.setStyleSheet("""
                        QPushButton { background-color: #95a5a6; color: white; border: none; border-radius: 8px;
                            font-size: 14px; font-weight: bold; padding: 10px 16px; min-width: 100px; }
                        QPushButton:hover { background-color: #7f8c8d; }
                    """)
                    btn_cancelar_sub.setCursor(Qt.PointingHandCursor)

                    btn_confirmar_sub = QPushButton("Confirmar")
                    btn_confirmar_sub.setStyleSheet("""
                        QPushButton { background-color: #2ecc71; color: white; border: none; border-radius: 8px;
                            font-size: 14px; font-weight: bold; padding: 10px 16px; min-width: 120px; }
                        QPushButton:hover { background-color: #27ae60; }
                    """)
                    btn_confirmar_sub.setCursor(Qt.PointingHandCursor)

                    sub_footer_layout.addStretch()
                    sub_footer_layout.addWidget(btn_cancelar_sub)
                    sub_footer_layout.addWidget(btn_confirmar_sub)
                    sub_layout.addWidget(sub_footer)

                    btn_cancelar_sub.clicked.connect(subdialog.reject)
                    btn_confirmar_sub.clicked.connect(subdialog.accept)

                    if subdialog.exec_() == QDialog.Accepted:
                        nuevo_extras = {}
                        for idx_u, spinboxes_u in enumerate(unidades_spinboxes):
                            extras_u = [
                                {
                                    "idIng": sp.idIng,
                                    "nomIng": sp.nomIng,
                                    "cantidadExtra": sp.value(),
                                    "precioExtra": sp.precioExtra,
                                }
                                for sp in spinboxes_u
                                if sp.value() > 0
                            ]
                            if extras_u:
                                nuevo_extras[idx_u] = extras_u
                        extras_por_unidad_ref[0] = nuevo_extras
                        texto = _texto_resumen_unidades_extra(nuevo_extras)
                        if texto:
                            lbl_extras.setText(texto)
                            lbl_extras.setStyleSheet("""
                                QLabel { font-size: 12px; color: #27ae60; padding: 4px 8px;
                                    background-color: #eafaf1; border-radius: 4px; border: 1px solid #a9dfbf; }
                            """)
                        else:
                            lbl_extras.setText("Sin ingredientes extra")

                def on_spin_changed_extra(nuevo_valor):
                    if (
                        extras_por_unidad_ref[0]
                        and cantidad_al_personalizar_extra[0] > 0
                        and nuevo_valor != cantidad_al_personalizar_extra[0]
                    ):
                        lbl_extras.setText(
                            f"⚠ Personalizaste para {cantidad_al_personalizar_extra[0]} unidad(es) — la cantidad cambió, personaliza de nuevo si es necesario"
                        )
                        lbl_extras.setStyleSheet("""
                            QLabel { font-size: 12px; color: #e67e22; padding: 4px 8px;
                                background-color: #fef9e7; border-radius: 4px; border: 1px solid #f39c12; }
                        """)

                spin.valueChanged.connect(on_spin_changed_extra)
                btn_extra.clicked.connect(abrir_personalizacion_extra)
                layout.addWidget(btn_extra)
                layout.addWidget(lbl_extras)

        footer_dialog_producto = QHBoxLayout()
        footer_dialog_producto.setSpacing(12)
        btn_cancelar_producto = QPushButton("Cancelar")
        btn_cancelar_producto.setCursor(Qt.PointingHandCursor)
        btn_cancelar_producto.setStyleSheet("""
            QPushButton { background-color: #95a5a6; color: white; border: none; border-radius: 8px;
                font-size: 14px; font-weight: bold; padding: 10px 16px; min-width: 100px; }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        btn_confirmar_producto = QPushButton("Confirmar")
        btn_confirmar_producto.setCursor(Qt.PointingHandCursor)
        btn_confirmar_producto.setStyleSheet("""
            QPushButton { background-color: #2ecc71; color: white; border: none; border-radius: 8px;
                font-size: 14px; font-weight: bold; padding: 10px 16px; min-width: 100px; }
            QPushButton:hover { background-color: #27ae60; }
        """)
        footer_dialog_producto.addStretch()
        footer_dialog_producto.addWidget(btn_cancelar_producto)
        footer_dialog_producto.addWidget(btn_confirmar_producto)
        layout.addLayout(footer_dialog_producto)
        btn_cancelar_producto.clicked.connect(dialog.reject)
        btn_confirmar_producto.clicked.connect(dialog.accept)

        if dialog.exec_() == QDialog.Accepted:
            tipo = "Local" if tipoLocal.isChecked() else "Para llevar"
            cantidad_final = spin.value()

            tiene_exclusiones = bandera and self._obtenerIngredientesProducto(nombre) and exclusiones_por_unidad_ref[0]
            tiene_extras = bandera and extras_por_unidad_ref[0]

            if tiene_exclusiones or tiene_extras:
                excl_por_unidad = exclusiones_por_unidad_ref[0]
                extras_por_unidad = extras_por_unidad_ref[0]
                grupos = {}
                for idx_u in range(cantidad_final):
                    excls = excl_por_unidad.get(idx_u, [])
                    extras_u = extras_por_unidad.get(idx_u, [])
                    clave_excl = frozenset(e["idIng"] for e in excls)
                    clave_extra = frozenset((e["idIng"], e["cantidadExtra"]) for e in extras_u)
                    clave = (clave_excl, clave_extra)
                    if clave not in grupos:
                        grupos[clave] = {"exclusiones": excls, "extras": extras_u, "cantidad": 0}
                    grupos[clave]["cantidad"] += 1
                for grupo in grupos.values():
                    self.agregarProductoTabla(
                        nombre, grupo["cantidad"], tipo, bandera, grupo["exclusiones"], grupo["extras"]
                    )
            else:
                self.agregarProductoTabla(nombre, cantidad_final, tipo, bandera, [], [])

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
                self.cursor.execute(
                    """
                    SELECT pi.idIng, pi.cantidadIngNecesitada, s.cantidadStock, s.unidadMedida
                    FROM ProductosIngredientes pi
                    JOIN Stock s ON pi.idIng = s.idIng
                    WHERE pi.idProd = ?
                """,
                    (id_producto,),
                )
                ingredientes = self.cursor.fetchall()
            else:
                self.cursor.execute("SELECT idProm FROM Promocion WHERE nomProm=?", (nombre,))
                row = self.cursor.fetchone()
                if not row:
                    return 0
                id_promocion = row[0]
                self.cursor.execute(
                    """
                    SELECT pp.idProd, pp.cantidadProdProm
                    FROM PromocionProd pp
                    WHERE pp.idProm = ?
                """,
                    (id_promocion,),
                )
                productos_promocion = self.cursor.fetchall()
                dicc = {}
                for id_prod, cant_prod in productos_promocion:
                    self.cursor.execute(
                        """
                        SELECT pi.idIng, (pi.cantidadIngNecesitada * ?) AS cantidad_necesaria,
                               s.cantidadStock, s.unidadMedida
                        FROM ProductosIngredientes pi
                        JOIN Stock s ON pi.idIng = s.idIng
                        WHERE pi.idProd = ?
                    """,
                        (cant_prod, id_prod),
                    )
                    for id_ing, cant_nec, stock, unidad in self.cursor.fetchall():
                        if id_ing not in dicc:
                            dicc[id_ing] = {
                                'cantidad_necesaria': float(cant_nec or 0),
                                'stock': float(stock or 0),
                                'unidad': unidad,
                            }
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
                nombre_producto = self._nombreRealDeFila(fila)
                cantidad = int(self.tabla.item(fila, 0).text())
                excl_fila = self.exclusiones_por_fila.get(fila, [])
                if isinstance(excl_fila, list):
                    ids_excluidos = {e["idIng"] for e in excl_fila if isinstance(e, dict) and "idIng" in e}
                else:
                    ids_excluidos = set()
                if id_ingrediente in ids_excluidos:
                    continue
                exclusiones_promo_fila = getattr(self, 'exclusiones_promo_por_fila', {}).get(fila, {})
                if isinstance(exclusiones_promo_fila, dict):
                    exclusiones_promo = exclusiones_promo_fila.get('exclusiones', {})
                else:
                    exclusiones_promo = {}
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT idProm FROM Promocion WHERE nomProm=?", (nombre_producto,))
                es_promocion = cursor.fetchone()
                if es_promocion:
                    id_promocion = es_promocion[0]
                    cursor.execute(
                        """
                        SELECT pp.idProd, pp.cantidadProdProm
                        FROM PromocionProd pp
                        WHERE pp.idProm = ?
                    """,
                        (id_promocion,),
                    )
                    for id_prod, cant_prod in cursor.fetchall():
                        unidades_data_prod = []
                        if isinstance(exclusiones_promo, dict) and str(id_prod) in exclusiones_promo:
                            raw = exclusiones_promo[str(id_prod)]
                            if isinstance(raw, list):
                                for item in raw:
                                    if isinstance(item, dict) and 'exclusiones' in item:
                                        unidades_data_prod.append(item)
                        total_unidades = cant_prod * cantidad
                        unidades_excluidas = 0
                        for ud in unidades_data_prod:
                            excls = ud.get('exclusiones', [])
                            if isinstance(excls, list):
                                if any(isinstance(e, dict) and e.get("idIng") == id_ingrediente for e in excls):
                                    unidades_excluidas += 1
                        unidades_activas = total_unidades - unidades_excluidas
                        if unidades_activas <= 0:
                            continue
                        cursor.execute(
                            """
                            SELECT cantidadIngNecesitada
                            FROM ProductosIngredientes
                            WHERE idProd = ? AND idIng = ?
                        """,
                            (id_prod, id_ingrediente),
                        )
                        resultado = cursor.fetchone()
                        if resultado:
                            cantidad_reservada += float(resultado[0] or 0) * unidades_activas
                else:
                    cursor.execute("SELECT idProd FROM Producto WHERE nomProd=?", (nombre_producto,))
                    r = cursor.fetchone()
                    if r:
                        id_producto = r[0]
                        cursor.execute(
                            """
                            SELECT cantidadIngNecesitada
                            FROM ProductosIngredientes
                            WHERE idProd = ? AND idIng = ?
                        """,
                            (id_producto, id_ingrediente),
                        )
                        resultado = cursor.fetchone()
                        if resultado:
                            cantidad_reservada += float(resultado[0] or 0) * cantidad
                conn.close()
        except Exception as e:
            print(f"Error al calcular ingredientes reservados: {e}")
            import traceback

            traceback.print_exc()
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
                nombre_producto = self._nombreRealDeFila(fila)
                cantidad_linea = int(self.tabla.item(fila, 0).text())
                excl_fila = self.exclusiones_por_fila.get(fila, [])
                ids_excluidos = {e["idIng"] for e in excl_fila}
                exclusiones_promo_fila = getattr(self, 'exclusiones_promo_por_fila', {}).get(fila, {})
                exclusiones_promo = exclusiones_promo_fila.get('exclusiones', {})
                cur.execute("SELECT idProm FROM Promocion WHERE nomProm=?", (nombre_producto,))
                prom = cur.fetchone()
                if prom:
                    id_prom = prom[0]
                    cur.execute(
                        """
                        SELECT pp.idProd, pp.cantidadProdProm
                        FROM PromocionProd pp
                        WHERE pp.idProm = ?
                    """,
                        (id_prom,),
                    )
                    for id_prod, cant_prod in cur.fetchall():
                        unidades_data_prod = []
                        if str(id_prod) in exclusiones_promo:
                            unidades_data_prod = exclusiones_promo[str(id_prod)]
                        total_unidades = cant_prod * cantidad_linea
                        cur.execute(
                            """
                            SELECT idIng, cantidadIngNecesitada
                            FROM ProductosIngredientes
                            WHERE idProd = ?
                        """,
                            (id_prod,),
                        )
                        for id_ing, cant_ing in cur.fetchall():
                            if id_ing in ids_excluidos:
                                continue
                            unidades_excluidas = sum(
                                1 for ud in unidades_data_prod if any(e["idIng"] == id_ing for e in ud['exclusiones'])
                            )
                            unidades_activas = total_unidades - unidades_excluidas
                            if unidades_activas <= 0:
                                continue
                            cant_ing_valor = float(cant_ing or 0)
                            if cant_ing_valor > 0:
                                delta = q2(cant_ing_valor * unidades_activas * signo)
                                cur.execute(
                                    """
                                    UPDATE Stock
                                    SET cantidadStock = MAX(0, ROUND(cantidadStock + ?, 2))
                                    WHERE idIng = ?
                                """,
                                    (delta, id_ing),
                                )
                else:
                    cur.execute("SELECT idProd FROM Producto WHERE nomProd=?", (nombre_producto,))
                    r = cur.fetchone()
                    if not r:
                        continue
                    id_prod = r[0]
                    cur.execute(
                        """
                        SELECT idIng, cantidadIngNecesitada
                        FROM ProductosIngredientes
                        WHERE idProd = ?
                    """,
                        (id_prod,),
                    )
                    for id_ing, cant_ing in cur.fetchall():
                        if id_ing in ids_excluidos:
                            continue
                        cant_ing_valor = float(cant_ing or 0)
                        if cant_ing_valor > 0:
                            delta = q2(cant_ing_valor * cantidad_linea * signo)
                            cur.execute(
                                """
                                UPDATE Stock
                                SET cantidadStock = MAX(0, ROUND(cantidadStock + ?, 2))
                                WHERE idIng = ?
                            """,
                                (delta, id_ing),
                            )
                    extras_fila = self.extras_por_fila.get(fila, [])
                    for extra in extras_fila:
                        cant_extra_valor = float(extra.get("cantidadExtra") or 0)
                        if cant_extra_valor > 0:
                            delta_extra = q2(cant_extra_valor * cantidad_linea * signo)
                            cur.execute(
                                """
                                UPDATE Stock
                                SET cantidadStock = MAX(0, ROUND(cantidadStock + ?, 2))
                                WHERE idIng = ?
                            """,
                                (delta_extra, extra["idIng"]),
                            )
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

    def agregarProductoTabla(self, nombre, cantidad, tipo, bandera, exclusiones=None, extras=None):
        if self.verificarBloqueo("agregar productos"):
            return
        exclusiones = exclusiones or []
        extras = extras or []
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        if bandera:
            self.cursor.execute("""SELECT precioVenta FROM Producto WHERE nomProd=?""", (nombre,))
            resultados = self.cursor.fetchone()
        else:
            self.cursor.execute("""SELECT precioProm FROM Promocion WHERE nomProm=?""", (nombre,))
            resultados = self.cursor.fetchone()
        precio_base = float(resultados[0])
        precio_extra_unitario = sum(float(e["precioExtra"]) * float(e["cantidadExtra"]) for e in extras)
        precio_unitario = precio_base + precio_extra_unitario
        excl_texto = self._textoExclusiones(exclusiones)
        extras_texto = self._textoExtras(extras)
        texto_completo = " | ".join(t for t in [excl_texto, extras_texto] if t)
        for row in range(self.tabla.rowCount()):
            excl_fila = self.exclusiones_por_fila.get(row, [])
            extras_fila = self.extras_por_fila.get(row, [])
            if not isinstance(excl_fila, list):
                continue
            ids_fila = set()
            for e in excl_fila:
                if isinstance(e, dict) and "idIng" in e:
                    ids_fila.add(e["idIng"])
            ids_nuevas = set()
            for e in exclusiones:
                if isinstance(e, dict) and "idIng" in e:
                    ids_nuevas.add(e["idIng"])
            mismo_excl = ids_fila == ids_nuevas
            mismo_extra = extras_fila == extras
            if (
                self.tabla.item(row, 1).text() == tipo
                and self.tabla.item(row, 2).data(Qt.UserRole) == nombre
                and mismo_excl
                and mismo_extra
            ):
                cant_actual = int(self.tabla.item(row, 0).text()) + cantidad
                self.tabla.item(row, 0).setText(str(cant_actual))
                self.tabla.item(row, 4).setText(f"{cant_actual * precio_unitario:.2f}")
                self.recalcularTotal()
                self.conn.close()
                return
        row = self.tabla.rowCount()
        self.tabla.insertRow(row)
        nombre_display = nombre if not texto_completo else f"{nombre}\n({texto_completo})"
        tooltip_cantidad = f"Cantidad: {cantidad}"
        tooltip_tipo = f"Tipo de consumo: {tipo}"
        tooltip_producto = "🖱 Haga clic para ver el detalle completo" + (
            f"\n({texto_completo})" if texto_completo else ""
        )
        tooltip_precio = f"Precio unitario: {precio_unitario:.2f} Bs"
        tooltip_subtotal = f"Subtotal: {cantidad * precio_unitario:.2f} Bs"
        item_cantidad = QTableWidgetItem(str(cantidad))
        item_cantidad.setTextAlignment(Qt.AlignCenter)
        item_cantidad.setToolTip(tooltip_cantidad)
        self.tabla.setItem(row, 0, item_cantidad)
        item_tipo = QTableWidgetItem(tipo)
        item_tipo.setTextAlignment(Qt.AlignCenter)
        item_tipo.setToolTip(tooltip_tipo)
        self.tabla.setItem(row, 1, item_tipo)
        item_nombre = QTableWidgetItem(nombre_display)
        item_nombre.setTextAlignment(Qt.AlignCenter)
        item_nombre.setData(Qt.UserRole, nombre)
        item_nombre.setToolTip(tooltip_producto)
        if texto_completo:
            item_nombre.setForeground(QColor("#c0392b"))
        self.tabla.setItem(row, 2, item_nombre)
        item_precio = QTableWidgetItem(f"{precio_unitario:.2f}")
        item_precio.setTextAlignment(Qt.AlignCenter)
        item_precio.setToolTip(tooltip_precio)
        self.tabla.setItem(row, 3, item_precio)
        total = cantidad * precio_unitario
        item_total = QTableWidgetItem(f"{total:.2f}")
        item_total.setTextAlignment(Qt.AlignCenter)
        item_total.setToolTip(tooltip_subtotal)
        self.tabla.setItem(row, 4, item_total)
        btn_container = QWidget()
        btn_container.setStyleSheet("background: transparent;")
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)
        btn = QPushButton("🗑️")
        btn.setFixedSize(90, 30)
        btn.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 6px; font-size: 14px; font-weight: bold; min-width: 90px; margin: 0px; padding: 0px; }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:pressed { background-color: #a93226; }
        """)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip("Eliminar producto")
        btn.clicked.connect(lambda _, r=row: self.eliminarFila(r))
        btn_layout.addWidget(btn, 0, Qt.AlignCenter)
        self.tabla.setCellWidget(row, 5, btn_container)
        self.exclusiones_por_fila[row] = exclusiones
        self.extras_por_fila[row] = extras
        self.tabla.setRowHeight(row, 60 if texto_completo else 50)
        self.tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.tabla.setColumnWidth(5, 110)
        self.recalcularTotal()
        self.conn.close()

    def recalcularTotal(self):
        totalVenta = 0.0
        for i in range(self.tabla.rowCount()):
            totalVenta += float(self.tabla.item(i, 4).text())
        self.totalVenta.setText(f"{totalVenta:.2f} Bs")

    def eliminarFila(self, row):
        if self.verificarBloqueo("eliminar productos"):
            return
        self.tabla.removeRow(row)
        nuevas_exclusiones = {}
        for idx, excl in self.exclusiones_por_fila.items():
            if idx < row:
                nuevas_exclusiones[idx] = excl
            elif idx > row:
                nuevas_exclusiones[idx - 1] = excl
        self.exclusiones_por_fila = nuevas_exclusiones
        nuevos_extras = {}
        for idx, extra in self.extras_por_fila.items():
            if idx < row:
                nuevos_extras[idx] = extra
            elif idx > row:
                nuevos_extras[idx - 1] = extra
        self.extras_por_fila = nuevos_extras
        if hasattr(self, 'exclusiones_promo_por_fila'):
            nuevas_exclusiones_promo = {}
            for idx, excl in self.exclusiones_promo_por_fila.items():
                if idx < row:
                    nuevas_exclusiones_promo[idx] = excl
                elif idx > row:
                    nuevas_exclusiones_promo[idx - 1] = excl
            self.exclusiones_promo_por_fila = nuevas_exclusiones_promo
        for i in range(self.tabla.rowCount()):
            btn_container = self.tabla.cellWidget(i, 5)
            if btn_container is None:
                continue
            btn_layout = btn_container.layout()
            if btn_layout and btn_layout.count() > 0:
                btn = btn_layout.itemAt(0).widget()
                if btn and isinstance(btn, QPushButton):
                    try:
                        btn.clicked.disconnect()
                    except Exception:
                        pass
                    btn.clicked.connect(lambda _, r=i: self.eliminarFila(r))
        self.recalcularTotal()

    def mostrarDetalleFilaPedido(self, row, column):
        if column != 2:
            return
        item_nombre = self.tabla.item(row, 2)
        if item_nombre is None:
            return
        nombre = item_nombre.data(Qt.UserRole) or item_nombre.text().split("\n")[0]
        item_tipo = self.tabla.item(row, 1)
        item_cantidad = self.tabla.item(row, 0)
        item_precio = self.tabla.item(row, 3)
        item_subtotal = self.tabla.item(row, 4)
        if not (item_tipo and item_cantidad and item_precio and item_subtotal):
            return
        tipo = item_tipo.text()
        cantidad = item_cantidad.text()
        precio_unitario = item_precio.text()
        subtotal = item_subtotal.text()

        es_promo = hasattr(self, 'exclusiones_promo_por_fila') and row in self.exclusiones_promo_por_fila

        dialog = QDialog(self)
        dialog.setWindowTitle("Detalle del producto")
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
        subtitulo = QLabel("Promoción" if es_promo else "Producto")
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

        def fila_info(etiqueta, valor):
            w = QWidget()
            l = QHBoxLayout(w)
            l.setContentsMargins(0, 0, 0, 0)
            lbl1 = QLabel(f"<b>{etiqueta}:</b>")
            lbl1.setStyleSheet("font-size: 14px;")
            lbl2 = QLabel(str(valor))
            lbl2.setStyleSheet("font-size: 14px;")
            lbl2.setAlignment(Qt.AlignRight)
            l.addWidget(lbl1)
            l.addStretch()
            l.addWidget(lbl2)
            return w

        cuerpo_layout.addWidget(fila_info("Cantidad", cantidad))
        cuerpo_layout.addWidget(fila_info("Tipo de consumo", tipo))
        cuerpo_layout.addWidget(fila_info("Precio unitario", f"{precio_unitario} Bs"))
        cuerpo_layout.addWidget(fila_info("Subtotal", f"{subtotal} Bs"))

        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setStyleSheet("background-color: #e2e8f0; margin-top: 4px; margin-bottom: 4px;")
        cuerpo_layout.addWidget(separador)

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

        if es_promo:
            datos_promo = self.exclusiones_promo_por_fila.get(row, {})
            productos_promo_lista = datos_promo.get('productos_promo', [])
            excl_por_producto = datos_promo.get('exclusiones', {})
            extras_por_producto = datos_promo.get('extras', {})
            cantidad_combos = datos_promo.get('cantidad_promociones', 1)

            nombres_por_id = {str(p['idProd']): p['nombre'] for p in productos_promo_lista}
            unidades_por_id = {str(p['idProd']): p.get('cantidad', 1) * cantidad_combos for p in productos_promo_lista}

            ids_con_personalizacion = sorted(
                set(excl_por_producto.keys()) | set(extras_por_producto.keys()), key=lambda x: nombres_por_id.get(x, x)
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

                for id_prod_str in ids_con_personalizacion:
                    nombre_prod = nombres_por_id.get(id_prod_str, f"Producto {id_prod_str}")
                    total_unidades_prod = unidades_por_id.get(id_prod_str, "?")

                    prod_frame = QFrame()
                    prod_frame.setStyleSheet("""
                        QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; }
                    """)
                    prod_layout = QVBoxLayout(prod_frame)
                    prod_layout.setContentsMargins(12, 10, 12, 10)
                    prod_layout.setSpacing(6)

                    prod_titulo = QLabel(f"🍔 {nombre_prod}  ({total_unidades_prod} unidad(es) en total)")
                    prod_titulo.setStyleSheet(
                        "font-weight: bold; font-size: 15px; color: #2c3e50; background: transparent; border: none;"
                    )
                    prod_titulo.setWordWrap(True)
                    prod_layout.addWidget(prod_titulo)

                    excl_unidades = {u['unidad']: u['exclusiones'] for u in excl_por_producto.get(id_prod_str, [])}
                    extra_unidades = {u['unidad']: u['extras'] for u in extras_por_producto.get(id_prod_str, [])}
                    todas_unidades_idx = sorted(set(excl_unidades.keys()) | set(extra_unidades.keys()))

                    for idx_u in todas_unidades_idx:
                        lbl_unidad = QLabel(f"Unidad #{idx_u + 1}")
                        lbl_unidad.setStyleSheet(
                            "font-weight: 600; font-size: 13px; color: #7f8c8d; background: transparent; border: none; margin-top: 4px;"
                        )
                        prod_layout.addWidget(lbl_unidad)

                        if excl_unidades.get(idx_u):
                            nombres_excl = ", ".join(e['nomIng'] for e in excl_unidades[idx_u])
                            lbl_e = QLabel(f"✗  Sin: {nombres_excl}")
                            lbl_e.setWordWrap(True)
                            lbl_e.setStyleSheet("""
                                color: #c0392b; font-size: 14px; font-weight: 600; background: transparent;
                                border: none; padding-left: 12px;
                            """)
                            prod_layout.addWidget(lbl_e)

                        if extra_unidades.get(idx_u):
                            nombres_extra = ", ".join(
                                f"+{e['cantidadExtra']} {e['nomIng']}" for e in extra_unidades[idx_u]
                            )
                            lbl_x = QLabel(f"➕  Extra: {nombres_extra}")
                            lbl_x.setWordWrap(True)
                            lbl_x.setStyleSheet("""
                                color: #27ae60; font-size: 14px; font-weight: 600; background: transparent;
                                border: none; padding-left: 12px;
                            """)
                            prod_layout.addWidget(lbl_x)

                    if isinstance(total_unidades_prod, int):
                        normales_prod = total_unidades_prod - len(todas_unidades_idx)
                        if normales_prod > 0:
                            lbl_normal = QLabel(f"{normales_prod} unidad(es) — sin ninguna personalización")
                            lbl_normal.setWordWrap(True)
                            lbl_normal.setStyleSheet("""
                                color: #7f8c8d; font-size: 13px; font-style: italic; background: transparent;
                                border: none; padding-left: 12px; margin-top: 4px;
                            """)
                            prod_layout.addWidget(lbl_normal)

                    cuerpo_layout.addWidget(prod_frame)

                unidades_sin_cambios = [
                    p for p in productos_promo_lista if str(p['idProd']) not in ids_con_personalizacion
                ]
                if unidades_sin_cambios:
                    nombres_sin_cambios = ", ".join(p['nombre'] for p in unidades_sin_cambios)
                    lbl_resto = QLabel(
                        f"El resto de productos de la promoción ({nombres_sin_cambios}) no tienen ninguna personalización."
                    )
                    lbl_resto.setWordWrap(True)
                    lbl_resto.setStyleSheet("color: #7f8c8d; font-size: 13px; font-style: italic; margin-top: 6px;")
                    cuerpo_layout.addWidget(lbl_resto)
        else:
            excl = self.exclusiones_por_fila.get(row, [])
            extras = self.extras_por_fila.get(row, [])
            texto_excl = ", ".join(e['nomIng'] for e in excl) if excl else ""
            texto_extra = ", ".join(f"+{e['cantidadExtra']} {e['nomIng']}" for e in extras) if extras else ""

            if not texto_excl and not texto_extra:
                lbl_vacio = QLabel("Sin personalización — todos los ingredientes originales")
                lbl_vacio.setWordWrap(True)
                lbl_vacio.setStyleSheet("""
                    color: #27ae60; font-size: 14px; font-weight: 500; padding: 8px 12px;
                    background-color: #eafaf1; border-radius: 6px; border-left: 4px solid #2ecc71;
                """)
                cuerpo_layout.addWidget(lbl_vacio)
            else:
                if texto_excl:
                    bloque_personalizacion(
                        f"Ingredientes excluidos (aplica a las {cantidad} unidad(es)):",
                        texto_excl,
                        "#fdecea",
                        "#c0392b",
                        "#e74c3c",
                    )
                if texto_extra:
                    bloque_personalizacion(
                        f"Ingredientes extra (aplica a las {cantidad} unidad(es)):",
                        texto_extra,
                        "#eafaf1",
                        "#27ae60",
                        "#2ecc71",
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

    def _nombreRealDeFila(self, fila):
        item = self.tabla.item(fila, 2)
        if item:
            dato = item.data(Qt.UserRole)
            return dato if dato else item.text().split("\n")[0]
        return ""

    def mostrarEmpleados(self):
        if self.verificarBloqueo("ver empleados"):
            return
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
        if self.verificarBloqueo("ver mesas"):
            return
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
                }}
                QPushButton:pressed {{
                    background-color: {self._darken_color(color, 0.3)};
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
        color = QColor(hex_color)
        return color.darker(int(100 + factor * 100)).name()

    def cargarSecciones(self, idSeccion):
        if self.verificarBloqueo("cargar secciones"):
            return
        self.idSeccionActual = idSeccion
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
            btn.setFixedSize(150, 230)
            btn.setStyleSheet("""
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
            vbox = QVBoxLayout(btn)
            vbox.setSpacing(2)
            labImg = QLabel()
            labImg.setPixmap(pix.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            labImg.setAlignment(Qt.AlignCenter)
            vbox.addWidget(labImg)
            label = QLabel(str(idMesa))
            label.setAlignment(Qt.AlignCenter)
            vbox.addWidget(label)
            if not disponible:
                self.cursor.execute(
                    """SELECT E.aliasEmp
                                    FROM DetallesVenta DV
                                    INNER JOIN Empleado E ON DV.idMeseroActual=E.codEmp
                                    INNER JOIN Venta V ON DV.fechaRegVenta=V.fechaReg
                                    WHERE idMesa=? AND idSeccion=?
                                    ORDER BY DV.fechaRegDetalleVenta
                                    DESC LIMIT 1""",
                    (idMesa, idSeccion),
                )
                resultado_mesero = self.cursor.fetchone()
                meseroAsignado = resultado_mesero[0] if resultado_mesero else "Sin asignar"
                label2 = QLabel(meseroAsignado)
                label2.setStyleSheet("QLabel {color: #2c3e50; font-size: 12px; font-weight: 500; }")
                label2.setAlignment(Qt.AlignCenter)
                vbox.addWidget(label2)
                botonPedidos = QPushButton("Ver Pedidos")
                botonPedidos.setFixedHeight(25)
                botonPedidos.setStyleSheet("""
                    QPushButton{
                        background-color: #3498db;
                        color: white;
                        border-radius: 4px;
                        padding: 3px;
                        font-size: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover{ background-color: #2980b9; }
                """)
                botonPedidos.setCursor(Qt.PointingHandCursor)
                botonPedidos.clicked.connect(
                    lambda checked, idSecc=idSeccion, m=idMesa: self.mostrarDetallesVentaMesa(m, idSecc)
                )
                vbox.addWidget(botonPedidos)
                botonCobrar = QPushButton("Cobrar")
                botonCobrar.setFixedHeight(25)
                botonCobrar.setStyleSheet("""
                    QPushButton{
                        background-color: #2ecc71;
                        color: white;
                        border-radius: 4px;
                        padding: 3px;
                        font-size: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover{ background-color: #27ae60; }
                """)
                botonCobrar.setCursor(Qt.PointingHandCursor)
                botonCobrar.clicked.connect(lambda checked, idSecc=idSeccion, m=idMesa: self.cobrarMesa(m, idSecc))
                vbox.addWidget(botonCobrar)
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

    def mostrarDetallesVentaMesa(self, numMesa, idSeccion):
        self.fecha_actual_dialogo = None
        self.numMesa_actual = numMesa
        self.idSeccion_actual = idSeccion
        self.fila_expandida = -1
        if self.dialogo_detalles is not None:
            try:
                self.dialogo_detalles.close()
                self.dialogo_detalles.deleteLater()
            except Exception:
                pass
            self.dialogo_detalles = None
        if self.timer_unico is not None:
            try:
                self.timer_unico.stop()
                self.timer_unico.deleteLater()
            except Exception:
                pass
            self.timer_unico = None

        self.dialogo_detalles = QDialog(self)
        self.dialogo_detalles.setWindowTitle(f"Pedidos Pendientes - Mesa {numMesa}")
        self.dialogo_detalles.setFixedSize(1400, 800)
        layoutPrincipal = QVBoxLayout()
        self.dialogo_detalles.setLayout(layoutPrincipal)

        header = QLabel(f"PEDIDOS PENDIENTES - MESA {numMesa}")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 10px;
                text-align: center;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        layoutPrincipal.addWidget(header)

        self.tabla_pedidos_pendientes = QTableWidget()
        self.tabla_pedidos_pendientes.setColumnCount(5)
        self.tabla_pedidos_pendientes.setHorizontalHeaderLabels(["Fecha", "Hora", "Tiempo", "Detalles", "Accion"])
        self.tabla_pedidos_pendientes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_pedidos_pendientes.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabla_pedidos_pendientes.verticalHeader().setVisible(True)
        self.tabla_pedidos_pendientes.verticalHeader().setDefaultSectionSize(70)
        self.tabla_pedidos_pendientes.verticalHeader().setMinimumSectionSize(60)
        self.tabla_pedidos_pendientes.setSelectionMode(QTableWidget.NoSelection)
        self.tabla_pedidos_pendientes.setFocusPolicy(Qt.NoFocus)
        self.tabla_pedidos_pendientes.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_pedidos_pendientes.setAlternatingRowColors(True)
        self.tabla_pedidos_pendientes.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                gridline-color: #e2e8f0;
                font-size: 14px;
            }
            QTableWidget::item { padding: 8px 8px; border-bottom: 1px solid #f1f5f9; }
            QTableWidget::item:hover { background-color: #f8fafc; }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 14px 8px;
                border: none;
                font-weight: bold;
                font-size: 15px;
            }
            QScrollBar:vertical { border: none; background: #f8fafc; width: 14px; border-radius: 7px; }
            QScrollBar::handle:vertical { background: #cbd5e1; min-height: 30px; border-radius: 7px; margin: 2px; }
            QScrollBar::handle:vertical:hover { background: #94a3b8; }
        """)
        layoutPrincipal.addWidget(self.tabla_pedidos_pendientes)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT fechaReg, numVenta
            FROM Venta
            WHERE idMesa = ? AND idSeccion = ?
            ORDER BY fechaReg DESC
            LIMIT 1
        """,
            (numMesa, idSeccion),
        )
        venta = cursor.fetchone()
        if not venta:
            QMessageBox.information(self, "Información", "No hay pedidos para esta mesa.")
            conn.close()
            return

        fechaRegVenta, numVenta = venta

        cursor.execute(
            """
            SELECT DISTINCT fechaRegDetalleVenta
            FROM DetallesVenta
            WHERE numVenta = ? AND fechaRegVenta = ? AND estadoDetalleVenta = 'Preparacion'
            ORDER BY fechaRegDetalleVenta DESC
        """,
            (numVenta, fechaRegVenta),
        )
        fechas_detalles = cursor.fetchall()

        self.fechas_por_fila = {}
        for fecha_tuple in fechas_detalles:
            fecha_detalle = fecha_tuple[0]
            fila = self.tabla_pedidos_pendientes.rowCount()
            self.tabla_pedidos_pendientes.setRowCount(fila + 1)
            fechaCompleta = datetime.strptime(fecha_detalle, "%Y-%m-%d %H:%M:%S.%f")
            self.fechas_por_fila[fila] = fechaCompleta
            fechaMostrada = fechaCompleta.strftime("%d/%m/%Y")
            itemFecha = QTableWidgetItem(fechaMostrada)
            itemFecha.setTextAlignment(Qt.AlignCenter)
            itemFecha.setFont(QFont("Segoe UI", 12))
            itemFecha.setFlags(itemFecha.flags() & ~Qt.ItemIsSelectable)
            self.tabla_pedidos_pendientes.setItem(fila, 0, itemFecha)

            hora = fechaCompleta.strftime("%I:%M %p")
            itemHora = QTableWidgetItem(hora)
            itemHora.setTextAlignment(Qt.AlignCenter)
            itemHora.setFont(QFont("Segoe UI", 12))
            itemHora.setFlags(itemHora.flags() & ~Qt.ItemIsSelectable)
            self.tabla_pedidos_pendientes.setItem(fila, 1, itemHora)

            fechaActual = datetime.now()
            diferencia = (fechaActual - fechaCompleta).total_seconds()
            minutos = int(diferencia // 60)
            estado_tiempo = "Reciente" if minutos < 10 else "En espera" if minutos < 20 else "Urgente"
            itemDiferencia = QTableWidgetItem(f"{estado_tiempo} - Hace {minutos} min")
            itemDiferencia.setTextAlignment(Qt.AlignCenter)
            itemDiferencia.setFont(QFont("Segoe UI", 12, QFont.Bold))
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
            self.tabla_pedidos_pendientes.setItem(fila, 2, itemDiferencia)

            cursor.execute(
                """
                SELECT
                    Dt.idDetalleVenta,
                    COALESCE(P.nomProd, Prom.nomProm) as nombre,
                    Dt.cantidadProdDet,
                    Dt.tipoConsumo,
                    Dt.cantidadMarcado,
                    CASE WHEN Dt.idProd IS NOT NULL THEN 'producto' ELSE 'promocion' END as tipo_producto,
                    Dt.idProm
                FROM DetallesVenta Dt
                LEFT JOIN Producto P ON P.idProd = Dt.idProd
                LEFT JOIN Promocion Prom ON Prom.idProm = Dt.idProm
                WHERE Dt.fechaRegDetalleVenta = ?
                ORDER BY Dt.tipoConsumo, nombre
            """,
                (fecha_detalle,),
            )
            productos_detalle = cursor.fetchall()

            exclusiones_por_detalle = {}
            for row_det in productos_detalle:
                id_det = row_det[0]
                cursor.execute(
                    """
                    SELECT nomIng FROM DetallesVentaExclusiones WHERE idDetalleVenta=?
                """,
                    (id_det,),
                )
                excls = [r[0] for r in cursor.fetchall()]
                if excls:
                    exclusiones_por_detalle[id_det] = excls

            container_widget = QWidget()
            container_layout = QVBoxLayout(container_widget)
            container_layout.setContentsMargins(8, 6, 8, 6)
            container_layout.setSpacing(4)

            header_widget = QWidget()
            header_layout = QHBoxLayout(header_widget)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(8)

            preview_widget = QWidget()
            preview_layout = QVBoxLayout(preview_widget)
            preview_layout.setContentsMargins(0, 0, 0, 0)
            preview_layout.setSpacing(2)

            tiene_local = False
            tiene_llevar = False
            productos_mostrados = []

            for id_det, nombre, cantidad, tipo, marcado, tipo_prod, id_prom in productos_detalle:
                if tipo_prod == 'promocion':
                    cursor.execute(
                        """
                        SELECT pp.idProd, p.nomProd, pp.cantidadProdProm
                        FROM PromocionProd pp
                        JOIN Producto p ON pp.idProd = p.idProd
                        WHERE pp.idProm = ?
                    """,
                        (id_prom,),
                    )
                    productos_promo = cursor.fetchall()

                    for id_prod_p, nom_prod_p, cant_prod_p in productos_promo:
                        cursor.execute(
                            """
                            SELECT COUNT(*) FROM DetallesVentaUnidades
                            WHERE idDetalleVenta = ? AND idProd = ?
                        """,
                            (id_det, id_prod_p),
                        )
                        total_unidades = cursor.fetchone()[0]
                        cursor.execute(
                            """
                            SELECT COUNT(*) FROM DetallesVentaUnidades
                            WHERE idDetalleVenta = ? AND idProd = ? AND marcado = 1
                        """,
                            (id_det, id_prod_p),
                        )
                        marcadas_unidades = cursor.fetchone()[0]
                        restante = total_unidades - marcadas_unidades

                        if restante > 0:
                            cursor.execute(
                                """
                                SELECT DISTINCT nomIng FROM DetallesVentaExclusionesPromo
                                WHERE idDetalleVenta=? AND idProd=?
                            """,
                                (id_det, id_prod_p),
                            )
                            excl_rows_promo = cursor.fetchall()
                            excl_texto_promo = (
                                ("sin: " + ", ".join(sorted(r[0] for r in excl_rows_promo))) if excl_rows_promo else ""
                            )

                            cursor.execute(
                                """
                                SELECT nomIng, cantidadExtra FROM DetallesVentaExtras
                                WHERE idDetalleVenta=? AND idProd=?
                            """,
                                (id_det, id_prod_p),
                            )
                            extra_rows_promo = cursor.fetchall()
                            extras_texto_promo = (
                                ("extra: " + ", ".join(f"+{c} {n}" for n, c in extra_rows_promo))
                                if extra_rows_promo
                                else ""
                            )

                            personalizacion_promo = " | ".join(t for t in [excl_texto_promo, extras_texto_promo] if t)

                            productos_mostrados.append(
                                {
                                    'nombre': nom_prod_p,
                                    'tipo': tipo,
                                    'restante': restante,
                                    'total': total_unidades,
                                    'marcado': marcadas_unidades,
                                    'personalizacion': personalizacion_promo,
                                }
                            )
                            if tipo == "Local":
                                tiene_local = True
                            else:
                                tiene_llevar = True
                else:
                    restante = cantidad - marcado
                    if restante > 0:
                        cursor.execute("SELECT nomIng FROM DetallesVentaExclusiones WHERE idDetalleVenta=?", (id_det,))
                        excl_rows = cursor.fetchall()
                        excl_texto_prod = ("sin: " + ", ".join(r[0] for r in excl_rows)) if excl_rows else ""
                        extras_texto_prod = self._obtenerExtrasTextoPorDetalle(cursor, id_det)
                        personalizacion = " | ".join(t for t in [excl_texto_prod, extras_texto_prod] if t)
                        productos_mostrados.append(
                            {
                                'nombre': nombre,
                                'tipo': tipo,
                                'restante': restante,
                                'total': cantidad,
                                'marcado': marcado,
                                'personalizacion': personalizacion,
                            }
                        )
                        if tipo == "Local":
                            tiene_local = True
                        else:
                            tiene_llevar = True

            preview_text = ""
            for i, prod in enumerate(productos_mostrados[:3]):
                tipo_texto = "[L]" if prod['tipo'] == "Local" else "[P]"
                preview_text += f"{tipo_texto} {prod['restante']}/{prod['total']} {prod['nombre'][:15]}  "
            if len(productos_mostrados) > 3:
                preview_text += f"... (+{len(productos_mostrados) - 3})"

            preview_label = QLabel(preview_text if preview_text else "Completado")
            preview_label.setStyleSheet(
                "font-size: 13px; color: #2c3e50; font-weight: 500; border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px;"
            )
            preview_layout.addWidget(preview_label)
            header_layout.addWidget(preview_widget)
            header_layout.addStretch()
            expand_icon = QLabel("v")
            expand_icon.setStyleSheet("font-size: 16px; color: #7f8c8d; padding: 2px 8px;")
            header_layout.addWidget(expand_icon)
            container_layout.addWidget(header_widget)

            expandido_widget = QWidget()
            expandido_widget.setVisible(False)
            expandido_layout = QVBoxLayout(expandido_widget)
            expandido_layout.setContentsMargins(12, 8, 8, 4)
            expandido_layout.setSpacing(6)

            for prod in productos_mostrados:
                if prod['restante'] > 0:
                    tipo_texto = "[Local]" if prod['tipo'] == "Local" else "[Llevar]"
                    item_widget = QWidget()
                    item_layout = QVBoxLayout(item_widget)
                    item_layout.setContentsMargins(0, 0, 0, 0)
                    item_layout.setSpacing(2)

                    fila_prod = QWidget()
                    fila_prod_layout = QHBoxLayout(fila_prod)
                    fila_prod_layout.setContentsMargins(0, 0, 0, 0)
                    fila_prod_layout.setSpacing(8)

                    icono_label = QLabel(f"{tipo_texto}")
                    icono_label.setStyleSheet("font-size: 12px; min-width: 70px; font-weight: bold;")
                    fila_prod_layout.addWidget(icono_label)

                    texto_label = QLabel(f"{prod['restante']}/{prod['total']}  x  {prod['nombre']}")
                    texto_label.setWordWrap(True)
                    texto_label.setStyleSheet("font-size: 12px; padding: 2px 0px; color: #2c3e50;")
                    fila_prod_layout.addWidget(texto_label, 1)
                    item_layout.addWidget(fila_prod)

                    if prod.get('personalizacion'):
                        personalizacion_label = QLabel(f"    {prod['personalizacion']}")
                        personalizacion_label.setWordWrap(True)
                        personalizacion_label.setStyleSheet(
                            "font-size: 11px; padding: 0px 0px 2px 0px; color: #c0392b; font-weight: 500;"
                        )
                        item_layout.addWidget(personalizacion_label)

                    expandido_layout.addWidget(item_widget)

            expandido_layout.addStretch()
            container_layout.addWidget(expandido_widget)

            color_fondo = "#ffffff"
            if tiene_llevar and tiene_local:
                color_fondo = "#fef9e7"
            elif tiene_llevar:
                color_fondo = "#fdedec"
            else:
                color_fondo = "#e6f2ff"

            container_widget.setStyleSheet(f"QWidget {{ background-color: {color_fondo}; border-radius: 6px; }}")
            container_widget.setCursor(Qt.PointingHandCursor)

            def make_toggle_function(f, icon_label):
                def toggle(event):
                    self.toggle_fila(f, icon_label)

                return toggle

            container_widget.mousePressEvent = make_toggle_function(fila, expand_icon)
            self.tabla_pedidos_pendientes.setCellWidget(fila, 3, container_widget)

            btn_marcar = QPushButton("Marcar Pendientes")
            btn_marcar.setStyleSheet("""
                QPushButton { background-color: #f39c12; color: white; border: none;
                    border-radius: 6px; padding: 8px 16px; font-weight: bold; font-size: 13px; }
                QPushButton:hover { background-color: #e67e22; }
            """)
            btn_marcar.clicked.connect(
                lambda checked, fecha=fecha_detalle: self.mostrarCardsParaMarcar(fecha, numMesa, idSeccion)
            )
            self.tabla_pedidos_pendientes.setCellWidget(fila, 4, btn_marcar)
            self.tabla_pedidos_pendientes.setRowHeight(fila, 70)

        conn.close()

        if self.tabla_pedidos_pendientes.rowCount() == 0:
            self.tabla_pedidos_pendientes.setRowCount(1)
            item = QTableWidgetItem("No hay pedidos pendientes para esta mesa")
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(QFont("Segoe UI", 14, QFont.Bold))
            item.setForeground(QColor("#7f8c8d"))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.tabla_pedidos_pendientes.setSpan(0, 0, 1, 5)
            self.tabla_pedidos_pendientes.setItem(0, 0, item)

        self.timer_unico = QTimer(self.dialogo_detalles)

        def actualizar_todas_las_filas():
            if self.dialogo_detalles and self.dialogo_detalles.isVisible():
                fecha_actual = datetime.now()
                for fila, fecha_completa in self.fechas_por_fila.items():
                    diferencia = (fecha_actual - fecha_completa).total_seconds()
                    minutos = int(diferencia // 60)
                    estado_tiempo = "Reciente" if minutos < 10 else "En espera" if minutos < 20 else "Urgente"
                    item = QTableWidgetItem(f"{estado_tiempo} - Hace {minutos} min")
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFont(QFont("Segoe UI", 12, QFont.Bold))
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
                    self.tabla_pedidos_pendientes.setItem(fila, 2, item)

        self.timer_unico.timeout.connect(actualizar_todas_las_filas)
        self.timer_unico.start(60000)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border: none; border-radius: 8px;
                padding: 12px 40px; font-size: 16px; font-weight: bold; margin-top: 10px; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        btn_cerrar.setCursor(Qt.PointingHandCursor)
        btn_cerrar.clicked.connect(self.cerrarDialogoDetalles)
        layoutPrincipal.addWidget(btn_cerrar, alignment=Qt.AlignCenter)

        self.dialogo_detalles.exec_()

    def cerrarDialogoDetalles(self):
        if self.timer_unico is not None:
            try:
                self.timer_unico.stop()
                self.timer_unico.deleteLater()
            except Exception:
                pass
            self.timer_unico = None
        if self.dialogo_detalles:
            self.dialogo_detalles.accept()
            self.dialogo_detalles = None

    def toggle_fila(self, fila, icon_label):
        if self.fila_expandida == fila:
            container = self.tabla_pedidos_pendientes.cellWidget(fila, 3)
            if container:
                expandido = container.layout().itemAt(1).widget()
                if expandido:
                    expandido.setVisible(False)
                icon_label.setText("v")
                self.tabla_pedidos_pendientes.setRowHeight(fila, 70)
            self.fila_expandida = -1
        else:
            if self.fila_expandida != -1:
                old_container = self.tabla_pedidos_pendientes.cellWidget(self.fila_expandida, 3)
                if old_container:
                    old_expandido = old_container.layout().itemAt(1).widget()
                    if old_expandido:
                        old_expandido.setVisible(False)
                    old_header = old_container.layout().itemAt(0).widget()
                    if old_header:
                        old_icon = old_header.layout().itemAt(2).widget()
                        if old_icon:
                            old_icon.setText("v")
                    self.tabla_pedidos_pendientes.setRowHeight(self.fila_expandida, 70)
            container = self.tabla_pedidos_pendientes.cellWidget(fila, 3)
            if container:
                expandido = container.layout().itemAt(1).widget()
                if expandido:
                    expandido.setVisible(True)
                    expandido.show()
                    icon_label.setText("^")
                    altura_expandido = expandido.sizeHint().height()
                    nueva_altura = 70 + altura_expandido + 15
                    self.tabla_pedidos_pendientes.setRowHeight(fila, nueva_altura)
            self.fila_expandida = fila

    def crearCardProducto(
        self, nombre, total, listos, faltan, entradas_str, tipo, exclusiones=None, excl_key=None, extras_texto=""
    ):
        exclusiones = exclusiones or []
        excl_key = excl_key or ()
        card = QFrame()
        color_fondo = "#e6f2ff" if tipo == "Local" else "#fdedec"
        color_borde = "#3498db" if tipo == "Local" else "#e74c3c"
        card.setStyleSheet(
            f"QFrame{{background-color:{color_fondo};border:2px solid {color_borde};border-radius:10px;padding:10px;}}"
        )
        card_layout = QVBoxLayout(card)

        titulo_label = QLabel(f"<b>{nombre}</b>")
        titulo_label.setStyleSheet("font-size:14px;font-weight:bold;color:#2c3e50;")
        titulo_label.setWordWrap(True)
        card_layout.addWidget(titulo_label)

        if exclusiones:
            excl_label = QLabel("sin: " + ", ".join(exclusiones))
            excl_label.setStyleSheet(
                "QLabel{font-size:12px;color:#c0392b;font-weight:bold;padding:4px 8px;background-color:#fdecea;border-radius:4px;border-left:3px solid #e74c3c;}"
            )
            excl_label.setWordWrap(True)
            card_layout.addWidget(excl_label)

        if extras_texto:
            extras_label = QLabel(extras_texto)
            extras_label.setStyleSheet(
                "QLabel{font-size:12px;color:#27ae60;font-weight:bold;padding:4px 8px;background-color:#eafaf1;border-radius:4px;border-left:3px solid #2ecc71;}"
            )
            extras_label.setWordWrap(True)
            card_layout.addWidget(extras_label)

        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        lbl_total = QLabel(f"<b>Total:</b> {total}")
        lbl_listos = QLabel(f"<b>Listos:</b> {listos}")
        lbl_faltan = QLabel(f"<b>Faltan:</b> {faltan}")
        info_layout.addWidget(lbl_total)
        info_layout.addWidget(lbl_listos)
        info_layout.addWidget(lbl_faltan)
        info_layout.addStretch()
        card_layout.addWidget(info_widget)

        progreso = QProgressBar()
        progreso.setMaximum(max(total, 1))
        progreso.setValue(listos)
        progreso.setFormat(f"{listos}/{total}")
        progreso.setFixedHeight(20)
        color_chunk = "#65c0fc" if tipo == "Local" else "#e87d72"
        progreso.setStyleSheet(
            f"QProgressBar{{border:1px solid #bbb;border-radius:5px;text-align:center;}}QProgressBar::chunk{{background-color:{color_chunk};border-radius:5px;}}"
        )
        card_layout.addWidget(progreso)

        botones = QHBoxLayout()
        btn_menos = QPushButton("-1")
        btn_menos.setFixedSize(50, 37)
        btn_menos.setStyleSheet(
            "QPushButton{background-color:#e74c3c;color:white;border-radius:4px;font-weight:bold;font-size:12px;padding:0px;margin:0px;min-width:50px;}QPushButton:hover{background-color:#c0392b;}"
        )
        btn_mas = QPushButton("+1")
        btn_mas.setFixedSize(50, 37)
        btn_mas.setStyleSheet(
            "QPushButton{background-color:#3498db;color:white;border-radius:4px;font-weight:bold;font-size:12px;padding:0px;margin:0px;min-width:50px;}QPushButton:hover{background-color:#2980b9;}"
        )
        btn_todos = QPushButton("Todos")
        btn_todos.setFixedSize(40, 37)
        btn_todos.setStyleSheet(
            "QPushButton{background-color:#2ecc71;color:white;border-radius:4px;font-weight:bold;font-size:12px;min-width:40px;}QPushButton:hover{background-color:#27ae60;}"
        )

        btn_menos.clicked.connect(
            lambda _, e=entradas_str, c=card, t=total, n=nombre, tp=tipo, ek=excl_key: (
                self.actualizarProgresoConResumen(e, -1, c, t, n, tp, False, ek)
            )
        )
        btn_mas.clicked.connect(
            lambda _, e=entradas_str, c=card, t=total, n=nombre, tp=tipo, ek=excl_key: (
                self.actualizarProgresoConResumen(e, 1, c, t, n, tp, False, ek)
            )
        )
        btn_todos.clicked.connect(
            lambda _, e=entradas_str, c=card, t=total, n=nombre, tp=tipo, ek=excl_key: (
                self.actualizarProgresoConResumen(e, t, c, t, n, tp, True, ek)
            )
        )

        botones.addWidget(btn_menos)
        botones.addWidget(btn_mas)
        botones.addWidget(btn_todos)
        botones.addStretch()
        card_layout.addLayout(botones)
        return card

    def mostrarCardsParaMarcar(self, fecha_detalle, numMesa, idSeccion):
        self.fecha_actual_dialogo = fecha_detalle
        self.actualizar_al_cerrar = False
        if self.dialogo_cards is not None:
            try:
                self.dialogo_cards.close()
                self.dialogo_cards.deleteLater()
            except Exception:
                pass
        self.dialogo_cards = QDialog(self.dialogo_detalles)
        self.dialogo_cards.setWindowTitle(f"Marcar Productos - Mesa {numMesa}")
        self.dialogo_cards.setFixedSize(1400, 800)
        layout = QVBoxLayout(self.dialogo_cards)
        header = QLabel(f"MARCAR PRODUCTOS PENDIENTES - Mesa {numMesa}")
        header.setStyleSheet(
            "QLabel { font-size: 20px; font-weight: bold; color: white; padding: 15px; background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #f39c12,stop:1 #e67e22); border-radius: 8px; }"
        )
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(20)
        local_widget = QWidget()
        local_layout = QVBoxLayout(local_widget)
        local_label = QLabel("PRODUCTOS LOCAL")
        local_label.setStyleSheet(
            "QLabel{font-size:18px;font-weight:bold;color:white;background-color:#3498db;padding:10px;border-radius:6px;}"
        )
        local_label.setAlignment(Qt.AlignCenter)
        local_layout.addWidget(local_label)
        local_scroll = QScrollArea()
        local_scroll.setWidgetResizable(True)
        local_scroll.setStyleSheet("QScrollArea{border:1px solid #3498db;border-radius:6px;}")
        local_content = QWidget()
        local_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.local_cards_layout = QVBoxLayout(local_content)
        self.local_cards_layout.setSpacing(10)
        self.local_cards_layout.setContentsMargins(5, 5, 5, 5)
        self.local_cards_layout.addStretch()
        local_scroll.setWidget(local_content)
        local_layout.addWidget(local_scroll)
        llevar_widget = QWidget()
        llevar_layout = QVBoxLayout(llevar_widget)
        llevar_label = QLabel("PRODUCTOS PARA LLEVAR")
        llevar_label.setStyleSheet(
            "QLabel{font-size:18px;font-weight:bold;color:white;background-color:#e74c3c;padding:10px;border-radius:6px;}"
        )
        llevar_label.setAlignment(Qt.AlignCenter)
        llevar_layout.addWidget(llevar_label)
        llevar_scroll = QScrollArea()
        llevar_scroll.setWidgetResizable(True)
        llevar_scroll.setStyleSheet("QScrollArea{border:1px solid #e74c3c;border-radius:6px;}")
        llevar_content = QWidget()
        llevar_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.llevar_cards_layout = QVBoxLayout(llevar_content)
        self.llevar_cards_layout.setSpacing(10)
        self.llevar_cards_layout.setContentsMargins(5, 5, 5, 5)
        self.llevar_cards_layout.addStretch()
        llevar_scroll.setWidget(llevar_content)
        llevar_layout.addWidget(llevar_scroll)
        resumen_widget = QWidget()
        resumen_layout = QVBoxLayout(resumen_widget)
        resumen_label = QLabel("RESUMEN DE FALTANTES")
        resumen_label.setStyleSheet(
            "QLabel{font-size:18px;font-weight:bold;color:white;background-color:#2ecc71;padding:10px;border-radius:6px;}"
        )
        resumen_label.setAlignment(Qt.AlignCenter)
        resumen_layout.addWidget(resumen_label)
        resumen_scroll = QScrollArea()
        resumen_scroll.setWidgetResizable(True)
        resumen_scroll.setStyleSheet("QScrollArea{border:1px solid #2ecc71;border-radius:6px;}")
        self.resumen_content = QWidget()
        self.resumen_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.resumen_layout = QVBoxLayout(self.resumen_content)
        self.resumen_layout.setSpacing(5)
        self.resumen_layout.setContentsMargins(5, 5, 5, 5)
        self.resumen_layout.addStretch()
        resumen_scroll.setWidget(self.resumen_content)
        resumen_layout.addWidget(resumen_scroll)
        main_layout.addWidget(local_widget)
        main_layout.addWidget(llevar_widget)
        main_layout.addWidget(resumen_widget)
        layout.addWidget(main_widget, 1)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        self.productos_faltantes_global = []

        cursor.execute(
            """
            SELECT Dt.idDetalleVenta, Dt.tipoConsumo, Dt.idProd, Dt.idProm
            FROM DetallesVenta Dt
            WHERE Dt.fechaRegDetalleVenta = ?
        """,
            (fecha_detalle,),
        )
        detalles = cursor.fetchall()

        grupos = {}

        for id_det, tipo_consumo, id_prod, id_prom in detalles:
            if id_prod:
                cursor.execute("SELECT nomProd FROM Producto WHERE idProd=?", (id_prod,))
                fila = cursor.fetchone()
                if not fila:
                    continue
                nom_prod = fila[0]

                cursor.execute(
                    """
                    SELECT idUnidad, numUnidad, marcado
                    FROM DetallesVentaUnidades
                    WHERE idDetalleVenta=? AND idProd=?
                    ORDER BY numUnidad ASC
                """,
                    (id_det, id_prod),
                )
                unidades = cursor.fetchall()

                for id_unidad, num_unidad, marcado in unidades:
                    cursor.execute(
                        """
                        SELECT idIng, nomIng FROM DetallesVentaExclusiones
                        WHERE idDetalleVenta=?
                        ORDER BY nomIng
                    """,
                        (id_det,),
                    )
                    excl_rows = cursor.fetchall()
                    excl_ids = frozenset(r[0] for r in excl_rows)
                    excl_nombres = sorted([r[1] for r in excl_rows])

                    cursor.execute(
                        """
                        SELECT idIng, nomIng, cantidadExtra FROM DetallesVentaExtras
                        WHERE idDetalleVenta=?
                        ORDER BY nomIng
                    """,
                        (id_det,),
                    )
                    extra_rows = cursor.fetchall()
                    extra_ids = frozenset((r[0], r[2]) for r in extra_rows)
                    extras_texto_grupo = (
                        ("extra: " + ", ".join(f"+{r[2]} {r[1]}" for r in extra_rows)) if extra_rows else ""
                    )

                    clave = (nom_prod, tipo_consumo, excl_ids, extra_ids)
                    if clave not in grupos:
                        grupos[clave] = {
                            'nombre': nom_prod,
                            'tipo': tipo_consumo,
                            'exclusiones': excl_nombres,
                            'extras_texto': extras_texto_grupo,
                            'id_unidades_pendientes': [],
                            'id_unidades_listas': [],
                        }
                    if marcado:
                        grupos[clave]['id_unidades_listas'].append(id_unidad)
                    else:
                        grupos[clave]['id_unidades_pendientes'].append(id_unidad)

            elif id_prom:
                cursor.execute(
                    """
                    SELECT pp.idProd, p.nomProd
                    FROM PromocionProd pp
                    JOIN Producto p ON pp.idProd = p.idProd
                    WHERE pp.idProm = ?
                """,
                    (id_prom,),
                )
                productos_promo = cursor.fetchall()

                for id_prod_p, nom_prod_p in productos_promo:
                    cursor.execute(
                        """
                        SELECT idUnidad, numUnidad, marcado
                        FROM DetallesVentaUnidades
                        WHERE idDetalleVenta=? AND idProd=?
                        ORDER BY numUnidad ASC
                    """,
                        (id_det, id_prod_p),
                    )
                    unidades = cursor.fetchall()

                    for id_unidad, num_unidad, marcado in unidades:
                        cursor.execute(
                            """
                            SELECT COUNT(*) FROM DetallesVentaUnidades
                            WHERE idDetalleVenta=? AND idProd=? AND numUnidad < ?
                        """,
                            (id_det, id_prod_p, num_unidad),
                        )
                        idx_relativo = cursor.fetchone()[0]

                        cursor.execute(
                            """
                            SELECT idIng, nomIng FROM DetallesVentaExclusionesPromo
                            WHERE idDetalleVenta=? AND idProd=? AND numUnidad=?
                            ORDER BY nomIng
                        """,
                            (id_det, id_prod_p, idx_relativo),
                        )
                        excl_rows = cursor.fetchall()
                        excl_ids = frozenset(r[0] for r in excl_rows)
                        excl_nombres = sorted([r[1] for r in excl_rows])

                        cursor.execute(
                            """
                            SELECT idIng, nomIng, cantidadExtra FROM DetallesVentaExtras
                            WHERE idDetalleVenta=? AND idProd=? AND numUnidad=?
                            ORDER BY nomIng
                        """,
                            (id_det, id_prod_p, idx_relativo),
                        )
                        extra_rows = cursor.fetchall()
                        extra_ids = frozenset((r[0], r[2]) for r in extra_rows)
                        extras_texto_grupo = (
                            ("extra: " + ", ".join(f"+{r[2]} {r[1]}" for r in extra_rows)) if extra_rows else ""
                        )

                        clave = (nom_prod_p, tipo_consumo, excl_ids, extra_ids)
                        if clave not in grupos:
                            grupos[clave] = {
                                'nombre': nom_prod_p,
                                'tipo': tipo_consumo,
                                'exclusiones': excl_nombres,
                                'extras_texto': extras_texto_grupo,
                                'id_unidades_pendientes': [],
                                'id_unidades_listas': [],
                            }
                        if marcado:
                            grupos[clave]['id_unidades_listas'].append(id_unidad)
                        else:
                            grupos[clave]['id_unidades_pendientes'].append(id_unidad)

        for clave, g in grupos.items():
            total = len(g['id_unidades_pendientes']) + len(g['id_unidades_listas'])
            listos = len(g['id_unidades_listas'])
            faltan = len(g['id_unidades_pendientes'])
            if total == 0:
                continue
            if faltan == 0:
                continue
            extras_texto_g = g.get('extras_texto', '')
            excl_key = (tuple(sorted(g['exclusiones'])), extras_texto_g)
            self.productos_faltantes_global.append((g['nombre'], faltan, g['tipo'], excl_key))
            pendientes_str = ','.join(str(x) for x in g['id_unidades_pendientes'])
            listas_str = ','.join(str(x) for x in g['id_unidades_listas'])
            entradas_str = f"P:{pendientes_str}|L:{listas_str}"
            card = self.crearCardProducto(
                g['nombre'],
                total,
                listos,
                faltan,
                entradas_str,
                g['tipo'],
                g['exclusiones'],
                excl_key=excl_key,
                extras_texto=extras_texto_g,
            )
            if g['tipo'] == "Local":
                self.local_cards_layout.insertWidget(self.local_cards_layout.count() - 1, card)
            else:
                self.llevar_cards_layout.insertWidget(self.llevar_cards_layout.count() - 1, card)

        self.actualizarResumen()
        conn.close()

        if self.local_cards_layout.count() <= 1 and self.llevar_cards_layout.count() <= 1:
            QMessageBox.information(self.dialogo_cards, "Informacion", "No hay productos pendientes para marcar.")
            return

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet(
            "QPushButton{background-color:#e74c3c;color:white;border:none;border-radius:6px;padding:10px 30px;font-weight:bold;margin-top:10px;}QPushButton:hover{background-color:#c0392b;}"
        )
        btn_cerrar.clicked.connect(self.cerrarDialogoCards)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignCenter)
        self.dialogo_cards.exec_()

    def _imprimir_en_consola(self, titulo, datos_venta, items):
        if titulo == "PEDIDO A COCINA":
            self._imprimir_en_consola_cocina(datos_venta, items)
            return
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
            clave = (producto, tipo)
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
        lineas.append("=" * 44)
        lineas.append(f"{'TOTAL:':>30}{total_general:>14.2f} Bs")
        lineas.append("=" * 44)
        print("\n".join(lineas))

    def _imprimir_en_consola_cocina(self, datos_venta, items_raw):
        from datetime import datetime

        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%I:%M %p")
        lineas = []
        lineas.append("=" * 44)
        lineas.append(f"{'PEDIDO COCINA':^44}")
        lineas.append("=" * 44)
        lineas.append(f"Fecha: {fecha}  Hora: {hora}")
        lineas.append(f"Nro. Venta: {datos_venta.get('num_venta', '')}")
        lineas.append(f"Mesero: {datos_venta.get('empleado', '')}")
        lineas.append(f"Salon: {datos_venta.get('seccion', '')}  Mesa: {datos_venta.get('mesa', '')}")
        lineas.append("-" * 44)
        lineas_cocina = self.manejador_impresion._parsear_items_cocina(items_raw)
        lineas.append(f"{'CANT':<5}{'PRODUCTO':<32}{'T':<3}")
        lineas.append("-" * 44)
        grupos_cocina = {}
        for l in lineas_cocina:
            excl_tuple = tuple(l['exclusiones']) if l['exclusiones'] else ()
            clave = (l['producto'], l['tipo'], excl_tuple)
            if clave in grupos_cocina:
                grupos_cocina[clave]['cantidad'] += l['cantidad']
            else:
                grupos_cocina[clave] = dict(l)
        for g in grupos_cocina.values():
            prod = g['producto']
            if len(prod) > 29:
                prod = prod[:26] + "..."
            tipo_cod = "L" if g['tipo'] == 'Local' else "LL"
            lineas.append(f"{g['cantidad']:<5}{prod:<32}{tipo_cod:<3}")
            if g['exclusiones']:
                for excl_linea in g['exclusiones']:
                    partes = [excl_linea[i : i + 36] for i in range(0, len(excl_linea), 36)]
                    for parte in partes:
                        lineas.append(f"     sin: {parte}")
        lineas.append("=" * 44)
        print("\n".join(lineas))

    def actualizarProgresoConResumen(
        self,
        entradas_str,
        cantidad,
        card,
        total_mostrado,
        nombre_producto,
        tipo_consumo,
        marcar_todos=False,
        excl_key=(),
    ):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            partes = entradas_str.split('|')
            pendientes_ids = []
            listas_ids = []
            for parte in partes:
                if parte.startswith('P:'):
                    raw = parte[2:]
                    pendientes_ids = [int(x) for x in raw.split(',') if x.strip()]
                elif parte.startswith('L:'):
                    raw = parte[2:]
                    listas_ids = [int(x) for x in raw.split(',') if x.strip()]

            cambios_realizados = False

            if marcar_todos:
                for id_unidad in pendientes_ids:
                    cursor.execute("UPDATE DetallesVentaUnidades SET marcado=1 WHERE idUnidad=?", (id_unidad,))
                if pendientes_ids:
                    cambios_realizados = True
                    listas_ids = listas_ids + pendientes_ids
                    pendientes_ids = []

            elif cantidad > 0:
                if pendientes_ids:
                    id_unidad = pendientes_ids[0]
                    cursor.execute("UPDATE DetallesVentaUnidades SET marcado=1 WHERE idUnidad=?", (id_unidad,))
                    cambios_realizados = True
                    listas_ids = listas_ids + [pendientes_ids.pop(0)]

            else:
                if listas_ids:
                    id_unidad = listas_ids[-1]
                    cursor.execute("UPDATE DetallesVentaUnidades SET marcado=0 WHERE idUnidad=?", (id_unidad,))
                    cambios_realizados = True
                    pendientes_ids = pendientes_ids + [listas_ids.pop(-1)]

            if cambios_realizados:
                conn.commit()
                self.actualizar_al_cerrar = True

                ids_det_afectados = set()
                todos_ids_unidad = pendientes_ids + listas_ids
                for id_unidad in todos_ids_unidad:
                    cursor.execute("SELECT idDetalleVenta FROM DetallesVentaUnidades WHERE idUnidad=?", (id_unidad,))
                    r = cursor.fetchone()
                    if r:
                        ids_det_afectados.add(r[0])

                for id_det in ids_det_afectados:
                    cursor.execute("SELECT COUNT(*) FROM DetallesVentaUnidades WHERE idDetalleVenta=?", (id_det,))
                    total_unidades_det = cursor.fetchone()[0]
                    cursor.execute(
                        "SELECT COUNT(*) FROM DetallesVentaUnidades WHERE idDetalleVenta=? AND marcado=1", (id_det,)
                    )
                    marcadas_det = cursor.fetchone()[0]
                    todo_marcado = 1 if marcadas_det == total_unidades_det else 0
                    cursor.execute(
                        """
                        UPDATE DetallesVenta
                        SET cantidadMarcado = ?,
                        marcado = ?
                        WHERE idDetalleVenta=?
                    """,
                        (marcadas_det, todo_marcado, id_det),
                    )

                for id_det in ids_det_afectados:
                    cursor.execute(
                        """
                        SELECT COUNT(*) = 0 FROM DetallesVentaUnidades 
                        WHERE idDetalleVenta = ? AND marcado = 0
                    """,
                        (id_det,),
                    )
                    todas_marcadas = cursor.fetchone()[0]
                    cursor.execute("SELECT estadoDetalleVenta FROM DetallesVenta WHERE idDetalleVenta=?", (id_det,))
                    fila_estado = cursor.fetchone()
                    estado_actual = fila_estado[0] if fila_estado else None
                    if todas_marcadas:
                        if estado_actual == 'Preparacion':
                            cursor.execute(
                                """
                                UPDATE DetallesVenta 
                                SET estadoDetalleVenta = 'Cobrar' 
                                WHERE idDetalleVenta = ?
                            """,
                                (id_det,),
                            )
                    else:
                        if estado_actual == 'Cobrar':
                            cursor.execute(
                                """
                                UPDATE DetallesVenta 
                                SET estadoDetalleVenta = 'Preparacion' 
                                WHERE idDetalleVenta = ?
                            """,
                                (id_det,),
                            )

                conn.commit()

                total_nuevo = len(pendientes_ids) + len(listas_ids)
                listos_nuevo = len(listas_ids)
                faltan_nuevo = len(pendientes_ids)

                nuevo_entradas_str = (
                    f"P:{','.join(str(x) for x in pendientes_ids)}|L:{','.join(str(x) for x in listas_ids)}"
                )

                if card and isinstance(card, QFrame) and not card.isHidden():
                    cl = card.layout()
                    if cl:
                        for i in range(cl.count()):
                            item = cl.itemAt(i)
                            if not item:
                                continue
                            w = item.widget()
                            if isinstance(w, QProgressBar):
                                w.setMaximum(max(total_nuevo, 1))
                                w.setValue(listos_nuevo)
                                w.setFormat(f"{listos_nuevo}/{total_nuevo}")
                                w.repaint()
                            elif isinstance(w, QWidget) and w.layout() and isinstance(w.layout(), QHBoxLayout):
                                for j in range(w.layout().count()):
                                    hi = w.layout().itemAt(j)
                                    if hi and hi.widget() and isinstance(hi.widget(), QLabel):
                                        lbl = hi.widget()
                                        texto = lbl.text()
                                        if "Total:" in texto:
                                            lbl.setText(f"<b>Total:</b> {total_nuevo}")
                                            lbl.repaint()
                                        elif "Listos:" in texto:
                                            lbl.setText(f"<b>Listos:</b> {listos_nuevo}")
                                            lbl.repaint()
                                        elif "Faltan:" in texto:
                                            lbl.setText(f"<b>Faltan:</b> {faltan_nuevo}")
                                            lbl.repaint()

                        for i in range(cl.count()):
                            item = cl.itemAt(i)
                            if not item:
                                continue
                            sub = item.layout()
                            if sub and isinstance(sub, QHBoxLayout):
                                for j in range(sub.count()):
                                    hi = sub.itemAt(j)
                                    if hi and hi.widget() and isinstance(hi.widget(), QPushButton):
                                        btn = hi.widget()
                                        txt = btn.text()
                                        if txt == "-1":
                                            try:
                                                btn.clicked.disconnect()
                                            except Exception:
                                                pass
                                            btn.clicked.connect(
                                                lambda _, e=nuevo_entradas_str, c=card, t=total_nuevo, n=nombre_producto, tp=tipo_consumo, ek=excl_key: (
                                                    self.actualizarProgresoConResumen(e, -1, c, t, n, tp, False, ek)
                                                )
                                            )
                                        elif txt == "+1":
                                            try:
                                                btn.clicked.disconnect()
                                            except Exception:
                                                pass
                                            btn.clicked.connect(
                                                lambda _, e=nuevo_entradas_str, c=card, t=total_nuevo, n=nombre_producto, tp=tipo_consumo, ek=excl_key: (
                                                    self.actualizarProgresoConResumen(e, 1, c, t, n, tp, False, ek)
                                                )
                                            )
                                        elif txt == "Todos":
                                            try:
                                                btn.clicked.disconnect()
                                            except Exception:
                                                pass
                                            btn.clicked.connect(
                                                lambda _, e=nuevo_entradas_str, c=card, t=total_nuevo, n=nombre_producto, tp=tipo_consumo, ek=excl_key: (
                                                    self.actualizarProgresoConResumen(e, t, c, t, n, tp, True, ek)
                                                )
                                            )

                encontrado_en_resumen = False
                for i, entrada in enumerate(self.productos_faltantes_global):
                    nombre, faltan, tipo, ek = entrada
                    if nombre == nombre_producto and tipo == tipo_consumo and ek == excl_key:
                        if faltan_nuevo <= 0:
                            self.productos_faltantes_global.pop(i)
                        else:
                            self.productos_faltantes_global[i] = (nombre, faltan_nuevo, tipo, ek)
                        encontrado_en_resumen = True
                        break

                if not encontrado_en_resumen and faltan_nuevo > 0:
                    self.productos_faltantes_global.append((nombre_producto, faltan_nuevo, tipo_consumo, excl_key))

                self.actualizarResumen()

        except Exception as e:
            conn.rollback()
            print(f"Error al actualizar marcado: {e}")
            import traceback

            traceback.print_exc()
        finally:
            conn.close()

    def actualizarResumen(self):
        while self.resumen_layout.count():
            item = self.resumen_layout.takeAt(0)
            if item.widget():
                try:
                    item.widget().deleteLater()
                except Exception:
                    pass

        total_faltantes = 0
        for nombre, faltan, tipo, *_ in self.productos_faltantes_global:
            if faltan > 0:
                item_text = QLabel(f"* {nombre} ({tipo}): {faltan} faltantes")
                color = "#3498db" if tipo == "Local" else "#e74c3c"
                item_text.setStyleSheet(f"font-size:15px;color:{color};font-weight:500;padding-left:10px;")
                self.resumen_layout.addWidget(item_text)
                total_faltantes += faltan

        if total_faltantes == 0:
            completo_label = QLabel("Todos los productos estan listos!")
            completo_label.setStyleSheet("font-size:16px;color:#27ae60;font-weight:bold;padding:10px;")
            self.resumen_layout.addWidget(completo_label)
        else:
            total_label = QLabel(f"<b>TOTAL FALTANTES: {total_faltantes}</b>")
            total_label.setStyleSheet("font-size:16px;color:#e74c3c;font-weight:bold;margin-top:5px;padding-left:10px;")
            self.resumen_layout.addWidget(total_label)

        self.resumen_layout.addStretch()

    def cerrarDialogoCards(self):
        if self.dialogo_cards:
            self.dialogo_cards.accept()
            self.dialogo_cards = None

        if self.dialogo_detalles and self.numMesa_actual and self.idSeccion_actual and self.actualizar_al_cerrar:
            self.dialogo_detalles.close()
            self.dialogo_detalles = None
            self.mostrarDetallesVentaMesa(self.numMesa_actual, self.idSeccion_actual)
        elif self.dialogo_detalles and self.actualizar_al_cerrar:
            self.dialogo_detalles.close()
            self.dialogo_detalles = None
            if self.numMesa_actual and self.idSeccion_actual:
                self.mostrarDetallesVentaMesa(self.numMesa_actual, self.idSeccion_actual)

    def cobrarMesa(self, numMesa, idSeccion):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM DetallesVentaUnidades DVU
            JOIN DetallesVenta DV ON DVU.idDetalleVenta = DV.idDetalleVenta
            JOIN Venta V ON V.numVenta = DV.numVenta AND V.fechaReg = DV.fechaRegVenta
            WHERE V.idMesa = ? AND V.idSeccion = ?
              AND DVU.marcado = 0
        """,
            (numMesa, idSeccion),
        )
        unidades_pendientes = cursor.fetchone()[0]

        if unidades_pendientes > 0:
            QMessageBox.warning(
                self, "No se puede cobrar", f"Esta mesa tiene {unidades_pendientes} unidad(es) sin marcar como listas."
            )
            conn.close()
            return

        cursor.execute(
            """
            SELECT V.numVenta, DATE(V.fechaReg) FROM Venta V
            WHERE V.idMesa = ? AND V.idSeccion = ?
            ORDER BY V.fechaReg DESC LIMIT 1
        """,
            (numMesa, idSeccion),
        )
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            numVenta, fecha = resultado
            self.abrirCobro(fecha, numVenta, numMesa, idSeccion)
        else:
            QMessageBox.warning(self, "Error", "No se encontro ninguna venta para esta mesa")

    def abrirCobro(self, fecha, numVenta, numMesa, idSeccion):
        try:
            dialogo = DialogoCobroVenta(fecha, numVenta, numMesa, idSeccion, self)
            if dialogo.exec_() == QDialog.Accepted:
                self.limpiarCampos()
                if hasattr(self, 'idSeccionActual') and self.idSeccionActual:
                    self.cargarSecciones(self.idSeccionActual)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el dialogo de cobro: {str(e)}")
            import traceback

            traceback.print_exc()

    def actualizarHora(self):
        self.campoTiempo.setText(datetime.now().strftime("%I:%M %p"))

    def _dialogoExclusionesPromo(self, nombre_promo, productos_promo, exclusiones_previas=None, extras_previas=None):
        if not productos_promo:
            return {}, {}
        exclusiones_previas = exclusiones_previas or {}
        extras_previas = extras_previas or {}
        dialog = QDialog(self)
        dialog.setWindowTitle("Personalizar promoción")
        dialog.setMinimumWidth(900)
        dialog.setMaximumWidth(1200)
        dialog.setStyleSheet("""
            QDialog { background-color: white; font-family: 'Segoe UI', Arial, sans-serif; }
            QTabWidget::pane { border: 1px solid #e2e8f0; background-color: #f8fafc; }
            QTabBar::tab { background-color: #e2e8f0; padding: 10px 20px; margin-right: 4px; font-weight: bold; min-width: 140px; }
            QTabBar::tab:selected { background-color: #3498db; color: white; }
            QTabBar::tab:hover { background-color: #2980b9; color: white; }
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { border: none; background: #f1f5f9; width: 10px; border-radius: 5px; }
            QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 5px; min-height: 30px; }
            QScrollBar::handle:vertical:hover { background: #94a3b8; }
            QCheckBox { spacing: 12px; font-size: 14px; color: #2c3e50; background: transparent; }
            QCheckBox::indicator { width: 20px; height: 20px; border-radius: 5px; border: 2px solid #4a89dc; background: white; }
            QCheckBox::indicator:checked { background-color: #4a89dc; border: 2px solid #4a89dc; }
            QCheckBox::indicator:unchecked:hover { background-color: #e6f2ff; }
            QLabel { color: #2c3e50; font-size: 14px; font-weight: 500; background: transparent; }
            QPushButton { border-radius: 8px; font-size: 14px; font-weight: bold; min-width: 100px; border: none; padding: 10px 16px; }
            QPushButton#todos_unidad { background-color: #3498db; color: white; font-size: 10px; padding: 4px 8px; min-width: 50px; }
            QPushButton#ninguno_unidad { background-color: #e74c3c; color: white; font-size: 10px; padding: 4px 8px; min-width: 50px; }
            QFrame { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; }
            QSpinBox {
                background-color: white; border: 2px solid #e2e8f0; border-radius: 6px;
                padding: 2px 6px; font-size: 12px; min-height: 30px; max-width: 70px;
            }
            QSpinBox:focus { border: 2px solid #27ae60; }
            QSpinBox::up-button {
                background-color: #3498db; border: none;
                width: 22px; height: 19px;
                border-radius: 0px 4px 0px 0px;
                subcontrol-origin: border; subcontrol-position: top right;
            }
            QSpinBox::up-button:hover { background-color: #2980b9; }
            QSpinBox::down-button {
                background-color: #e74c3c; border: none;
                width: 22px; height: 19px;
                border-radius: 0px 0px 4px 0px;
                subcontrol-origin: border; subcontrol-position: bottom right;
            }
            QSpinBox::down-button:hover { background-color: #c0392b; }
            QSpinBox::up-arrow {
                image: none; border-left: 3px solid transparent; border-right: 3px solid transparent;
                border-bottom: 3px solid white; width: 0; height: 0;
            }
            QSpinBox::down-arrow {
                image: none; border-left: 3px solid transparent; border-right: 3px solid transparent;
                border-top: 3px solid white; width: 0; height: 0;
            }
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
        titulo = QLabel("🎁 Personalizar promoción")
        titulo.setStyleSheet("QLabel { color: white; font-size: 18px; font-weight: bold; background: transparent; }")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)
        subtitulo = QLabel(nombre_promo)
        subtitulo.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.9); font-size: 14px; font-weight: 500; background: transparent; }"
        )
        subtitulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitulo)
        layout.addWidget(header)
        ayuda_widget = QWidget()
        ayuda_widget.setStyleSheet("QWidget { background-color: #fef9e7; border-bottom: 1px solid #f39c12; }")
        ayuda_layout = QHBoxLayout(ayuda_widget)
        ayuda_layout.setContentsMargins(20, 10, 20, 10)
        ayuda_text = QLabel(
            "⚠️  Personaliza cada unidad individualmente — desmarca lo que NO quiere y suma lo que quiere extra"
        )
        ayuda_text.setWordWrap(True)
        ayuda_text.setStyleSheet("background: transparent; font-size: 12px; color: #e67e22; font-weight: 500;")
        ayuda_layout.addWidget(ayuda_text)
        layout.addWidget(ayuda_widget)
        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget { background-color: #f8fafc; } QTabBar::tab { min-width: 150px; }")
        exclusiones_por_producto = {}
        extras_por_producto = {}
        for prod in productos_promo:
            id_prod = prod['idProd']
            nombre_prod = prod['nombre']
            cantidad_promo = prod['cantidad']
            ingredientes = self._obtenerIngredientesProducto(nombre_prod)
            ingredientes_extra = self._obtenerIngredientesProductoParaExtra(nombre_prod)
            excl_previas_prod = exclusiones_previas.get(str(id_prod), [])
            excl_previas_por_unidad = {}
            for ud in excl_previas_prod:
                if isinstance(ud, dict) and 'unidad' in ud:
                    excl_previas_por_unidad[ud['unidad']] = {e['idIng'] for e in ud.get('exclusiones', [])}
            extras_previas_prod = extras_previas.get(str(id_prod), [])
            extras_previas_por_unidad = {}
            for ud in extras_previas_prod:
                if isinstance(ud, dict) and 'unidad' in ud:
                    extras_previas_por_unidad[ud['unidad']] = {
                        e['idIng']: e['cantidadExtra'] for e in ud.get('extras', [])
                    }
            tab_widget = QWidget()
            tab_layout = QVBoxLayout(tab_widget)
            tab_layout.setContentsMargins(16, 16, 16, 16)
            tab_layout.setSpacing(12)
            cantidad_label = QLabel(f"Cantidad en promoción: {cantidad_promo} unidades")
            cantidad_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px;")
            tab_layout.addWidget(cantidad_label)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setMaximumHeight(500)
            scroll.setStyleSheet(
                "QScrollArea { border: 1px solid #e2e8f0; border-radius: 8px; background-color: white; }"
            )
            contenedor = QWidget()
            contenedor.setStyleSheet("background: white;")
            v_layout = QVBoxLayout(contenedor)
            v_layout.setContentsMargins(12, 12, 12, 12)
            v_layout.setSpacing(15)
            if ingredientes or ingredientes_extra:
                unidades_widgets = []
                for unidad_idx in range(cantidad_promo):
                    ids_excluidos_prev_unidad = excl_previas_por_unidad.get(unidad_idx, set())
                    cantidades_extra_prev_unidad = extras_previas_por_unidad.get(unidad_idx, {})
                    unidad_frame = QFrame()
                    unidad_frame.setStyleSheet(
                        "QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; margin: 2px; }"
                    )
                    unidad_layout = QVBoxLayout(unidad_frame)
                    unidad_layout.setSpacing(8)
                    unidad_header = QWidget()
                    unidad_header_layout = QHBoxLayout(unidad_header)
                    unidad_header_layout.setContentsMargins(8, 4, 8, 4)
                    unidad_titulo = QLabel(f"Unidad #{unidad_idx + 1}")
                    unidad_titulo.setStyleSheet("font-weight: bold; color: #3498db; font-size: 13px;")
                    unidad_header_layout.addWidget(unidad_titulo)
                    botones_rapidos = QWidget()
                    botones_layout = QHBoxLayout(botones_rapidos)
                    botones_layout.setContentsMargins(0, 0, 0, 0)
                    btn_todos_unidad = QPushButton("✓ Todos")
                    btn_todos_unidad.setObjectName("todos_unidad")
                    btn_ninguno_unidad = QPushButton("✗ Ninguno")
                    btn_ninguno_unidad.setObjectName("ninguno_unidad")
                    btn_todos_unidad.setFixedSize(70, 28)
                    btn_ninguno_unidad.setFixedSize(70, 28)
                    botones_layout.addWidget(btn_todos_unidad)
                    botones_layout.addWidget(btn_ninguno_unidad)
                    unidad_header_layout.addWidget(botones_rapidos)
                    unidad_header_layout.addStretch()
                    unidad_layout.addWidget(unidad_header)

                    unidad_checkboxes = []
                    if ingredientes:
                        etiqueta_quitar = QLabel("Quitar ingredientes:")
                        etiqueta_quitar.setStyleSheet(
                            "font-size: 13px; font-weight: bold; color: #7f8c8d; background: transparent;"
                        )
                        unidad_layout.addWidget(etiqueta_quitar)
                        ingredientes_layout = QVBoxLayout()
                        ingredientes_layout.setSpacing(4)
                        ingredientes_layout.setContentsMargins(8, 4, 8, 4)
                        for ing in ingredientes:
                            item_widget = QWidget()
                            item_widget.setStyleSheet("background: transparent;")
                            item_layout = QHBoxLayout(item_widget)
                            item_layout.setContentsMargins(8, 4, 8, 4)
                            item_layout.setSpacing(12)
                            cb = QCheckBox()
                            cb.setChecked(ing["idIng"] not in ids_excluidos_prev_unidad)
                            cb.idIng = ing["idIng"]
                            cb.nomIng = ing["nomIng"]
                            cb.setStyleSheet("""
                                QCheckBox { spacing: 10px; font-size: 14px; font-weight: 600; color: #2c3e50; background: transparent; }
                                QCheckBox::indicator { width: 20px; height: 20px; border-radius: 4px; border: 2px solid #3498db; background: white; }
                                QCheckBox::indicator:checked { background-color: #3498db; border: 2px solid #3498db; }
                                QCheckBox::indicator:unchecked { background-color: white; }
                            """)
                            ing_nombre = QLabel(ing["nomIng"])
                            ing_nombre.setStyleSheet(
                                "background: transparent; font-size: 14px; color: #2c3e50; font-weight: 600; border: none;"
                            )
                            estado_label = QLabel()
                            estado_label.setStyleSheet(
                                "background: transparent; font-size: 13px; font-weight: bold; border: none; padding: 3px 10px; border-radius: 4px;"
                            )

                            def actualizar_estado(checked, lbl=estado_label, widget=item_widget):
                                if checked:
                                    lbl.setText("✓ Incluido")
                                    lbl.setStyleSheet(
                                        "background: #e8f5e9; font-size: 13px; color: #2ecc71; font-weight: bold; border: none; padding: 3px 10px; border-radius: 4px;"
                                    )
                                    widget.setStyleSheet("background: transparent; border-bottom: 1px solid #e2e8f0;")
                                else:
                                    lbl.setText("✗ Excluido")
                                    lbl.setStyleSheet(
                                        "background: #ffebee; font-size: 13px; color: #e74c3c; font-weight: bold; border: none; padding: 3px 10px; border-radius: 4px;"
                                    )
                                    widget.setStyleSheet("background: #fff5f5; border-bottom: 1px solid #ffcdd2;")

                            actualizar_estado(cb.isChecked())
                            cb.toggled.connect(actualizar_estado)
                            item_layout.addWidget(cb)
                            item_layout.addWidget(ing_nombre, 1)
                            item_layout.addWidget(estado_label)
                            unidad_checkboxes.append(cb)
                            ingredientes_layout.addWidget(item_widget)

                        def crear_funcion_todos_unidad(checks):
                            def marcar_todos():
                                for ch in checks:
                                    ch.setChecked(True)

                            return marcar_todos

                        def crear_funcion_ninguno_unidad(checks):
                            def marcar_ninguno():
                                for ch in checks:
                                    ch.setChecked(False)

                            return marcar_ninguno

                        btn_todos_unidad.clicked.connect(crear_funcion_todos_unidad(unidad_checkboxes))
                        btn_ninguno_unidad.clicked.connect(crear_funcion_ninguno_unidad(unidad_checkboxes))
                        unidad_layout.addLayout(ingredientes_layout)
                    else:
                        btn_todos_unidad.setVisible(False)
                        btn_ninguno_unidad.setVisible(False)

                    unidad_spinboxes_extra = []
                    if ingredientes_extra:
                        separador_extra = QWidget()
                        separador_extra.setFixedHeight(1)
                        separador_extra.setStyleSheet("background-color: #e2e8f0; border: none;")
                        unidad_layout.addWidget(separador_extra)
                        etiqueta_extra = QLabel("Agregar extra:")
                        etiqueta_extra.setStyleSheet(
                            "font-size: 13px; font-weight: bold; color: #27ae60; background: transparent;"
                        )
                        unidad_layout.addWidget(etiqueta_extra)
                        extras_layout = QVBoxLayout()
                        extras_layout.setSpacing(4)
                        extras_layout.setContentsMargins(8, 4, 8, 4)
                        for idIng_e, nomIng_e, precioExtra_e in ingredientes_extra:
                            item_w = QWidget()
                            item_w.setStyleSheet("background: transparent;")
                            item_l = QHBoxLayout(item_w)
                            item_l.setContentsMargins(8, 4, 8, 4)
                            item_l.setSpacing(10)
                            lbl_ing_extra = QLabel(f"{nomIng_e}  (+{precioExtra_e:.2f} Bs c/u)")
                            lbl_ing_extra.setStyleSheet(
                                "background: transparent; font-size: 14px; color: #2c3e50; font-weight: 600; border: none;"
                            )
                            sp = QSpinBox()
                            sp.setRange(0, 20)
                            sp.setValue(int(cantidades_extra_prev_unidad.get(idIng_e, 0)))
                            sp.idIng = idIng_e
                            sp.nomIng = nomIng_e
                            sp.precioExtra = precioExtra_e
                            item_l.addWidget(lbl_ing_extra, 1)
                            item_l.addWidget(sp)
                            unidad_spinboxes_extra.append(sp)
                            extras_layout.addWidget(item_w)
                        unidad_layout.addLayout(extras_layout)

                    v_layout.addWidget(unidad_frame)
                    unidades_widgets.append(
                        {
                            'frame': unidad_frame,
                            'checkboxes': unidad_checkboxes,
                            'spinboxes_extra': unidad_spinboxes_extra,
                        }
                    )
                v_layout.addStretch()
                scroll.setWidget(contenedor)
                tab_layout.addWidget(scroll)
                exclusiones_por_producto[str(id_prod)] = {
                    'nombre': nombre_prod,
                    'unidades': unidades_widgets,
                    'cantidad': cantidad_promo,
                }
                extras_por_producto[str(id_prod)] = {
                    'nombre': nombre_prod,
                    'unidades': unidades_widgets,
                    'cantidad': cantidad_promo,
                }
            else:
                no_ing = QLabel(f"{nombre_prod} no tiene ingredientes para personalizar")
                no_ing.setAlignment(Qt.AlignCenter)
                no_ing.setStyleSheet("padding: 20px; color: #7f8c8d; font-size: 12px;")
                v_layout.addWidget(no_ing)
                scroll.setWidget(contenedor)
                tab_layout.addWidget(scroll)
                exclusiones_por_producto[str(id_prod)] = {
                    'nombre': nombre_prod,
                    'unidades': [],
                    'cantidad': cantidad_promo,
                }
                extras_por_producto[str(id_prod)] = {'nombre': nombre_prod, 'unidades': [], 'cantidad': cantidad_promo}
            tabs.addTab(tab_widget, f"{nombre_prod} (x{cantidad_promo})")
        layout.addWidget(tabs)
        footer = QWidget()
        footer.setStyleSheet("QWidget { background-color: #f8f9fa; border-top: 1px solid #e2e8f0; }")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 16, 20, 16)
        footer_layout.setSpacing(12)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(
            "QPushButton { background-color: #95a5a6; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; padding: 10px 16px; min-width: 100px; } QPushButton:hover { background-color: #7f8c8d; }"
        )
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_confirmar = QPushButton("Confirmar")
        btn_confirmar.setStyleSheet(
            "QPushButton { background-color: #2ecc71; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; padding: 10px 16px; min-width: 120px; } QPushButton:hover { background-color: #27ae60; }"
        )
        btn_confirmar.setCursor(Qt.PointingHandCursor)
        footer_layout.addStretch()
        footer_layout.addWidget(btn_cancelar)
        footer_layout.addWidget(btn_confirmar)
        layout.addWidget(footer)
        btn_cancelar.clicked.connect(dialog.reject)
        btn_confirmar.clicked.connect(dialog.accept)
        if dialog.exec_() != QDialog.Accepted:
            return None, None
        resultado_exclusiones = {}
        resultado_extras = {}
        for id_prod_str, data in exclusiones_por_producto.items():
            unidades_data_excl = []
            unidades_data_extra = []
            for unidad_idx, unidad in enumerate(data['unidades']):
                excluidos = [
                    {"idIng": cb.idIng, "nomIng": cb.nomIng} for cb in unidad['checkboxes'] if not cb.isChecked()
                ]
                if excluidos:
                    unidades_data_excl.append({'unidad': unidad_idx, 'exclusiones': excluidos})
                extras_elegidos = [
                    {"idIng": sp.idIng, "nomIng": sp.nomIng, "cantidadExtra": sp.value(), "precioExtra": sp.precioExtra}
                    for sp in unidad['spinboxes_extra']
                    if sp.value() > 0
                ]
                if extras_elegidos:
                    unidades_data_extra.append({'unidad': unidad_idx, 'extras': extras_elegidos})
            if unidades_data_excl:
                resultado_exclusiones[id_prod_str] = unidades_data_excl
            if unidades_data_extra:
                resultado_extras[id_prod_str] = unidades_data_extra
        return resultado_exclusiones, resultado_extras

    def _textoExclusionesPromo(self, exclusiones_por_producto):
        if not exclusiones_por_producto:
            return ""

        partes = []
        for id_prod_str, unidades_data in exclusiones_por_producto.items():
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT nomProd FROM Producto WHERE idProd=?", (int(id_prod_str),))
            prod = cursor.fetchone()
            conn.close()
            nombre_prod = prod[0] if prod else id_prod_str

            unidades_con_excl = []
            for unidad_data in unidades_data:
                if unidad_data['exclusiones']:
                    excl_nombres = [e["nomIng"] for e in unidad_data['exclusiones']]
                    unidades_con_excl.append(f"#{unidad_data['unidad'] + 1}: sin {', '.join(excl_nombres)}")

            if unidades_con_excl:
                partes.append(f"{nombre_prod} [{'; '.join(unidades_con_excl)}]")

        return " | ".join(partes)

    def _textoExtrasPromo(self, extras_por_producto):
        if not extras_por_producto:
            return ""
        partes = []
        for id_prod_str, unidades_data in extras_por_producto.items():
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT nomProd FROM Producto WHERE idProd=?", (int(id_prod_str),))
            prod = cursor.fetchone()
            conn.close()
            nombre_prod = prod[0] if prod else id_prod_str

            unidades_con_extra = []
            for unidad_data in unidades_data:
                if unidad_data['extras']:
                    extra_nombres = [f"+{e['cantidadExtra']} {e['nomIng']}" for e in unidad_data['extras']]
                    unidades_con_extra.append(f"#{unidad_data['unidad'] + 1}: {', '.join(extra_nombres)}")

            if unidades_con_extra:
                partes.append(f"{nombre_prod} [{'; '.join(unidades_con_extra)}]")

        return " | ".join(partes)

    def dialogPromocion(self, nombre_promo):
        if self.verificarBloqueo("agregar productos"):
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT idProm, precioProm FROM Promocion WHERE nomProm=?", (nombre_promo,))
        promo = cursor.fetchone()
        if not promo:
            conn.close()
            return
        id_prom, precio_unitario = promo
        cursor.execute(
            """
            SELECT P.idProd, P.nomProd, PP.cantidadProdProm
            FROM PromocionProd PP
            JOIN Producto P ON PP.idProd = P.idProd
            WHERE PP.idProm = ?
        """,
            (id_prom,),
        )
        productos_promo = [{"idProd": r[0], "nombre": r[1], "cantidad": r[2]} for r in cursor.fetchall()]
        conn.close()

        dialog = QDialog(self)
        dialog.setWindowTitle("Añadir promoción")
        dialog.setStyleSheet("""
            QDialog { background-color: #f8fafc; border-radius: 10px; font-family: 'Segoe UI', Arial, sans-serif; }
            QLabel { color: #2c3e50; font-size: 14px; font-weight: 500; margin-bottom: 6px; }
            QSpinBox { background-color: #ffffff; border: 2px solid #e2e8f0; border-radius: 6px; padding: 6px 10px; font-size: 14px; min-height: 40px; }
            QSpinBox:focus { border: 2px solid #4a89dc; background-color: #f0f7ff; }
            QSpinBox::up-button { background-color: #3498db; border: none; width: 35px; height: 28px; border-radius: 0px 5px 0px 0px; subcontrol-origin: border; subcontrol-position: top right; }
            QSpinBox::up-button:hover { background-color: #2980b9; }
            QSpinBox::down-button { background-color: #e74c3c; border: none; width: 35px; height: 28px; border-radius: 0px 5px 0px 0px; subcontrol-origin: border; subcontrol-position: bottom right; }
            QSpinBox::down-button:hover { background-color: #c0392b; }
            QRadioButton { font-size: 14px; color: #2c3e50; padding: 6px 2px; spacing: 8px; }
            QRadioButton::indicator { width: 18px; height: 18px; border-radius: 9px; border: 2px solid #4a89dc; background: #ffffff; }
            QRadioButton::indicator:checked { background-color: #4a89dc; border: 2px solid #4a89dc; }
            QDialogButtonBox { background: #f5f7fa; border-top: 1px solid #e2e8f0; padding: 12px 16px; }
            QDialogButtonBox QPushButton { background-color: #3498db; color: #ffffff; border: none; border-radius: 8px; padding: 10px 18px; min-width: 110px; font-weight: bold; }
            QDialogButtonBox QPushButton:hover { background-color: #2980b9; }
        """)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Promoción: {nombre_promo}"))

        if getattr(self, "validar_stock", False):
            max_disponible = self.verificarStockDisponible(nombre_promo, False)
            info_texto = f"Máximo disponible: {max_disponible} unidades" if max_disponible > 0 else "Stock insuficiente"
            spin = QSpinBox()
            spin.setRange(1, max(1, max_disponible))
            spin.setValue(1)
        else:
            info_texto = "Sin validar stock (entrada libre)"
            spin = QSpinBox()
            spin.setRange(1, 9999)
            spin.setValue(1)
        info_label = QLabel(info_texto)
        layout.addWidget(info_label)
        layout.addWidget(QLabel("Cantidad de promociones:"))
        layout.addWidget(spin)

        tipoLocal = QRadioButton("Local")
        tipoLlevar = QRadioButton("Para llevar")
        tipoLocal.setChecked(True)
        layout.addWidget(tipoLocal)
        layout.addWidget(tipoLlevar)

        productos_con_ingredientes = [p for p in productos_promo if self._obtenerIngredientesProducto(p['nombre'])]
        exclusiones_promo_seleccionadas = {}
        extras_promo_seleccionadas = {}
        cantidad_al_personalizar = [0]

        if productos_con_ingredientes:
            btn_personalizar = QPushButton("Personalizar ingredientes por producto")
            btn_personalizar.setStyleSheet("""
                QPushButton { background-color: #8e44ad; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; font-size: 13px; }
                QPushButton:hover { background-color: #7d3c98; }
            """)
            lbl_exclusiones = QLabel("Sin exclusiones")
            lbl_exclusiones.setStyleSheet("""
                QLabel { font-size: 12px; color: #27ae60; padding: 4px 8px; background-color: #eafaf1; border-radius: 4px; border: 1px solid #a9dfbf; }
            """)
            lbl_exclusiones.setWordWrap(True)

            lbl_extras = QLabel("Sin ingredientes extra")
            lbl_extras.setStyleSheet("""
                QLabel { font-size: 12px; color: #27ae60; padding: 4px 8px; background-color: #eafaf1; border-radius: 4px; border: 1px solid #a9dfbf; }
            """)
            lbl_extras.setWordWrap(True)

            def abrir_exclusiones_promo():
                nonlocal exclusiones_promo_seleccionadas, extras_promo_seleccionadas
                cantidad_actual = spin.value()
                cantidad_al_personalizar[0] = cantidad_actual
                productos_expandidos = []
                for p in productos_promo:
                    productos_expandidos.append(
                        {'idProd': p['idProd'], 'nombre': p['nombre'], 'cantidad': p['cantidad'] * cantidad_actual}
                    )
                resultado_excl, resultado_extra = self._dialogoExclusionesPromo(
                    nombre_promo, productos_expandidos, exclusiones_promo_seleccionadas, extras_promo_seleccionadas
                )
                if resultado_excl is not None:
                    exclusiones_promo_seleccionadas = resultado_excl
                    extras_promo_seleccionadas = resultado_extra or {}
                    if exclusiones_promo_seleccionadas:
                        texto = self._textoExclusionesPromo(exclusiones_promo_seleccionadas)
                        lbl_exclusiones.setText(texto)
                        lbl_exclusiones.setStyleSheet("""
                            QLabel { font-size: 12px; color: #c0392b; padding: 4px 8px; background-color: #fdecea; border-radius: 4px; border: 1px solid #f5c6cb; }
                        """)
                    else:
                        lbl_exclusiones.setText("Sin exclusiones")
                        lbl_exclusiones.setStyleSheet("""
                            QLabel { font-size: 12px; color: #27ae60; padding: 4px 8px; background-color: #eafaf1; border-radius: 4px; border: 1px solid #a9dfbf; }
                        """)
                    if extras_promo_seleccionadas:
                        texto_extra = self._textoExtrasPromo(extras_promo_seleccionadas)
                        lbl_extras.setText(texto_extra)
                        lbl_extras.setStyleSheet("""
                            QLabel { font-size: 12px; color: #27ae60; padding: 4px 8px; background-color: #eafaf1; border-radius: 4px; border: 1px solid #a9dfbf; }
                        """)
                    else:
                        lbl_extras.setText("Sin ingredientes extra")
                        lbl_extras.setStyleSheet("""
                            QLabel { font-size: 12px; color: #27ae60; padding: 4px 8px; background-color: #eafaf1; border-radius: 4px; border: 1px solid #a9dfbf; }
                        """)

            def on_spin_changed(nuevo_valor):
                nonlocal exclusiones_promo_seleccionadas
                if (
                    exclusiones_promo_seleccionadas
                    and cantidad_al_personalizar[0] > 0
                    and nuevo_valor != cantidad_al_personalizar[0]
                ):
                    lbl_exclusiones.setText(
                        f"⚠ Personalizaste para {cantidad_al_personalizar[0]} promocion(es) — la cantidad cambió, personaliza de nuevo si es necesario"
                    )
                    lbl_exclusiones.setStyleSheet("""
                        QLabel { font-size: 12px; color: #e67e22; padding: 4px 8px; background-color: #fef9e7; border-radius: 4px; border: 1px solid #f39c12; }
                    """)

            spin.valueChanged.connect(on_spin_changed)
            btn_personalizar.clicked.connect(abrir_exclusiones_promo)
            layout.addWidget(btn_personalizar)
            layout.addWidget(lbl_exclusiones)
            layout.addWidget(lbl_extras)

        footer_promo = QHBoxLayout()
        footer_promo.setSpacing(12)
        btn_cancelar_promo = QPushButton("Cancelar")
        btn_cancelar_promo.setCursor(Qt.PointingHandCursor)
        btn_cancelar_promo.setStyleSheet("""
            QPushButton { background-color: #95a5a6; color: white; border: none; border-radius: 8px;
                font-size: 14px; font-weight: bold; padding: 10px 16px; min-width: 100px; }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        btn_confirmar_promo = QPushButton("Confirmar")
        btn_confirmar_promo.setCursor(Qt.PointingHandCursor)
        btn_confirmar_promo.setStyleSheet("""
            QPushButton { background-color: #2ecc71; color: white; border: none; border-radius: 8px;
                font-size: 14px; font-weight: bold; padding: 10px 16px; min-width: 100px; }
            QPushButton:hover { background-color: #27ae60; }
        """)
        footer_promo.addStretch()
        footer_promo.addWidget(btn_cancelar_promo)
        footer_promo.addWidget(btn_confirmar_promo)
        layout.addLayout(footer_promo)
        btn_cancelar_promo.clicked.connect(dialog.reject)
        btn_confirmar_promo.clicked.connect(dialog.accept)

        if dialog.exec_() == QDialog.Accepted:
            tipo = "Local" if tipoLocal.isChecked() else "Para llevar"
            self.agregarPromocionTabla(
                nombre_promo,
                spin.value(),
                tipo,
                productos_promo,
                exclusiones_promo_seleccionadas,
                extras_promo_seleccionadas,
            )

    def agregarPromocionTabla(
        self, nombre_promo, cantidad, tipo, productos_promo, exclusiones_por_producto=None, extras_por_producto=None
    ):
        if self.verificarBloqueo("agregar productos"):
            return
        exclusiones_por_producto = exclusiones_por_producto or {}
        extras_por_producto = extras_por_producto or {}
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT precioProm FROM Promocion WHERE nomProm=?", (nombre_promo,))
        precio_base_promo = float(self.cursor.fetchone()[0])

        costo_extras_total = sum(
            extra["cantidadExtra"] * extra["precioExtra"]
            for lista_unidades in (extras_por_producto or {}).values()
            for unidad_data in lista_unidades
            for extra in unidad_data["extras"]
        )
        costo_extras_por_combo = (costo_extras_total / cantidad) if cantidad > 0 else 0
        precio_unitario = precio_base_promo + costo_extras_por_combo

        texto_exclusiones_nuevo = self._textoExclusionesPromo(exclusiones_por_producto)
        texto_extras_nuevo = self._textoExtrasPromo(extras_por_producto)
        texto_personalizacion_nuevo = " | ".join(t for t in [texto_exclusiones_nuevo, texto_extras_nuevo] if t)

        for row in range(self.tabla.rowCount()):
            if self.tabla.item(row, 1).text() == tipo and self.tabla.item(row, 2).data(Qt.UserRole) == nombre_promo:
                datos_fila = (
                    self.exclusiones_promo_por_fila.get(row, {}) if hasattr(self, 'exclusiones_promo_por_fila') else {}
                )
                excl_promo_fila = datos_fila.get('exclusiones', {})
                extras_promo_fila = datos_fila.get('extras', {})
                texto_excl_fila = self._textoExclusionesPromo(excl_promo_fila)
                texto_extras_fila = self._textoExtrasPromo(extras_promo_fila)
                texto_personalizacion_fila = " | ".join(t for t in [texto_excl_fila, texto_extras_fila] if t)
                if texto_personalizacion_fila == texto_personalizacion_nuevo:
                    cant_actual = int(self.tabla.item(row, 0).text()) + cantidad
                    self.tabla.item(row, 0).setText(str(cant_actual))
                    self.tabla.item(row, 4).setText(f"{cant_actual * precio_unitario:.2f}")
                    self.recalcularTotal()
                    self.conn.close()
                    return

        row = self.tabla.rowCount()
        self.tabla.insertRow(row)
        nombre_display = (
            nombre_promo if not texto_personalizacion_nuevo else f"{nombre_promo}\n({texto_personalizacion_nuevo})"
        )

        tooltip_cantidad = f"Cantidad: {cantidad}"
        tooltip_tipo = f"Tipo de consumo: {tipo}"
        tooltip_producto = "🖱 Haga clic para ver el detalle completo" + (
            f"\n({texto_personalizacion_nuevo})" if texto_personalizacion_nuevo else ""
        )
        tooltip_precio = f"Precio unitario: {precio_unitario:.2f} Bs"
        tooltip_subtotal = f"Subtotal: {cantidad * precio_unitario:.2f} Bs"

        item_cantidad = QTableWidgetItem(str(cantidad))
        item_cantidad.setTextAlignment(Qt.AlignCenter)
        item_cantidad.setToolTip(tooltip_cantidad)
        self.tabla.setItem(row, 0, item_cantidad)

        item_tipo = QTableWidgetItem(tipo)
        item_tipo.setTextAlignment(Qt.AlignCenter)
        item_tipo.setToolTip(tooltip_tipo)
        self.tabla.setItem(row, 1, item_tipo)

        item_nombre = QTableWidgetItem(nombre_display)
        item_nombre.setTextAlignment(Qt.AlignCenter)
        item_nombre.setData(Qt.UserRole, nombre_promo)
        item_nombre.setToolTip(tooltip_producto)
        if texto_personalizacion_nuevo:
            item_nombre.setForeground(QColor("#c0392b"))
        self.tabla.setItem(row, 2, item_nombre)

        item_precio = QTableWidgetItem(f"{precio_unitario:.2f}")
        item_precio.setTextAlignment(Qt.AlignCenter)
        item_precio.setToolTip(tooltip_precio)
        self.tabla.setItem(row, 3, item_precio)

        total = cantidad * precio_unitario
        item_total = QTableWidgetItem(f"{total:.2f}")
        item_total.setTextAlignment(Qt.AlignCenter)
        item_total.setToolTip(tooltip_subtotal)
        self.tabla.setItem(row, 4, item_total)

        btn_container = QWidget()
        btn_container.setStyleSheet("background: transparent;")
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)

        btn = QPushButton("🗑️")
        btn.setFixedSize(90, 30)
        btn.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 6px; font-size: 14px; font-weight: bold; min-width: 90px; margin: 0px; padding: 0px; }
            QPushButton:hover { background-color: #c0392b; }
            QPushButton:pressed { background-color: #a93226; }
        """)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip("Eliminar producto")
        btn.clicked.connect(lambda _, r=row: self.eliminarFila(r))
        btn_layout.addWidget(btn, 0, Qt.AlignCenter)
        self.tabla.setCellWidget(row, 5, btn_container)

        self.exclusiones_por_fila[row] = []
        self.extras_por_fila[row] = []
        if not hasattr(self, 'exclusiones_promo_por_fila'):
            self.exclusiones_promo_por_fila = {}
        self.exclusiones_promo_por_fila[row] = {
            'productos_promo': productos_promo,
            'exclusiones': exclusiones_por_producto,
            'extras': extras_por_producto,
            'cantidad_promociones': cantidad,
        }

        self.tabla.setRowHeight(row, 80 if texto_personalizacion_nuevo else 50)
        self.tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.tabla.setColumnWidth(5, 110)
        self.recalcularTotal()
        self.conn.close()

    def _guardarExclusionesPromo(self, id_detalle_venta, exclusiones_por_producto):
        for id_prod_str, unidades_data in exclusiones_por_producto.items():
            for unidad_data in unidades_data:
                unidad_idx = unidad_data['unidad']
                for excl in unidad_data['exclusiones']:
                    self.cursor.execute(
                        """
                        INSERT INTO DetallesVentaExclusionesPromo (idDetalleVenta, idProd, idIng, nomIng, numUnidad)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        (id_detalle_venta, int(id_prod_str), excl["idIng"], excl["nomIng"], unidad_idx),
                    )

    def _guardarExtrasPromo(self, id_detalle_venta, extras_por_producto):
        if not extras_por_producto:
            return
        for id_prod_str, unidades_data in extras_por_producto.items():
            for unidad_data in unidades_data:
                unidad_idx = unidad_data['unidad']
                for extra in unidad_data['extras']:
                    self.cursor.execute(
                        """
                        INSERT INTO DetallesVentaExtras (idDetalleVenta, idIng, nomIng, cantidadExtra, precioExtra, idProd, numUnidad)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            id_detalle_venta,
                            extra["idIng"],
                            extra["nomIng"],
                            extra["cantidadExtra"],
                            extra["precioExtra"],
                            int(id_prod_str),
                            unidad_idx,
                        ),
                    )


if __name__ == "__main__":
    aplicacion = QApplication(sys.argv)
    pagina = RegistrarPedidos("DIRECTORIO")
    pagina.show()
    sys.exit(aplicacion.exec_())
