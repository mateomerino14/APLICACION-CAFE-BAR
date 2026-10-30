import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from functools import partial
import usb.core
import usb.util
import serial.tools.list_ports
import serial
from Rutas import get_db_path

DB_PATH = get_db_path()

class Impresoras(QWidget):
    def __init__(self):
        super().__init__()
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
            QMessageBox QPushButton:hover { background-color: #2980b9; }
        """)
        self.set_up()
        
    def set_up(self):
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.crearInterfazImpresoras()
        self.cargarImpresoras()
        self.showMaximized()
        
    def crearInterfazImpresoras(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        frameLayout = QVBoxLayout(frame)
        frameLayout.setSpacing(10)
        tituloSeccion = QLabel("Gestión de Impresoras Térmicas")
        tituloSeccion.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        """)
        frameLayout.addWidget(tituloSeccion)
        btnDetectar = QPushButton("Detectar Impresoras Térmicas Conectadas")
        btnDetectar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btnDetectar.setCursor(Qt.PointingHandCursor)
        btnDetectar.clicked.connect(self.detectarImpresorasTermicas)
        frameLayout.addWidget(btnDetectar)
        texto1=QLabel("Impresoras térmicas detectadas:")
        texto1.setStyleSheet("""color:purple;
                                font-weight:bold; 
                                font-size:20px;""")
        frameLayout.addWidget(texto1)
        self.listaImpresoras = QListWidget()
        self.listaImpresoras.setMinimumHeight(120)
        self.listaImpresoras.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                background-color: #f9f9f9;
                outline: 0;
            }
            QListWidget:focus { outline: 0; }
            QListWidget::viewport { outline: 0; }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
                color: #2c3e50;
            }
            QListWidget::item:selected {
                background-color: #d6eaf8;
                color: #2c3e50;
            }
            QListWidget::item:selected:active { color: #2c3e50; }
            QListWidget::item:selected:!active { color: #2c3e50; }
        """)
        frameLayout.addWidget(self.listaImpresoras)
        btnAnadir = QPushButton("Añadir Impresora Seleccionada a la Base de Datos")
        btnAnadir.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        btnAnadir.setCursor(Qt.PointingHandCursor)
        btnAnadir.clicked.connect(self.anadirImpresoraBD)
        frameLayout.addWidget(btnAnadir)
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        separador.setStyleSheet("color: #bdc3c7;")
        separador.setMaximumHeight(10)
        frameLayout.addWidget(separador)
        frameConfig = QFrame()
        frameConfig.setStyleSheet("""
            QFrame {
                background-color: #f0f8ff;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            }
        """)
        layoutConfig = QVBoxLayout(frameConfig)
        self.checkboxDual = QCheckBox("Permitir que una misma impresora sea para Barra y Cocina")
        self.checkboxDual.setStyleSheet("""
            QCheckBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
            }
        """)
        self.checkboxDual.setCursor(Qt.PointingHandCursor)
        self.checkboxDual.stateChanged.connect(self.actualizarSeleccion)
        layoutConfig.addWidget(self.checkboxDual)
        layoutCheckboxes = QHBoxLayout()
        self.checkBarra = QCheckBox("Usar para Barra")
        self.checkBarra.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: bold;
                color: #004A00;
                padding: 5px;
            }
        """)
        self.checkBarra.setCursor(Qt.PointingHandCursor)
        self.checkBarra.stateChanged.connect(self.onCheckBarraChanged)
        self.checkCocina = QCheckBox("Usar para Cocina")
        self.checkCocina.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: bold;
                color: #804400;
                padding: 5px;
            }
        """)
        self.checkCocina.setCursor(Qt.PointingHandCursor)
        self.checkCocina.stateChanged.connect(self.onCheckCocinaChanged)
        layoutCheckboxes.addWidget(self.checkBarra)
        layoutCheckboxes.addWidget(self.checkCocina)
        layoutCheckboxes.addStretch(1)
        layoutConfig.addLayout(layoutCheckboxes)
        frameLayout.addWidget(frameConfig)
        layoutSeleccion = QHBoxLayout()
        layoutSeleccion.setSpacing(20)
        frameBarra = QFrame()
        frameBarra.setStyleSheet("""
            QFrame {
                background-color: #eafaf1;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layoutBarra = QVBoxLayout(frameBarra)
        texto2=QLabel("Impresora para Barra:")
        texto2.setStyleSheet("""color:#004A00;
                                font-weight:bold; 
                                font-size:20px;""")
        layoutBarra.addWidget(texto2)
        self.comboBarra = QComboBox()
        self.comboBarra.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
        """)
        self.comboBarra.currentIndexChanged.connect(self.onComboBarraChanged)
        layoutBarra.addWidget(self.comboBarra)
        btnSeleccionarBarra = QPushButton("Seleccionar para Barra")
        btnSeleccionarBarra.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-size: 15px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        btnSeleccionarBarra.setCursor(Qt.PointingHandCursor)
        btnSeleccionarBarra.clicked.connect(partial(self.seleccionarImpresoraDesdeBoton, "Barra"))
        layoutBarra.addWidget(btnSeleccionarBarra)
        btnDeseleccionarBarra = QPushButton("Deseleccionar Barra")
        btnDeseleccionarBarra.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        btnDeseleccionarBarra.setCursor(Qt.PointingHandCursor)
        btnDeseleccionarBarra.clicked.connect(partial(self.deseleccionarImpresoraDesdeBoton, "Barra"))
        layoutBarra.addWidget(btnDeseleccionarBarra)
        frameCocina = QFrame()
        frameCocina.setStyleSheet("""
            QFrame {
                background-color: #fef9e7;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layoutCocina = QVBoxLayout(frameCocina)
        texto3=QLabel("Impresora para Cocina:")
        texto3.setStyleSheet("""color:#804400;
                                font-weight:bold; 
                                font-size:20px;""")
        layoutCocina.addWidget(texto3)
        self.comboCocina = QComboBox()
        self.comboCocina.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
        """)
        self.comboCocina.currentIndexChanged.connect(self.onComboCocinaChanged)
        layoutCocina.addWidget(self.comboCocina)
        btnSeleccionarCocina = QPushButton("Seleccionar para Cocina")
        btnSeleccionarCocina.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-size: 15px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        btnSeleccionarCocina.setCursor(Qt.PointingHandCursor)
        btnSeleccionarCocina.clicked.connect(partial(self.seleccionarImpresoraDesdeBoton, "Cocina"))
        layoutCocina.addWidget(btnSeleccionarCocina)
        btnDeseleccionarCocina = QPushButton("Deseleccionar Cocina")
        btnDeseleccionarCocina.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        btnDeseleccionarCocina.setCursor(Qt.PointingHandCursor)
        btnDeseleccionarCocina.clicked.connect(partial(self.deseleccionarImpresoraDesdeBoton, "Cocina"))
        layoutCocina.addWidget(btnDeseleccionarCocina)
        layoutSeleccion.addWidget(frameBarra, 1)
        layoutSeleccion.addWidget(frameCocina, 1)
        frameLayout.addLayout(layoutSeleccion)
        btnPrueba = QPushButton("Probar Impresión")
        btnPrueba.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        btnPrueba.setCursor(Qt.PointingHandCursor)
        btnPrueba.clicked.connect(self.probarImpresion)
        frameLayout.addWidget(btnPrueba)
        frameLayout.addStretch(1)
        scroll_area.setWidget(frame)
        self.layoutPrincipal.addWidget(scroll_area)
    
    def onCheckBarraChanged(self):
        if self.checkboxDual.isChecked():
            if not self.checkBarra.signalsBlocked():
                is_checked = self.checkBarra.isChecked()
                id_impresora = self.comboBarra.currentData()
                if id_impresora:
                    self.marcarImpresoraExclusiva("Barra", id_impresora, is_checked)
    
    def onCheckCocinaChanged(self):
        if self.checkboxDual.isChecked():
            if not self.checkCocina.signalsBlocked():
                is_checked = self.checkCocina.isChecked()
                id_impresora = self.comboCocina.currentData()
                if id_impresora:
                    self.marcarImpresoraExclusiva("Cocina", id_impresora, is_checked)
    
    def marcarImpresoraExclusiva(self, tipo, id_impresora, activado):
        columna = "es_barra" if tipo == "Barra" else "es_cocina"
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            if activado:
                cursor.execute(f"UPDATE Impresora SET {columna} = 0")
                cursor.execute(f"UPDATE Impresora SET {columna} = 1 WHERE idImpresora = ?", (id_impresora,))
                QMessageBox.information(self, "Éxito", f"Impresora marcada para {tipo} correctamente.")
            else:
                cursor.execute(f"UPDATE Impresora SET {columna} = 0 WHERE idImpresora = ?", (id_impresora,))
                QMessageBox.information(self, "Éxito", f"Impresora desmarcada para {tipo} correctamente.")
            conn.commit()
            conn.close()
            self.actualizarCombosModoDual()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {str(e)}")
    
    def actualizarSeleccion(self):
        if self.checkboxDual.isChecked():
            self.actualizarCombosModoDual()
            self.checkBarra.setEnabled(True)
            self.checkCocina.setEnabled(True)
        else:
            self.cargarImpresoras()
            self.checkBarra.setEnabled(False)
            self.checkCocina.setEnabled(False)
            self.checkBarra.blockSignals(True)
            self.checkCocina.blockSignals(True)
            self.checkBarra.setChecked(False)
            self.checkCocina.setChecked(False)
            self.checkBarra.blockSignals(False)
            self.checkCocina.blockSignals(False)
    
    def actualizarCombosModoDual(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT idImpresora, idVendor, idProducto, dispositivo, es_barra, es_cocina FROM Impresora")
            impresoras = cursor.fetchall()
            conn.close()
            seleccion_barra_actual = self.comboBarra.currentData()
            seleccion_cocina_actual = self.comboCocina.currentData()
            self.comboBarra.clear()
            self.comboCocina.clear()
            for impresora in impresoras:
                id_impresora, id_vendor, id_producto, dispositivo, es_barra, es_cocina = impresora
                texto = f"ID: {id_impresora}"
                if id_vendor > 0 and id_producto > 0:
                    texto += f" - VID: 0x{id_vendor:04x}, PID: 0x{id_producto:04x}"
                if dispositivo:
                    texto += f" - {dispositivo}"
                if es_barra == 1:
                    texto += " [Barra ✓]"
                if es_cocina == 1:
                    texto += " [Cocina ✓]"
                self.comboBarra.addItem(texto, id_impresora)
                self.comboCocina.addItem(texto, id_impresora)
            
            if seleccion_barra_actual:
                index = self.comboBarra.findData(seleccion_barra_actual)
                if index >= 0:
                    self.comboBarra.setCurrentIndex(index)
            
            if seleccion_cocina_actual:
                index = self.comboCocina.findData(seleccion_cocina_actual)
                if index >= 0:
                    self.comboCocina.setCurrentIndex(index)
            
            self.actualizarCheckboxes()
            
        except Exception as e:
            print(f"Error al actualizar combos modo dual: {e}")
    
    def actualizarCheckboxes(self):
        id_impresora_barra = self.comboBarra.currentData()
        id_impresora_cocina = self.comboCocina.currentData()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            if id_impresora_barra:
                cursor.execute("SELECT es_barra FROM Impresora WHERE idImpresora = ?", (id_impresora_barra,))
                resultado = cursor.fetchone()
                if resultado:
                    self.checkBarra.blockSignals(True)
                    self.checkBarra.setChecked(resultado[0] == 1)
                    self.checkBarra.blockSignals(False)
            
            if id_impresora_cocina:
                cursor.execute("SELECT es_cocina FROM Impresora WHERE idImpresora = ?", (id_impresora_cocina,))
                resultado = cursor.fetchone()
                if resultado:
                    self.checkCocina.blockSignals(True)
                    self.checkCocina.setChecked(resultado[0] == 1)
                    self.checkCocina.blockSignals(False)
            conn.close()
        except Exception as e:
            print(f"Error al actualizar checkboxes: {e}")
    
    def onComboBarraChanged(self):
        if self.checkboxDual.isChecked():
            self.actualizarCheckboxes()
    
    def onComboCocinaChanged(self):
        if self.checkboxDual.isChecked():
            self.actualizarCheckboxes()
    
    def seleccionarImpresoraDesdeBoton(self, tipo):
        if tipo == "Barra":
            combo = self.comboBarra
            checkbox = self.checkBarra
        else:
            combo = self.comboCocina
            checkbox = self.checkCocina
        id_impresora = combo.currentData()
        if not id_impresora:
            QMessageBox.warning(self, "Advertencia", f"Por favor, seleccione una impresora para {tipo}.")
            return
        if self.checkboxDual.isChecked():
            checkbox.blockSignals(True)
            checkbox.setChecked(True)
            checkbox.blockSignals(False)
            self.marcarImpresoraExclusiva(tipo, id_impresora, True)
        else:
            self.seleccionarImpresoraExclusiva(tipo, id_impresora)
    
    def deseleccionarImpresoraDesdeBoton(self, tipo):
        if tipo == "Barra":
            combo = self.comboBarra
            checkbox = self.checkBarra
        else:
            combo = self.comboCocina
            checkbox = self.checkCocina
        id_impresora = combo.currentData()
        if not id_impresora:
            QMessageBox.warning(self, "Advertencia", f"Por favor, seleccione una impresora para deseleccionar de {tipo}.")
            return
        if self.checkboxDual.isChecked():
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)
            self.marcarImpresoraExclusiva(tipo, id_impresora, False)
        else:
            self.deseleccionarImpresoraExclusiva(tipo, id_impresora)
    
    def seleccionarImpresoraExclusiva(self, tipo, id_impresora):
        columna = "es_barra" if tipo == "Barra" else "es_cocina"
        otro_tipo = "es_cocina" if tipo == "Barra" else "es_barra"
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(f"UPDATE Impresora SET {columna} = 0")
            cursor.execute(f"UPDATE Impresora SET {columna} = 1 WHERE idImpresora = ?", (id_impresora,))
            cursor.execute(f"UPDATE Impresora SET {otro_tipo} = 0 WHERE idImpresora = ?", (id_impresora,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Éxito", f"Impresora seleccionada para {tipo} correctamente.")
            self.cargarImpresoras()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo seleccionar la impresora: {str(e)}")
    
    def deseleccionarImpresoraExclusiva(self, tipo, id_impresora):
        columna = "es_barra" if tipo == "Barra" else "es_cocina"
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(f"UPDATE Impresora SET {columna} = 0 WHERE idImpresora = ?", (id_impresora,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Éxito", f"Impresora deseleccionada para {tipo} correctamente.")
            self.cargarImpresoras()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo deseleccionar la impresora: {str(e)}")
    
    def detectarImpresorasTermicas(self):
        self.listaImpresoras.clear()
        dispositivos_encontrados = False
        dispositivos_unicos = {}
        try:
            puertos = serial.tools.list_ports.comports()
            for puerto in puertos:
                descripcion = puerto.description.lower()
                es_impresora_termica = any(term in descripcion for term in [
                    'thermal', 'pos', 'receipt', 'ticket', 'termica', 
                    'ethernet/thermal', 'usb receipt', 'serial printer',
                    'bixolon', 'epson tm', 'citizen', 'starmicro', 'zjiang'
                ])
                es_impresora_normal = any(term in descripcion for term in [
                    'printer', 'print', 'laser', 'inkjet', 'deskjet', 
                    'epson', 'hp', 'canon', 'brother', 'lexmark',
                    'xerox', 'samsung', 'ricoh', 'kyocera', 'okidata'
                ])
                if es_impresora_termica or es_impresora_normal:
                    tipo = "TÉRMICA" if es_impresora_termica else "NORMAL"
                    clave = f"SERIAL:{puerto.device}"
                    if puerto.vid and puerto.pid:
                        clave += f":{puerto.vid:04x}:{puerto.pid:04x}"
                    if clave in dispositivos_unicos:
                        continue
                    dispositivos_unicos[clave] = True
                    if puerto.vid and puerto.pid:
                        item_text = f"{tipo}: {puerto.description} - VID: 0x{puerto.vid:04x}, PID: 0x{puerto.pid:04x} - {puerto.device}"
                    else:
                        item_text = f"{tipo}: {puerto.description} - {puerto.device}"
                    en_bd = self.impresoraEnBD(puerto.vid or 0, puerto.pid or 0)
                    if en_bd:
                        item_text += " (Ya en BD)"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, {
                        'vid': puerto.vid or 0,
                        'pid': puerto.pid or 0,
                        'en_bd': en_bd,
                        'dispositivo': puerto.device,
                        'descripcion': puerto.description,
                        'es_termica': es_impresora_termica,
                        'es_normal': es_impresora_normal
                    })
                    if en_bd:
                        item.setForeground(QColor("#7f8c8d"))
                    self.listaImpresoras.addItem(item)
                    dispositivos_encontrados = True
        except Exception as e:
            print(f"Error con pySerial: {e}")
        try:
            dispositivos_usb = usb.core.find(find_all=True)
            if dispositivos_usb:
                for dispositivo in list(dispositivos_usb):
                    try:
                        id_vendor = dispositivo.idVendor
                        id_product = dispositivo.idProduct
                        try:
                            manufacturer = usb.util.get_string(dispositivo, dispositivo.iManufacturer) or ""
                            product = usb.util.get_string(dispositivo, dispositivo.iProduct) or ""
                            descripcion = f"{manufacturer} {product}".strip()
                        except Exception:
                            descripcion = "Dispositivo USB"
                        es_probable_impresora = False
                        desc_lower = descripcion.lower()
                        if any(term in desc_lower for term in ['printer', 'print', 'epson', 'hp', 'canon', 'brother']):
                            es_probable_impresora = True
                        vids_impresoras = [
                            0x04B8, 0x03F0, 0x04A9, 0x04F9, 0x043D, 0x0924
                        ]
                        if id_vendor in vids_impresoras:
                            es_probable_impresora = True
                        if es_probable_impresora and descripcion:
                            clave = f"USB:{id_vendor:04x}:{id_product:04x}"
                            if clave in dispositivos_unicos:
                                usb.util.dispose_resources(dispositivo)
                                continue
                            dispositivos_unicos[clave] = True
                            tipo = "USB"
                            en_bd = self.impresoraEnBD(id_vendor, id_product)
                            item_text = f"{tipo}: {descripcion} - VID: 0x{id_vendor:04x}, PID: 0x{id_product:04x}"
                            if en_bd:
                                item_text += " (Ya en BD)"
                            item = QListWidgetItem(item_text)
                            item.setData(Qt.UserRole, {
                                'vid': id_vendor,
                                'pid': id_product,
                                'en_bd': en_bd,
                                'dispositivo': '',
                                'descripcion': descripcion,
                                'es_termica': False,
                                'es_normal': True
                            })
                            if en_bd:
                                item.setForeground(QColor("#7f8c8d"))
                            self.listaImpresoras.addItem(item)
                            dispositivos_encontrados = True
                        usb.util.dispose_resources(dispositivo)
                    except Exception as e:
                        print(f"Error con dispositivo USB: {e}")
                        continue
        except Exception as e:
            print(f"Error con pyUSB: {e}")
        try:
            import platform
            if platform.system() == "Windows":
                import win32print
                impresoras_windows = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
                for impresora in impresoras_windows:
                    nombre_impresora = impresora[2]
                    if nombre_impresora:
                        clave = f"WINDOWS:{nombre_impresora}"
                        if clave in dispositivos_unicos:
                            continue
                        dispositivos_unicos[clave] = True
                        item_text = f"WINDOWS: {nombre_impresora}"
                        try:
                            conn = sqlite3.connect(DB_PATH)
                            cursor = conn.cursor()
                            cursor.execute("SELECT * FROM Impresora WHERE dispositivo = ?", 
                                          (nombre_impresora,))
                            en_bd = cursor.fetchone() is not None
                            conn.close()
                        except Exception:
                            en_bd = False
                        if en_bd:
                            item_text += " (Ya en BD)"
                        item = QListWidgetItem(item_text)
                        item.setData(Qt.UserRole, {
                            'vid': 0,
                            'pid': 0,
                            'en_bd': en_bd,
                            'dispositivo': nombre_impresora,
                            'descripcion': nombre_impresora,
                            'es_termica': False,
                            'es_normal': True
                        })
                        if en_bd:
                            item.setForeground(QColor("#7f8c8d"))
                        self.listaImpresoras.addItem(item)
                        dispositivos_encontrados = True
        except ImportError:
            print("win32print no disponible (no es Windows)")
        except Exception as e:
            print(f"Error con win32print: {e}")
        
        if not dispositivos_encontrados:
            self.listaImpresoras.addItem("No se detectaron impresoras")
            self.listaImpresoras.addItem("Conecte una impresora y vuelva a intentar")
    
    def impresoraEnBD(self, id_vendor, id_product):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Impresora WHERE idVendor = ? AND idProducto = ?", (id_vendor, id_product))
            resultado = cursor.fetchone()
            conn.close()
            return resultado is not None
        except Exception:
            return False
    
    def anadirImpresoraBD(self):
        item_actual = self.listaImpresoras.currentItem()
        if not item_actual:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione una impresora de la lista.")
            return
        datos = item_actual.data(Qt.UserRole)
        if not datos:
            return
        id_vendor = datos.get('vid', 0)
        id_product = datos.get('pid', 0)
        en_bd = datos.get('en_bd', False)
        dispositivo = datos.get('dispositivo', '')
        if en_bd:
            QMessageBox.information(self, "Información", "Esta impresora ya está en la base de datos.")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            if id_vendor == 0 and id_product == 0 and dispositivo:
                cursor.execute("INSERT INTO Impresora (idVendor, idProducto, dispositivo, es_barra, es_cocina) VALUES (?, ?, ?, 0, 0)", 
                              (0, 0, dispositivo))
            else:
                cursor.execute("INSERT INTO Impresora (idVendor, idProducto, dispositivo, es_barra, es_cocina) VALUES (?, ?, ?, 0, 0)", 
                              (id_vendor, id_product, dispositivo))
            
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Éxito", "Impresora añadida correctamente a la base de datos.")
            self.cargarImpresoras()
            self.detectarImpresorasTermicas()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo añadir la impresora: {str(e)}")
    
    def cargarImpresoras(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT idImpresora, idVendor, idProducto, dispositivo, es_barra, es_cocina FROM Impresora")
            impresoras = cursor.fetchall()
            conn.close()
            seleccion_barra_actual = self.comboBarra.currentData()
            seleccion_cocina_actual = self.comboCocina.currentData()
            self.comboBarra.clear()
            self.comboCocina.clear()
            impresoras_barra = []
            impresoras_cocina = []
            for impresora in impresoras:
                id_impresora, id_vendor, id_producto, dispositivo, es_barra, es_cocina = impresora
                texto = f"ID: {id_impresora}"
                if id_vendor > 0 and id_producto > 0:
                    texto += f" - VID: 0x{id_vendor:04x}, PID: 0x{id_producto:04x}"
                if dispositivo:
                    texto += f" - {dispositivo}"
                if self.checkboxDual.isChecked():
                    if es_barra == 1:
                        texto += " [Barra ✓]"
                    if es_cocina == 1:
                        texto += " [Cocina ✓]"
                    self.comboBarra.addItem(texto, id_impresora)
                    self.comboCocina.addItem(texto, id_impresora)
                else:
                    if es_barra == 0:
                        self.comboBarra.addItem(texto, id_impresora)
                    if es_cocina == 0:
                        self.comboCocina.addItem(texto, id_impresora)
                if es_barra == 1:
                    impresoras_barra.append(id_impresora)
                if es_cocina == 1:
                    impresoras_cocina.append(id_impresora)
            if impresoras_barra:
                index = self.comboBarra.findData(impresoras_barra[0])
                if index >= 0:
                    self.comboBarra.setCurrentIndex(index)
            elif seleccion_barra_actual and self.comboBarra.findData(seleccion_barra_actual) >= 0:
                index = self.comboBarra.findData(seleccion_barra_actual)
                self.comboBarra.setCurrentIndex(index)
            if impresoras_cocina:
                index = self.comboCocina.findData(impresoras_cocina[0])
                if index >= 0:
                    self.comboCocina.setCurrentIndex(index)
            elif seleccion_cocina_actual and self.comboCocina.findData(seleccion_cocina_actual) >= 0:
                index = self.comboCocina.findData(seleccion_cocina_actual)
                self.comboCocina.setCurrentIndex(index)
            self.actualizarCheckboxes()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las impresoras: {str(e)}")
    

    def probarImpresion(self):
        dialog = QDialog(self)
        dialog.setStyleSheet("""
            QDialog {
                background: #ffffff;
                border-radius: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #2c3e50;
                font-size: 15px;
                font-weight: 600;
                padding: 6px 2px 12px 2px;
            }
            QComboBox {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 6px;
                padding: 8px 10px;
                min-height: 36px;
            }
            QComboBox:focus {
                border: 2px solid #2980b9;
                background-color: #f8f9fa;
            }
            QComboBox QAbstractItemView {
                background: #ffffff;
                border: 1px solid #3498db;
                selection-background-color: #3498db;
                selection-color: #ffffff;
                outline: none;
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
                border-radius: 10px;
                padding: 8px 18px;
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
        dialog.setWindowTitle("Probar Impresión")
        dialog.setFixedSize(400, 200)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Seleccione la impresora a probar:"))
        combo = QComboBox()
        combo.addItem("Impresora de Barra", "Barra")
        combo.addItem("Impresora de Cocina", "Cocina")
        layout.addWidget(combo)
        layout.addStretch(1)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec_() == QDialog.Accepted:
            tipo = combo.currentData()
            self.ejecutarPruebaImpresion(tipo)
    

    def ejecutarPruebaImpresion(self, tipo):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            if tipo == "Barra":
                cursor.execute("SELECT idImpresora, idVendor, idProducto, dispositivo FROM Impresora WHERE es_barra = 1")
            else:
                cursor.execute("SELECT idImpresora, idVendor, idProducto, dispositivo FROM Impresora WHERE es_cocina = 1")
            impresoras = cursor.fetchall()
            conn.close()
            if not impresoras:
                QMessageBox.warning(self, "Advertencia", 
                                  f"No hay una impresora seleccionada para {tipo}.\n"
                                  f"Por favor, seleccione una impresora primero.")
                return
            for impresora in impresoras:
                id_impresora, id_vendor, id_producto, dispositivo = impresora
                mensaje = "================================\n"
                mensaje += f"Prueba de impresión - {tipo}\n"
                mensaje += f"Impresora ID: {id_impresora}\n"
                mensaje += "================================\n"
                mensaje += "Esta es una prueba de impresión\n"
                mensaje += "desde el sistema de cafebar.\n"
                mensaje += "================================\n"
                mensaje += "¡Impresión exitosa!\n"
                mensaje += "\n" * 3
                if self.imprimir_realmente(dispositivo, id_vendor, id_producto, mensaje):
                    QMessageBox.information(self, "Éxito", 
                                          f"Se envió correctamente la prueba a la impresora de {tipo}.\n"
                                          f"Dispositivo: {dispositivo}")
                else:
                    QMessageBox.warning(self, "Advertencia", 
                                      f"No se pudo imprimir en la impresora {dispositivo}.\n"
                                      f"Verifique que esté conectada.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo realizar la prueba: {str(e)}")
    

    def imprimir_realmente(self, dispositivo, vid, pid, texto):
        try:
            if dispositivo and ('COM' in dispositivo.upper() or '/dev/' in dispositivo):
                try:
                    puerto = serial.Serial(
                        port=dispositivo,
                        baudrate=9600,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=2
                    )
                    comando_inicial = b'\x1b\x40'
                    comando_corte = b'\n' * 5 + b'\x1d\x56\x00'
                    puerto.write(comando_inicial)
                    puerto.write(texto.encode('utf-8', errors='ignore'))
                    puerto.write(comando_corte)
                    puerto.close()
                    return True
                except serial.SerialException as e:
                    print(f"Error de comunicación serial: {e}")
                    return False
            elif vid > 0 and pid > 0:
                try:
                    dev = usb.core.find(idVendor=vid, idProduct=pid)
                    if dev is None:
                        return False
                    if dev.is_kernel_driver_active(0):
                        dev.detach_kernel_driver(0)
                    dev.set_configuration()
                    cfg = dev.get_active_configuration()
                    intf = cfg[(0,0)]
                    ep_out = None
                    for ep in intf:
                        if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                            ep_out = ep
                            break
                    if ep_out:
                        dev.write(ep_out.bEndpointAddress, texto.encode('utf-8'))
                        usb.util.dispose_resources(dev)
                        return True
                    else:
                        usb.util.dispose_resources(dev)
                        return False
                except Exception as e:
                    print(f"Error USB: {e}")
                    return False
            elif dispositivo:
                try:
                    import platform
                    if platform.system() == "Windows":
                        import win32print
                        
                        es_termica = any(term in dispositivo.lower() for term in [
                            'thermal', 'termica', 'ticket', 'receipt', 'pos',
                            'tm-', 'tsp', 'bixolon', 'star', 'citizen', 'zjiang'
                        ])
                        
                        if es_termica:
                            texto_limpio = texto.encode('latin-1', errors='ignore')
                            contenido_bytes = b'\x1b\x40'
                            contenido_bytes += texto_limpio
                            contenido_bytes += b'\n' * 5
                            contenido_bytes += b'\x1d\x56\x00'
                            hPrinter = win32print.OpenPrinter(dispositivo)
                            try:
                                doc_info = ("Prueba Cafebar", None, "RAW")
                                win32print.StartDocPrinter(hPrinter, 1, doc_info)
                                win32print.StartPagePrinter(hPrinter)
                                win32print.WritePrinter(hPrinter, contenido_bytes)
                                win32print.EndPagePrinter(hPrinter)
                                win32print.EndDocPrinter(hPrinter)
                                return True
                            finally:
                                win32print.ClosePrinter(hPrinter)
                        else:
                            import win32ui
                            hdc = win32ui.CreateDC()
                            hdc.CreatePrinterDC(dispositivo)
                            hdc.StartDoc("Prueba Impresión")
                            hdc.StartPage()
                            font = win32ui.CreateFont({
                                "name": "Courier New",
                                "height": 100,
                                "weight": 400,
                            })
                            hdc.SelectObject(font)
                            line_height = 150
                            y = 100
                            for line in texto.split('\n'):
                                hdc.TextOut(100, y, line)
                                y += line_height
                            hdc.EndPage()
                            hdc.EndDoc()
                            return True
                    return False
                except Exception as e:
                    print(f"Error impresión Windows: {e}")
                    return False
            return False
            
        except Exception as e:
            print(f"Error general en impresión: {e}")
            return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Impresoras()
    ventana.show()
    sys.exit(app.exec_())