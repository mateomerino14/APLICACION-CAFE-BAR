import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from Rutas import get_db_path, get_resource_path

DB_PATH = get_db_path()
DIRECCION_IMAGEN = get_resource_path('Imagenes')


class Pop_up_ModificacionProductos(QDialog):
    def __init__(self, id_prod, producto_data, ingredientes_data, parent=None):
        super().__init__(parent)
        self.id_prod = id_prod
        self.setWindowTitle("MODIFICAR PRODUCTO")
        self.setFixedSize(1000, 750)

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e6f7ff, stop: 1 #cce6ff);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                font-weight: bold;
                color: #2c3e50;
                font-size: 14px;
                min-width: 120px;
                padding: 2px;
            }
            QLineEdit, QComboBox {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QTextEdit{
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #2980b9;
                background-color: #f8f9fa;
            }
            QTextEdit:focus{
                border: 2px solid #2980b9;
                background-color: #f8f9fa;
            }
            QComboBox QAbstractItemView {
                background-color:white;
                font-size:12px;
                font-weight: bold;
                selection-background-color: #3498db;
                selection-color: white;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #3498db;
                width: 0;
                height: 0;
                margin-right: 10px;
            }
            QComboBox[popupShown="true"]::down-arrow {
                border-bottom: 5px solid #3498db;
                border-top: none;
            }
            QPushButton {
                border-radius: 6px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 14px;
                border: none;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                transform: translateY(1px);
            }
            QMessageBox {
                background: #ffffff;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 15px;
                font-weight: 500;
                min-width:325px;
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
        layoutPrincipal = QVBoxLayout()
        layoutPrincipal.setSpacing(15)
        layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layoutPrincipal)
        titulo = QLabel("MODIFICAR PRODUCTO")
        titulo.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y1: 0,
                stop: 0 #3498db, stop: 1 #2980b9);
            border-radius: 10px;
            color: white;
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layoutPrincipal.addWidget(titulo)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #f0f0f0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #3498db;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2980b9;
            }
        """)
        contenido_widget = QWidget()
        contenido_layout = QVBoxLayout(contenido_widget)
        contenido_layout.setSpacing(20)
        imagen_layout = QHBoxLayout()
        imagen_layout.addStretch()
        self.imagen = QPushButton()
        self.imagen.setFixedSize(220, 220)
        self.imagen.setStyleSheet("""
            QPushButton {
                border: 3px dashed #3498db;
                background: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                border: 3px dashed #2980b9;
                background: #f8f9fa;
            }
        """)
        self.imagen.setCursor(Qt.PointingHandCursor)
        self.imagen.clicked.connect(self.actualizarFoto)
        try:
            if producto_data and producto_data[4]:
                pixmap = QPixmap()
                pixmap.loadFromData(producto_data[4])
                self.imagen.setIcon(QIcon(pixmap))
            else:
                camara_path = get_resource_path(os.path.join('Imagenes', 'camara.png'))
                if os.path.exists(camara_path):
                    self.imagen.setIcon(QIcon(camara_path))
                else:
                    pixmap = QPixmap(200, 200)
                    pixmap.fill(QColor("#3498db"))
                    self.imagen.setIcon(QIcon(pixmap))
        except Exception as e:
            self.mostrarError(f"Error al cargar imagen: {str(e)}")
        self.imagen.setIconSize(QSize(210, 210))
        imagen_layout.addWidget(self.imagen)
        imagen_layout.addStretch()
        contenido_layout.addLayout(imagen_layout)
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame{
                background: white;
                border-radius: 10px;
                padding: 20px;
                border: 2px solid #e0e0e0;
            }
        """)
        form_layout = QGridLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(15, 15, 15, 15)
        self.campoNombre = QLineEdit(producto_data[0] if producto_data else "")
        nombre_producto_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ0-9°%.,\\-\\s]*")
        self.campoNombre.setValidator(QRegExpValidator(nombre_producto_regex))
        self.campoNombre.setMaxLength(30)
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT nomProd FROM Producto WHERE activo = 1 ORDER BY nomProd COLLATE NOCASE ASC")
            nombres_productos = [row[0] for row in c.fetchall()]
            conn.close()
        except Exception:
            nombres_productos = []
        completer_nombre = QCompleter(nombres_productos, self)
        completer_nombre.setCaseSensitivity(Qt.CaseInsensitive)
        completer_nombre.setFilterMode(Qt.MatchContains)
        self.campoNombre.setCompleter(completer_nombre)
        self.campoDescripcion = QTextEdit(producto_data[1] if producto_data and producto_data[1] else "")
        self.campoDescripcion.setMaximumHeight(80)
        MAX_LARGO_DESCRIPCION = 200

        def limitar_descripcion_edit():
            texto = self.campoDescripcion.toPlainText()
            if len(texto) > MAX_LARGO_DESCRIPCION:
                cursor = self.campoDescripcion.textCursor()
                posicion = cursor.position()
                self.campoDescripcion.blockSignals(True)
                self.campoDescripcion.setPlainText(texto[:MAX_LARGO_DESCRIPCION])
                cursor.setPosition(min(posicion, MAX_LARGO_DESCRIPCION))
                self.campoDescripcion.setTextCursor(cursor)
                self.campoDescripcion.blockSignals(False)

        self.campoDescripcion.textChanged.connect(limitar_descripcion_edit)
        self.campoDescripcion.setStyleSheet("""QTextEdit{
            background-color: white;
            border: 2px solid #3498db;
            border-radius: 6px;
            padding: 10px;
            font-size: 14px;
            selection-background-color: #3498db;
            selection-color: white;
        }
        QTextEdit:focus{
            border: 2px solid #2980b9;
            background-color: #f8f9fa;
        }""")
        self.campoPrecio = QLineEdit(str(producto_data[2]) if producto_data else "0.00")
        self.campoCosto = QLineEdit(str(producto_data[3]) if producto_data else "0.00")
        validador = QRegExpValidator(QRegExp(r"[0-9]{1,8}(\.[0-9]{0,2})?"))
        self.campoPrecio.setValidator(validador)
        self.campoPrecio.setMaxLength(11)
        self.campoCosto.setValidator(validador)
        self.campoCosto.setMaxLength(11)
        self.comboCategoria = QComboBox()
        self.comboSubcategoria = QComboBox()
        if producto_data:
            try:
                self.cargarComboboxes(producto_data[6], producto_data[5])
            except Exception as e:
                self.mostrarError(f"Error al cargar comboboxes: {str(e)}")
        form_layout.addWidget(QLabel("📝 Nombre:"), 0, 0)
        form_layout.addWidget(self.campoNombre, 0, 1)
        form_layout.addWidget(QLabel("📄 Descripción:"), 1, 0)
        form_layout.addWidget(self.campoDescripcion, 1, 1)
        form_layout.addWidget(QLabel("💰 Precio Venta:"), 2, 0)
        form_layout.addWidget(self.campoPrecio, 2, 1)
        form_layout.addWidget(QLabel("📊 Costo Fabricación:"), 3, 0)
        form_layout.addWidget(self.campoCosto, 3, 1)
        form_layout.addWidget(QLabel("🏷️ Categoría:"), 4, 0)
        form_layout.addWidget(self.comboCategoria, 4, 1)
        form_layout.addWidget(QLabel("🔖 Subcategoría:"), 5, 0)
        form_layout.addWidget(self.comboSubcategoria, 5, 1)
        contenido_layout.addWidget(form_container)
        ingredientes_container = QFrame()
        ingredientes_container.setFixedHeight(400)
        ingredientes_layout = QVBoxLayout(ingredientes_container)
        ingredientes_title = QLabel("🥗 Ingredientes del Producto")
        ingredientes_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background: #e8f4fc;
            border-radius: 8px;
        """)
        ingredientes_layout.addWidget(ingredientes_title)
        agregar_ingrediente_layout = QHBoxLayout()
        agregar_ingrediente_layout.setContentsMargins(0, 10, 0, 10)
        self.nuevo_ingrediente = QComboBox()
        self.nuevo_ingrediente.setEditable(True)
        self.nuevo_ingrediente.setInsertPolicy(QComboBox.NoInsert)
        self.nuevo_ingrediente.setMinimumHeight(35)
        self.nuevo_ingrediente.setMinimumWidth(250)
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.nuevo_ingrediente.setCompleter(self.completer)
        self.cargarIngredientesDisponibles()
        self.cantidad_nuevo = QLineEdit()
        self.cantidad_nuevo.setPlaceholderText("Cantidad")
        self.cantidad_nuevo.setValidator(validador)
        self.cantidad_nuevo.setMaxLength(11)
        self.cantidad_nuevo.setMinimumHeight(35)
        self.cantidad_nuevo.setMinimumWidth(120)
        self.descripcion_nuevo = QLabel()
        self.descripcion_nuevo.setVisible(False)
        btn_agregar = QPushButton("➕ Agregar")
        btn_agregar.setStyleSheet("""
            QPushButton {
                background: #2ecc71;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #27ae60;
            }
        """)
        btn_agregar.setCursor(Qt.PointingHandCursor)
        btn_agregar.setMinimumHeight(35)
        btn_agregar.clicked.connect(self.agregarIngrediente)
        agregar_ingrediente_layout.addWidget(QLabel("Ingrediente:"))
        agregar_ingrediente_layout.addWidget(self.nuevo_ingrediente)
        agregar_ingrediente_layout.addWidget(self.cantidad_nuevo)
        agregar_ingrediente_layout.addWidget(btn_agregar)
        ingredientes_layout.addLayout(agregar_ingrediente_layout)
        self.nuevo_ingrediente.currentIndexChanged.connect(
            lambda: self.actualizarDescripcionNuevo(
                self.nuevo_ingrediente.currentText(), self.descripcion_nuevo, self.cantidad_nuevo
            )
        )
        self.nuevo_ingrediente.editTextChanged.connect(
            lambda: self.actualizarDescripcionNuevo(
                self.nuevo_ingrediente.currentText(), self.descripcion_nuevo, self.cantidad_nuevo
            )
        )

        self.tablaIngredientes = QTableWidget()
        self.tablaIngredientes.setColumnCount(4)
        self.tablaIngredientes.setHorizontalHeaderLabels(["Ingrediente", "Cantidad", "Modificar", "Eliminar"])
        self.tablaIngredientes.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tablaIngredientes.verticalHeader().setVisible(False)
        self.tablaIngredientes.horizontalHeader().setStretchLastSection(False)
        header = self.tablaIngredientes.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.tablaIngredientes.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tablaIngredientes.setSelectionMode(QTableWidget.NoSelection)
        self.tablaIngredientes.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tablaIngredientes.setFocusPolicy(Qt.NoFocus)
        self.tablaIngredientes.setAlternatingRowColors(True)
        self.tablaIngredientes.setWordWrap(True)
        self.tablaIngredientes.setTextElideMode(Qt.ElideRight)
        self.tablaIngredientes.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
                font-size: 13px;
            }
            QTableWidget::item:hover {
                background: #e3f2fd;
            }
            QTableWidget::item:selected {
                background: #3498db;
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5dade2, stop: 1 #3498db);
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        if ingredientes_data:
            try:
                self.cargarIngredientes(ingredientes_data)
            except Exception as e:
                self.mostrarError(f"Error al cargar ingredientes: {str(e)}")
        ingredientes_layout.addWidget(self.tablaIngredientes)
        contenido_layout.addWidget(ingredientes_container)
        botones_container = QFrame()
        botones_container.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
                border: 2px solid #e0e0e0;
            }
        """)
        botones_layout = QHBoxLayout(botones_container)
        btnGuardar = QPushButton("Guardar Cambios")
        btnCancelar = QPushButton("Cancelar")
        btnGuardar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #27ae60, stop: 1 #219653);
                color: white;
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #219653, stop: 1 #1e8449);
            }
            QPushButton:pressed {
                background: #1e8449;
            }
        """)
        btnCancelar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e74c3c, stop: 1 #c0392b);
                color: white;
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c0392b, stop: 1 #a93226);
            }
            QPushButton:pressed {
                background: #a93226;
            }
        """)
        btnGuardar.clicked.connect(self.guardarCambios)
        btnCancelar.clicked.connect(self.reject)
        botones_layout.addStretch()
        botones_layout.addWidget(btnGuardar)
        botones_layout.addWidget(btnCancelar)
        botones_layout.addStretch()
        contenido_layout.addWidget(botones_container)
        scroll_area.setWidget(contenido_widget)
        layoutPrincipal.addWidget(scroll_area)

    def cargarIngredientesDisponibles(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            consulta = """SELECT nomIng FROM Stock WHERE disponible = 1 ORDER BY nomIng COLLATE NOCASE ASC"""
            c.execute(consulta)
            resultados = c.fetchall()
            conn.close()
            if resultados:
                elementos = [str(elem[0]) for elem in resultados]
                modelo = QStringListModel()
                modelo.setStringList(elementos)
                self.completer.setModel(modelo)
                self.nuevo_ingrediente.addItems(elementos)
            self.nuevo_ingrediente.setCurrentIndex(-1)
            self.nuevo_ingrediente.setEditText("")
        except Exception as e:
            self.mostrarError(f"Error al cargar ingredientes: {str(e)}")

    def actualizarDescripcionNuevo(self, textoIngrediente, campoDescripcion, campoCantidad):
        if not textoIngrediente:
            campoDescripcion.setText("")
            campoCantidad.setPlaceholderText("Cantidad")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            consulta = """SELECT descripcion, unidadMedida FROM Stock WHERE UPPER(nomIng)=UPPER(?)"""
            c.execute(consulta, (textoIngrediente,))
            dupla = c.fetchone()
            conn.close()
            if dupla is not None:
                campoDescripcion.setText(str(dupla[0]))
                campoCantidad.setPlaceholderText(f"{str(dupla[1])}")
            else:
                campoDescripcion.setText("")
                campoCantidad.setPlaceholderText("Cantidad")
        except Exception as e:
            self.mostrarError(f"Error al actualizar descripción: {str(e)}")

    def obtenerFilaDesdeBoton(self, boton):
        indice = self.tablaIngredientes.indexAt(boton.mapTo(self.tablaIngredientes.viewport(), QPoint(0, 0)))
        return indice.row()

    def agregarIngrediente(self):
        try:
            ingrediente = self.nuevo_ingrediente.currentText()
            cantidad = self.cantidad_nuevo.text()
            if not ingrediente or not cantidad:
                self.mostrarAdvertencia("Debe elegir un ingrediente y cantidad")
                return
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "SELECT nomIng, descripcion FROM Stock WHERE UPPER(nomIng)=UPPER(?) AND disponible = 1", (ingrediente,)
            )
            resultado = c.fetchone()
            if not resultado:
                conn.close()
                self.mostrarAdvertencia("El ingrediente seleccionado no existe o no está disponible")
                return
            descripcion = str(resultado[1]) if resultado[1] else ""
            conn.close()
            for i in range(self.tablaIngredientes.rowCount()):
                if self.tablaIngredientes.item(i, 0).text().upper() == ingrediente.upper():
                    self.mostrarAdvertencia("Este ingrediente ya está agregado al producto")
                    return
            fila = self.tablaIngredientes.rowCount()
            self.tablaIngredientes.insertRow(fila)
            item_nombre = QTableWidgetItem(ingrediente)
            item_nombre.setTextAlignment(Qt.AlignCenter)
            item_nombre.setToolTip(ingrediente)
            self.tablaIngredientes.setItem(fila, 0, item_nombre)
            item_nombre.setData(Qt.UserRole, descripcion)
            item_cantidad = QTableWidgetItem(str(cantidad))
            item_cantidad.setTextAlignment(Qt.AlignCenter)
            item_cantidad.setToolTip(str(cantidad))
            self.tablaIngredientes.setItem(fila, 1, item_cantidad)
            btnModificar = QPushButton("✏️")
            btnModificar.setStyleSheet("""
                QPushButton {
                    background: #f39c12;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #e67e22;
                }
            """)
            btnModificar.setCursor(Qt.PointingHandCursor)
            btnModificar.clicked.connect(lambda checked, b=btnModificar: self.modificarIngrediente(b))
            self.tablaIngredientes.setCellWidget(fila, 2, btnModificar)
            btnEliminar = QPushButton("🗑️")
            btnEliminar.setStyleSheet("""
                QPushButton {
                    background: #e74c3c;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #c0392b;
                }
            """)
            btnEliminar.setCursor(Qt.PointingHandCursor)
            btnEliminar.clicked.connect(lambda checked, b=btnEliminar: self.eliminarIngrediente(b))
            self.tablaIngredientes.setCellWidget(fila, 3, btnEliminar)
            self.tablaIngredientes.scrollToBottom()
            self.nuevo_ingrediente.setEditText("")
            self.nuevo_ingrediente.setCurrentIndex(-1)
            self.cantidad_nuevo.clear()
            self.cantidad_nuevo.setPlaceholderText("Cantidad")
            self.descripcion_nuevo.clear()
        except Exception as e:
            self.mostrarError(f"Error al agregar ingrediente: {str(e)}")

    def mostrarError(self, mensaje):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
        """)
        for label in msg.findChildren(QLabel):
            label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    color: black;
                    margin: 0px;
                    padding: 0px;
                    border: none;
                }
            """)
            if label.text() == mensaje:
                label.setContentsMargins(10, 0, 0, 0)
                label.setStyleSheet("""width:280px; background:transparent;""")
            elif label.pixmap() is not None:
                label.setContentsMargins(0, 0, 0, 0)
                label.setFixedSize(40, 40)
        msg.exec_()

    def mostrarAdvertencia(self, mensaje):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Advertencia")
        msg.setText(mensaje)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
        """)
        for label in msg.findChildren(QLabel):
            label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    color: black;
                    margin: 0px;
                    padding: 0px;
                    border: none;
                }
            """)
            if label.text() == mensaje:
                label.setContentsMargins(10, 0, 0, 0)
                label.setStyleSheet("""width:280px; background:transparent;""")
            elif label.pixmap() is not None:
                label.setContentsMargins(0, 0, 0, 0)
                label.setFixedSize(40, 40)
        msg.exec_()

    def mostrarExito(self, mensaje):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Éxito")
        msg.setText(mensaje)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
        """)
        for label in msg.findChildren(QLabel):
            label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    color: black;
                    margin: 0px;
                    padding: 0px;
                    border: none;
                }
            """)
            if label.text() == mensaje:
                label.setContentsMargins(10, 0, 0, 0)
                label.setStyleSheet("""width:280px; background:transparent;""")
            elif label.pixmap() is not None:
                label.setContentsMargins(0, 0, 0, 0)
                label.setFixedSize(40, 40)
        msg.exec_()

    def cargarComboboxes(self, categoria_actual, subcategoria_actual):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT nomCategoria FROM Categoria WHERE activa = 1 ORDER BY nomCategoria COLLATE NOCASE ASC")
            categorias = [str(item[0]) for item in c.fetchall()]
            self.comboCategoria.addItems(categorias)
            if categoria_actual in categorias:
                self.comboCategoria.setCurrentText(categoria_actual)
            self.comboCategoria.currentTextChanged.connect(self.actualizarSubcategorias)
            self.actualizarSubcategorias(categoria_actual)
            if subcategoria_actual:
                self.comboSubcategoria.setCurrentText(subcategoria_actual)
            conn.close()
        except Exception as e:
            self.mostrarError(f"Error al cargar comboboxes: {str(e)}")
            raise

    def actualizarSubcategorias(self, categoria):
        try:
            self.comboSubcategoria.clear()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                """SELECT S.nombre FROM Subcategoria S
                       JOIN Categoria C ON S.idCategoria = C.idCategoria
                       WHERE C.nomCategoria = ? AND S.activa = 1
                       ORDER BY S.nombre COLLATE NOCASE ASC""",
                (categoria,),
            )
            subcategorias = [str(item[0]) for item in c.fetchall()]
            self.comboSubcategoria.addItems(subcategorias)
            conn.close()
        except Exception as e:
            self.mostrarError(f"Error al actualizar subcategorías: {str(e)}")

    def cargarIngredientes(self, ingredientes_data):
        try:
            self.tablaIngredientes.setRowCount(0)
            for row, (nombre, descripcion, cantidad) in enumerate(ingredientes_data):
                self.tablaIngredientes.insertRow(row)
                item_nombre = QTableWidgetItem(nombre)
                item_nombre.setTextAlignment(Qt.AlignCenter)
                item_nombre.setToolTip(nombre)
                item_nombre.setData(Qt.UserRole, descripcion)
                self.tablaIngredientes.setItem(row, 0, item_nombre)
                item_cantidad = QTableWidgetItem(str(cantidad))
                item_cantidad.setTextAlignment(Qt.AlignCenter)
                item_cantidad.setToolTip(str(cantidad))
                self.tablaIngredientes.setItem(row, 1, item_cantidad)
                btnModificar = QPushButton("✏️")
                btnModificar.setStyleSheet("""
                    QPushButton {
                        background: #f39c12;
                        color: white;
                        border-radius: 5px;
                        padding: 5px;
                        font-weight: bold;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background: #e67e22;
                    }
                """)
                btnModificar.setCursor(Qt.PointingHandCursor)
                btnModificar.clicked.connect(lambda checked, b=btnModificar: self.modificarIngrediente(b))
                self.tablaIngredientes.setCellWidget(row, 2, btnModificar)
                btnEliminar = QPushButton("🗑️")
                btnEliminar.setStyleSheet("""
                    QPushButton {
                        background: #e74c3c;
                        color: white;
                        border-radius: 5px;
                        padding: 5px;
                        font-weight: bold;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background: #c0392b;
                    }
                """)
                btnEliminar.setCursor(Qt.PointingHandCursor)
                btnEliminar.clicked.connect(lambda checked, b=btnEliminar: self.eliminarIngrediente(b))
                self.tablaIngredientes.setCellWidget(row, 3, btnEliminar)
        except Exception as e:
            self.mostrarError(f"Error al cargar ingredientes: {str(e)}")
            raise

    def modificarIngrediente(self, boton):
        try:
            fila = self.obtenerFilaDesdeBoton(boton)
            if fila < 0:
                return

            nombre = self.tablaIngredientes.item(fila, 0).text()
            cantidad = self.tablaIngredientes.item(fila, 1).text()
            descripcion_actual = self.tablaIngredientes.item(fila, 0).data(Qt.UserRole) or ""

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""SELECT nomIng FROM Stock WHERE disponible = 1 ORDER BY nomIng COLLATE NOCASE ASC""")
            ingredientes = [str(elem[0]) for elem in c.fetchall()]
            conn.close()

            dialog = QDialog(self)
            dialog.setWindowTitle("Modificar Ingrediente")
            dialog.setFixedSize(450, 200)
            dialog.setStyleSheet("""
                QDialog {
                    background: #f8f9fa;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
            """)

            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            nombre_ingrediente = QComboBox()
            nombre_ingrediente.setEditable(True)
            nombre_ingrediente.setInsertPolicy(QComboBox.NoInsert)
            nombre_ingrediente.setMinimumHeight(35)

            completer = QCompleter()
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            nombre_ingrediente.setCompleter(completer)

            modelo = QStringListModel()
            modelo.setStringList(ingredientes)
            completer.setModel(modelo)
            nombre_ingrediente.addItems(ingredientes)
            nombre_ingrediente.setCurrentText(nombre)
            descripcion_label = QLabel()
            descripcion_label.setVisible(False)
            cantidad_edit = QLineEdit(cantidad)
            cantidad_edit.setValidator(QRegExpValidator(QRegExp(r"[0-9]{1,8}(\.[0-9]{0,2})?")))
            cantidad_edit.setMaxLength(11)
            cantidad_edit.setMinimumHeight(35)
            cantidad_edit.setPlaceholderText("Cantidad")
            cantidad_edit.setStyleSheet("""
                QLineEdit {
                    background: white;
                    border: 2px solid #3498db;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 2px solid #2980b9;
                    background-color: #f8f9fa;
                }
            """)

            def actualizar_descripcion():
                texto = nombre_ingrediente.currentText()
                if texto:
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute("SELECT descripcion FROM Stock WHERE UPPER(nomIng)=UPPER(?)", (texto,))
                        resultado = c.fetchone()
                        conn.close()
                        if resultado and resultado[0]:
                            descripcion_label.setText(str(resultado[0]))
                        else:
                            descripcion_label.setText("")
                    except Exception as e:
                        self.mostrarError(f"Error al actualizar descripción: {str(e)}")

            nombre_ingrediente.currentIndexChanged.connect(actualizar_descripcion)
            nombre_ingrediente.editTextChanged.connect(actualizar_descripcion)
            descripcion_label.setText(descripcion_actual)

            form_layout = QGridLayout()
            form_layout.setSpacing(10)
            form_layout.addWidget(QLabel("Ingrediente:"), 0, 0)
            form_layout.addWidget(nombre_ingrediente, 0, 1)
            form_layout.addWidget(QLabel("Cantidad:"), 1, 0)
            form_layout.addWidget(cantidad_edit, 1, 1)
            layout.addLayout(form_layout)

            btn_layout = QHBoxLayout()
            btn_guardar = QPushButton("Guardar")
            btn_cancelar = QPushButton("Cancelar")
            btn_guardar.setStyleSheet("""
                QPushButton {
                    background: #27ae60;
                    color: white;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background: #219653;
                }
            """)
            btn_cancelar.setStyleSheet("""
                QPushButton {
                    background: #e74c3c;
                    color: white;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background: #c0392b;
                }
            """)

            def guardar_modificacion():
                if not nombre_ingrediente.currentText() or not cantidad_edit.text():
                    self.mostrarAdvertencia("Debe llenar todos los campos")
                    return
                try:
                    nombre_actual = self.tablaIngredientes.item(fila, 0).text()
                    if nombre_ingrediente.currentText() == nombre_actual:
                        dialog.accept()
                    else:
                        for i in range(self.tablaIngredientes.rowCount()):
                            if (
                                i != fila
                                and self.tablaIngredientes.item(i, 0).text().upper()
                                == nombre_ingrediente.currentText().upper()
                            ):
                                self.mostrarAdvertencia("Este ingrediente ya está registrado")
                                return
                        dialog.accept()
                except Exception as e:
                    self.mostrarError(f"Error al comprobar ingrediente: {str(e)}")

            btn_guardar.clicked.connect(guardar_modificacion)
            btn_cancelar.clicked.connect(dialog.reject)

            btn_layout.addWidget(btn_guardar)
            btn_layout.addWidget(btn_cancelar)
            layout.addLayout(btn_layout)

            if dialog.exec_() == QDialog.Accepted:
                self.tablaIngredientes.item(fila, 0).setText(nombre_ingrediente.currentText())
                self.tablaIngredientes.item(fila, 0).setToolTip(nombre_ingrediente.currentText())
                self.tablaIngredientes.item(fila, 0).setData(Qt.UserRole, descripcion_label.text())
                self.tablaIngredientes.item(fila, 1).setText(cantidad_edit.text())
                self.tablaIngredientes.item(fila, 1).setToolTip(cantidad_edit.text())
        except Exception as e:
            self.mostrarError(f"Error al modificar ingrediente: {str(e)}")

    def eliminarIngrediente(self, boton):
        try:
            fila = self.obtenerFilaDesdeBoton(boton)
            if fila >= 0:
                self.tablaIngredientes.removeRow(fila)
        except Exception as e:
            self.mostrarError(f"Error al eliminar ingrediente: {str(e)}")

    def actualizarFoto(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.webp)"
            )
            if file_path:
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.imagen.setIcon(QIcon(pixmap))
                    self.imagen.setIconSize(QSize(200, 200))
        except Exception as e:
            self.mostrarError(f"Error al actualizar foto: {str(e)}")

    def obtenerBytesImagen(self):
        try:
            icon = self.imagen.icon()
            if icon.isNull():
                return None
            pixmap = icon.pixmap(200, 200)
            buffer = QBuffer()
            buffer.open(QIODevice.ReadWrite)
            pixmap.save(buffer, "PNG")
            return buffer.data()
        except Exception as e:
            self.mostrarError(f"Error al obtener bytes de imagen: {str(e)}")
            return None

    def guardarCambios(self):
        try:
            if not self.campoCosto.text().strip():
                self.mostrarAdvertencia("El costo del producto es obligatorio")
                return

            if not self.campoPrecio.text().strip():
                self.mostrarAdvertencia("El precio del producto es obligatorio")
                return

            if not self.campoNombre.text().strip():
                self.mostrarAdvertencia("El nombre del producto es obligatorio")
                return

            if not self.comboCategoria.currentText() or not self.comboSubcategoria.currentText():
                self.mostrarAdvertencia("Debe seleccionar categoría y subcategoría")
                return

            if self.tablaIngredientes.rowCount() == 0:
                self.mostrarAdvertencia("Debe contener al menos 1 ingrediente")
                return

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            c.execute(
                "SELECT idSubcategoria FROM Subcategoria WHERE nombre = ? AND activa = 1",
                (self.comboSubcategoria.currentText(),),
            )
            resultado = c.fetchone()
            if not resultado:
                self.mostrarAdvertencia("Subcategoría no válida")
                return
            id_subcategoria = resultado[0]

            c.execute(
                """UPDATE Producto SET nomProd=?, descripcion=?, precioVenta=?, 
                      costoFabricacion=?, imgProd=?, idSubcategoria=? WHERE idProd=?""",
                (
                    self.campoNombre.text(),
                    self.campoDescripcion.toPlainText(),
                    float(self.campoPrecio.text()),
                    float(self.campoCosto.text()),
                    self.obtenerBytesImagen(),
                    id_subcategoria,
                    self.id_prod,
                ),
            )

            c.execute("DELETE FROM ProductosIngredientes WHERE idProd = ?", (self.id_prod,))

            for row in range(self.tablaIngredientes.rowCount()):
                nombre_ing = self.tablaIngredientes.item(row, 0).text()
                cantidad_texto = self.tablaIngredientes.item(row, 1).text()

                try:
                    cantidad = float(cantidad_texto)
                except ValueError:
                    self.mostrarAdvertencia(f"Cantidad inválida en fila {row + 1}")
                    continue

                c.execute("SELECT idIng FROM Stock WHERE nomIng = ? AND disponible = 1", (nombre_ing,))
                resultado_ing = c.fetchone()
                if not resultado_ing:
                    self.mostrarAdvertencia(f"Ingrediente '{nombre_ing}' no encontrado")
                    continue
                id_ing = resultado_ing[0]

                c.execute(
                    "INSERT INTO ProductosIngredientes (idProd, idIng, cantidadIngNecesitada) VALUES (?, ?, ?)",
                    (self.id_prod, id_ing, cantidad),
                )

            conn.commit()
            conn.close()
            self.mostrarExito("Producto modificado correctamente")
            self.accept()
        except Exception as e:
            self.mostrarError(f"Error al guardar: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ingredientes_ejemplo = [
        ("Harina", "Harina de trigo especial", 2.5),
        ("Azúcar", "Azúcar blanca refinada", 1.0),
        ("Huevos", "Huevos frescos de gallina", 3.0),
    ]
    dialogo = Pop_up_ModificacionProductos(
        1, ("Pastel", "Delicioso pastel de chocolate", 25.0, 12.0, None, "Postres", "Repostería"), ingredientes_ejemplo
    )
    dialogo.show()
    sys.exit(app.exec_())
