import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from Rutas import get_db_path

DB_PATH = get_db_path()

class Pop_up_ModificacionIngredientes(QDialog):
    def __init__(self, datos, parent=None):
        super().__init__(parent)
        self.nombres_existentes = []
        self.setWindowTitle("MODIFICACIÓN DE INGREDIENTE")
        self.setFixedSize(700, 930)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8fcff, stop: 1 #e3f0ff);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMessageBox {
                background: #ffffff;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 15px;
                font-weight: 500;
                background: transparent;
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
        
        self.crearPantallaModificacion(datos)
        
    def crearPantallaModificacion(self, datos):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(40, 30, 40, 30)
        titulo_container = QFrame()
        titulo_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3498db, stop: 1 #2980b9);
                border-radius: 15px;
                padding: 15px;
            }
        """)
        titulo_layout = QHBoxLayout(titulo_container)
        titulo_layout.setContentsMargins(0, 0, 0, 0)
        titulo = QLabel("✏️ MODIFICAR INGREDIENTE")
        titulo.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
                background: transparent;
                padding: 5px;
            }
        """)
        titulo.setAlignment(Qt.AlignCenter)
        titulo_layout.addWidget(titulo)
        main_layout.addWidget(titulo_container)
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                border: 1px solid #d0e0f0;
                padding: 25px;
            }
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        label_style = """
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
                background: transparent;
                padding: 5px 0;
                letter-spacing: 0.5px;
            }
        """
        field_style = """
            QLineEdit, QComboBox {
                background-color: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 12px 15px;
                font-size: 14px;
                color: #1e293b;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
            QTextEdit {
                background-color: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 12px 15px;
                font-size: 14px;
                color: #1e293b;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QTextEdit:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
            QTextEdit QScrollBar:vertical {
                width: 10px;
                background: #f0f0f0;
                border-radius: 5px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #3498db;
                border-radius: 5px;
                min-height: 20px;
            }
            QTextEdit QScrollBar::handle:vertical:hover {
                background: #2980b9;
            }
            QTextEdit QScrollBar::add-line:vertical, QTextEdit QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #3498db;
                width: 0;
                height: 0;
                margin-right: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 5px;
                font-size: 14px;
                selection-background-color: #3498db;
                selection-color: white;
                outline: none;
            }
        """
        nombre_label = QLabel("📛 NOMBRE DEL INGREDIENTE")
        nombre_label.setStyleSheet(label_style)
        form_layout.addWidget(nombre_label)
        self.campoNombre = QLineEdit()
        self.campoNombre.setPlaceholderText("Ingrese el nombre del ingrediente")
        letras_regex = QRegExp("[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+")
        self.campoNombre.setValidator(QRegExpValidator(letras_regex))
        self.campoNombre.setMaxLength(30)
        self.campoNombre.setText(datos[1])
        self.campoNombre.setStyleSheet(field_style)

        self.completerNombre = QCompleter(self.nombres_existentes, self)
        self.completerNombre.setCaseSensitivity(Qt.CaseInsensitive)
        self.completerNombre.setFilterMode(Qt.MatchContains)
        self.campoNombre.setCompleter(self.completerNombre)

        form_layout.addWidget(self.campoNombre)
        descripcion_label = QLabel("📋 DESCRIPCIÓN")
        descripcion_label.setStyleSheet(label_style)
        form_layout.addWidget(descripcion_label)
        self.campoDescripcion = QTextEdit()
        self.campoDescripcion.setPlaceholderText("Ingrese la descripción del ingrediente (opcional)")
        self.campoDescripcion.setText(datos[2])
        self.campoDescripcion.setFixedHeight(70)
        self.campoDescripcion.setStyleSheet(field_style)
        MAX_LARGO_DESCRIPCION_ING = 200
        def limitar_descripcion_ing_mod():
            texto = self.campoDescripcion.toPlainText()
            if len(texto) > MAX_LARGO_DESCRIPCION_ING:
                cursor = self.campoDescripcion.textCursor()
                posicion = cursor.position()
                self.campoDescripcion.blockSignals(True)
                self.campoDescripcion.setPlainText(texto[:MAX_LARGO_DESCRIPCION_ING])
                cursor.setPosition(min(posicion, MAX_LARGO_DESCRIPCION_ING))
                self.campoDescripcion.setTextCursor(cursor)
                self.campoDescripcion.blockSignals(False)
        self.campoDescripcion.textChanged.connect(limitar_descripcion_ing_mod)
        form_layout.addWidget(self.campoDescripcion)
        cantidad_label = QLabel("⚖️ CANTIDAD EN STOCK")
        cantidad_label.setStyleSheet(label_style)
        form_layout.addWidget(cantidad_label)
        self.campoCantidad = QLineEdit()
        self.campoCantidad.setPlaceholderText("0.00")
        cantidadRegex = QRegExp(r"[0-9]{1,8}(\.[0-9]{0,2})?")
        self.campoCantidad.setValidator(QRegExpValidator(cantidadRegex))
        self.campoCantidad.setMaxLength(11)
        self.campoCantidad.setText(datos[3])
        self.campoCantidad.setStyleSheet(field_style)
        form_layout.addWidget(self.campoCantidad)
        unidad_label = QLabel("📏 UNIDAD DE MEDIDA")
        unidad_label.setStyleSheet(label_style)
        form_layout.addWidget(unidad_label)
        self.campoUnidadMedida = QComboBox()
        self.campoUnidadMedida.setEditable(True)
        self.campoUnidadMedida.setInsertPolicy(QComboBox.NoInsert)
        unidades = ["Kilogramos", "Litros", "Onzas", "Gramos", "Mililitros", "Unidades"]
        self.campoUnidadMedida.addItems(unidades)
        completer = QCompleter()
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        modelo = QStringListModel()
        modelo.setStringList(unidades)
        completer.setModel(modelo)
        self.campoUnidadMedida.setCompleter(completer)
        unidad_actual = datos[4]
        index = self.campoUnidadMedida.findText(unidad_actual, Qt.MatchFixedString)
        if index >= 0:
            self.campoUnidadMedida.setCurrentIndex(index)
        else:
            self.campoUnidadMedida.setCurrentText(unidad_actual)
        self.campoUnidadMedida.setStyleSheet(field_style)
        form_layout.addWidget(self.campoUnidadMedida)
        precioExtra_label = QLabel("💲 PRECIO EXTRA (Bs) — al agregarlo como extra en un pedido")
        precioExtra_label.setStyleSheet(label_style)
        form_layout.addWidget(precioExtra_label)
        self.campoPrecioExtra = QLineEdit()
        self.campoPrecioExtra.setPlaceholderText("0.00")
        precioExtraRegex = QRegExp(r"[0-9]{1,8}(\.[0-9]{0,2})?")
        self.campoPrecioExtra.setValidator(QRegExpValidator(precioExtraRegex))
        self.campoPrecioExtra.setMaxLength(11)
        precio_extra_actual = datos[5] if len(datos) > 5 and datos[5] not in (None, "") else "0"
        self.campoPrecioExtra.setText(str(precio_extra_actual))
        self.campoPrecioExtra.setStyleSheet(field_style)
        form_layout.addWidget(self.campoPrecioExtra)
        form_layout.addStretch()
        main_layout.addWidget(form_container)
        botones_container = QFrame()
        botones_container.setStyleSheet("""
            QFrame {
                background: transparent;
                margin-top: 10px;
            }
        """)
        botones_layout = QHBoxLayout(botones_container)
        botones_layout.setSpacing(20)
        self.btn_cancelar = QPushButton("CANCELAR")
        self.btn_cancelar.setCursor(Qt.PointingHandCursor)
        self.btn_cancelar.clicked.connect(self.cerrarVentanaCancelar)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e74c3c, stop: 1 #c0392b);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 25px;
                font-weight: bold;
                font-size: 15px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ff6b6b, stop: 1 #ee5253);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c0392b, stop: 1 #e74c3c);
                transform: translateY(1px);
            }
        """)
        self.btn_modificar = QPushButton("MODIFICAR")
        self.btn_modificar.setCursor(Qt.PointingHandCursor)
        self.btn_modificar.clicked.connect(lambda: self.modificarRegistro(datos))
        self.btn_modificar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2ecc71, stop: 1 #27ae60);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 25px;
                font-weight: bold;
                font-size: 15px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #32ff7e, stop: 1 #3ae374);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #27ae60, stop: 1 #2ecc71);
                transform: translateY(1px);
            }
        """)
        
        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_cancelar)
        botones_layout.addWidget(self.btn_modificar)
        botones_layout.addStretch()
        main_layout.addWidget(botones_container)

    def showEvent(self, event):
        super().showEvent(event)
        self.completerNombre.setModel(QStringListModel(self.nombres_existentes))
        
    def modificarRegistro(self, datos):
        if not self.campoNombre.text().strip():
            QMessageBox.warning(self, "Advertencia", "¡El nombre del ingrediente es obligatorio!")
            return
            
        if not self.campoUnidadMedida.currentText().strip():
            QMessageBox.warning(self, "Advertencia", "¡La unidad de medida es obligatoria!")
            return
            
        if not self.campoCantidad.text().strip():
            QMessageBox.warning(self, "Advertencia", "¡La cantidad en stock es obligatoria!")
            return
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        consulta = """SELECT * FROM Stock WHERE UPPER(nomIng)=UPPER(?) AND idIng != ?"""
        c.execute(consulta, (self.campoNombre.text().strip(), int(datos[0])))
        resultados = c.fetchall()
        if resultados:
            QMessageBox.warning(self, "Advertencia", "Este ingrediente ya está registrado")
            conn.close()
            return
            
        try:
            precio_extra_texto = self.campoPrecioExtra.text().strip()
            precio_extra_valor = float(precio_extra_texto) if precio_extra_texto != "" else 0.0
            consulta = """UPDATE Stock 
                       SET nomIng=?, descripcion=?, cantidadStock=?, unidadMedida=?, precioExtra=?
                       WHERE idIng=?"""
            c.execute(consulta, (
                self.campoNombre.text().strip(), 
                self.campoDescripcion.toPlainText().strip(), 
                float(self.campoCantidad.text()) if self.campoCantidad.text() else 0.00,
                self.campoUnidadMedida.currentText().strip(),
                precio_extra_valor,
                int(datos[0])
            ))
            conn.commit()
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Éxito")
            msg.setText("Ingrediente modificado exitosamente")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: #2c3e50;
                    font-size: 14px;
                    font-weight: 500;
                    min-width: 250px;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 8px;
                    padding: 8px 20px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            msg.exec_()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al modificar: {str(e)}")
        finally:
            conn.close()
        
    def cerrarVentanaCancelar(self):
        self.reject()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    datos_ejemplo = [1, "Azúcar", "Azúcar refinada para repostería", "50", "Kilogramos", "0.50"]
    pagina = Pop_up_ModificacionIngredientes(datos_ejemplo)
    pagina.show()
    sys.exit(app.exec_())