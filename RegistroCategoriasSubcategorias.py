import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from Pop_up_ModificacionSubcategoria import Pop_up_ModificacionSubcategoria
from nucleo.Rutas import get_db_path, get_resource_path

DB_PATH = get_db_path()


class RegistroCategoriasSubcategorias(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            self{background-color: #f8fafc;
            font-family: 'Segoe UI', Arial, sans-serif;}
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
        self.conjunto = set()
        self.set_up()

    def set_up(self):
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.iniciarPagina()
        self.showMaximized()

    def iniciarPagina(self):
        layout1 = QHBoxLayout()
        self.layoutPrincipal.addLayout(layout1, stretch=20)
        layout2 = QVBoxLayout()
        layout2.setSpacing(30)
        layout1.addLayout(layout2)
        self.tablaRegistrados = QTableWidget()
        self.tablaRegistrados.setColumnCount(4)
        self.tablaRegistrados.setHorizontalHeaderLabels(["Subcategorías", "Imagen", "Modificar", "Eliminar"])
        self.tablaRegistrados.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tablaRegistrados.setSelectionMode(QTableWidget.NoSelection)
        self.tablaRegistrados.setFocusPolicy(Qt.NoFocus)
        self.tablaRegistrados.verticalHeader().setDefaultSectionSize(90)
        self.tablaRegistrados.verticalHeader().setVisible(False)
        header = self.tablaRegistrados.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.tablaRegistrados.setColumnWidth(1, 100)
        self.tablaRegistrados.setColumnWidth(2, 110)
        self.tablaRegistrados.setColumnWidth(3, 110)
        self.tablaRegistrados.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                gridline-color: #e0e0e0;
                font-size: 14px;
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #e8e8e8;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 14px 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
                border-right: 1px solid #2980b9;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QTableCornerButton::section {
                background-color: #3498db;
                border-top-left-radius: 7px;
            }
        """)
        layout1.addWidget(self.tablaRegistrados)
        categoria_container = QFrame()
        categoria_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 15px;
                border: 1px solid #d0e0f0;
                padding: 15px;
                margin-bottom: 5px;
            }
        """)
        categoria_layout = QVBoxLayout(categoria_container)
        categoria_layout.setSpacing(10)
        categoria_titulo = QLabel("🏷️ CATEGORÍA")
        categoria_titulo.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #3498db;
                background: transparent;
                padding: 5px;
                border-bottom: 2px solid #3498db;
            }
        """)
        categoria_layout.addWidget(categoria_titulo)
        layoutCategoria = QHBoxLayout()
        camp1 = QLabel("Nombre: ")
        self.camp2 = QLineEdit()
        self.camp2.setPlaceholderText("Nombre de la Categoría")
        self.camp2.setFixedHeight(40)
        self.completer_categoria = QCompleter()
        self.completer_categoria.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer_categoria.setFilterMode(Qt.MatchContains)
        self.completer_categoria.setCompletionMode(QCompleter.PopupCompletion)
        self.camp2.setCompleter(self.completer_categoria)
        self.cargarCategoriasCompleter()
        self.camp2.textChanged.connect(self.filtrarCategorias)
        self.btnImagenCategoria = QPushButton("Subir Imagen Categoría")
        self.btnImagenCategoria.setFixedHeight(40)
        self.btnImagenCategoria.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.btnImagenCategoria.clicked.connect(self.subirImagenCategoria)
        self.imagenCategoria = None
        camp1.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #2c3e50;
                font-size: 16px;
                min-width: 100px;
                border-radius:10px;
                background-color: transparent;
                qproperty-alignment: AlignCenter;
            }
        """)
        self.camp2.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #2980b9;
                border-width: 2px;
            }
        """)
        layoutCategoria.addWidget(camp1)
        layoutCategoria.addWidget(self.camp2)
        layoutCategoria.addWidget(self.btnImagenCategoria)
        categoria_layout.addLayout(layoutCategoria)
        self.labelImagenCategoria = QLabel()
        self.labelImagenCategoria.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px dashed #3498db;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        self.labelImagenCategoria.setFixedSize(220, 180)
        self.labelImagenCategoria.setAlignment(Qt.AlignCenter)
        default_image_path = get_resource_path(os.path.join('Imagenes', 'camara.png'))
        if os.path.exists(default_image_path):
            pixmap = QPixmap(default_image_path)
            pixmap = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.labelImagenCategoria.setPixmap(pixmap)
            self.imagenCategoria = default_image_path
        else:
            self.labelImagenCategoria.setText("Imagen\npor defecto")
            self.labelImagenCategoria.setStyleSheet("""
                QLabel {
                    background-color: #ecf0f1;
                    border: 2px dashed #95a5a6;
                    border-radius: 10px;
                    color: #7f8c8d;
                    font-weight: bold;
                    padding: 15px;
                    font-size: 14px;
                }
            """)
        categoria_layout.addWidget(self.labelImagenCategoria, alignment=Qt.AlignCenter)
        layout2.addWidget(categoria_container)
        subcategoria_container = QFrame()
        subcategoria_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 15px;
                border: 1px solid #d0e0f0;
                padding: 15px;
                margin-bottom: 5px;
            }
        """)
        subcategoria_layout = QVBoxLayout(subcategoria_container)
        subcategoria_layout.setSpacing(10)
        subcategoria_titulo = QLabel("🔖 SUBCATEGORÍA")
        subcategoria_titulo.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #e67e22;
                background: transparent;
                padding: 5px;
                border-bottom: 2px solid #e67e22;
            }
        """)
        subcategoria_layout.addWidget(subcategoria_titulo)
        layoutSubcategoria = QHBoxLayout()
        camp3 = QLabel("Nombre: ")
        self.camp4 = QLineEdit()
        self.camp4.setPlaceholderText("Nombre de la Subcategoría")
        self.camp4.setFixedHeight(40)

        self.btnImagenSubcategoria = QPushButton("Subir Imagen Subcategoría")
        self.btnImagenSubcategoria.setFixedHeight(40)
        self.btnImagenSubcategoria.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.btnImagenSubcategoria.clicked.connect(self.subirImagenSubcategoria)
        self.imagenSubcategoria = None
        self.labelImagenSubcategoria = QLabel()
        self.labelImagenSubcategoria.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px dashed #e67e22;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        self.labelImagenSubcategoria.setFixedSize(220, 180)
        self.labelImagenSubcategoria.setAlignment(Qt.AlignCenter)
        default_image_path = get_resource_path(os.path.join('Imagenes', 'camara.png'))
        if os.path.exists(default_image_path):
            pixmap = QPixmap(default_image_path)
            pixmap = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.labelImagenSubcategoria.setPixmap(pixmap)
        camp3.setStyleSheet(camp1.styleSheet())
        self.camp4.setStyleSheet(self.camp2.styleSheet())
        botonAnadir = QPushButton("Añadir")
        botonAnadir.setFocusPolicy(Qt.NoFocus)
        botonAnadir.setFixedHeight(40)
        botonAnadir.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 12px 25px;
                font-weight: bold;
                min-width: 120px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        botonAnadir.clicked.connect(lambda: self.anadirElemento(self.camp4.text()))
        layoutSubcategoria.addWidget(camp3)
        layoutSubcategoria.addWidget(self.camp4)
        layoutSubcategoria.addWidget(self.btnImagenSubcategoria)
        layoutSubcategoria.addWidget(botonAnadir)
        subcategoria_layout.addLayout(layoutSubcategoria)
        subcategoria_layout.addWidget(self.labelImagenSubcategoria, alignment=Qt.AlignCenter)
        layout2.addWidget(subcategoria_container)
        layout2.addStretch(1)
        botonRegistrar = QPushButton("Registrar")
        botonRegistrar.setFixedHeight(50)
        botonRegistrar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 14px 30px;
                font-size: 16px;
                font-weight: bold;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        botonRegistrar.clicked.connect(lambda: self.subirInformacion(self.camp2.text()))
        self.layoutPrincipal.addWidget(botonRegistrar, alignment=Qt.AlignCenter)

    def cargarCategoriasCompleter(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            consulta = (
                """SELECT nomCategoria FROM Categoria WHERE activa = 1 ORDER BY nomCategoria COLLATE NOCASE ASC"""
            )
            c.execute(consulta)
            resultados = c.fetchall()
            conn.close()
            if resultados:
                elementos = [str(elem[0]) for elem in resultados]
                modelo = QStringListModel()
                modelo.setStringList(elementos)
                self.completer_categoria.setModel(modelo)
        except Exception as e:
            print(f"Error al cargar categorías: {e}")

    def filtrarCategorias(self, texto):
        if texto:
            self.completer_categoria.setCompletionPrefix(texto)
            self.completer_categoria.complete()

    def subirImagenCategoria(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_name:
            pixmap = QPixmap(file_name)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.labelImagenCategoria.setPixmap(pixmap)
                self.imagenCategoria = file_name
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Error")
                msg.setText("No se pudo cargar la imagen seleccionada.")
                msg.exec_()

    def subirImagenSubcategoria(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen para Subcategoría", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_name:
            pixmap = QPixmap(file_name)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.labelImagenSubcategoria.setPixmap(pixmap)
                self.imagenSubcategoria = file_name
            else:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Error")
                msg.setText("No se pudo cargar la imagen seleccionada.")
                msg.exec_()

    def subirInformacion(self, cat):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if cat == "":
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("El nombre de la categoría no puede estar vacío")
            msg.exec_()
            return
        cat_upper = cat.upper()
        consulta = """SELECT * FROM Categoria WHERE UPPER(nomCategoria)=?"""
        c.execute(consulta, (cat_upper,))
        resultados = c.fetchall()
        if resultados:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("La categoría ya existe")
            msg.exec_()
            return
        if self.tablaRegistrados.rowCount() == 0:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("La categoría debe tener por lo menos una subcategoría")
            msg.exec_()
            return
        imagen_cat_bytes = None
        if self.imagenCategoria and os.path.exists(self.imagenCategoria):
            with open(self.imagenCategoria, 'rb') as f:
                imagen_cat_bytes = f.read()
        else:
            default_image_path = get_resource_path(os.path.join('Imagenes', 'camara.png'))
            if os.path.exists(default_image_path):
                with open(default_image_path, 'rb') as f:
                    imagen_cat_bytes = f.read()
        consulta = """INSERT INTO Categoria(nomCategoria, imagenCategoria) VALUES(?, ?)"""
        c.execute(consulta, (cat, imagen_cat_bytes))
        indiceCat = c.lastrowid
        consulta = """INSERT INTO Subcategoria(idCategoria, nombre, imagenSubcategoria) VALUES(?, ?, ?)"""
        subcategorias_con_imagenes = []
        for fila in range(self.tablaRegistrados.rowCount()):
            nombre_subcat = self.tablaRegistrados.item(fila, 0).text()
            imagen_subcat = None
            widget_imagen = self.tablaRegistrados.cellWidget(fila, 1)
            if widget_imagen and hasattr(widget_imagen, 'imagen_bytes'):
                imagen_subcat = widget_imagen.imagen_bytes
            else:
                default_image_path = get_resource_path(os.path.join('Imagenes', 'camara.png'))
                if os.path.exists(default_image_path):
                    with open(default_image_path, 'rb') as f:
                        imagen_subcat = f.read()
            subcategorias_con_imagenes.append((nombre_subcat, imagen_subcat))
        for nombre_subcat, imagen_subcat in subcategorias_con_imagenes:
            c.execute(consulta, (indiceCat, nombre_subcat, imagen_subcat))
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Confirmación")
        msg.setText("¡Se ha registrado con éxito!")
        msg.exec_()
        conn.commit()
        conn.close()
        self.tablaRegistrados.setRowCount(0)
        self.camp4.setText("")
        self.camp2.setText("")
        self.imagenSubcategoria = None
        self.conjunto.clear()
        default_image_path = get_resource_path(os.path.join('Imagenes', 'camara.png'))
        if os.path.exists(default_image_path):
            pixmap = QPixmap(default_image_path)
            pixmap = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.labelImagenCategoria.setPixmap(pixmap)
            self.imagenCategoria = default_image_path
            pixmap_sub = QPixmap(default_image_path)
            pixmap_sub = pixmap_sub.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.labelImagenSubcategoria.setPixmap(pixmap_sub)
        else:
            self.labelImagenCategoria.setText("Imagen\npor defecto")
            self.labelImagenSubcategoria.setText("Imagen\npor defecto")
        self.cargarCategoriasCompleter()

    def anadirElemento(self, elemento, bandera=True):
        if elemento == "":
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("El campo de subcategoría no puede estar vacío")
            msg.exec_()
            return
        elemento_upper = elemento.upper()
        conjunto_upper = {item.upper() for item in self.conjunto}
        if elemento_upper in conjunto_upper and bandera == True:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("La subcategoría ya está registrada")
            msg.exec_()
            return
        fila = self.tablaRegistrados.rowCount()
        self.tablaRegistrados.insertRow(fila)
        self.tablaRegistrados.setRowHeight(fila, 90)
        item = QTableWidgetItem(elemento)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFont(QFont("Segoe UI", 12, QFont.Bold))
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.tablaRegistrados.setItem(fila, 0, item)
        imagen_label = QLabel()
        imagen_label.setAlignment(Qt.AlignCenter)
        imagen_label.setFixedSize(80, 70)
        imagen_label.setContentsMargins(2, 2, 2, 2)
        imagen_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #dee2e6;
                padding: 5px;
                margin-top: 5px;
                margin-bottom: 10px;
            }
        """)
        if self.imagenSubcategoria and os.path.exists(self.imagenSubcategoria):
            pixmap = QPixmap(self.imagenSubcategoria)
            pixmap = pixmap.scaled(60, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            imagen_label.setPixmap(pixmap)
            with open(self.imagenSubcategoria, 'rb') as f:
                imagen_label.imagen_bytes = f.read()
        else:
            default_image_path = get_resource_path(os.path.join('Imagenes', 'camara.png'))
            if os.path.exists(default_image_path):
                pixmap = QPixmap(default_image_path)
                pixmap = pixmap.scaled(60, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                imagen_label.setPixmap(pixmap)
                with open(default_image_path, 'rb') as f:
                    imagen_label.imagen_bytes = f.read()
            else:
                imagen_label.setText("Imagen\ndefecto")
                imagen_label.setStyleSheet("""
                    QLabel {
                        background-color: #e9ecef;
                        border-radius: 8px;
                        border: 1px solid #ced4da;
                        color: #6c757d;
                        font-size: 9px;
                        font-weight: bold;
                        padding: 5px;
                        margin-top: 5px;
                        margin-bottom: 10px;
                        qproperty-alignment: AlignCenter;
                    }
                """)
        self.tablaRegistrados.setCellWidget(fila, 1, imagen_label)
        botonModificar = QPushButton("Modificar")
        botonModificar.setFixedSize(100, 45)
        botonModificar.setContentsMargins(5, 5, 5, 5)
        estilo_boton_modificar = """
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 6px;
                padding: 8px 5px;
                font-weight: bold;
                font-size: 13px;
                border: none;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """
        botonModificar.setStyleSheet(estilo_boton_modificar)
        botonModificar.clicked.connect(lambda _, e=elemento: self.modificarElemento(e, botonModificar))
        self.tablaRegistrados.setCellWidget(fila, 2, botonModificar)
        botonEliminar = QPushButton("Eliminar")
        botonEliminar.setFixedSize(100, 45)
        botonEliminar.setContentsMargins(5, 5, 5, 5)
        estilo_boton_eliminar = """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 6px;
                padding: 8px 5px;
                font-weight: bold;
                font-size: 13px;
                border: none;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """
        botonEliminar.setStyleSheet(estilo_boton_eliminar)
        botonEliminar.clicked.connect(lambda _, e=elemento: self.eliminarElemento(e, botonEliminar))
        self.tablaRegistrados.setCellWidget(fila, 3, botonEliminar)
        self.conjunto.add(elemento)
        self.tablaRegistrados.scrollToBottom()
        self.camp4.setText("")
        self.imagenSubcategoria = None
        default_image_path = get_resource_path(os.path.join('Imagenes', 'camara.png'))
        if os.path.exists(default_image_path):
            pixmap = QPixmap(default_image_path)
            pixmap = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.labelImagenSubcategoria.setPixmap(pixmap)
        for i in range(self.tablaRegistrados.rowCount()):
            if i % 2 == 0:
                self.tablaRegistrados.item(i, 0).setBackground(QColor(248, 249, 250))
            else:
                self.tablaRegistrados.item(i, 0).setBackground(QColor(255, 255, 255))

    def modificarElemento(self, elemento, boton):
        fila = self.tablaRegistrados.indexAt(boton.mapTo(self.tablaRegistrados.viewport(), QPoint(0, 0))).row()
        imagen_widget = self.tablaRegistrados.cellWidget(fila, 1)
        imagen_data = None
        if imagen_widget and hasattr(imagen_widget, 'imagen_bytes'):
            imagen_data = imagen_widget.imagen_bytes
        conjunto_excepto_actual = {item.upper() for item in self.conjunto}
        elemento_upper = elemento.upper()
        conjunto_excepto_actual.discard(elemento_upper)
        miniPantalla = Pop_up_ModificacionSubcategoria(elemento, conjunto_excepto_actual, imagen_data, self)
        if miniPantalla.exec_() == QDialog.Accepted:
            nuevo = miniPantalla.getSub()
            nueva_imagen = miniPantalla.getImagen()
            if nuevo:
                nuevo_upper = nuevo.upper()
                if nuevo_upper in conjunto_excepto_actual and nuevo_upper != elemento_upper:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Error")
                    msg.setText(f"La subcategoría '{nuevo}' ya existe en la tabla")
                    msg.exec_()
                    return
                self.conjunto.discard(elemento)
                self.conjunto.add(nuevo)
                self.tablaRegistrados.item(fila, 0).setText(nuevo)
                if nueva_imagen:
                    imagen_label = QLabel()
                    imagen_label.setAlignment(Qt.AlignCenter)
                    imagen_label.setFixedSize(80, 70)
                    imagen_label.setContentsMargins(2, 2, 2, 2)
                    imagen_label.setStyleSheet("""
                        QLabel {
                            background-color: #f8f9fa;
                            border-radius: 8px;
                            border: 1px solid #dee2e6;
                            padding: 5px;
                            margin-top: 5px;
                            margin-bottom: 10px;
                        }
                    """)
                    pixmap = QPixmap()
                    pixmap.loadFromData(nueva_imagen)
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(60, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        imagen_label.setPixmap(pixmap)
                        imagen_label.imagen_bytes = nueva_imagen
                    self.tablaRegistrados.setCellWidget(fila, 1, imagen_label)
                boton_modificar = self.tablaRegistrados.cellWidget(fila, 2)
                boton_modificar.clicked.disconnect()
                boton_modificar.clicked.connect(lambda _, e=nuevo: self.modificarElemento(e, boton_modificar))
                boton_eliminar = self.tablaRegistrados.cellWidget(fila, 3)
                boton_eliminar.clicked.disconnect()
                boton_eliminar.clicked.connect(lambda _, e=nuevo: self.eliminarElemento(e, boton_eliminar))

    def eliminarElemento(self, elemento, boton):
        self.conjunto.discard(elemento)
        indice = self.tablaRegistrados.indexAt(boton.mapTo(self.tablaRegistrados.viewport(), QPoint(0, 0)))
        fila = indice.row()
        self.tablaRegistrados.removeRow(fila)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = RegistroCategoriasSubcategorias()
    pagina.show()
    sys.exit(app.exec_())
