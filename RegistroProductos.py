import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from Pop_up_RegistroProductoModificacionIngrediente import Pop_up_RegistroProductoModificacionIngrediente
from Pop_up_RegistroProductos import Pop_up_RegistroProductos
from Rutas import get_db_path, get_resource_path

DB_PATH = get_db_path()
DIRECCION_IMAGENES = get_resource_path('Imagenes')


class RegistroProductos(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel:not(QMessageBox) {
                font-weight: bold;
                color: #2c3e50;
                font-size: 15px;
                min-width: 100px;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QTextEdit {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 3px;
                font-size: 14px;
            }
            QTextEdit QScrollBar:vertical {
                 width: 12px; 
                 background: #f0f0f0;
             }
            QTextEdit QScrollBar::handle:vertical {
                 background: #a0a0a0;
                 min-height: 20px;
                 border-radius: 6px;
             }
            QTextEdit QScrollBar::add-line:vertical, QTextEdit QScrollBar::sub-line:vertical {
                 border: none;
                 background: none;
                 height: 0px; 
             }
            QTextEdit QScrollBar::handle:vertical:pressed {
                 background: #606060;
             }
            QComboBox{
                border:2px solid #3498db;
                background:white;
                padding: 5px;
                min-height: 20px;
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
        self.set_up()

    def set_up(self):
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.iniciarPagina()
        self.showMaximized()

    def showEvent(self, event):
        super().showEvent(event)
        self._refrescarTablaIngredientesPendientes()

    def _refrescarTablaIngredientesPendientes(self):
        """
        Los ingredientes que ya se agregaron a la tabla (pero el producto aun
        no se registro) quedan guardados con su idIng. Cada vez que esta
        pantalla vuelve a mostrarse (por ejemplo, si el usuario fue a
        Modificar Ingredientes y volvio), se vuelve a consultar el nombre y
        la descripcion actuales de cada ingrediente por su idIng, para que
        la tabla nunca muestre datos desactualizados.
        """
        if not hasattr(self, "tablaRegistrados"):
            return
        tabla = self.tablaRegistrados
        if tabla.rowCount() == 0:
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for fila in range(tabla.rowCount()):
            item_nombre = tabla.item(fila, 0)
            item_descripcion = tabla.item(fila, 1)
            if item_nombre is None or item_descripcion is None:
                continue
            idIng = item_nombre.data(Qt.UserRole + 1)
            if idIng is None:
                continue
            c.execute("SELECT nomIng, descripcion FROM Stock WHERE idIng=?", (idIng,))
            resultado = c.fetchone()
            if resultado is None:
                item_nombre.setBackground(QColor(255, 230, 230))
                item_descripcion.setBackground(QColor(255, 230, 230))
                item_nombre.setToolTip(
                    "Este ingrediente fue eliminado. Quítelo y agregue uno válido antes de registrar."
                )
                continue
            nombre_actual, descripcion_actual = resultado
            descripcion_actual = descripcion_actual if descripcion_actual else ""
            if item_nombre.text() != nombre_actual:
                if item_nombre.text() in self.conjuntoIngredientes:
                    self.conjuntoIngredientes.discard(item_nombre.text())
                self.conjuntoIngredientes.add(nombre_actual)
                item_nombre.setText(nombre_actual)
            if item_descripcion.text() != descripcion_actual:
                item_descripcion.setText(descripcion_actual)
                item_nombre.setData(Qt.UserRole, descripcion_actual)
            item_nombre.setBackground(QColor(255, 255, 255))
            item_descripcion.setBackground(QColor(255, 255, 255))
            item_nombre.setToolTip("")
        conn.close()

    def cargarNombresProductos(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT nomProd FROM Producto ORDER BY nomProd COLLATE NOCASE ASC")
            nombres = [row[0] for row in c.fetchall()]
            conn.close()
            return nombres
        except Exception:
            return []

    def iniciarPagina(self):
        layout1 = QHBoxLayout()
        self.layoutPrincipal.addLayout(layout1, stretch=20)
        layout2 = QVBoxLayout()
        layout2.setSpacing(25)
        layout1.addLayout(layout2)
        tablaRegistrados = QTableWidget()
        self.tablaRegistrados = tablaRegistrados
        tablaRegistrados.setColumnCount(5)
        conjunto = set()
        self.conjuntoIngredientes = conjunto
        tablaRegistrados.setHorizontalHeaderLabels(["Ingrediente", "Descripcion", "Cantidad", "Modificar", "Eliminar"])
        tablaRegistrados.setEditTriggers(QTableWidget.NoEditTriggers)
        tablaRegistrados.setSelectionMode(QTableWidget.NoSelection)
        tablaRegistrados.setFocusPolicy(Qt.NoFocus)
        header = tablaRegistrados.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        tablaRegistrados.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                gridline-color: #ecf0f1;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 5px;
                border: none;
            }
        """)
        layout1.addWidget(tablaRegistrados)
        layoutCategoria = QHBoxLayout()
        nombre = QLabel("Nombre:")
        nombre.setStyleSheet("""
            font-weight: bold;
            color: #2c3e50;
            font-size: 15px;
            min-width: 100px;
            border-radius:10px;
            background-color: transparent;
        """)
        campoNombre = QLineEdit()
        campoNombre.setPlaceholderText("Nombre del producto")
        campoNombre.setFixedHeight(40)
        nombre_producto_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ0-9°%.,\\-\\s]*")
        campoNombre.setValidator(QRegExpValidator(nombre_producto_regex))
        campoNombre.setMaxLength(30)

        self.completerProductos = QCompleter(self.cargarNombresProductos(), self)
        self.completerProductos.setCaseSensitivity(Qt.CaseInsensitive)
        self.completerProductos.setFilterMode(Qt.MatchContains)
        campoNombre.setCompleter(self.completerProductos)

        layoutCategoria.addWidget(nombre, alignment=Qt.AlignTop)
        layoutCategoria.addWidget(campoNombre)
        layoutCategoria2 = QHBoxLayout()
        descripcion = QLabel("Descripcion:")
        descripcion.setStyleSheet("""
            font-weight: bold;
            color: #2c3e50;
            font-size: 15px;
            min-width: 100px;
            border-radius:10px;
            background-color: transparent;
        """)
        campoDescripcion = QTextEdit()
        campoDescripcion.setPlaceholderText("Descripcion del productos (Opcional)")
        campoDescripcion.setFixedHeight(60)
        MAX_LARGO_DESCRIPCION = 200

        def limitar_descripcion():
            texto = campoDescripcion.toPlainText()
            if len(texto) > MAX_LARGO_DESCRIPCION:
                cursor = campoDescripcion.textCursor()
                posicion = cursor.position()
                campoDescripcion.blockSignals(True)
                campoDescripcion.setPlainText(texto[:MAX_LARGO_DESCRIPCION])
                cursor.setPosition(min(posicion, MAX_LARGO_DESCRIPCION))
                campoDescripcion.setTextCursor(cursor)
                campoDescripcion.blockSignals(False)

        campoDescripcion.textChanged.connect(limitar_descripcion)
        layoutCategoria2.addWidget(descripcion, alignment=Qt.AlignTop)
        layoutCategoria2.addWidget(campoDescripcion)
        layoutCategoria3 = QHBoxLayout()
        precioVenta = QLabel("Precio Venta:")
        precioVenta.setStyleSheet("""
            font-weight: bold;
            color: #2c3e50;
            font-size: 15px;
            min-width: 100px;
            border-radius:10px;
            background-color: transparent;
        """)
        campoPrecioVenta = QLineEdit()
        campoPrecioVenta.setPlaceholderText("0.00")
        campoPrecioVenta.setFixedHeight(40)
        precio_regex = QRegExp(r"[0-9]{1,8}(\.[0-9]{0,2})?")
        campoPrecioVenta.setValidator(QRegExpValidator(precio_regex))
        campoPrecioVenta.setMaxLength(11)
        layoutCategoria3.addWidget(precioVenta, alignment=Qt.AlignTop)
        layoutCategoria3.addWidget(campoPrecioVenta)
        layoutCategoria4 = QHBoxLayout()
        costoFabricacion = QLabel("Costo de Fabricacion:")
        costoFabricacion.setStyleSheet("""
            font-weight: bold;
            color: #2c3e50;
            font-size: 15px;
            min-width: 100px;
            border-radius:10px;
            background-color: transparent;
        """)
        campoCostoFabricacion = QLineEdit()
        campoCostoFabricacion.setPlaceholderText("0.00")
        campoCostoFabricacion.setFixedHeight(40)
        campoCostoFabricacion.setValidator(QRegExpValidator(precio_regex))
        campoCostoFabricacion.setMaxLength(11)
        layoutCategoria4.addWidget(costoFabricacion, alignment=Qt.AlignTop)
        layoutCategoria4.addWidget(campoCostoFabricacion)
        layoutCategoria5 = QHBoxLayout()
        categoria = QLabel("Categoria:")
        categoria.setStyleSheet("""
            font-weight: bold;
            color: #2c3e50;
            font-size: 15px;
            min-width: 100px;
            border-radius:10px;
            background-color: transparent;
        """)
        self.campoCategoria = QComboBox()
        self.cargarCategorias()
        self.campoCategoria.setFixedHeight(30)
        layoutCategoria5.addWidget(categoria, alignment=Qt.AlignTop)
        layoutCategoria5.addWidget(self.campoCategoria)
        layout2.addLayout(layoutCategoria)
        layout2.addLayout(layoutCategoria2)
        layout2.addLayout(layoutCategoria3)
        layout2.addLayout(layoutCategoria4)
        layout2.addLayout(layoutCategoria5)
        layoutCategoria6 = QHBoxLayout()
        subcategoria = QLabel("Subcategoria:")
        subcategoria.setStyleSheet("""
            font-weight: bold;
            color: #2c3e50;
            font-size: 15px;
            min-width: 100px;
            border-radius:10px;
            background-color: transparent;
        """)
        self.campoSubcategoria = QComboBox()
        self.cargarSubcategorias()
        self.campoSubcategoria.setFixedHeight(30)
        self.campoCategoria.currentIndexChanged.connect(
            lambda: self.recargarComboSubcategoria(self.campoCategoria.currentText(), self.campoSubcategoria)
        )
        layoutCategoria6.addWidget(subcategoria, alignment=Qt.AlignTop)
        layoutCategoria6.addWidget(self.campoSubcategoria)
        layout2.addLayout(layoutCategoria6)
        layoutCategoria7 = QHBoxLayout()
        ingrediente = QLabel("Ingrediente:")
        ingrediente.setStyleSheet("""
            font-weight: bold;
            color: #2c3e50;
            font-size: 15px;
            min-width: 100px;
            border-radius:10px;
            background-color: transparent;
        """)
        self.campoIngrediente = QComboBox()
        self.campoIngrediente.setEditable(True)
        self.campoIngrediente.setInsertPolicy(QComboBox.NoInsert)
        self.campoIngrediente.setFixedWidth(300)
        self.campoIngrediente.setFixedHeight(30)
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.campoIngrediente.setCompleter(self.completer)
        self.cargarIngredientes()
        self.campoCantidad = QLineEdit()
        self.campoCantidad.setPlaceholderText("")
        self.campoCantidad.setValidator(QRegExpValidator(precio_regex))
        self.campoCantidad.setMaxLength(11)
        self.campoCantidad.setFixedHeight(35)
        self.campoCantidad.setFixedWidth(100)

        self.campoIngrediente.currentIndexChanged.connect(
            lambda: self.actualizarPlaceholderUnidad(self.campoIngrediente.currentText())
        )
        self.campoIngrediente.editTextChanged.connect(
            lambda: self.actualizarPlaceholderUnidad(self.campoIngrediente.currentText())
        )

        layoutCategoria7.addWidget(ingrediente, alignment=Qt.AlignTop)
        layoutCategoria7.addWidget(self.campoIngrediente)
        layoutCategoria7.addWidget(self.campoCantidad)
        botonAnadir = QPushButton("Añadir")
        botonAnadir.setFixedHeight(35)
        botonAnadir.setFixedWidth(100)
        botonAnadir.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 80px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)

        layoutCategoria7.addWidget(botonAnadir)
        layout2.addLayout(layoutCategoria7)

        botonRegistrar = QPushButton("Registrar")
        botonRegistrar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 18px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        botonRegistrar.clicked.connect(
            lambda: self.subirInformacion(
                campoNombre,
                campoDescripcion,
                campoPrecioVenta,
                campoCostoFabricacion,
                self.campoCategoria,
                self.campoSubcategoria,
                tablaRegistrados,
                self.campoCantidad,
                conjunto,
            )
        )
        botonAnadir.clicked.connect(
            lambda: self.anadirElemento(
                self.campoIngrediente.currentText(), self.campoCantidad.text(), tablaRegistrados, conjunto
            )
        )
        self.layoutPrincipal.addWidget(botonRegistrar)

    def actualizarPlaceholderUnidad(self, textoIngrediente):
        if not textoIngrediente:
            self.campoCantidad.setPlaceholderText("")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            consulta = """SELECT unidadMedida FROM Stock WHERE UPPER(nomIng)=UPPER(?)"""
            c.execute(consulta, (textoIngrediente,))
            resultado = c.fetchone()
            conn.close()
            if resultado and resultado[0]:
                self.campoCantidad.setPlaceholderText(resultado[0])
            else:
                self.campoCantidad.setPlaceholderText("")
        except Exception as e:
            print(f"Error al actualizar placeholder: {e}")
            self.campoCantidad.setPlaceholderText("")

    def cargarCategorias(self):
        self.campoCategoria.clear()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        consulta = """SELECT nomCategoria FROM Categoria WHERE activa=1 ORDER BY nomCategoria COLLATE NOCASE ASC"""
        c.execute(consulta)
        resultados = c.fetchall()
        conn.close()
        if resultados:
            elementos = [str(elem[0]) for elem in resultados]
            self.campoCategoria.addItems(elementos)
            self.campoCategoria.setCurrentIndex(-1)

    def cargarSubcategorias(self):
        self.campoSubcategoria.clear()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        consulta = """SELECT nombre FROM Subcategoria WHERE activa=1 ORDER BY nombre COLLATE NOCASE ASC"""
        c.execute(consulta)
        resultados = c.fetchall()
        conn.close()
        if resultados:
            elementos = [str(elem[0]) for elem in resultados]
            self.campoSubcategoria.addItems(elementos)
            self.campoSubcategoria.setCurrentIndex(-1)

    def cargarIngredientes(self):
        self.campoIngrediente.clear()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        consulta = """SELECT nomIng FROM Stock ORDER BY nomIng COLLATE NOCASE ASC"""
        c.execute(consulta)
        resultados = c.fetchall()
        conn.close()
        if resultados:
            elementos = [str(elem[0]) for elem in resultados]
            modelo = QStringListModel()
            modelo.setStringList(elementos)
            self.completer.setModel(modelo)
            self.campoIngrediente.addItems(elementos)

        self.campoIngrediente.setCurrentIndex(-1)
        self.campoIngrediente.setEditText("")

    def limpiarCampos(self, campo1, campo2, campo3, campo4, campo5, campo6, tabla, cantidad, conjunto):
        campo1.setText("")
        campo2.setText("")
        campo3.setText("")
        campo4.setText("")
        cantidad.setText("")
        cantidad.setPlaceholderText("")
        self.campoIngrediente.setEditText("")
        self.campoIngrediente.setCurrentIndex(-1)
        campo5.setCurrentIndex(-1)
        campo6.setCurrentIndex(-1)
        tabla.setRowCount(0)
        conjunto.clear()
        self.completerProductos.setModel(QStringListModel(self.cargarNombresProductos()))

    def recargarComboSubcategoria(self, eleccion, campoSubcategoria):
        campoSubcategoria.clear()
        if not eleccion:
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        consulta = """SELECT S.nombre FROM Subcategoria S, Categoria C 
                   WHERE S.idCategoria=C.idCategoria AND C.nomCategoria=? AND S.activa=1 
                   ORDER BY S.nombre COLLATE NOCASE ASC"""
        c.execute(consulta, (eleccion,))
        resultados = [str(elem[0]) for elem in c.fetchall()]
        conn.close()
        if resultados:
            campoSubcategoria.addItems(resultados)
        campoSubcategoria.setCurrentIndex(-1)

    def subirInformacion(self, campo1, campo2, campo3, campo4, campo5, campo6, tabla, cantidad, conjunto):
        campo11 = campo1.text()
        campo22 = campo2.toPlainText()
        campo33 = campo3.text()
        campo44 = campo4.text()
        campo55 = campo5.currentText()
        campo66 = campo6.currentText()
        if campo11 == "" or campo33 == "" or campo44 == "" or campo55 == "" or campo66 == "":
            QMessageBox.information(self, "Advertencia", "Debe llenar los campos obligatorios")
            return
        if tabla.rowCount() == 0:
            QMessageBox.information(self, "Advertencia", "El producto debe contener por lo menos un ingrediente")
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        campo11_upper = campo11.upper()
        c.execute("""SELECT * FROM Producto WHERE UPPER(nomProd)=?""", (campo11_upper,))
        resultados = c.fetchall()
        if resultados:
            QMessageBox.information(self, "Advertencia", "Este producto ya ha sido registrado")
            return
        pagina = Pop_up_RegistroProductos([campo11, campo22, campo33, campo44, campo66], tabla)
        if pagina.exec_() == QDialog.Accepted:
            self.limpiarCampos(campo1, campo2, campo3, campo4, campo5, campo6, tabla, cantidad, conjunto)

    def obtenerInfoIngrediente(self, nombreIngrediente):
        if not nombreIngrediente:
            return None, None, None
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "SELECT idIng, descripcion, unidadMedida FROM Stock WHERE UPPER(nomIng)=UPPER(?)", (nombreIngrediente,)
            )
            resultado = c.fetchone()
            conn.close()
            if resultado:
                return resultado[0], resultado[1] if resultado[1] else "", resultado[2] if resultado[2] else ""
            return None, "", ""
        except Exception as e:
            print(f"Error al obtener info del ingrediente: {e}")
            return None, "", ""

    def anadirElemento(self, nombreIngrediente, cantidad, tabla, conjunto, bandera=True):
        if not nombreIngrediente or not cantidad:
            QMessageBox.critical(self, "Error", "Debe llenar los campos obligatorios porfavor")
            return

        idIng, descripcion, unidad = self.obtenerInfoIngrediente(nombreIngrediente)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT nomIng FROM Stock WHERE UPPER(nomIng)=UPPER(?)", (nombreIngrediente,))
        if not c.fetchone():
            conn.close()
            QMessageBox.critical(self, "Error", "El ingrediente seleccionado no existe")
            return
        conn.close()

        identificador = nombreIngrediente
        identificador_upper = identificador.upper()
        conjunto_upper = {item.upper() for item in conjunto}

        if identificador_upper in conjunto_upper and bandera == True:
            QMessageBox.critical(self, "Error", "El ingrediente ya está registrado")
            return

        fila = tabla.rowCount()
        tabla.insertRow(fila)

        botonModificar = QPushButton()
        modificar_icon_path = get_resource_path(os.path.join('Imagenes', 'modificarCategoria.jpg'))
        if os.path.exists(modificar_icon_path):
            botonModificar.setIcon(QIcon(modificar_icon_path))
        else:
            botonModificar.setText("✏️")

        estilo_botones_tabla = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """
        botonModificar.setStyleSheet(estilo_botones_tabla)
        botonModificar.clicked.connect(
            lambda checked, e=identificador, ing=nombreIngrediente, desc=descripcion, cant=cantidad: (
                self.modificarElemento(e, ing, desc, cant, tabla, conjunto, botonModificar)
            )
        )

        botonEliminar = QPushButton()
        eliminar_icon_path = get_resource_path(os.path.join('Imagenes', 'eliminarSubcategoria.png'))
        if os.path.exists(eliminar_icon_path):
            botonEliminar.setIcon(QIcon(eliminar_icon_path))
        else:
            botonEliminar.setText("🗑️")
        botonEliminar.setStyleSheet(estilo_botones_tabla)
        botonEliminar.clicked.connect(
            lambda checked, e=identificador: self.eliminarElemento(e, tabla, conjunto, botonEliminar)
        )

        item_nombre = QTableWidgetItem(nombreIngrediente)
        item_nombre.setTextAlignment(Qt.AlignCenter)
        item_nombre.setData(Qt.UserRole, descripcion)
        item_nombre.setData(Qt.UserRole + 1, idIng)
        tabla.setItem(fila, 0, item_nombre)

        item_descripcion = QTableWidgetItem(descripcion)
        item_descripcion.setTextAlignment(Qt.AlignCenter)
        tabla.setItem(fila, 1, item_descripcion)

        item_cantidad = QTableWidgetItem(cantidad)
        item_cantidad.setTextAlignment(Qt.AlignCenter)
        tabla.setItem(fila, 2, item_cantidad)

        tabla.setCellWidget(fila, 3, botonModificar)
        tabla.setCellWidget(fila, 4, botonEliminar)

        conjunto.add(identificador)
        tabla.scrollToBottom()

        self.campoIngrediente.setEditText("")
        self.campoIngrediente.setCurrentIndex(-1)
        self.campoCantidad.setText("")
        self.campoCantidad.setPlaceholderText("")

    def modificarElemento(self, elemento, nombreIngrediente, descripcion, cantidad, tabla, conjunto, boton):
        # Se consulta la base por idIng porque los datos del botón pueden estar desactualizados
        indice = tabla.indexAt(boton.mapTo(tabla.viewport(), QPoint(0, 0)))
        fila = indice.row()
        if fila < 0:
            return

        elemento_actual = tabla.item(fila, 0).text()
        descripcion_actual = tabla.item(fila, 1).text()
        cantidad_actual = tabla.item(fila, 2).text()
        idIng_actual = tabla.item(fila, 0).data(Qt.UserRole + 1)

        if idIng_actual is not None:
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT nomIng, descripcion FROM Stock WHERE idIng=?", (idIng_actual,))
                resultado = c.fetchone()
                conn.close()
                if resultado:
                    elemento_actual = resultado[0]
                    descripcion_actual = resultado[1] if resultado[1] else ""
            except Exception as e:
                print(f"Error al refrescar datos del ingrediente: {e}")

        conjunto_excepto_actual = {item.upper() for item in conjunto}
        conjunto_excepto_actual.discard(elemento_actual.upper())

        lista = [elemento_actual, cantidad_actual, descripcion_actual]
        miniPantalla = Pop_up_RegistroProductoModificacionIngrediente(
            elemento_actual, lista, conjunto_excepto_actual, self
        )

        if miniPantalla.exec_() == QDialog.Accepted:
            nuevo = miniPantalla.getIden()
            conjunto.discard(elemento_actual)
            conjunto.add(nuevo[0])

            tabla.item(fila, 0).setText(nuevo[1])
            tabla.item(fila, 0).setData(Qt.UserRole, nuevo[2])
            tabla.item(fila, 0).setData(Qt.UserRole + 1, nuevo[4])
            tabla.item(fila, 1).setText(nuevo[2])
            tabla.item(fila, 2).setText(nuevo[3])

            boton_nuevo = tabla.cellWidget(fila, 3)
            boton_nuevo.clicked.disconnect()
            boton_nuevo.clicked.connect(
                lambda checked, e=nuevo[0], ing=nuevo[1], desc=nuevo[2], cant=nuevo[3]: self.modificarElemento(
                    e, ing, desc, cant, tabla, conjunto, boton_nuevo
                )
            )

            boton_eliminar_nuevo = tabla.cellWidget(fila, 4)
            boton_eliminar_nuevo.clicked.disconnect()
            boton_eliminar_nuevo.clicked.connect(
                lambda checked, e=nuevo[0]: self.eliminarElemento(e, tabla, conjunto, boton_eliminar_nuevo)
            )

    def eliminarElemento(self, elemento, tabla, conjunto, boton):
        conjunto.discard(elemento)
        indice = tabla.indexAt(boton.mapTo(tabla.viewport(), QPoint(0, 0)))
        fila = indice.row()
        tabla.removeRow(fila)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = RegistroProductos()
    pagina.show()
    sys.exit(app.exec_())
