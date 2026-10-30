import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
import math
from datetime import datetime
from Rutas import get_db_path

DB_PATH = get_db_path()

class Familia(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget{
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
                background-color: #3b78c7;
            }
            
            QPushButton:pressed {
                background-color: #2a69b5;
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
        """)
        
        self.set_up()
        
    def set_up(self):
        self.layoutDatos = QHBoxLayout()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20,20,20,20)
        self.anadirAreaRegistro()
        self.showMaximized()
   
    def anadirAreaRegistro(self):
        contenedorSeccion = QWidget()
        layoutSeccion = QHBoxLayout()
        contenedorSeccion.setLayout(layoutSeccion)
        campoDatos = QWidget()
        campoDatos.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
                border: 1px solid #e2e8f0;
            }
        """)
        layoutDatos = QVBoxLayout()
        campoDatos.setLayout(layoutDatos)
        layoutEleccion = QHBoxLayout()
        self.etiqueta = QLabel("Area de interes")
        self.opcion1 = QRadioButton("Promociones")
        self.opcion2 = QRadioButton("Productos")
        layoutEleccion.addWidget(self.opcion1)
        layoutEleccion.addWidget(self.opcion2)
        self.opcion1.clicked.connect(self.desHabilitarCampos)
        self.opcion2.clicked.connect(self.HabilitarCampos)
        self.etiquetaCategoria = QLabel("Categoria de Productos")
        self.categoria = QComboBox()
        self.cargarCategorias()
        self.categoria.currentIndexChanged.connect(self.cargarSubcategorias)
        self.categoria.currentIndexChanged.connect(lambda: self.detalles.setText(""))
        self.etiquetaSubcategorias = QLabel("Subcategoria de Productos")
        self.subcategorias = QComboBox()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""SELECT nombre FROM Subcategoria WHERE activa=TRUE""")
        resultados = c.fetchall()
        conn.close()
        lista = [elem[0] for elem in resultados]
        self.subcategorias.addItems(lista)
        self.subcategorias.setCurrentIndex(-1)
        self.subcategorias.currentIndexChanged.connect(lambda: self.detalles.setText(""))
        self.etiquetaDetalles = QLabel("Detalles")
        self.detalles = QTextEdit("")
        self.detalles.setReadOnly(True)
        botonGenerar = QPushButton("GENERAR PRODUCTOS")
        botonGenerar.setCursor(Qt.PointingHandCursor)
        botonGenerar.clicked.connect(self.generarProductos)
        self.etiquetaCategoria.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 15px;
            margin-bottom: 8px;
        """)
        self.etiquetaSubcategorias.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 15px;
            margin-bottom: 8px;
        """)
        self.etiquetaDetalles.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 15px;
            margin-bottom: 8px;
        """)
        self.detalles.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #012345;
            padding: 3px;
            font-weight: bold;
        """)
        botonGenerar.setStyleSheet("""
            QPushButton {
                background-color: #4a89dc;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #3b78c7;
            }
            QPushButton:pressed {
                background-color: #2a69b5;
            }
        """)
        layoutDatos.addWidget(self.etiqueta)
        layoutDatos.addLayout(layoutEleccion)
        layoutDatos.addWidget(self.etiquetaCategoria)
        layoutDatos.addWidget(self.categoria)
        layoutDatos.addWidget(self.etiquetaSubcategorias)
        layoutDatos.addWidget(self.subcategorias)
        layoutDatos.addWidget(self.etiquetaDetalles)
        layoutDatos.addWidget(self.detalles)
        layoutDatos.addWidget(botonGenerar)
        layoutSeccion.addWidget(campoDatos, stretch=2)
        contenedorMesas = QWidget()
        self.layoutMesas = QVBoxLayout()
        contenedorMesas.setLayout(self.layoutMesas)
        scroll = QScrollArea()
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        scroll.setWidget(contenedorMesas)
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layoutSeccion.addWidget(scroll, stretch=10)
        self.layoutPrincipal.addWidget(contenedorSeccion, stretch=8)
     

    def cargarSubcategorias(self):
        categoria = self.categoria.currentText()
        if not categoria:
            self.subcategorias.clear()
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("""SELECT idCategoria FROM Categoria WHERE nomCategoria=? AND activa=TRUE""", (categoria,))
            resultado = c.fetchone()
            if resultado is None:
                self.subcategorias.clear()
                conn.close()
                return
            indiceCategoria = resultado[0]
            c.execute("""SELECT nombre FROM Subcategoria WHERE idCategoria=? AND activa=TRUE""", (indiceCategoria,))
            resultados = c.fetchall()
            if resultados:
                lista = [elem[0] for elem in resultados]
                self.subcategorias.clear()
                self.subcategorias.addItems(lista)
                self.subcategorias.setCurrentIndex(-1)
            else:
                self.subcategorias.clear() 
        except Exception as e:
            print(f"Error en cargarSubcategorias: {e}")
        finally:
            conn.close()
    
    def cargarCategorias(self):
        self.categoria.clear()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("""SELECT nomCategoria FROM Categoria WHERE activa=TRUE""")
            resultados = c.fetchall()
            if resultados:
                listaCategorias = [elem[0] for elem in resultados]
                self.categoria.addItems(listaCategorias)
                self.categoria.setCurrentIndex(-1)  
        except Exception as e:
            print(f"Error en cargarCategorias: {e}")
        finally:
            conn.close()
    
    def desHabilitarCampos(self):
        self.etiquetaCategoria.setVisible(False)
        self.categoria.setVisible(False)
        self.etiquetaSubcategorias.setVisible(False)
        self.subcategorias.setVisible(False)
        self.detalles.setText("")
        self.limpiarCampo(self.layoutMesas)
        
    def HabilitarCampos(self):
        self.etiquetaCategoria.setVisible(True)
        self.categoria.setVisible(True)
        self.etiquetaSubcategorias.setVisible(True)
        self.subcategorias.setVisible(True)
        self.detalles.setText("")
        self.limpiarCampo(self.layoutMesas)

    def generarProductos(self):
        self.limpiarCampo(self.layoutMesas)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if self.opcion1.isChecked():     
            c.execute("""SELECT * FROM Promocion WHERE activo=TRUE""")
            resultados = c.fetchall()
            conn.close()
            if not resultados:
                QMessageBox.information(self, "Sin resultados", "No se encontraron promociones activas")
                return
            self.mostrarPromociones(resultados)
        elif self.opcion2.isChecked():
            if self.categoria.currentText() == "" or self.subcategorias.currentText() == "":
                QMessageBox.information(self, "Rellenar campos solicitados", "Debe seleccionar una categoria y subcategoria de producto")
                conn.close()
                return
            c.execute("""
                SELECT P.* 
                FROM Producto P 
                JOIN Subcategoria S ON P.idSubcategoria = S.idSubcategoria 
                JOIN Categoria C ON S.idCategoria = C.idCategoria  
                WHERE P.activo=TRUE
                AND C.activa=TRUE
                AND S.activa=TRUE
                AND C.nomCategoria=? AND S.nombre=?
            """, (self.categoria.currentText(), self.subcategorias.currentText()))
            resultados = c.fetchall()
            conn.close()
            if not resultados:
                QMessageBox.information(self, "Sin resultados", "No se encontraron productos con los criterios seleccionados")
                return
            self.mostrarProductos(resultados)
        else:
            QMessageBox.information(self, "Rellenar campos solicitados", "Se debe seleccionar el area de interes")
            conn.close()
            return
    
    def mostrarPromociones(self, promociones):
        fila_actual = QHBoxLayout()
        fila_actual.setSpacing(10)
        for i, promocion in enumerate(promociones):
            if i % 10 == 0 and i != 0:
                self.layoutMesas.addLayout(fila_actual)
                fila_actual = QHBoxLayout()
                fila_actual.setSpacing(10)
            contenedorProm = QWidget()
            layoutPromocion = QVBoxLayout()
            layoutPromocion.setContentsMargins(5, 5, 5, 5)
            contenedorProm.setLayout(layoutPromocion)
            etiquetaNombre = QLabel(promocion[1])
            etiquetaNombre.setWordWrap(True)
            pixmap = QPixmap()
            if promocion[3]:
                pixmap.loadFromData(promocion[3])
            else:
                pixmap = QPixmap(90, 150)
                pixmap.fill(Qt.lightGray)
            etiquetaImagen = QLabel()
            etiquetaImagen.setPixmap(pixmap.scaled(90, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            etiquetaPrecio = QLabel(f"Precio: {promocion[2]} Bs")
            botonDetalles = QPushButton("Ver Detalles")
            botonDetalles.setFixedHeight(30)
            botonDetalles.setCursor(Qt.PointingHandCursor)
            botonDetalles.clicked.connect(lambda checked, idProm=promocion[0]: self.cargarDetallesPromocion(idProm))
            contenedorProm.setFixedHeight(240)
            contenedorProm.setFixedWidth(120)
            contenedorProm.setStyleSheet("""
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            """)
            botonDetalles.setStyleSheet("""
                background-color: #4a89dc;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                padding: 2px;
                min-width: 100px;
                max-width: 110px;
            """)
            etiquetaPrecio.setStyleSheet("""
                font-size: 13px;
                color: #38a169;
                font-weight: bold;
            """)
            etiquetaNombre.setStyleSheet("""
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                min-height: 40px;
            """)
            etiquetaImagen.setStyleSheet("""
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            """)
            layoutPromocion.addWidget(etiquetaNombre, alignment=Qt.AlignCenter)
            layoutPromocion.addWidget(etiquetaImagen, alignment=Qt.AlignCenter)
            layoutPromocion.addWidget(etiquetaPrecio, alignment=Qt.AlignCenter)
            layoutPromocion.addWidget(botonDetalles)
            fila_actual.addWidget(contenedorProm)
        resto = (10 - (len(promociones) % 10)) % 10
        if resto != 0 and len(promociones) > 0:
            for _ in range(resto):
                contenedorVacio = QWidget()
                contenedorVacio.setFixedHeight(240)
                contenedorVacio.setFixedWidth(120)
                contenedorVacio.setStyleSheet("""background-color: transparent;""")
                fila_actual.addWidget(contenedorVacio)
        if fila_actual.count() > 0:
            self.layoutMesas.addLayout(fila_actual)
        self.layoutMesas.addStretch(1)
    
    def mostrarProductos(self, productos):
        fila_actual = QHBoxLayout()
        fila_actual.setSpacing(10)
        for i, producto in enumerate(productos):
            if i % 10 == 0 and i != 0:
                self.layoutMesas.addLayout(fila_actual)
                fila_actual = QHBoxLayout()
                fila_actual.setSpacing(10)
            contenedorProd = QWidget()
            layoutProducto = QVBoxLayout()
            layoutProducto.setContentsMargins(5, 5, 5, 5)
            contenedorProd.setLayout(layoutProducto)
            etiquetaNombre = QLabel(producto[1])
            etiquetaNombre.setWordWrap(True)
            pixmap = QPixmap()
            if producto[6]:
                pixmap.loadFromData(producto[6])
            else:
                pixmap = QPixmap(90, 150)
                pixmap.fill(Qt.lightGray)
            etiquetaImagen = QLabel()
            etiquetaImagen.setPixmap(pixmap.scaled(90, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            etiquetaVenta = QLabel(f"Venta: {producto[3]} Bs")
            etiquetaCosto = QLabel(f"Costo: {producto[4]} Bs")
            botonDetalles = QPushButton("Ver Detalles")
            botonDetalles.setFixedHeight(30)
            botonDetalles.setCursor(Qt.PointingHandCursor)
            botonDetalles.clicked.connect(lambda checked, idProd=producto[0]: self.cargarDetallesProducto(idProd))
            contenedorProd.setFixedHeight(240)
            contenedorProd.setFixedWidth(120)
            contenedorProd.setStyleSheet("""
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            """)
            botonDetalles.setStyleSheet("""
                background-color: #4a89dc;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                padding: 2px;
                min-width: 100px;
                max-width: 110px;
            """)
            etiquetaVenta.setStyleSheet("""
                font-size: 12px;
                color: #38a169;
                font-weight: bold;
            """)
            etiquetaCosto.setStyleSheet("""
                font-size: 12px;
                color: #e74c3c;
                font-weight: bold;
            """)
            etiquetaNombre.setStyleSheet("""
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                min-height: 40px;
            """)
            etiquetaImagen.setStyleSheet("""
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            """)
            layoutProducto.addWidget(etiquetaNombre, alignment=Qt.AlignCenter)
            layoutProducto.addWidget(etiquetaImagen, alignment=Qt.AlignCenter)
            layoutProducto.addWidget(etiquetaVenta, alignment=Qt.AlignCenter)
            layoutProducto.addWidget(etiquetaCosto, alignment=Qt.AlignCenter)
            layoutProducto.addWidget(botonDetalles)
            fila_actual.addWidget(contenedorProd)
        resto = (10 - (len(productos) % 10)) % 10
        if resto != 0 and len(productos) > 0:
            for _ in range(resto):
                contenedorVacio = QWidget()
                contenedorVacio.setFixedHeight(240)
                contenedorVacio.setFixedWidth(120)
                contenedorVacio.setStyleSheet("""background-color: transparent;""")
                fila_actual.addWidget(contenedorVacio)
        if fila_actual.count() > 0:
            self.layoutMesas.addLayout(fila_actual)
        self.layoutMesas.addStretch(1)
    
    def cargarDetallesPromocion(self, idProm):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT P.nomProd, PP.cantidadProdProm 
            FROM PromocionProd PP
            JOIN Producto P ON PP.idProd = P.idProd 
            WHERE PP.idProm=?
        """, (idProm,))
        productos = c.fetchall()
        c.execute("""
            SELECT fechaEspecifica, fechaInicio, fechaFin, horaInicio, horaFin 
            FROM Promocion WHERE idProm=?
        """, (idProm,))
        promocion_data = c.fetchone()
        c.execute("""
            SELECT diaSemana FROM PromocionDias WHERE idProm=? ORDER BY diaSemana
        """, (idProm,))
        dias = c.fetchall()
        conn.close()
        
        html = """
        <style>
            .titulo { color: #2c3e50; font-size: 16px; font-weight: bold; margin-top: 10px; }
            .producto { color: #27ae60; font-size: 14px; margin-left: 10px; }
            .fecha { color: #e67e22; font-size: 14px; }
            .hora { color: #3498db; font-size: 14px; }
            .dias { color: #9b59b6; font-size: 14px; }
            .activo { color: #27ae60; font-size: 14px; font-weight: bold; }
            .inactivo { color: #e74c3c; font-size: 14px; font-weight: bold; }
            .info { color: #7f8c8d; font-size: 13px; font-style: italic; }
            hr { border: 1px solid #ecf0f1; }
        </style>
        """
        
        html += "<div class='titulo'>📦 PRODUCTOS</div>"
        for nom_prod, cantidad in productos:
            html += f"<div class='producto'>• {cantidad}x {nom_prod}</div>"
        
        html += "<hr>"
        html += "<div class='titulo'>⏰ DISPONIBILIDAD</div>"
        
        fecha_especifica = promocion_data[0]
        fecha_inicio = promocion_data[1]
        fecha_fin = promocion_data[2]
        hora_inicio = promocion_data[3]
        hora_fin = promocion_data[4]
        
        ahora = datetime.now()
        fecha_actual = ahora.date()
        hora_actual = ahora.time()
        dia_semana_actual = ahora.weekday() + 1
        disponible_ahora = True
        
        if fecha_especifica:
            try:
                fecha_esp = datetime.strptime(fecha_especifica, "%Y-%m-%d").date()
                if fecha_esp != fecha_actual:
                    disponible_ahora = False
                html += f"<div class='fecha'>• Fecha específica: {fecha_esp.strftime('%d/%m/%Y')}</div>"
            except Exception:
                html += "<div class='inactivo'>• Fecha específica: Formato inválido</div>"
                disponible_ahora = False
        elif fecha_inicio and fecha_fin:
            try:
                fecha_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                fecha_f = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                if not (fecha_ini <= fecha_actual <= fecha_f):
                    disponible_ahora = False
                html += f"<div class='fecha'>• Período: {fecha_ini.strftime('%d/%m/%Y')} - {fecha_f.strftime('%d/%m/%Y')}</div>"
            except Exception:
                html += "<div class='inactivo'>• Período: Formato inválido</div>"
                disponible_ahora = False
        else:
            html += "<div class='info'>• Período: Sin restricción de fechas</div>"

        # Los días de la semana son una restricción independiente del tipo de
        # fecha configurado: se evalúan y se muestran siempre que existan,
        # ya sea que la promoción tenga fecha específica, rango de fechas,
        # o ninguna restricción de fecha (es decir, "todas las semanas").
        if dias:
            dias_numeros = [dia[0] for dia in dias]
            dia_nombres = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            dias_texto = [dia_nombres[dia_num-1] for dia_num in dias_numeros if 1 <= dia_num <= 7]

            if dia_semana_actual not in dias_numeros:
                disponible_ahora = False

            if dias_texto:
                html += f"<div class='dias'>• Días disponibles: {', '.join(dias_texto)}</div>"

        if hora_inicio and hora_fin and hora_inicio != "00:00:00" and hora_fin != "23:59:59":
            try:
                hora_ini = datetime.strptime(hora_inicio, "%H:%M:%S").time()
                hora_f = datetime.strptime(hora_fin, "%H:%M:%S").time()
                if not (hora_ini <= hora_actual <= hora_f):
                    disponible_ahora = False
                html += f"<div class='hora'>• Horario: {hora_ini.strftime('%H:%M')} - {hora_f.strftime('%H:%M')}</div>"
            except Exception:
                html += "<div class='inactivo'>• Horario: Formato inválido</div>"
        else:
            html += "<div class='info'>• Horario: Todo el día</div>"
        
        html += "<hr>"
        html += "<div class='titulo'>🔴 ESTADO ACTUAL</div>"
        if disponible_ahora:
            html += "<div class='activo'>• ✅ PROMOCIÓN ACTIVA AHORA</div>"
        else:
            html += "<div class='inactivo'>• ❌ PROMOCIÓN NO DISPONIBLE AHORA</div>"

        self.detalles.setHtml(html)
    
    def cargarDetallesProducto(self, idProd):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT descripcion FROM Producto WHERE idProd=?", (idProd,))
        desc_row = c.fetchone()
        descripcion = desc_row[0] if desc_row else ""
        c.execute("""
            SELECT S.nomIng, PI.cantidadIngNecesitada, S.cantidadStock, S.unidadMedida
            FROM ProductosIngredientes PI
            JOIN Stock S ON PI.idIng = S.idIng
            WHERE PI.idProd = ?
        """, (idProd,))
        ingredientes = c.fetchall()
        conn.close()
        
        html = """
        <style>
            .titulo { color: #2c3e50; font-size: 16px; font-weight: bold; margin-top: 10px; }
            .descripcion { color: #34495e; font-size: 14px; background: #f8f9fa; padding: 8px; border-radius: 5px; }
            .ingrediente { color: #e67e22; font-size: 14px; margin-left: 10px; }
            .stock { color: #3498db; font-size: 14px; margin-left: 10px; }
            .warning { color: #f39c12; font-size: 14px; font-weight: bold; }
            .error { color: #e74c3c; font-size: 14px; font-weight: bold; }
            .success { color: #27ae60; font-size: 14px; }
            .info { color: #7f8c8d; font-size: 13px; font-style: italic; }
            hr { border: 1px solid #ecf0f1; }
            .stock-alto { color: #27ae60; font-size: 14px; }
            .stock-bajo { color: #e67e22; font-size: 14px; }
            .stock-cero { color: #e74c3c; font-size: 14px; }
        </style>
        """
        
        html += "<div class='titulo'>📝 DESCRIPCIÓN</div>"
        html += f"<div class='descripcion'>{descripcion or '—'}</div>"
        
        html += "<hr>"
        html += "<div class='titulo'>🥗 INGREDIENTES NECESARIOS</div>"
        
        max_productos = float('inf')
        detalles_ingredientes = []
        
        for nom_ing, cant_necesaria, cant_stock, unidad in ingredientes:
            cant_necesaria = cant_necesaria or 0
            cant_stock = cant_stock or 0
            unidad = unidad or ""
            
            stock_class = "stock-alto"
            if cant_stock == 0:
                stock_class = "stock-cero"
            elif cant_stock < 10:
                stock_class = "stock-bajo"
            
            if cant_necesaria > 0:
                productos_posibles = cant_stock / cant_necesaria
                max_productos = min(max_productos, productos_posibles)
                detalles_ingredientes.append(
                    f"<div class='ingrediente'>• {nom_ing}:</div>"
                    f"<div class='{stock_class}'>  - Necesario: {cant_necesaria} {unidad}</div>"
                    f"<div class='{stock_class}'>  - Stock: {cant_stock} {unidad}</div>"
                )
        
        if detalles_ingredientes:
            for det in detalles_ingredientes:
                html += det
        else:
            html += "<div class='info'>• (sin ingredientes registrados)</div>"
        
        html += "<hr>"
        html += "<div class='titulo'>📊 CÁLCULO DE PRODUCCIÓN</div>"
        
        if not ingredientes or not detalles_ingredientes:
            unidades_str = "indeterminado"
            html += f"<div class='info'>• Se pueden fabricar aproximadamente: {unidades_str} unidades</div>"
        elif math.isinf(max_productos):
            unidades_str = "∞"
            html += f"<div class='success'>• Se pueden fabricar aproximadamente: {unidades_str} unidades</div>"
        elif math.isnan(max_productos) or max_productos < 0:
            unidades_str = "indeterminado"
            html += f"<div class='info'>• Se pueden fabricar aproximadamente: {unidades_str} unidades</div>"
        else:
            unidades = max(0, math.floor(max_productos))
            if unidades == 0:
                html += f"<div class='error'>• Se pueden fabricar aproximadamente: {unidades} unidades</div>"
            elif unidades < 5:
                html += f"<div class='warning'>• Se pueden fabricar aproximadamente: {unidades} unidades</div>"
            else:
                html += f"<div class='success'>• Se pueden fabricar aproximadamente: {unidades} unidades</div>"
        
        if not ingredientes or not detalles_ingredientes:
            html += "<div class='warning'>⚠️ No se encontraron ingredientes registrados para este producto</div>"
        else:
            if not math.isfinite(max_productos):
                html += "<div class='info'>⚠️ Cálculo no acotado por falta de insumos limitantes</div>"
            elif max_productos == 0:
                html += "<div class='error'>❌ Stock insuficiente para fabricar ninguna unidad</div>"
            elif max_productos < 5:
                html += "<div class='warning'>⚠️ Stock bajo - considerar reabastecimiento</div>"
        
        self.detalles.setHtml(html)
    
    def limpiarCampo(self, layout):
        if layout is None:
            return
        while layout.count() > 0:
            hijo = layout.takeAt(0)
            if hijo.widget():
                hijo.widget().deleteLater()
            else:
                if hijo.layout():
                    self.limpiarCampo(hijo.layout())
                    hijo.layout().deleteLater()
    
    def cerrarVentana(self):
        self.close()
        
        
if __name__ == "__main__":
    aplicacion = QApplication(sys.argv)
    pagina = Familia()
    pagina.show()
    sys.exit(aplicacion.exec_())