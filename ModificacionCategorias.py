import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from functools import partial
from Rutas import get_db_path, get_images_dir

DB_PATH = get_db_path()

DIRECCION_LUPA = get_images_dir()

class ModificacionCategorias(QWidget):
    def __init__(self):
        super().__init__()
        self.layoutDatos = QHBoxLayout()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #aed6f1;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 10px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px;
                font-size: 16px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
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
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20,20,20,20)
        self.set_up()
        

    def set_up(self):
        self.crearFiltro()
        self.campoModificar()
        self.showMaximized()
        

    def crearFiltro(self):
        layoutFiltro = QHBoxLayout()
        self.campoBusqueda = QLineEdit()
        self.campoBusqueda.setFixedWidth(300)
        textoBusqueda = QLabel("Nombre: ")
        botonBusqueda = QPushButton()
        
        self.campoBusqueda.setStyleSheet("""
                            QLineEdit {
                                padding: 8px 12px;
                                font-size: 16px;
                                border: 2px solid #4a7dbc;
                                border-radius: 6px;
                                background-color: white;
                            }
                            QLineEdit:focus {
                                border-color: #6a9cec;
                            }
                        """)
        textoBusqueda.setStyleSheet("""
                            font-size: 18px;
                            font-weight: bold;
                            color: #4a7dbc;
                            background-color:transparent;
                        """)   
        botonBusqueda.setStyleSheet("""
                            QPushButton {
                                min-width: 0px;
                                background-color: #4a7dbc;
                                border: none;
                                border-radius: 6px;
                                padding: 8px;
                            }
                            QPushButton:hover {
                                background-color: #6a9cec;
                            }
                        """)
        botonBusqueda.setIcon(QIcon(f"{DIRECCION_LUPA}\\lupa.png"))
        botonBusqueda.clicked.connect(lambda: self.filtrarDatos(self.campoBusqueda.text().strip()))
        self.campoBusqueda.returnPressed.connect(lambda: self.filtrarDatos(self.campoBusqueda.text().strip()))
        layoutFiltro.addStretch(3)
        layoutFiltro.addWidget(textoBusqueda, alignment=Qt.AlignLeft, stretch=0)
        layoutFiltro.addWidget(self.campoBusqueda, alignment=Qt.AlignLeft, stretch=60)
        layoutFiltro.addWidget(botonBusqueda, alignment=Qt.AlignLeft, stretch=40)
        layoutFiltro.addStretch(100)
        self.layoutPrincipal.addLayout(layoutFiltro)
        

    def filtrarDatos(self, texto):
        tabla = self.tabla
        tabla.setRowCount(0)
        conn = sqlite3.connect(DB_PATH)
        if texto == "":
            consulta = """SELECT c.idCategoria, c.nomCategoria, 
                         COUNT(s.idSubcategoria) as num_subcategorias
                         FROM Categoria c
                         LEFT JOIN Subcategoria s ON c.idCategoria = s.idCategoria AND s.activa = 1
                         WHERE c.activa = 1
                         GROUP BY c.idCategoria, c.nomCategoria
                         ORDER BY c.nomCategoria ASC"""
            c = conn.cursor()
            resultado = c.execute(consulta)
        else:
            consulta = """SELECT c.idCategoria, c.nomCategoria, 
                         COUNT(s.idSubcategoria) as num_subcategorias
                         FROM Categoria c
                         LEFT JOIN Subcategoria s ON c.idCategoria = s.idCategoria AND s.activa = 1
                         WHERE c.activa = 1 AND c.nomCategoria LIKE ?
                         GROUP BY c.idCategoria, c.nomCategoria
                         ORDER BY c.nomCategoria ASC"""
            c = conn.cursor()
            resultado = c.execute(consulta, (f"{texto}%",))
        registros = resultado.fetchall()
        for f, registro in enumerate(registros):
            tabla.insertRow(f)
            item_id = QTableWidgetItem(str(registro[0]))
            item_id.setTextAlignment(Qt.AlignCenter)
            tabla.setItem(f, 0, item_id)
            item_nombre = QTableWidgetItem(registro[1])
            item_nombre.setTextAlignment(Qt.AlignCenter)
            tabla.setItem(f, 1, item_nombre)
            num_subs = str(registro[2])
            item_subs = QTableWidgetItem(num_subs)
            item_subs.setTextAlignment(Qt.AlignCenter)
            tabla.setItem(f, 2, item_subs)
            widget_botones = QWidget()
            layout_botones = QHBoxLayout(widget_botones)
            layout_botones.setContentsMargins(5, 5, 5, 5)
            layout_botones.setSpacing(10)
            boton_mod = QPushButton()
            boton_mod.setStyleSheet("""background-color: #f8f9fa;""")
            boton_mod.setCursor(Qt.PointingHandCursor)
            boton_mod.setIcon(QIcon(f"{DIRECCION_LUPA}\\modificarEmpleado.jpg"))
            boton_mod.setIconSize(QSize(50, 50))
            boton_mod.clicked.connect(partial(self.pantallaModificarCategoria, f))
            boton_subs = QPushButton()
            boton_subs.setStyleSheet("""background-color: #f8f9fa;""")
            boton_subs.setCursor(Qt.PointingHandCursor)
            boton_subs.setIcon(QIcon(f"{DIRECCION_LUPA}\\modificarSubcategorias.jpg"))
            boton_subs.setIconSize(QSize(50, 50))
            boton_subs.clicked.connect(partial(self.gestionarSubcategorias, f))
            layout_botones.addWidget(boton_mod)
            layout_botones.addWidget(boton_subs)
            tabla.setCellWidget(f, 3, widget_botones)
        conn.close()
        

    def campoModificar(self):
        layoutCampoModificar = QHBoxLayout()
        layoutCampoModificar.setSpacing(0)
        campoTabla = QWidget()
        campoEstilo = """background-color:white;
                       margin-bottom:20px;
                       border-radius:10px;"""
        campoTabla.setStyleSheet(campoEstilo)
        layoutTabla = QVBoxLayout()
        campoTabla.setLayout(layoutTabla)
        self.tabla = QTableWidget()
        self.tabla.setFocusPolicy(False)
        self.tabla.setStyleSheet("""
                             QTableWidget {
                                    background-color: #f8f9fa;  
                                    gridline-color: #dee2e6;    
                                    border: 1px solid #ced4da;  
                                    font-family: 'Segoe UI';    
                            }
                            QHeaderView::section{
                                background-color: #495057;  
                                color: #ffffff;             
                                font-weight: bold;          
                                border: none;    
                            }
                            QTableWidget::item {
                                color: #343a40; 
                            }
                            QHeaderView {
                                margin: 0;
                                padding: 0;
                            }
                            QScrollBar::handle:vertical {
                                background: #adb5bd; 
                                border-radius: 5px;
                            }
                            QScrollBar:vertical {
                                width: 10px; 
                                background: #f1f3f5;  
                                border: none;
                            }
                            """)
        self.cargarDatos()
        self.tabla.verticalHeader().setDefaultSectionSize(130)
        self.tabla.setFocusPolicy(Qt.NoFocus)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setSelectionMode(QTableWidget.NoSelection)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layoutTabla.addWidget(self.tabla)
        layoutCampoModificar.addWidget(campoTabla)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().setDefaultSectionSize(150)
        self.layoutPrincipal.addLayout(layoutCampoModificar)
        
    def cargarDatos(self):
        conn = sqlite3.connect(DB_PATH)
        consulta = """SELECT c.idCategoria, c.nomCategoria, 
                     COUNT(s.idSubcategoria) as num_subcategorias
                     FROM Categoria c
                     LEFT JOIN Subcategoria s ON c.idCategoria = s.idCategoria AND s.activa = 1
                     WHERE c.activa = 1
                     GROUP BY c.idCategoria, c.nomCategoria
                     ORDER BY c.nomCategoria ASC"""
        
        c = conn.cursor()
        resultado = c.execute(consulta)
        columnas = ["ID", "Nombre Categoría", "Nº Subcategorías", "Acciones"]
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)
        self.tabla.setRowCount(0)
        anchos_columnas = {
            'ID': 100,
            'Nombre Categoría': 350,
            'Nº Subcategorías': 150
        }
        for i, col_name in enumerate(columnas[:-1]):
            if col_name in anchos_columnas:
                self.tabla.setColumnWidth(i, anchos_columnas[col_name])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        registros = resultado.fetchall()
        for f, registro in enumerate(registros):
            self.tabla.insertRow(f)
            item_id = QTableWidgetItem(str(registro[0]))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(f, 0, item_id)
            item_nombre = QTableWidgetItem(registro[1])
            item_nombre.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(f, 1, item_nombre)
            num_subs = str(registro[2])
            item_subs = QTableWidgetItem(num_subs)
            item_subs.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(f, 2, item_subs)
            widget_botones = QWidget()
            layout_botones = QHBoxLayout(widget_botones)
            layout_botones.setContentsMargins(5, 5, 5, 5)
            layout_botones.setSpacing(10)
            boton_mod = QPushButton()
            boton_mod.setStyleSheet("""background-color: #f8f9fa;""")
            boton_mod.setCursor(Qt.PointingHandCursor)
            boton_mod.setIcon(QIcon(f"{DIRECCION_LUPA}\\modificarEmpleado.jpg"))
            boton_mod.setIconSize(QSize(50, 50))
            boton_mod.clicked.connect(partial(self.pantallaModificarCategoria, f))
            boton_subs = QPushButton()
            boton_subs.setStyleSheet("""background-color: #f8f9fa;""")
            boton_subs.setCursor(Qt.PointingHandCursor)
            boton_subs.setIcon(QIcon(f"{DIRECCION_LUPA}\\modificarSubcategorias.jpg"))
            boton_subs.setIconSize(QSize(50, 50))
            boton_subs.clicked.connect(partial(self.gestionarSubcategorias, f))
            layout_botones.addWidget(boton_mod)
            layout_botones.addWidget(boton_subs)
            self.tabla.setCellWidget(f, 3, widget_botones)
        conn.close()
        
    def pantallaModificarCategoria(self, fila):
        scroll_position = self.tabla.verticalScrollBar().value() if hasattr(self, 'tabla') else 0
        if not (0 <= fila < self.tabla.rowCount()):
            QMessageBox.warning(self, "Error", "Fila seleccionada no válida")
            return
        try:
            id_categoria = self.tabla.item(fila, 0).text()
            nombre_actual = self.tabla.item(fila, 1).text()
            dialogo = ModificarCategoriaDialog(id_categoria, nombre_actual, self)
            if dialogo.exec_() == QDialog.Accepted:
                if hasattr(self, 'tabla'):
                    self.tabla.verticalScrollBar().setValue(scroll_position)
                self.filtrarDatos(self.campoBusqueda.text().strip())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al modificar: {str(e)}")
            if hasattr(self, 'tabla'):
                self.tabla.verticalScrollBar().setValue(scroll_position)
    

    def gestionarSubcategorias(self, fila):
        scroll_position = self.tabla.verticalScrollBar().value() if hasattr(self, 'tabla') else 0
        if not (0 <= fila < self.tabla.rowCount()):
            QMessageBox.warning(self, "Error", "Fila seleccionada no válida")
            return
        try:
            id_categoria = self.tabla.item(fila, 0).text()
            nombre_categoria = self.tabla.item(fila, 1).text()
            dialogo = GestionarSubcategoriasDialog(id_categoria, nombre_categoria, self)
            dialogo.exec_()
            if hasattr(self, 'tabla'):
                self.tabla.verticalScrollBar().setValue(scroll_position)
            self.filtrarDatos(self.campoBusqueda.text().strip())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al gestionar subcategorías: {str(e)}")
            if hasattr(self, 'tabla'):
                self.tabla.verticalScrollBar().setValue(scroll_position)

