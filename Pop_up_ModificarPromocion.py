import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Rutas import get_db_path

DB_PATH = get_db_path()

class Pop_up_ModificarPromocion(QDialog):
    def __init__(self, nomProm, parent=None):
        super().__init__(parent)
        QLocale.setDefault(QLocale(QLocale.Spanish, QLocale.Bolivia))
        self.nomProm = nomProm
        self.setWindowTitle("MODIFICAR PROMOCIÓN")
        self.setFixedSize(1000, 900)

        self.setStyleSheet("""
            QDialog { 
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e6f7ff, stop: 1 #cce6ff);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel { 
                font-weight: bold; 
                font-size: 14px; 
                color: #2c3e50; 
                padding: 2px;
            }
            QLineEdit, QSpinBox, QComboBox { 
                background: white; 
                border: 2px solid #3498db; 
                border-radius: 6px; 
                padding: 10px; 
                font-size: 14px;
            }
            QLineEdit:focus { 
                border: 2px solid #2980b9;
                background-color: #f8f9fa;
            }
            QDateEdit, QTimeEdit {
                background: white;
                border: 2px solid #3498db;
                border-radius: 6px;
                padding: 5px;
                font-size: 12px;
            }
            QCheckBox {
                spacing: 5px;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                font-size: 14px;
            }
            QPushButton { 
                border-radius: 6px; 
                padding: 10px 20px; 
                font-weight: bold; 
                font-size: 14px;
                border: none;
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
        layoutPrincipal.setContentsMargins(20,20,20,20)
        layoutPrincipal.setSpacing(15)
        self.setLayout(layoutPrincipal)
        titulo = QLabel(f"Modificar Promoción: {nomProm}")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            padding: 15px;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y1: 0,
                stop: 0 #3498db, stop: 1 #2980b9);
            border-radius: 10px;
        """)
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
        contenido_layout.setSpacing(15)
        self.botonImagen = QPushButton()
        self.botonImagen.setFixedSize(180,180)
        self.botonImagen.setCursor(Qt.PointingHandCursor)
        self.botonImagen.setStyleSheet("""
            QPushButton {
                border: 2px dashed #3498db;
                background: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                border: 2px dashed #2980b9;
                background: #f8f9fa;
            }
        """)
        self.botonImagen.clicked.connect(self.actualizarFoto)
        contenido_layout.addWidget(self.botonImagen, alignment=Qt.AlignCenter)
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                padding: 20px;
                border: 2px solid #e0e0e0;
            }
        """)
        form_layout = QGridLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(15, 15, 15, 15)
        self.campoNombre = QLineEdit()
        self.campoNombre.setFixedHeight(38)
        nombre_promocion_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ0-9°%.,\\-\\s]*")
        self.campoNombre.setValidator(QRegExpValidator(nombre_promocion_regex))
        self.campoNombre.setMaxLength(30)
        self.campoPrecio = QLineEdit()
        self.campoPrecio.setFixedHeight(38)
        validador = QRegExpValidator(QRegExp(r"[0-9]{1,8}(\.[0-9]{0,2})?"))
        self.campoPrecio.setValidator(validador)
        self.campoPrecio.setMaxLength(11)

        # --- COMPLETER para sugerir nombres ya registrados ---
        self.completerNombres = QCompleter(self.cargarNombresPromociones(), self)
        self.completerNombres.setCaseSensitivity(Qt.CaseInsensitive)
        self.completerNombres.setFilterMode(Qt.MatchContains)
        self.campoNombre.setCompleter(self.completerNombres)
        # -----------------------------------------------------

        form_layout.addWidget(QLabel("📝 Nombre:"),0,0)
        form_layout.addWidget(self.campoNombre,0,1)
        form_layout.addWidget(QLabel("💰 Precio:"),1,0)
        form_layout.addWidget(self.campoPrecio,1,1)
        contenido_layout.addWidget(form_container)
        layoutControlTiempo = QVBoxLayout()
        layoutControlTiempo.setSpacing(8)
        grupoFechaEspecifica = QGroupBox("Fecha Específica")
        layoutFechaEspec = QHBoxLayout()
        self.checkFechaEspec = QCheckBox("Activar fecha específica")
        self.dateFechaEspec = QDateEdit()
        self.dateFechaEspec.setDisplayFormat("dd/MM/yyyy")
        self.dateFechaEspec.setLocale(QLocale(QLocale.Spanish, QLocale.Bolivia))
        self.dateFechaEspec.setCalendarPopup(True)
        self.dateFechaEspec.setDate(QDate.currentDate())
        self.dateFechaEspec.setEnabled(False)
        self.dateFechaEspec.setFixedHeight(28)
        self.timeInicioFechaEspec = QTimeEdit()
        self.timeInicioFechaEspec.setTime(QTime(9, 0))
        self.timeInicioFechaEspec.setEnabled(False)
        self.timeInicioFechaEspec.setFixedHeight(28)
        self.timeFinFechaEspec = QTimeEdit()
        self.timeFinFechaEspec.setTime(QTime(18, 0))
        self.timeFinFechaEspec.setEnabled(False)
        self.timeFinFechaEspec.setFixedHeight(28)
        def toggle_fecha_espec(checked):
            self.dateFechaEspec.setEnabled(checked)
            self.timeInicioFechaEspec.setEnabled(checked)
            self.timeFinFechaEspec.setEnabled(checked)
            if checked:
                self.checkPeriodo.setChecked(False)
                self.checkDiasSemana.setChecked(False)
            self.actualizar_colores_horas()
        self.checkFechaEspec.toggled.connect(toggle_fecha_espec)
        layoutFechaEspec.addWidget(self.checkFechaEspec)
        layoutFechaEspec.addWidget(QLabel("Fecha:"))
        layoutFechaEspec.addWidget(self.dateFechaEspec)
        layoutFechaEspec.addWidget(QLabel("Hora inicio:"))
        layoutFechaEspec.addWidget(self.timeInicioFechaEspec)
        layoutFechaEspec.addWidget(QLabel("Hora fin:"))
        layoutFechaEspec.addWidget(self.timeFinFechaEspec)
        layoutFechaEspec.addStretch()
        grupoFechaEspecifica.setLayout(layoutFechaEspec)
        layoutControlTiempo.addWidget(grupoFechaEspecifica)
        grupoPeriodo = QGroupBox("Período de Tiempo")
        layoutPeriodo = QVBoxLayout()
        layoutFechas = QHBoxLayout()
        self.checkPeriodo = QCheckBox("Activar período")
        self.dateInicio = QDateEdit()
        self.dateInicio.setDisplayFormat("dd/MM/yyyy")
        self.dateInicio.setLocale(QLocale(QLocale.Spanish, QLocale.Bolivia))
        self.dateFin = QDateEdit()
        self.dateFin.setDisplayFormat("dd/MM/yyyy")
        self.dateFin.setLocale(QLocale(QLocale.Spanish, QLocale.Bolivia))
        self.dateInicio.setCalendarPopup(True)
        self.dateFin.setCalendarPopup(True)
        self.dateInicio.setDate(QDate.currentDate())
        self.dateFin.setDate(QDate.currentDate().addDays(7))
        self.dateInicio.setEnabled(False)
        self.dateFin.setEnabled(False)
        self.dateInicio.setFixedHeight(28)
        self.dateFin.setFixedHeight(28)
        self.timeInicioPeriodo = QTimeEdit()
        self.timeInicioPeriodo.setTime(QTime(9, 0))
        self.timeInicioPeriodo.setEnabled(False)
        self.timeInicioPeriodo.setFixedHeight(28)
        self.timeFinPeriodo = QTimeEdit()
        self.timeFinPeriodo.setTime(QTime(18, 0))
        self.timeFinPeriodo.setEnabled(False)
        self.timeFinPeriodo.setFixedHeight(28)
        def toggle_periodo(checked):
            self.dateInicio.setEnabled(checked)
            self.dateFin.setEnabled(checked)
            self.timeInicioPeriodo.setEnabled(checked)
            self.timeFinPeriodo.setEnabled(checked)
            if checked:
                self.checkFechaEspec.setChecked(False)
            self.actualizar_colores_horas()
        self.checkPeriodo.toggled.connect(toggle_periodo)
        layoutFechas.addWidget(self.checkPeriodo)
        layoutFechas.addWidget(QLabel("Desde:"))
        layoutFechas.addWidget(self.dateInicio)
        layoutFechas.addWidget(QLabel("Hasta:"))
        layoutFechas.addWidget(self.dateFin)
        layoutFechas.addWidget(QLabel("Hora inicio:"))
        layoutFechas.addWidget(self.timeInicioPeriodo)
        layoutFechas.addWidget(QLabel("Hora fin:"))
        layoutFechas.addWidget(self.timeFinPeriodo)
        layoutFechas.addStretch()
        layoutPeriodo.addLayout(layoutFechas)
        grupoPeriodo.setLayout(layoutPeriodo)
        layoutControlTiempo.addWidget(grupoPeriodo)
        grupoHorasDias = QGroupBox("Horas para Días de la Semana")
        layoutHorasDias = QHBoxLayout()
        self.timeInicioDias = QTimeEdit()
        self.timeInicioDias.setTime(QTime(9, 0))
        self.timeInicioDias.setFixedHeight(28)
        self.timeFinDias = QTimeEdit()
        self.timeFinDias.setTime(QTime(18, 0))
        self.timeFinDias.setFixedHeight(28)
        layoutHorasDias.addWidget(QLabel("Hora inicio:"))
        layoutHorasDias.addWidget(self.timeInicioDias)
        layoutHorasDias.addWidget(QLabel("Hora fin:"))
        layoutHorasDias.addWidget(self.timeFinDias)
        layoutHorasDias.addStretch()
        grupoHorasDias.setLayout(layoutHorasDias)
        layoutControlTiempo.addWidget(grupoHorasDias)
        grupoDiasSemana = QGroupBox("Días de la Semana")
        layoutDias = QHBoxLayout()
        self.diasCheckboxes = []
        dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for i, dia in enumerate(dias, 1):
            checkbox = QCheckBox(dia)
            checkbox.diaNum = i
            self.diasCheckboxes.append(checkbox)
            layoutDias.addWidget(checkbox)
        layoutDias.addStretch()
        grupoDiasSemana.setLayout(layoutDias)
        layoutControlTiempo.addWidget(grupoDiasSemana)
        self.checkDiasSemana = QCheckBox("Activar días de la semana")
        def toggle_dias_semana(checked):
            if checked:
                self.checkFechaEspec.setChecked(False)
            self.actualizar_colores_horas()
        self.checkDiasSemana.toggled.connect(toggle_dias_semana)
        layoutControlTiempo.insertWidget(2, self.checkDiasSemana)
        contenido_layout.addLayout(layoutControlTiempo)
        layoutFiltros = QHBoxLayout()
        layoutFiltros.addWidget(QLabel("Categoría:"))
        self.comboCategorias = QComboBox()
        self.comboCategorias.setFixedWidth(220)
        self.comboCategorias.setFixedHeight(43)
        self.comboCategorias.setMinimumContentsLength(20)
        self.comboCategorias.currentIndexChanged.connect(self.cargarSubcategorias)
        layoutFiltros.addWidget(self.comboCategorias)
        layoutFiltros.addWidget(QLabel("Subcategoría:"))
        self.comboSubcategorias = QComboBox()
        self.comboSubcategorias.setFixedWidth(220)
        self.comboSubcategorias.setFixedHeight(43)
        self.comboSubcategorias.setMinimumContentsLength(20)
        self.comboSubcategorias.currentIndexChanged.connect(self.cargarProductosPorSubcategoria)
        layoutFiltros.addWidget(self.comboSubcategorias)
        layoutFiltros.addStretch()
        contenido_layout.addLayout(layoutFiltros)
        layoutAgregarProducto = QHBoxLayout()
        layoutAgregarProducto.addWidget(QLabel("Producto:"))
        self.comboProductos = QComboBox()
        self.comboProductos.setFixedWidth(280)
        self.comboProductos.setFixedHeight(43)
        self.comboProductos.setMinimumContentsLength(20)
        layoutAgregarProducto.addWidget(self.comboProductos)
        layoutAgregarProducto.addWidget(QLabel("Cantidad:"))
        self.editCantidad = QLineEdit()
        self.editCantidad.setPlaceholderText("Cantidad")
        self.editCantidad.setFixedWidth(100)
        self.editCantidad.setFixedHeight(43)
        self.editCantidad.setValidator(QRegExpValidator(QRegExp("[0-9]+")))
        self.editCantidad.setMaxLength(3)
        layoutAgregarProducto.addWidget(self.editCantidad)
        btnAgregar = QPushButton("➕ Agregar Producto")
        btnAgregar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #27ae60, stop: 1 #219653);
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #219653, stop: 1 #1e8449);
            }
        """)
        btnAgregar.clicked.connect(self.agregarProducto)
        layoutAgregarProducto.addWidget(btnAgregar)
        layoutAgregarProducto.addStretch()
        contenido_layout.addLayout(layoutAgregarProducto)
        self.tablaProductos = QTableWidget()
        self.tablaProductos.setFixedHeight(250)
        self.tablaProductos.setColumnCount(4)
        self.tablaProductos.setHorizontalHeaderLabels(["Producto","Cantidad","Modificar","Eliminar"])
        header = self.tablaProductos.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch) 
        self.tablaProductos.verticalHeader().setVisible(False)
        self.tablaProductos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tablaProductos.setSelectionMode(QTableWidget.NoSelection)
        self.tablaProductos.setAlternatingRowColors(True)
        self.tablaProductos.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                alternate-background-color: #f8f9fa;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5dade2, stop: 1 #3498db);
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        contenido_layout.addWidget(QLabel("📦 Productos en la promoción:"))
        contenido_layout.addWidget(self.tablaProductos)
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
                padding: 12px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #219653, stop: 1 #1e8449);
            }
        """)
        btnCancelar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e74c3c, stop: 1 #c0392b);
                color: white;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c0392b, stop: 1 #a93226);
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
        self.cargarDatos()
        self.cargarCategorias()

    # --- MÉTODO NUEVO: carga nombres de promociones excluyendo la actual ---
    def cargarNombresPromociones(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""SELECT nomProm FROM Promocion 
                         WHERE nomProm != ? 
                         ORDER BY nomProm COLLATE NOCASE ASC""", (self.nomProm,))
            nombres = [row[0] for row in c.fetchall()]
            conn.close()
            return nombres
        except Exception:
            return []
    # -----------------------------------------------------------------------

    def cargarCategorias(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT idCategoria, nomCategoria FROM Categoria WHERE activa = 1 ORDER BY nomCategoria")
        categorias = c.fetchall()
        conn.close()
        self.comboCategorias.clear()
        self.comboCategorias.addItem("Todas las categorías", -1)
        for id_cat, nombre in categorias:
            self.comboCategorias.addItem(nombre, id_cat)
        if self.comboCategorias.count() > 1:
            self.comboCategorias.setCurrentIndex(1)

    def cargarSubcategorias(self):
        categoria_id = self.comboCategorias.currentData()
        self.comboSubcategorias.clear()
        if categoria_id == -1:
            self.comboSubcategorias.addItem("Todas las subcategorías", -1)
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                SELECT S.idSubcategoria, S.nombre 
                FROM Subcategoria S
                WHERE S.activa = 1 
                ORDER BY S.nombre
            """)
            subcategorias = c.fetchall()
            conn.close()
            
            for id_sub, nombre in subcategorias:
                self.comboSubcategorias.addItem(nombre, id_sub)
        else:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                SELECT S.idSubcategoria, S.nombre 
                FROM Subcategoria S
                WHERE S.idCategoria = ? AND S.activa = 1 
                ORDER BY S.nombre
            """, (categoria_id,))
            subcategorias = c.fetchall()
            conn.close()
            
            self.comboSubcategorias.addItem("Todas las subcategorías", -1)
            for id_sub, nombre in subcategorias:
                self.comboSubcategorias.addItem(nombre, id_sub)
        if self.comboSubcategorias.count() > 0:
            self.comboSubcategorias.setCurrentIndex(0)

    def cargarProductosPorSubcategoria(self):
        subcategoria_id = self.comboSubcategorias.currentData()
        categoria_id = self.comboCategorias.currentData()
        self.comboProductos.clear()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if subcategoria_id == -1 and categoria_id == -1:
            c.execute("""
                SELECT P.nomProd 
                FROM Producto P
                JOIN Subcategoria S ON P.idSubcategoria = S.idSubcategoria
                WHERE P.activo = 1 
                ORDER BY P.nomProd
            """)
        elif subcategoria_id == -1 and categoria_id != -1:
            c.execute("""
                SELECT P.nomProd 
                FROM Producto P
                JOIN Subcategoria S ON P.idSubcategoria = S.idSubcategoria
                WHERE P.activo = 1 AND S.idCategoria = ?
                ORDER BY P.nomProd
            """, (categoria_id,))
        else:
            c.execute("""
                SELECT P.nomProd 
                FROM Producto P
                WHERE P.activo = 1 AND P.idSubcategoria = ?
                ORDER BY P.nomProd
            """, (subcategoria_id,))
        
        productos = [p[0] for p in c.fetchall()]
        conn.close()
        self.comboProductos.addItems(productos)
        if self.comboProductos.count() == 0:
            self.comboProductos.addItem("No hay productos disponibles")

    def actualizar_colores_horas(self):
        for widget in [self.timeInicioFechaEspec, self.timeFinFechaEspec,
                       self.timeInicioPeriodo, self.timeFinPeriodo,
                       self.timeInicioDias, self.timeFinDias]:
            widget.setStyleSheet("""
                QTimeEdit {
                    background: white;
                    border: 2px solid #3498db;
                    border-radius: 6px;
                    padding: 5px;
                    font-size: 12px;
                }
            """)
        if self.checkFechaEspec.isChecked():
            self.timeInicioFechaEspec.setStyleSheet("""
                QTimeEdit {
                    background: #ffe6e6;
                    border: 2px solid #e74c3c;
                    border-radius: 6px;
                    padding: 5px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
            self.timeFinFechaEspec.setStyleSheet("""
                QTimeEdit {
                    background: #ffe6e6;
                    border: 2px solid #e74c3c;
                    border-radius: 6px;
                    padding: 5px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
        elif self.checkPeriodo.isChecked():
            if self.checkDiasSemana.isChecked():
                self.timeInicioDias.setStyleSheet("""
                    QTimeEdit {
                        background: #ffe6e6;
                        border: 2px solid #e74c3c;
                        border-radius: 6px;
                        padding: 5px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """)
                self.timeFinDias.setStyleSheet("""
                    QTimeEdit {
                        background: #ffe6e6;
                        border: 2px solid #e74c3c;
                        border-radius: 6px;
                        padding: 5px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """)
            else:
                self.timeInicioPeriodo.setStyleSheet("""
                    QTimeEdit {
                        background: #ffe6e6;
                        border: 2px solid #e74c3c;
                        border-radius: 6px;
                        padding: 5px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """)
                self.timeFinPeriodo.setStyleSheet("""
                    QTimeEdit {
                        background: #ffe6e6;
                        border: 2px solid #e74c3c;
                        border-radius: 6px;
                        padding: 5px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                """)
                
        elif self.checkDiasSemana.isChecked():
            self.timeInicioDias.setStyleSheet("""
                QTimeEdit {
                    background: #ffe6e6;
                    border: 2px solid #e74c3c;
                    border-radius: 6px;
                    padding: 5px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
            self.timeFinDias.setStyleSheet("""
                QTimeEdit {
                    background: #ffe6e6;
                    border: 2px solid #e74c3c;
                    border-radius: 6px;
                    padding: 5px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)

    def cargarDatos(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT idProm, nomProm, precioProm, imgProm, 
                   fechaEspecifica, fechaInicio, fechaFin, 
                   horaInicio, horaFin 
            FROM Promocion 
            WHERE nomProm=?
        """, (self.nomProm,))
        resultado = c.fetchone()
        if not resultado:
            QMessageBox.critical(self, "Advertencia", "Promoción no encontrada")
            self.reject()
            return
        self.idProm = resultado[0]
        self.campoNombre.setText(resultado[1])
        self.campoPrecio.setText(str(resultado[2]))
        if resultado[3]:
            pixmap = QPixmap()
            pixmap.loadFromData(resultado[3])
            self.botonImagen.setIcon(QIcon(pixmap))
            self.botonImagen.setIconSize(QSize(170, 170))
        fecha_especifica = resultado[4]
        fecha_inicio = resultado[5]
        fecha_fin = resultado[6]
        hora_inicio = resultado[7]
        hora_fin = resultado[8]
        c.execute("SELECT COUNT(*) FROM PromocionDias WHERE idProm=?", (self.idProm,))
        tiene_dias_semana = c.fetchone()[0] > 0
        self.checkFechaEspec.setChecked(False)
        self.checkPeriodo.setChecked(False)
        self.checkDiasSemana.setChecked(False)
        if fecha_especifica is not None:
            self.checkFechaEspec.setChecked(True)
            self.dateFechaEspec.setDate(QDate.fromString(fecha_especifica, "yyyy-MM-dd"))
            if hora_inicio is not None:
                self.timeInicioFechaEspec.setTime(QTime.fromString(hora_inicio, "HH:mm:ss"))
            if hora_fin is not None:
                self.timeFinFechaEspec.setTime(QTime.fromString(hora_fin, "HH:mm:ss"))   
        elif fecha_inicio is not None:
            self.checkPeriodo.setChecked(True)
            self.dateInicio.setDate(QDate.fromString(fecha_inicio, "yyyy-MM-dd"))
            if fecha_fin is not None:
                self.dateFin.setDate(QDate.fromString(fecha_fin, "yyyy-MM-dd"))
            if tiene_dias_semana:
                self.checkDiasSemana.setChecked(True)
                if hora_inicio is not None:
                    self.timeInicioDias.setTime(QTime.fromString(hora_inicio, "HH:mm:ss"))
                if hora_fin is not None:
                    self.timeFinDias.setTime(QTime.fromString(hora_fin, "HH:mm:ss"))
            else:
                if hora_inicio is not None:
                    self.timeInicioPeriodo.setTime(QTime.fromString(hora_inicio, "HH:mm:ss"))
                if hora_fin is not None:
                    self.timeFinPeriodo.setTime(QTime.fromString(hora_fin, "HH:mm:ss")) 
        elif tiene_dias_semana:
            self.checkDiasSemana.setChecked(True)
            if hora_inicio is not None:
                self.timeInicioDias.setTime(QTime.fromString(hora_inicio, "HH:mm:ss"))
            if hora_fin is not None:
                self.timeFinDias.setTime(QTime.fromString(hora_fin, "HH:mm:ss"))
        c.execute("SELECT diaSemana FROM PromocionDias WHERE idProm=?", (self.idProm,))
        dias = [d[0] for d in c.fetchall()]
        for checkbox in self.diasCheckboxes:
            checkbox.setChecked(checkbox.diaNum in dias)
        self.actualizar_colores_horas()
        c.execute("""
            SELECT P.nomProd, PP.cantidadProdProm
            FROM PromocionProd PP
            JOIN Producto P ON PP.idProd = P.idProd
            WHERE PP.idProm = ?
        """, (self.idProm,))
        productos = c.fetchall()
        self.cargarTablaProductos(productos)
        conn.close()

    def cargarTablaProductos(self, productos):
        self.tablaProductos.setRowCount(0)
        for row, (nombre, cantidad) in enumerate(productos):
            self.tablaProductos.insertRow(row)
            item=QTableWidgetItem(nombre)
            item.setTextAlignment(Qt.AlignCenter)
            self.tablaProductos.setItem(row,0,item)
            item=QTableWidgetItem(str(cantidad))
            item.setTextAlignment(Qt.AlignCenter)
            self.tablaProductos.setItem(row,1,item)
            btnModificar = QPushButton("✏️")
            btnModificar.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #f39c12, stop: 1 #e67e22);
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #e67e22, stop: 1 #d35400);
                }
            """)
            btnModificar.setCursor(Qt.PointingHandCursor)
            btnModificar.clicked.connect(lambda _, r=row: self.modificarProducto(r))
            self.tablaProductos.setCellWidget(row,2,btnModificar)
            btnEliminar = QPushButton("🗑️")
            btnEliminar.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #e74c3c, stop: 1 #c0392b);
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #c0392b, stop: 1 #a93226);
                }
            """)
            btnEliminar.setCursor(Qt.PointingHandCursor)
            btnEliminar.clicked.connect(lambda _, r=row: self.eliminarProducto(r))
            self.tablaProductos.setCellWidget(row,3,btnEliminar)

    def agregarProducto(self):
        producto = self.comboProductos.currentText()
        cantidad = self.editCantidad.text().strip()
        if not producto or producto == "No hay productos disponibles":
            QMessageBox.warning(self, "Advertencia", "Seleccione un producto válido")
            return
        if not cantidad:
            QMessageBox.warning(self, "Advertencia", "Escriba una cantidad")
            return
        for row in range(self.tablaProductos.rowCount()):
            if self.tablaProductos.item(row,0).text() == producto:
                QMessageBox.warning(self, "Advertencia", f"El producto '{producto}' ya está en la promoción")
                return
        fila = self.tablaProductos.rowCount()
        self.tablaProductos.insertRow(fila)
        item=QTableWidgetItem(producto)
        item.setTextAlignment(Qt.AlignCenter)
        self.tablaProductos.setItem(fila,0,item)
        item=QTableWidgetItem(cantidad)
        item.setTextAlignment(Qt.AlignCenter)
        self.tablaProductos.setItem(fila,1,item)
        btnModificar = QPushButton("✏️")
        btnModificar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f39c12, stop: 1 #e67e22);
                color: white;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e67e22, stop: 1 #d35400);
            }
        """)
        btnModificar.setCursor(Qt.PointingHandCursor)
        btnModificar.clicked.connect(lambda _, r=fila: self.modificarProducto(r))
        self.tablaProductos.setCellWidget(fila,2,btnModificar)
        btnEliminar = QPushButton("🗑️")
        btnEliminar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e74c3c, stop: 1 #c0392b);
                    color: white;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c0392b, stop: 1 #a93226);
            }
        """)
        btnEliminar.setCursor(Qt.PointingHandCursor)
        btnEliminar.clicked.connect(lambda _, r=fila: self.eliminarProducto(r))
        self.tablaProductos.setCellWidget(fila,3,btnEliminar)
        self.editCantidad.clear()
        self.comboProductos.setCurrentIndex(0)

    def modificarProducto(self, fila):
        nombre_actual = self.tablaProductos.item(fila,0).text()
        cantidad_actual = self.tablaProductos.item(fila,1).text()
        dialog = QDialog(self)
        dialog.setWindowTitle("Modificar Producto")
        dialog.setFixedSize(620, 250)
        dialog.setStyleSheet("""
            QDialog {
                background: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout = QVBoxLayout(dialog)
        filtros_layout = QHBoxLayout()
        filtros_layout.addWidget(QLabel("Categoría:"))
        combo_categorias = QComboBox()
        combo_categorias.setFixedHeight(32)
        combo_categorias.setMinimumContentsLength(15)
        combo_categorias.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 5px;
                min-width: 150px;
            }
        """)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT idCategoria, nomCategoria FROM Categoria WHERE activa = 1 ORDER BY nomCategoria")
        categorias = c.fetchall()
        combo_categorias.addItem("Todas las categorías", -1)
        for id_cat, nombre in categorias:
            combo_categorias.addItem(nombre, id_cat)
        filtros_layout.addWidget(combo_categorias)
        filtros_layout.addWidget(QLabel("Subcategoría:"))
        combo_subcategorias = QComboBox()
        combo_subcategorias.setFixedHeight(32)
        combo_subcategorias.setMinimumContentsLength(15)
        combo_subcategorias.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 5px;
                min-width: 150px;
            }
        """)
        filtros_layout.addWidget(combo_subcategorias)
        filtros_layout.addStretch()

        def cargar_subcategorias_dialog():
            categoria_id = combo_categorias.currentData()
            combo_subcategorias.clear()
            if categoria_id == -1:
                c.execute("""
                    SELECT S.idSubcategoria, S.nombre 
                    FROM Subcategoria S
                    WHERE S.activa = 1 
                    ORDER BY S.nombre
                """)
                subcategorias = c.fetchall()
                combo_subcategorias.addItem("Todas las subcategorías", -1)
                for id_sub, nombre in subcategorias:
                    combo_subcategorias.addItem(nombre, id_sub)
            else:
                c.execute("""
                    SELECT S.idSubcategoria, S.nombre 
                    FROM Subcategoria S
                    WHERE S.idCategoria = ? AND S.activa = 1 
                    ORDER BY S.nombre
                """, (categoria_id,))
                subcategorias = c.fetchall()
                combo_subcategorias.addItem("Todas las subcategorías", -1)
                for id_sub, nombre in subcategorias:
                    combo_subcategorias.addItem(nombre, id_sub)
            if combo_subcategorias.count() > 0:
                combo_subcategorias.setCurrentIndex(0)

        def cargar_productos_dialog():
            subcategoria_id = combo_subcategorias.currentData()
            categoria_id = combo_categorias.currentData()
            combo.clear()
            if subcategoria_id == -1 and categoria_id == -1:
                c.execute("""
                    SELECT P.nomProd 
                    FROM Producto P
                    JOIN Subcategoria S ON P.idSubcategoria = S.idSubcategoria
                    WHERE P.activo = 1 
                    ORDER BY P.nomProd
                """)
            elif subcategoria_id == -1 and categoria_id != -1:
                c.execute("""
                    SELECT P.nomProd 
                    FROM Producto P
                    JOIN Subcategoria S ON P.idSubcategoria = S.idSubcategoria
                    WHERE P.activo = 1 AND S.idCategoria = ?
                    ORDER BY P.nomProd
                """, (categoria_id,))
            else:
                c.execute("""
                    SELECT P.nomProd 
                    FROM Producto P
                    WHERE P.activo = 1 AND P.idSubcategoria = ?
                    ORDER BY P.nomProd
                """, (subcategoria_id,))
            productos = [p[0] for p in c.fetchall()]
            if productos:
                combo.addItems(productos)
                if nombre_actual in productos:
                    combo.setCurrentText(nombre_actual)
                else:
                    combo.setCurrentIndex(0)
            else:
                combo.addItem("No hay productos disponibles")

        combo_categorias.currentIndexChanged.connect(lambda: cargar_subcategorias_dialog())
        combo_subcategorias.currentIndexChanged.connect(lambda: cargar_productos_dialog())
        layout.addLayout(filtros_layout)
        combo = QComboBox()
        combo.setMinimumContentsLength(18)
        combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 5px;
                min-width: 200px;
            }
        """)
        layout.addWidget(QLabel("Producto:"))
        layout.addWidget(combo)
        edit_cantidad = QLineEdit(cantidad_actual)
        edit_cantidad.setFixedHeight(35)
        edit_cantidad.setValidator(QRegExpValidator(QRegExp("[0-9]+")))
        edit_cantidad.setMaxLength(3)
        edit_cantidad.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        layout.addWidget(QLabel("Cantidad:"))
        layout.addWidget(edit_cantidad)
        btns = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_cancelar = QPushButton("Cancelar")
        btn_guardar.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
        """)
    
        def guardar():
            nuevo_nombre = combo.currentText()
            nueva_cantidad = edit_cantidad.text().strip()
            if not nuevo_nombre or nuevo_nombre == "No hay productos disponibles":
                QMessageBox.information(dialog, "Aviso", "Seleccione un producto válido")
                return
            if not nueva_cantidad:
                QMessageBox.information(dialog, "Aviso", "Debe llenar los campos necesarios")
                return
            for r in range(self.tablaProductos.rowCount()):
                if r != fila and self.tablaProductos.item(r,0).text() == nuevo_nombre:
                    QMessageBox.information(dialog, "Aviso", f"El producto '{nuevo_nombre}' ya está en la promoción")
                    return
            item=QTableWidgetItem(nuevo_nombre)
            item.setTextAlignment(Qt.AlignCenter)
            self.tablaProductos.setItem(fila,0,item)
            item=QTableWidgetItem(nueva_cantidad)
            item.setTextAlignment(Qt.AlignCenter)
            self.tablaProductos.setItem(fila,1,item)
            dialog.accept()

        btn_guardar.clicked.connect(guardar)
        btn_cancelar.clicked.connect(dialog.reject)
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        cargar_subcategorias_dialog()
        dialog.exec_()
        conn.close()

    def eliminarProducto(self,fila):
        self.tablaProductos.removeRow(fila)
        for i in range(self.tablaProductos.rowCount()):
            boton=self.tablaProductos.cellWidget(i,2)
            boton.disconnect()
            boton.clicked.connect(lambda _, r=i: self.modificarProducto(r))
            boton=self.tablaProductos.cellWidget(i,3)
            boton.disconnect()
            boton.clicked.connect(lambda _, r=i: self.eliminarProducto(r))

    def actualizarFoto(self):
        file_path,_ = QFileDialog.getOpenFileName(self,"Seleccionar imagen","","Imágenes (*.png *.jpg *.jpeg *.bmp *.webp)")
        if file_path:
            pixmap = QPixmap(file_path).scaled(160,160,Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.botonImagen.setIcon(QIcon(pixmap))
            self.botonImagen.setIconSize(QSize(160,160))

    def obtenerBytesImagen(self):
        icon = self.botonImagen.icon()
        if icon.isNull():
            return None
        pixmap = icon.pixmap(160,160)
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        pixmap.save(buffer,"PNG")
        return buffer.data()

    def guardarCambios(self):
        nombre = self.campoNombre.text().strip()
        try:
            precio = float(self.campoPrecio.text())
        except ValueError:
            QMessageBox.warning(self,"Advertencia","Precio inválido")
            return
        if not nombre:
            QMessageBox.warning(self,"Advertencia","Nombre obligatorio")
            return
        if self.tablaProductos.rowCount() == 0:
            QMessageBox.warning(self,"Advertencia","La promoción debe tener al menos un producto")
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""SELECT * FROM Promocion WHERE nomProm=?""",(nombre,))
        resultados=c.fetchall()
        if resultados and nombre!=self.nomProm:
            QMessageBox.warning(self,"Advertencia","Este nombre de promocion ya ha sido registrado")
            conn.close()
            return
        fecha_especifica = None
        fecha_inicio = None
        fecha_fin = None
        hora_inicio = None
        hora_fin = None
        if self.checkFechaEspec.isChecked():
            fecha_especifica = self.dateFechaEspec.date().toString("yyyy-MM-dd")
            hora_inicio = self.timeInicioFechaEspec.time().toString("HH:mm:00")
            hora_fin = self.timeFinFechaEspec.time().toString("HH:mm:00")
        elif self.checkPeriodo.isChecked():
            fecha_inicio = self.dateInicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.dateFin.date().toString("yyyy-MM-dd")
            if self.checkDiasSemana.isChecked():
                hora_inicio = self.timeInicioDias.time().toString("HH:mm:00")
                hora_fin = self.timeFinDias.time().toString("HH:mm:00")
            else:
                hora_inicio = self.timeInicioPeriodo.time().toString("HH:mm:00")
                hora_fin = self.timeFinPeriodo.time().toString("HH:mm:00")
        elif self.checkDiasSemana.isChecked():
            hora_inicio = self.timeInicioDias.time().toString("HH:mm:00")
            hora_fin = self.timeFinDias.time().toString("HH:mm:00")
        c.execute("""UPDATE Promocion SET nomProm=?, precioProm=?, imgProm=?, fechaEspecifica=?, 
                     fechaInicio=?, fechaFin=?, horaInicio=?, horaFin=? WHERE idProm=?""",
                  (nombre, precio, self.obtenerBytesImagen(), fecha_especifica, 
                   fecha_inicio, fecha_fin, hora_inicio, hora_fin, self.idProm))
        c.execute("DELETE FROM PromocionDias WHERE idProm=?", (self.idProm,))
        if self.checkDiasSemana.isChecked():
            for checkbox in self.diasCheckboxes:
                if checkbox.isChecked():
                    c.execute("INSERT INTO PromocionDias (idProm, diaSemana) VALUES (?,?)",
                             (self.idProm, checkbox.diaNum))
        c.execute("DELETE FROM PromocionProd WHERE idProm=?",(self.idProm,))
        for row in range(self.tablaProductos.rowCount()):
            nomProd = self.tablaProductos.item(row,0).text()
            cantidad = float(self.tablaProductos.item(row,1).text())
            c.execute("SELECT idProd FROM Producto WHERE nomProd=?",(nomProd,))
            idProd = c.fetchone()[0]
            c.execute("INSERT INTO PromocionProd (idProm,idProd,cantidadProdProm) VALUES (?,?,?)",(self.idProm,idProd,cantidad))
        conn.commit()
        conn.close()
        QMessageBox.information(self,"Éxito","Promoción modificada correctamente")
        self.accept()