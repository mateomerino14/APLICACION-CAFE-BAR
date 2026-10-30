import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3

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

class RegistroPromociones(QWidget):
    def __init__(self):
        super().__init__()  
        self.setStyleSheet("""
        QWidget{ 
            background-color: #f8fafc;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        .miLabelPersonalizado {
            font-weight: bold;
            color: #2c3e50;
            font-size: 13px;
            min-width: 90px;
        }
        QLineEdit {
            background-color: white;
            border: 2px solid #3498db;
            border-radius: 5px;
            padding: 6px;
            font-size: 13px;
        }
        QComboBox{
            border:2px solid #3498db;
            background:white;
            font-size: 12px;
         }
        QComboBox QAbstractItemView {
             background-color:white;
             font-size:11px;
             font-weight: bold;
        }
        QDateEdit, QTimeEdit {
            border:2px solid #3498db;
            background:white;
            border-radius: 5px;
            padding: 3px;
            font-size: 12px;
        }
        QCheckBox {
            spacing: 3px;
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
        QLabel {
            font-size: 12px;
        }
        QPushButton {
            font-size: 13px;
        }
        QMessageBox {
            background: #ffffff;
        }
        QMessageBox QLabel {
            color: #2c3e50;
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
        self.layoutPrincipal=QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(15,15,15,15)
        self.iniciarPagina()
        self.showMaximized()

    def cargarNombresPromociones(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT nomProm FROM Promocion ORDER BY nomProm COLLATE NOCASE ASC")
            nombres = [row[0] for row in c.fetchall()]
            conn.close()
            return nombres
        except Exception:
            return []

    def iniciarPagina(self):
        QLocale.setDefault(QLocale(QLocale.Spanish, QLocale.Bolivia))
        layout1=QHBoxLayout()
        self.layoutPrincipal.addLayout(layout1,stretch=20)
        layout2=QVBoxLayout()
        layout2.setSpacing(12)
        layout1.addLayout(layout2)
        tablaRegistrados=QTableWidget()
        tablaRegistrados.setColumnCount(6)
        conjunto=set()
        tablaRegistrados.setHorizontalHeaderLabels(["Producto","Precio de Venta","Cantidad","Subtotal","Operadores","Accion"])
        tablaRegistrados.setEditTriggers(QTableWidget.NoEditTriggers)
        tablaRegistrados.setSelectionMode(QTableWidget.NoSelection)
        tablaRegistrados.setFocusPolicy(Qt.NoFocus)
        header=tablaRegistrados.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        tablaRegistrados.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                gridline-color: #ecf0f1;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 4px;
                border: none;
                font-size: 13px;
            }
        """)
        layout3=QVBoxLayout()
        layout3.addWidget(tablaRegistrados)
        layout4=QHBoxLayout()
        layout4.setSpacing(0)
        layout4.addStretch(10)
        layout4.setContentsMargins(0,0,0,0)
        totalEtiqueta=QLabel("Total:")
        totalEtiqueta.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                background-color: #ecf0f1;
                padding: 8px;
                border-radius: 5px;
                border: 2px solid #bdc3c7;
            }
        """)
        self.totalCampo=QLabel("0.00")
        self.totalCampo.setStyleSheet("""
         QLabel {
             font-size: 18px;
             font-weight: bold;
             color: #e74c3c;
             background-color: #f9f9f9;
             padding: 8px;
             border-radius: 5px;
             border: 2px solid #e74c3c;
             min-width: 90px;
         }
     """)
        self.totalCampo.setAlignment(Qt.AlignCenter)
        layout4.addWidget(totalEtiqueta,stretch=1,alignment=Qt.AlignCenter)
        layout4.addWidget(self.totalCampo,stretch=1,alignment=Qt.AlignRight)
        layout3.addLayout(layout4)
        layout1.addLayout(layout3)
        layoutCategoria=QHBoxLayout()
        nombre=QLabel("Nombre:")
        nombre.setProperty("class", "miLabelPersonalizado")
        nombre.setStyleSheet("""background-color:transparent;""")
        campoNombre=QLineEdit()
        campoNombre.setPlaceholderText("Nombre de la Promocion")
        campoNombre.setFixedHeight(35)
        nombre_promocion_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ0-9°%.,\\-\\s]*")
        campoNombre.setValidator(QRegExpValidator(nombre_promocion_regex))
        campoNombre.setMaxLength(30)

        self.completerPromociones = QCompleter(self.cargarNombresPromociones(), self)
        self.completerPromociones.setCaseSensitivity(Qt.CaseInsensitive)
        self.completerPromociones.setFilterMode(Qt.MatchContains)
        campoNombre.setCompleter(self.completerPromociones)

        layoutCategoria.addWidget(nombre)
        layoutCategoria.addWidget(campoNombre)
        layoutCategoria3=QHBoxLayout()
        precioVenta=QLabel("Precio Venta:")
        precioVenta.setProperty("class", "miLabelPersonalizado")
        precioVenta.setStyleSheet("""background-color:transparent;""")
        campoPrecioVenta=QLineEdit()
        campoPrecioVenta.setPlaceholderText("0.00")
        campoPrecioVenta.setFixedHeight(35)
        validador=QRegExpValidator(QRegExp(r"[0-9]{1,8}(\.[0-9]{0,2})?"))
        campoPrecioVenta.setValidator(validador)
        campoPrecioVenta.setMaxLength(11)
        layoutCategoria3.addWidget(precioVenta)
        layoutCategoria3.addWidget(campoPrecioVenta)
        layout2.addLayout(layoutCategoria)
        layout2.addLayout(layoutCategoria3)
        layoutFiltros = QHBoxLayout()
        categoria_label = QLabel("Categoría:")
        categoria_label.setProperty("class", "miLabelPersonalizado")
        categoria_label.setStyleSheet("""background-color:transparent;""")
        self.comboCategoria = QComboBox()
        self.comboCategoria.setFixedWidth(180)
        self.comboCategoria.setFixedHeight(35)
        self.comboCategoria.currentIndexChanged.connect(self.cargar_subcategorias)
        subcategoria_label = QLabel("Subcategoría:")
        subcategoria_label.setProperty("class", "miLabelPersonalizado")
        subcategoria_label.setStyleSheet("""background-color:transparent;""")
        self.comboSubcategoria = QComboBox()
        self.comboSubcategoria.setFixedWidth(180)
        self.comboSubcategoria.setFixedHeight(35)
        self.comboSubcategoria.currentIndexChanged.connect(self.cargar_productos_por_subcategoria)
        layoutFiltros.addWidget(categoria_label)
        layoutFiltros.addWidget(self.comboCategoria)
        layoutFiltros.addWidget(subcategoria_label)
        layoutFiltros.addWidget(self.comboSubcategoria)
        layoutFiltros.addStretch()
        layout2.addLayout(layoutFiltros)
        layoutCategoria7=QHBoxLayout()
        ingrediente=QLabel("Producto:")
        ingrediente.setProperty("class", "miLabelPersonalizado")
        ingrediente.setStyleSheet("""background-color:transparent;""")
        self.campoProducto=QComboBox()
        self.campoProducto.setFixedWidth(250)
        self.campoProducto.setFixedHeight(35)
        self.cargar_categorias()
        cantidad=QLabel("Cantidad: ")
        cantidad.setProperty("class", "miLabelPersonalizado")
        cantidad.setStyleSheet("""background-color:transparent;""")
        campoCantidad=QLineEdit()
        campoCantidad.setPlaceholderText("0")
        campoCantidad.setValidator(QRegExpValidator(QRegExp("[0-9]+")))
        campoCantidad.setMaxLength(3)
        campoCantidad.setFixedHeight(35)
        layoutCategoria7.addWidget(ingrediente)
        layoutCategoria7.addWidget(self.campoProducto)
        layoutCategoria7.addWidget(cantidad)
        layoutCategoria7.addWidget(campoCantidad)
        botonAnadir=QPushButton("Añadir")
        botonAnadir.setFixedHeight(32)
        botonAnadir.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
                min-width: 70px;
                font-size: 13px;
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
                self.timeInicioDias.setStyleSheet("""
                    QTimeEdit {
                        border: 2px solid #e74c3c;
                        background-color: #ffeaea;
                        border-radius: 5px;
                        padding: 3px;
                        font-size: 12px;
                        color: #c0392b;
                        font-weight: bold;
                    }
                """)
                self.timeFinDias.setStyleSheet("""
                    QTimeEdit {
                        border: 2px solid #e74c3c;
                        background-color: #ffeaea;
                        border-radius: 5px;
                        padding: 3px;
                        font-size: 12px;
                        color: #c0392b;
                        font-weight: bold;
                    }
                """)
                if self.checkPeriodo.isChecked():
                    self.timeInicioPeriodo.setStyleSheet("""
                        QTimeEdit {
                            border: 2px solid #f39c12;
                            background-color: #fff3cd;
                            border-radius: 5px;
                            padding: 3px;
                            font-size: 12px;
                            color: #856404;
                        }
                    """)
                    self.timeFinPeriodo.setStyleSheet("""
                        QTimeEdit {
                            border: 2px solid #f39c12;
                            background-color: #fff3cd;
                            border-radius: 5px;
                            padding: 3px;
                            font-size: 12px;
                            color: #856404;
                        }
                    """)
            else:
                self.timeInicioDias.setStyleSheet("""
                    QTimeEdit {
                        border: 2px solid #3498db;
                        background: white;
                        border-radius: 5px;
                        padding: 3px;
                        font-size: 12px;
                    }
                """)
                self.timeFinDias.setStyleSheet("""
                    QTimeEdit {
                        border: 2px solid #3498db;
                        background: white;
                        border-radius: 5px;
                        padding: 3px;
                        font-size: 12px;
                    }
                """)
                if self.checkPeriodo.isChecked():
                    self.timeInicioPeriodo.setStyleSheet("""
                        QTimeEdit {
                            border: 2px solid #3498db;
                            background: white;
                            border-radius: 5px;
                            padding: 3px;
                            font-size: 12px;
                        }
                    """)
                    self.timeFinPeriodo.setStyleSheet("""
                        QTimeEdit {
                            border: 2px solid #3498db;
                            background: white;
                            border-radius: 5px;
                            padding: 3px;
                            font-size: 12px;
                        }
                    """)
        self.checkDiasSemana.toggled.connect(toggle_dias_semana)
        layoutControlTiempo.insertWidget(2, self.checkDiasSemana)
        def actualizar_estilos_periodo():
            if self.checkPeriodo.isChecked() and self.checkDiasSemana.isChecked():
                self.timeInicioPeriodo.setStyleSheet("""
                    QTimeEdit {
                        border: 2px solid #f39c12;
                        background-color: #fff3cd;
                        border-radius: 5px;
                        padding: 3px;
                        font-size: 12px;
                        color: #856404;
                    }
                """)
                self.timeFinPeriodo.setStyleSheet("""
                    QTimeEdit {
                        border: 2px solid #f39c12;
                        background-color: #fff3cd;
                        border-radius: 5px;
                        padding: 3px;
                        font-size: 12px;
                        color: #856404;
                    }
                """)
            elif self.checkPeriodo.isChecked():
                self.timeInicioPeriodo.setStyleSheet("""
                    QTimeEdit {
                        border: 2px solid #3498db;
                        background: white;
                        border-radius: 5px;
                        padding: 3px;
                        font-size: 12px;
                    }
                """)
                self.timeFinPeriodo.setStyleSheet("""
                    QTimeEdit {
                        border: 2px solid #3498db;
                        background: white;
                        border-radius: 5px;
                        padding: 3px;
                        font-size: 12px;
                    }
                """)
            else:
                self.timeInicioPeriodo.setStyleSheet("""
                    QTimeEdit {
                        border: 2px solid #3498db;
                        background: white;
                        border-radius: 5px;
                        padding: 3px;
                        font-size: 12px;
                    }
                """)
                self.timeFinPeriodo.setStyleSheet("""
                    QTimeEdit {
                        border: 2px solid #3498db;
                        background: white;
                        border-radius: 5px;
                        padding: 3px;
                        font-size: 12px;
                    }
                """)
        self.checkPeriodo.toggled.connect(actualizar_estilos_periodo)
        layout2.addLayout(layoutControlTiempo)
        layoutCategoria8=QHBoxLayout()
        imagenPromocion=QPushButton()
        camara_icon_path = get_resource_path(os.path.join('Imagenes', 'camara.png'))
        if os.path.exists(camara_icon_path):
            imagenPromocion.setIcon(QIcon(camara_icon_path))
        else:
            pixmap = QPixmap(120, 120)
            pixmap.fill(QColor("#3498db"))
            imagenPromocion.setIcon(QIcon(pixmap))
        imagenPromocion.setStyleSheet("""
          QPushButton {
              background-color: #ecf0f1;
              border: 2px dashed #3498db;
              border-radius: 8px;
          }
          QPushButton:hover {
              background-color: #d6eaf8;
              border: 2px dashed #2c81ba;
          }
          QPushButton:pressed {
              background-color: #aed6f1;
              border: 2px solid #2c81ba;
          }
      """)
        imagenPromocion.setFixedSize(140,140)
        imagenPromocion.setIconSize(QSize(120,120))
        imagenPromocion.clicked.connect(lambda:self.actualizarFoto(imagenPromocion))
        layoutCategoria8.addWidget(imagenPromocion)
        layout2.addLayout(layoutCategoria8)
        botonRegistrar=QPushButton("Registrar")
        botonRegistrar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 16px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        botonRegistrar.clicked.connect(lambda:self.subirInformacion(
            campoNombre, campoPrecioVenta, self.campoProducto, campoCantidad, 
            imagenPromocion, tablaRegistrados, conjunto))
        botonAnadir.clicked.connect(lambda:self.anadirElemento(
            [self.campoProducto.currentText(), campoCantidad.text()], 
            tablaRegistrados, conjunto,campoCantidad))
        self.layoutPrincipal.addStretch(2)
        self.layoutPrincipal.addWidget(botonRegistrar)
    

    def cargar_categorias(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        self.comboCategoria.clear()
        self.comboSubcategoria.clear()
        self.campoProducto.clear()
        self.comboCategoria.addItem("Todas las categorías", -1)
        c.execute("""SELECT idCategoria, nomCategoria FROM Categoria WHERE activa = 1 ORDER BY nomCategoria""")
        categorias = c.fetchall()
        for id_cat, nombre_cat in categorias:
            self.comboCategoria.addItem(nombre_cat, id_cat)
        conn.close()
        if self.comboCategoria.count() > 0:
            self.comboCategoria.setCurrentIndex(0)
            self.cargar_subcategorias()
    

    def cargar_subcategorias(self):
        categoria_id = self.comboCategoria.currentData()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        self.comboSubcategoria.clear()
        self.campoProducto.clear()
        self.comboSubcategoria.addItem("Todas las subcategorías", -1)
        if categoria_id == -1:
            c.execute("""SELECT idSubcategoria, nombre FROM Subcategoria WHERE activa = 1 ORDER BY nombre""")
        else:
            c.execute("""SELECT idSubcategoria, nombre FROM Subcategoria 
                        WHERE idCategoria = ? AND activa = 1 ORDER BY nombre""", (categoria_id,))
        subcategorias = c.fetchall()
        for id_subcat, nombre_subcat in subcategorias:
            self.comboSubcategoria.addItem(nombre_subcat, id_subcat)
        conn.close()
        if self.comboSubcategoria.count() > 0:
            self.comboSubcategoria.setCurrentIndex(0)
            self.cargar_productos_por_subcategoria()
    

    def cargar_productos_por_subcategoria(self):
        subcategoria_id = self.comboSubcategoria.currentData()
        categoria_id = self.comboCategoria.currentData()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        self.campoProducto.clear()
        self.campoProducto.setCurrentIndex(-1)
        if subcategoria_id == -1:
            if categoria_id == -1:
                consulta = """SELECT p.nomProd FROM Producto p
                            JOIN Subcategoria s ON p.idSubcategoria = s.idSubcategoria
                            WHERE p.activo = 1 AND s.activa = 1
                            ORDER BY p.nomProd"""
                c.execute(consulta)
            else:
                consulta = """SELECT p.nomProd FROM Producto p
                            JOIN Subcategoria s ON p.idSubcategoria = s.idSubcategoria
                            WHERE s.idCategoria = ? AND p.activo = 1 AND s.activa = 1
                            ORDER BY p.nomProd"""
                c.execute(consulta, (categoria_id,))
        else:
            consulta = """SELECT nomProd FROM Producto 
                         WHERE idSubcategoria = ? AND activo = 1
                         ORDER BY nomProd"""
            c.execute(consulta, (subcategoria_id,))
        resultados = [str(elem[0]) for elem in c.fetchall()]
        if len(resultados) > 20:
            letras_actuales = set()
            productos_ordenados = sorted(resultados)
            for producto in productos_ordenados:
                letra = producto[0].upper() if producto else ""
                if letra and letra not in letras_actuales:
                    self.campoProducto.addItem(f"--- {letra} ---")
                    self.campoProducto.model().item(self.campoProducto.count()-1).setEnabled(False)
                    letras_actuales.add(letra)
                self.campoProducto.addItem(producto)
        else:
            for producto in sorted(resultados):
                self.campoProducto.addItem(producto)
        conn.close()
        if self.campoProducto.count() > 0:
            for i in range(self.campoProducto.count()):
                if self.campoProducto.model().item(i).isEnabled():
                    self.campoProducto.setCurrentIndex(i)
                    break
    

    def actualizarProductos(self):
        self.cargar_categorias()


    def calcularTotal(self,tabla):
        total=0;
        for i in range(tabla.rowCount()):
            item=tabla.item(i,3)
            subtotal=float(item.text())
            total+=subtotal
        self.totalCampo.setText(f"{total:.2f}")


    def actualizarFoto(self,imagenProducto):
        file_path,_=QFileDialog.getOpenFileName(self,"Seleccionar una imagen","","Imágenes (*.png *.jpg *.jpeg *.bmp *.webp)")
        if file_path:
            pixmap=QPixmap(file_path)
            if not pixmap.isNull():
                pixmap=pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                imagenProducto.setIcon(QIcon(pixmap))
                imagenProducto.setIconSize(QSize(120,120))


    def limpiarCampos(self,campo1,campo2,campo3,campo4,campo5,tabla,conjunto):
        campo1.setText("")
        campo2.setText("")
        campo3.setCurrentIndex(-1)
        campo4.setText("")
        camara_icon_path = get_resource_path(os.path.join('Imagenes', 'camara.png'))
        if os.path.exists(camara_icon_path):
            campo5.setIcon(QIcon(camara_icon_path))
        else:
            pixmap = QPixmap(120, 120)
            pixmap.fill(QColor("#3498db"))
            campo5.setIcon(QIcon(pixmap))
        tabla.setRowCount(0)
        self.totalCampo.setText("0.00")
        conjunto.clear()
        self.checkFechaEspec.setChecked(False)
        self.checkPeriodo.setChecked(False)
        self.checkDiasSemana.setChecked(False)
        for checkbox in self.diasCheckboxes:
            checkbox.setChecked(False)
        self.timeInicioDias.setStyleSheet("""
            QTimeEdit {
                border: 2px solid #3498db;
                background: white;
                border-radius: 5px;
                padding: 3px;
                font-size: 12px;
            }
        """)
        self.timeFinDias.setStyleSheet("""
            QTimeEdit {
                border: 2px solid #3498db;
                background: white;
                border-radius: 5px;
                padding: 3px;
                font-size: 12px;
            }
        """)
        self.timeInicioPeriodo.setStyleSheet("""
            QTimeEdit {
                border: 2px solid #3498db;
                background: white;
                border-radius: 5px;
                padding: 3px;
                font-size: 12px;
            }
        """)
        self.timeFinPeriodo.setStyleSheet("""
            QTimeEdit {
                border: 2px solid #3498db;
                background: white;
                border-radius: 5px;
                padding: 3px;
                font-size: 12px;
            }
        """)
        self.completerPromociones.setModel(QStringListModel(self.cargarNombresPromociones()))
        self.cargar_categorias()


    def subirInformacion(self,nombre,precioVenta,campoProducto,campoCantidad,campoImagen,tabla,conjunto):
        campo11=nombre.text()
        campo22=precioVenta.text()       
        if campo11=="" or campo22=="":
            QMessageBox.information(self,"Advertencia","Debe llenar los campos obligatorios")
            return 
        if tabla.rowCount()==0:
            QMessageBox.information(self,"Advertencia","La promocion debe tener por lo menos un producto")
            return
        conn=sqlite3.connect(DB_PATH)
        c=conn.cursor()
        c.execute("""SELECT * FROM Promocion WHERE nomProm=?""",(campo11,))
        resultados=c.fetchall()
        conn.close()
        if resultados:
            QMessageBox.information(self,"Advertencia","Esta promocion ya ha sido registrada")
            return
        icono=campoImagen.icon()
        imagen=icono.pixmap(120,120)
        buffer=QBuffer()
        buffer.open(QIODevice.ReadWrite)
        imagen.save(buffer,"PNG")
        datosImagen=buffer.data()
        conn=sqlite3.connect(DB_PATH)
        c=conn.cursor()
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
        consulta="""INSERT INTO Promocion(
                    nomProm, precioProm, imgProm, fechaEspecifica, 
                    fechaInicio, fechaFin, horaInicio, horaFin) 
                    VALUES(?,?,?,?,?,?,?,?)"""
        c.execute(consulta,(campo11, campo22, datosImagen, fecha_especifica, fecha_inicio, fecha_fin, hora_inicio, hora_fin))
        indicePromocion=c.lastrowid
        if self.checkDiasSemana.isChecked():
            for checkbox in self.diasCheckboxes:
                if checkbox.isChecked():
                    c.execute("""INSERT INTO PromocionDias (idProm, diaSemana) VALUES (?,?)""",
                             (indicePromocion, checkbox.diaNum))
        for i in range(tabla.rowCount()):
            item=tabla.item(i,0)
            c.execute("""SELECT idProd FROM Producto WHERE nomProd=?""",(item.text(),))
            resultados=c.fetchone()
            indiceProducto=resultados[0]
            item=tabla.item(i,2)
            cantidad=int(item.text())
            consulta="""INSERT INTO PromocionProd VALUES(?,?,?)"""
            c.execute(consulta,(indicePromocion,indiceProducto,cantidad))
        conn.commit()
        conn.close()
        QMessageBox.information(self,"Confirmacion","La promocion se registro con exito")
        self.limpiarCampos(nombre,precioVenta,campoProducto,campoCantidad,campoImagen,tabla,conjunto)
    

    def anadirElemento(self,lista,tabla,conjunto,campoCantidad,bandera=True):
        if self.campoProducto.currentIndex() >= 0:
            current_item = self.campoProducto.model().item(self.campoProducto.currentIndex())
            if current_item and not current_item.isEnabled():
                QMessageBox.critical(self,"Error","No puede seleccionar un separador")
                return
        if lista[0]=="" or lista[1]=="":
            QMessageBox.critical(self,"Error","Debe llenar los campos obligatorios porfavor")
            return
        if lista[0] in conjunto and bandera==True:
           QMessageBox.critical(self,"Error","El producto ya esta registrado")
           return
        fila=tabla.rowCount()
        tabla.insertRow(fila)
        layoutBotonesCantidad=QHBoxLayout()
        layoutBotonesCantidad.setSpacing(12)
        layoutBotonesCantidad.setContentsMargins(0,0,0,0)
        botonAumentar=QPushButton()
        botonAumentar.setFixedHeight(22)
        suma_icon_path = get_resource_path(os.path.join('Imagenes', 'suma.jpg'))
        if os.path.exists(suma_icon_path):
            botonAumentar.setIcon(QIcon(suma_icon_path))
        else:
            botonAumentar.setText("+")
        botonAumentar.setIconSize(QSize(28,35))
        botonAumentar.setCursor(Qt.PointingHandCursor)
        estilo_botones_tabla = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-size: 12px;
            }
        """
        botonAumentar.setStyleSheet(estilo_botones_tabla)
        botonRestar=QPushButton()
        botonRestar.setFixedHeight(22)
        botonRestar.setCursor(Qt.PointingHandCursor)
        resta_icon_path = get_resource_path(os.path.join('Imagenes', 'resta.png'))
        if os.path.exists(resta_icon_path):
            botonRestar.setIcon(QIcon(resta_icon_path))
        else:
            botonRestar.setText("-")
        botonRestar.setIconSize(QSize(22,30))
        botonRestar.setStyleSheet(estilo_botones_tabla)
        botonAumentar.clicked.connect(lambda:self.aumentar(tabla,botonAumentar))
        botonRestar.clicked.connect(lambda:self.restar(tabla,botonRestar))
        layoutBotonesCantidad.addWidget(botonAumentar,alignment=Qt.AlignTop)
        layoutBotonesCantidad.addWidget(botonRestar,alignment=Qt.AlignTop)
        botonEliminar=QPushButton()
        eliminar_icon_path = get_resource_path(os.path.join('Imagenes', 'eliminarSubcategoria.png'))
        if os.path.exists(eliminar_icon_path):
            botonEliminar.setIcon(QIcon(eliminar_icon_path))
        else:
            botonEliminar.setText("🗑️")
        botonEliminar.setStyleSheet(estilo_botones_tabla)
        botonEliminar.clicked.connect(lambda _,e=lista[0]:self.eliminarElemento(e,tabla,conjunto,botonEliminar))
        conn=sqlite3.connect(DB_PATH)
        c=conn.cursor()
        c.execute("""SELECT precioVenta FROM Producto WHERE nomProd=?""",(lista[0],))
        resultados=c.fetchall()
        precio=resultados[0][0]
        conn.close()
        item=QTableWidgetItem(lista[0])
        item.setTextAlignment(Qt.AlignCenter)
        tabla.setItem(fila,0,item)
        item=QTableWidgetItem(str(precio))
        item.setTextAlignment(Qt.AlignCenter)
        tabla.setItem(fila,1,item)
        item=QTableWidgetItem(lista[1])
        item.setTextAlignment(Qt.AlignCenter)
        tabla.setItem(fila,2,item)
        subTotal=float(precio)*int(lista[1])
        item=QTableWidgetItem(f"{subTotal:.2f}")
        item.setTextAlignment(Qt.AlignCenter)
        tabla.setItem(fila,3,item)
        contenedorIncrementales=QWidget()
        contenedorIncrementales.setStyleSheet("""background-color:transparent;""")
        contenedorIncrementales.setLayout(layoutBotonesCantidad)
        tabla.setCellWidget(fila,4,contenedorIncrementales)
        tabla.setCellWidget(fila,5,botonEliminar)
        conjunto.add(lista[0])
        self.calcularTotal(tabla)
        tabla.scrollToBottom()
        campoCantidad.setText("")

    def aumentar(self,tabla,boton):
        indice=tabla.indexAt(boton.mapTo(tabla.viewport(),QPoint(0,0)))
        fila=indice.row()
        cantidad=int(tabla.item(fila,2).text())
        item=QTableWidgetItem(str(cantidad+1))
        item.setTextAlignment(Qt.AlignCenter)
        tabla.setItem(fila,2,item)
        nuevoPrecio=float(tabla.item(fila,1).text())*int(tabla.item(fila,2).text())
        item=QTableWidgetItem(f"{nuevoPrecio:.2f}")
        item.setTextAlignment(Qt.AlignCenter)
        tabla.setItem(fila,3,QTableWidgetItem(item))
        self.calcularTotal(tabla)
    

    def restar(self,tabla,boton):
        indice=tabla.indexAt(boton.mapTo(tabla.viewport(),QPoint(0,0)))
        fila=indice.row()
        cantidad=int(tabla.item(fila,2).text())
        if cantidad==0:
            return
        item=QTableWidgetItem(str(cantidad-1))
        item.setTextAlignment(Qt.AlignCenter)
        tabla.setItem(fila,2,item)
        nuevoPrecio=float(tabla.item(fila,1).text())*int(tabla.item(fila,2).text())
        item=QTableWidgetItem(f"{nuevoPrecio:.2f}")
        item.setTextAlignment(Qt.AlignCenter)
        tabla.setItem(fila,3,item)
        self.calcularTotal(tabla)
    
    
    def eliminarElemento(self,elemento,tabla,conjunto,boton):
        conjunto.discard(elemento)
        indice=tabla.indexAt(boton.mapTo(tabla.viewport(),QPoint(0,0)))
        fila=indice.row()
        tabla.removeRow(fila)
        self.calcularTotal(tabla)

if __name__=="__main__":
    app = QApplication(sys.argv)
    pagina=RegistroPromociones()
    pagina.show()
    sys.exit(app.exec_())