class ModificarCategoriaDialog(QDialog):
    def __init__(self, id_categoria, nombre_actual, parent=None):
        super().__init__(parent)
        self.id_categoria = id_categoria
        self.nombre_actual = nombre_actual
        self.imagen_modificada = False
        self.setWindowTitle("Modificar Categoría")
        self.setModal(True)
        self.setFixedSize(560, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 10px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QCompleter {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        titulo = QLabel("MODIFICAR CATEGORÍA")
        titulo.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #4a7dbc;
            padding-bottom: 10px;
            border-bottom: 2px solid #4a7dbc;
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layout_nombre = QHBoxLayout()
        label_nombre = QLabel("Nombre:")
        label_nombre.setStyleSheet("font-size: 16px; font-weight: bold;")
        label_nombre.setFixedWidth(120)
        self.input_nombre = QLineEdit()
        self.input_nombre.setText(nombre_actual)
        
        categorias = self.obtenerCategoriasExistentes()
        completer = QCompleter(categorias)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.input_nombre.setCompleter(completer)
        
        layout_nombre.addWidget(label_nombre)
        layout_nombre.addWidget(self.input_nombre)
        layout_imagen = QHBoxLayout()
        label_imagen = QLabel("Imagen:")
        label_imagen.setStyleSheet("font-size: 16px; font-weight: bold;")
        label_imagen.setFixedWidth(120)
        self.boton_seleccionar_img = QPushButton("Seleccionar Imagen")
        self.boton_seleccionar_img.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.boton_seleccionar_img.clicked.connect(self.seleccionarImagen)
        layout_imagen.addWidget(self.boton_seleccionar_img)
        preview_layout = QVBoxLayout()
        preview_label = QLabel("Vista previa:")
        preview_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.label_img_preview = QLabel("No hay imagen seleccionada")
        self.label_img_preview.setAlignment(Qt.AlignCenter)
        self.label_img_preview.setMinimumHeight(200)
        self.label_img_preview.setStyleSheet("""
            border: 2px dashed #bdc3c7;
            border-radius: 8px;
            padding: 20px;
            color: #7f8c8d;
        """)
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.label_img_preview)
        self.imagen_bytes = b''
        self.cargarImagenActual()
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(20)
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.guardarCambios)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        layout_botones.addStretch()
        layout_botones.addWidget(btn_guardar)
        layout_botones.addWidget(btn_cancelar)
        layout.addWidget(titulo)
        layout.addLayout(layout_nombre)
        layout.addLayout(layout_imagen)
        layout.addLayout(preview_layout, 1)
        layout.addLayout(layout_botones)
        self.setLayout(layout)
    
    def obtenerCategoriasExistentes(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT nomCategoria FROM Categoria WHERE activa = 1 ORDER BY nomCategoria")
            categorias = [row[0] for row in c.fetchall()]
            conn.close()
            return categorias
        except Exception as e:
            print(f"Error al obtener categorías: {e}")
            return []
    
    def cargarImagenActual(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT imagenCategoria FROM Categoria WHERE idCategoria = ?", (self.id_categoria,))
            resultado = c.fetchone()
            
            if resultado and resultado[0]:
                self.imagen_bytes = resultado[0]
                self.mostrarImagen(self.imagen_bytes)
            else:
                default_image_path = os.path.join(DIRECCION_LUPA, "camara.png")
                if os.path.exists(default_image_path):
                    with open(default_image_path, 'rb') as file:
                        self.imagen_bytes = file.read()
                    self.mostrarImagen(self.imagen_bytes)
            
            conn.close()
        except Exception as e:
            print(f"Error al cargar imagen actual: {e}")
    
    def mostrarImagen(self, imagen_bytes):
        try:
            pixmap = QPixmap()
            if pixmap.loadFromData(imagen_bytes):
                max_width = self.label_img_preview.width() - 40
                max_height = self.label_img_preview.height() - 40
                
                img_width = pixmap.width()
                img_height = pixmap.height()
                
                width_ratio = max_width / img_width if img_width > 0 else 1
                height_ratio = max_height / img_height if img_height > 0 else 1
                
                scale_factor = min(width_ratio, height_ratio)
                
                if scale_factor < 1:
                    new_width = int(img_width * scale_factor)
                    new_height = int(img_height * scale_factor)
                    scaled_pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                else:
                    scaled_pixmap = pixmap
                
                self.label_img_preview.setPixmap(scaled_pixmap)
                self.label_img_preview.setStyleSheet("border: 2px solid #27ae60; border-radius: 8px;")
            else:
                self.label_img_preview.setText("Error al cargar imagen")
        except Exception:
            self.label_img_preview.setText("Error al cargar imagen")
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.imagen_bytes:
            self.mostrarImagen(self.imagen_bytes)
    
    def seleccionarImagen(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", 
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_name:
            try:
                with open(file_name, 'rb') as file:
                    self.imagen_bytes = file.read()
                
                self.imagen_modificada = True
                self.mostrarImagen(self.imagen_bytes)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def guardarCambios(self):
        nuevo_nombre = self.input_nombre.text().strip()
        
        if not nuevo_nombre:
            QMessageBox.warning(self, "Advertencia", "El nombre de la categoría no puede estar vacío")
            return
        
        nuevo_nombre_upper = nuevo_nombre.upper()
        nombre_actual_upper = self.nombre_actual.upper()
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        if nuevo_nombre_upper != nombre_actual_upper:
            c.execute("SELECT COUNT(*) FROM Categoria WHERE UPPER(nomCategoria) = ? AND idCategoria != ?", 
                     (nuevo_nombre_upper, self.id_categoria))
            
            if c.fetchone()[0] > 0:
                QMessageBox.warning(self, "Advertencia", "Ya existe una categoría con ese nombre (ignorando mayúsculas/minúsculas)")
                conn.close()
                return
        
        try:
            c.execute("UPDATE Categoria SET nomCategoria = ?, imagenCategoria = ? WHERE idCategoria = ?",
                     (nuevo_nombre, self.imagen_bytes, self.id_categoria))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Categoría actualizada correctamente")
            self.accept()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar la categoría: {str(e)}")
            conn.close()

class GestionarSubcategoriasDialog(QDialog):
    def __init__(self, id_categoria, nombre_categoria, parent=None):
        super().__init__(parent)
        self.id_categoria = id_categoria
        self.nombre_categoria = nombre_categoria
        
        self.setWindowTitle(f"Subcategorías - {nombre_categoria}")
        self.setModal(True)
        self.setFixedSize(800, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTableWidget {
                background-color: #f8f9fa;  
                border: 1px solid #ced4da;  
                font-family: 'Segoe UI';    
            }
            QHeaderView::section{
                background-color: #495057;  
                color: #ffffff;             
                font-weight: bold;          
                border: none;    
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        titulo = QLabel(f"SUBCATEGORÍAS DE: {nombre_categoria.upper()}")
        titulo.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #4a7dbc;
            padding: 10px;
            background-color: white;
            border-radius: 8px;
            border: 2px solid #4a7dbc;
        """)
        titulo.setAlignment(Qt.AlignCenter)
        
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Nombre", "Estado", "Acciones"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setSelectionMode(QTableWidget.NoSelection)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.cargarSubcategorias()
        
        layout_botones = QHBoxLayout()
        
        btn_agregar = QPushButton("Agregar Subcategoría")
        btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_agregar.clicked.connect(self.agregarSubcategoria)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_cerrar.clicked.connect(self.accept)
        
        layout_botones.addWidget(btn_agregar)
        layout_botones.addStretch()
        layout_botones.addWidget(btn_cerrar)
        
        layout.addWidget(titulo)
        layout.addWidget(self.tabla, 1)
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def cargarSubcategorias(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT idSubcategoria, nombre, activa 
            FROM Subcategoria 
            WHERE idCategoria = ? 
            ORDER BY nombre ASC
        """, (self.id_categoria,))
        
        subcategorias = c.fetchall()
        conn.close()
        
        self.tabla.setRowCount(0)
        
        for f, (id_sub, nombre, activa) in enumerate(subcategorias):
            self.tabla.insertRow(f)
            
            item_nombre = QTableWidgetItem(nombre)
            item_nombre.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(f, 0, item_nombre)
            
            estado = "Activa" if activa else "Inactiva"
            color = "#27ae60" if activa else "#e74c3c"
            item_estado = QTableWidgetItem(estado)
            item_estado.setTextAlignment(Qt.AlignCenter)
            item_estado.setForeground(QBrush(QColor(color)))
            self.tabla.setItem(f, 1, item_estado)
            
            widget_botones = QWidget()
            layout_botones = QHBoxLayout(widget_botones)
            layout_botones.setContentsMargins(5, 5, 5, 5)
            layout_botones.setSpacing(5)
            
            btn_editar = QPushButton()
            btn_editar.setStyleSheet("""background-color: #f8f9fa;""")
            btn_editar.setCursor(Qt.PointingHandCursor)
            btn_editar.setIcon(QIcon(f"{DIRECCION_LUPA}\\modificarEmpleado.jpg"))
            btn_editar.setIconSize(QSize(30, 30))
            btn_editar.clicked.connect(partial(self.editarSubcategoria, f, id_sub))
            
            if activa:
                btn_desactivar = QPushButton("Desactivar")
                btn_desactivar.setStyleSheet("""
                    QPushButton {
                        background-color: #f39c12;
                        color: white;
                        border-radius: 6px;
                        padding: 5px 10px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #e67e22;
                    }
                """)
                btn_desactivar.clicked.connect(partial(self.cambiarEstadoSubcategoria, f, id_sub, nombre, 0))
            else:
                btn_activar = QPushButton("Activar")
                btn_activar.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border-radius: 6px;
                        padding: 5px 10px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #229954;
                    }
                """)
                btn_activar.clicked.connect(partial(self.cambiarEstadoSubcategoria, f, id_sub, nombre, 1))
            
            layout_botones.addWidget(btn_editar)
            if activa:
                layout_botones.addWidget(btn_desactivar)
            else:
                layout_botones.addWidget(btn_activar)
            layout_botones.addStretch()
            
            self.tabla.setCellWidget(f, 2, widget_botones)
        
        self.tabla.setColumnWidth(0, 350)
        self.tabla.setColumnWidth(1, 100)
    
    def agregarSubcategoria(self):
        dialogo = AgregarSubcategoriaDialog(self.id_categoria, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargarSubcategorias()
    
    def editarSubcategoria(self, fila, id_subcategoria):
        if fila >= self.tabla.rowCount():
            return
        
        nombre_actual = self.tabla.item(fila, 0).text()
        
        dialogo = EditarSubcategoriaDialog(id_subcategoria, nombre_actual, self)
        if dialogo.exec_() == QDialog.Accepted:
            self.cargarSubcategorias()
    
    def cambiarEstadoSubcategoria(self, fila, id_subcategoria, nombre_subcategoria, nuevo_estado):
        if fila >= self.tabla.rowCount():
            return
        
        accion = "activar" if nuevo_estado == 1 else "desactivar"
        
        reply = QMessageBox.question(
            self, 'Confirmar',
            f'¿Estás seguro de {accion} la subcategoría "{nombre_subcategoria}"?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            try:
                c.execute("UPDATE Subcategoria SET activa = ? WHERE idSubcategoria = ?",
                         (nuevo_estado, id_subcategoria))
                
                if nuevo_estado == 0:
                    c.execute("UPDATE Producto SET activo = 0 WHERE idSubcategoria = ?",
                             (id_subcategoria,))
                else:
                    c.execute("UPDATE Producto SET activo = 1 WHERE idSubcategoria = ?",
                             (id_subcategoria,))
                
                conn.commit()
                conn.close()
                
                mensaje = "activada" if nuevo_estado == 1 else "desactivada"
                QMessageBox.information(self, "Éxito", f"Subcategoría {mensaje} correctamente")
                self.cargarSubcategorias()
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"Error al cambiar estado: {str(e)}")
                conn.close()

class AgregarSubcategoriaDialog(QDialog):
    def __init__(self, id_categoria, parent=None):
        super().__init__(parent)
        self.id_categoria = id_categoria
        
        self.setWindowTitle("Agregar Subcategoría")
        self.setModal(True)
        self.setFixedSize(500, 600)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 10px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        titulo = QLabel("NUEVA SUBCATEGORÍA")
        titulo.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #27ae60;
            padding-bottom: 10px;
            border-bottom: 2px solid #27ae60;
        """)
        titulo.setAlignment(Qt.AlignCenter)
        
        layout_nombre = QVBoxLayout()
        label_nombre = QLabel("Nombre de la subcategoría:")
        label_nombre.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Ej: Refrescos, Cervezas, Postres...")
        
        layout_nombre.addWidget(label_nombre)
        layout_nombre.addWidget(self.input_nombre)
        
        layout_imagen = QVBoxLayout()
        label_imagen = QLabel("Imagen (opcional):")
        label_imagen.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.boton_seleccionar_img = QPushButton("Seleccionar Imagen")
        self.boton_seleccionar_img.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.boton_seleccionar_img.clicked.connect(self.seleccionarImagen)
        
        preview_layout = QVBoxLayout()
        preview_label = QLabel("Vista previa:")
        preview_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.label_img_preview = QLabel("No hay imagen seleccionada")
        self.label_img_preview.setAlignment(Qt.AlignCenter)
        self.label_img_preview.setMinimumHeight(200)
        self.label_img_preview.setStyleSheet("""
            border: 2px dashed #bdc3c7;
            border-radius: 8px;
            padding: 20px;
            color: #7f8c8d;
        """)
        
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.label_img_preview)
        
        layout_imagen.addWidget(label_imagen)
        layout_imagen.addWidget(self.boton_seleccionar_img)
        layout_imagen.addLayout(preview_layout)
        
        self.imagen_bytes = b''
        
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(20)
        
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.guardarSubcategoria)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        
        layout_botones.addStretch()
        layout_botones.addWidget(btn_guardar)
        layout_botones.addWidget(btn_cancelar)
        
        layout.addWidget(titulo)
        layout.addLayout(layout_nombre)
        layout.addLayout(layout_imagen, 1)
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def mostrarImagen(self, imagen_bytes):
        try:
            pixmap = QPixmap()
            if pixmap.loadFromData(imagen_bytes):
                max_width = self.label_img_preview.width() - 40
                max_height = self.label_img_preview.height() - 40
                
                img_width = pixmap.width()
                img_height = pixmap.height()
                
                width_ratio = max_width / img_width if img_width > 0 else 1
                height_ratio = max_height / img_height if img_height > 0 else 1
                
                scale_factor = min(width_ratio, height_ratio)
                
                if scale_factor < 1:
                    new_width = int(img_width * scale_factor)
                    new_height = int(img_height * scale_factor)
                    scaled_pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                else:
                    scaled_pixmap = pixmap
                
                self.label_img_preview.setPixmap(scaled_pixmap)
                self.label_img_preview.setStyleSheet("border: 2px solid #27ae60; border-radius: 8px;")
            else:
                self.label_img_preview.setText("Error al cargar imagen")
        except Exception:
            self.label_img_preview.setText("Error al cargar imagen")
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.imagen_bytes:
            self.mostrarImagen(self.imagen_bytes)
    
    def seleccionarImagen(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", 
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_name:
            try:
                with open(file_name, 'rb') as file:
                    self.imagen_bytes = file.read()
                
                self.mostrarImagen(self.imagen_bytes)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def guardarSubcategoria(self):
        nombre = self.input_nombre.text().strip()
        
        if not nombre:
            QMessageBox.warning(self, "Advertencia", "El nombre de la subcategoría no puede estar vacío")
            return
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        nombre_upper = nombre.upper()
        c.execute("SELECT COUNT(*) FROM Subcategoria WHERE UPPER(nombre) = ? AND idCategoria = ?", 
                 (nombre_upper, self.id_categoria))
        
        if c.fetchone()[0] > 0:
            QMessageBox.warning(self, "Advertencia", "Ya existe una subcategoría con ese nombre en esta categoría (ignorando mayúsculas/minúsculas)")
            conn.close()
            return
        
        try:
            if not self.imagen_bytes:
                default_image_path = os.path.join(DIRECCION_LUPA, "camara.png")
                if os.path.exists(default_image_path):
                    with open(default_image_path, 'rb') as file:
                        self.imagen_bytes = file.read()
            
            c.execute("""
                INSERT INTO Subcategoria (idCategoria, nombre, imagenSubcategoria, activa) 
                VALUES (?, ?, ?, 1)
            """, (self.id_categoria, nombre, self.imagen_bytes))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Subcategoría agregada correctamente")
            self.accept()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al agregar subcategoría: {str(e)}")
            conn.close()

class EditarSubcategoriaDialog(QDialog):
    def __init__(self, id_subcategoria, nombre_actual, parent=None):
        super().__init__(parent)
        self.id_subcategoria = id_subcategoria
        self.nombre_actual = nombre_actual
        
        self.setWindowTitle("Editar Subcategoría")
        self.setModal(True)
        self.setFixedSize(500, 600)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 10px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QCompleter {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        titulo = QLabel("EDITAR SUBCATEGORÍA")
        titulo.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #f39c12;
            padding-bottom: 10px;
            border-bottom: 2px solid #f39c12;
        """)
        titulo.setAlignment(Qt.AlignCenter)
        
        layout_nombre = QVBoxLayout()
        label_nombre = QLabel("Nombre:")
        label_nombre.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.input_nombre = QLineEdit()
        self.input_nombre.setText(nombre_actual)
        
        subcategorias = self.obtenerSubcategoriasExistentes()
        completer = QCompleter(subcategorias)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.input_nombre.setCompleter(completer)
        
        layout_nombre.addWidget(label_nombre)
        layout_nombre.addWidget(self.input_nombre)
        
        layout_imagen = QVBoxLayout()
        label_imagen = QLabel("Imagen:")
        label_imagen.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.boton_seleccionar_img = QPushButton("Seleccionar Imagen")
        self.boton_seleccionar_img.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.boton_seleccionar_img.clicked.connect(self.seleccionarImagen)
        
        preview_layout = QVBoxLayout()
        preview_label = QLabel("Vista previa:")
        preview_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.label_img_preview = QLabel("No hay imagen seleccionada")
        self.label_img_preview.setAlignment(Qt.AlignCenter)
        self.label_img_preview.setMinimumHeight(200)
        self.label_img_preview.setStyleSheet("""
            border: 2px dashed #bdc3c7;
            border-radius: 8px;
            padding: 20px;
            color: #7f8c8d;
        """)
        
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.label_img_preview)
        
        layout_imagen.addWidget(label_imagen)
        layout_imagen.addWidget(self.boton_seleccionar_img)
        layout_imagen.addLayout(preview_layout)
        
        self.imagen_bytes = b''
        self.cargarImagenActual()
        
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(20)
        
        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.guardarCambios)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        
        layout_botones.addStretch()
        layout_botones.addWidget(btn_guardar)
        layout_botones.addWidget(btn_cancelar)
        
        layout.addWidget(titulo)
        layout.addLayout(layout_nombre)
        layout.addLayout(layout_imagen, 1)
        layout.addLayout(layout_botones)
        
        self.setLayout(layout)
    
    def obtenerSubcategoriasExistentes(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT nombre FROM Subcategoria WHERE activa = 1 ORDER BY nombre")
            subcategorias = [row[0] for row in c.fetchall()]
            conn.close()
            return subcategorias
        except Exception as e:
            print(f"Error al obtener subcategorías: {e}")
            return []
    
    def cargarImagenActual(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT imagenSubcategoria FROM Subcategoria WHERE idSubcategoria = ?", (self.id_subcategoria,))
            resultado = c.fetchone()
            
            if resultado and resultado[0]:
                self.imagen_bytes = resultado[0]
                self.mostrarImagen(self.imagen_bytes)
            else:
                default_image_path = os.path.join(DIRECCION_LUPA, "camara.png")
                if os.path.exists(default_image_path):
                    with open(default_image_path, 'rb') as file:
                        self.imagen_bytes = file.read()
                    self.mostrarImagen(self.imagen_bytes)
            
            conn.close()
        except Exception as e:
            print(f"Error al cargar imagen actual: {e}")
    
    def mostrarImagen(self, imagen_bytes):
        try:
            pixmap = QPixmap()
            if pixmap.loadFromData(imagen_bytes):
                max_width = self.label_img_preview.width() - 40
                max_height = self.label_img_preview.height() - 40
                
                img_width = pixmap.width()
                img_height = pixmap.height()
                
                width_ratio = max_width / img_width if img_width > 0 else 1
                height_ratio = max_height / img_height if img_height > 0 else 1
                
                scale_factor = min(width_ratio, height_ratio)
                
                if scale_factor < 1:
                    new_width = int(img_width * scale_factor)
                    new_height = int(img_height * scale_factor)
                    scaled_pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                else:
                    scaled_pixmap = pixmap
                
                self.label_img_preview.setPixmap(scaled_pixmap)
                self.label_img_preview.setStyleSheet("border: 2px solid #27ae60; border-radius: 8px;")
            else:
                self.label_img_preview.setText("Error al cargar imagen")
        except Exception:
            self.label_img_preview.setText("Error al cargar imagen")
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.imagen_bytes:
            self.mostrarImagen(self.imagen_bytes)
    
    def seleccionarImagen(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", 
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_name:
            try:
                with open(file_name, 'rb') as file:
                    self.imagen_bytes = file.read()
                
                self.mostrarImagen(self.imagen_bytes)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def guardarCambios(self):
        nuevo_nombre = self.input_nombre.text().strip()
        
        if not nuevo_nombre:
            QMessageBox.warning(self, "Advertencia", "El nombre de la subcategoría no puede estar vacío")
            return
        
        nuevo_nombre_upper = nuevo_nombre.upper()
        nombre_actual_upper = self.nombre_actual.upper()
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        if nuevo_nombre_upper != nombre_actual_upper:
            c.execute("SELECT COUNT(*) FROM Subcategoria WHERE UPPER(nombre) = ? AND idSubcategoria != ?", 
                     (nuevo_nombre_upper, self.id_subcategoria))
            
            if c.fetchone()[0] > 0:
                QMessageBox.warning(self, "Advertencia", "Ya existe una subcategoría con ese nombre (ignorando mayúsculas/minúsculas)")
                conn.close()
                return
        
        try:
            c.execute("UPDATE Subcategoria SET nombre = ?, imagenSubcategoria = ? WHERE idSubcategoria = ?",
                     (nuevo_nombre, self.imagen_bytes, self.id_subcategoria))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Subcategoría actualizada correctamente")
            self.accept()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar: {str(e)}")
            conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = ModificacionCategorias()
    pagina.show()
    sys.exit(app.exec_())