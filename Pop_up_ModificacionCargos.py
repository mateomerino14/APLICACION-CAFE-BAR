import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from nucleo.Rutas import get_db_path

DB_PATH = get_db_path()


class Pop_up_ModificacionCargos(QDialog):
    def __init__(self, id_cargo, nom_cargo, parent=None):
        super().__init__(parent)
        self.id_cargo = id_cargo
        self.nom_cargo = nom_cargo
        self.setWindowTitle("MODIFICACIÓN DE CARGOS")
        self.setFixedSize(1000, 900)
        self.setStyleSheet("""
            QDialog {
                background: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
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
            QMessageBox QPushButton:hover { background-color: #2980b9; }
            QScrollArea {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 16px;
                border-radius: 8px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #94a3b8;
                min-height: 40px;
                border-radius: 8px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #64748b;
            }
            QScrollBar::handle:vertical:pressed {
                background: #475569;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.crearPantallaModificacion()

    def obtener_todas_subpantallas_agrupadas(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT p.idPant, p.nomPant, s.idSubPant, s.nomSubPant, s.accion
            FROM Pantalla p
            JOIN Subpantalla s ON p.idPant = s.idPant
            ORDER BY p.idPant, s.nomSubPant
        """)
        resultados = c.fetchall()
        conn.close()

        pantallas = {}
        for id_pant, nom_pant, id_sub, nom_sub, accion in resultados:
            if id_pant not in pantallas:
                pantallas[id_pant] = {'nombre': nom_pant, 'subpantallas': []}
            pantallas[id_pant]['subpantallas'].append({'id': id_sub, 'nombre': nom_sub, 'accion': accion})
        return pantallas

    def obtener_subpantallas_seleccionadas(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            SELECT s.idSubPant
            FROM PermisosCargoSubpantalla pcs
            JOIN Subpantalla s ON pcs.idSubPant = s.idSubPant
            WHERE pcs.idCarg = ?
        """,
            (self.id_cargo,),
        )
        resultados = c.fetchall()
        conn.close()
        return [r[0] for r in resultados]

    def crearPantallaModificacion(self):
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background: white;
            }
        """)

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(main_widget)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layoutDatos = QVBoxLayout(main_widget)
        layoutDatos.setSpacing(20)
        layoutDatos.setContentsMargins(30, 25, 30, 25)

        titulo = QLabel(f"MODIFICAR CARGO: {self.nom_cargo}")
        titulo.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #2c3e50;
                font-weight: bold;
                padding: 15px 0px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3498db, stop: 1 #2c3e50);
                border-radius: 8px;
                color: white;
                margin-bottom: 5px;
            }
        """)
        titulo.setAlignment(Qt.AlignCenter)
        layoutDatos.addWidget(titulo)

        layoutCargo = QHBoxLayout()
        cargo = QLabel("Cargo:")
        campoCargo = QLabel(self.nom_cargo)
        label_style = """
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
                padding: 8px 5px;
            }
        """
        campo_style = """
            QLabel {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                color: #495057;
                font-weight: 500;
                min-height: 20px;
            }
        """
        cargo.setStyleSheet(label_style)
        campoCargo.setStyleSheet(campo_style)
        campoCargo.setMinimumHeight(40)
        campoCargo.setAlignment(Qt.AlignCenter)
        layoutCargo.addWidget(cargo)
        layoutCargo.addWidget(campoCargo)
        layoutDatos.addLayout(layoutCargo)

        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        separador.setStyleSheet("""
            QFrame {
                background-color: #dee2e6;
                margin: 15px 0px;
                height: 2px;
                border: none;
            }
        """)
        layoutDatos.addWidget(separador)

        tituloSecciones = QLabel("PERMISOS DE ACCESO POR SUBECCIÓN")
        tituloSecciones.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                background-color: #6c757d;
                padding: 10px 15px;
                border-radius: 6px;
                margin-bottom: 5px;
            }
        """)
        tituloSecciones.setAlignment(Qt.AlignCenter)
        layoutDatos.addWidget(tituloSecciones)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(350)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(20, 20, 20, 20)

        checkbox_style = """
            QCheckBox {
                font-size: 14px;
                color: #495057;
                spacing: 12px;
                padding: 8px 12px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #dee2e6;
            }
            QCheckBox:hover {
                background-color: #e9ecef;
                border: 1px solid #ced4da;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #adb5bd;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background-color: #28a745;
                border: 2px solid #218838;
                image: url(none);
            }
            QCheckBox::indicator:unchecked:hover {
                border: 2px solid #6c757d;
            }
        """

        self.checkboxes = []
        self.checkboxes_por_pantalla = {}

        pantallas = self.obtener_todas_subpantallas_agrupadas()
        seleccionadas = self.obtener_subpantallas_seleccionadas()

        for id_pant, pantalla in pantallas.items():
            seccion_widget = QWidget()
            seccion_widget.setStyleSheet("""
                QWidget {
                    background-color: #f8fafc;
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                }
            """)
            seccion_layout = QVBoxLayout(seccion_widget)

            header_seccion = QHBoxLayout()
            titulo_seccion = QLabel(f"📌 {pantalla['nombre']}")
            titulo_seccion.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #1e293b;
                background-color: #e2e8f0;
                padding: 10px 15px;
                border-radius: 6px;
                margin: 5px;
            """)
            header_seccion.addWidget(titulo_seccion, 1)

            btn_seleccionar_todas = QPushButton("✓ Todas")
            btn_seleccionar_todas.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            btn_seleccionar_todas.setCursor(Qt.PointingHandCursor)
            header_seccion.addWidget(btn_seleccionar_todas)

            btn_deseleccionar_todas = QPushButton("✗ Ninguna")
            btn_deseleccionar_todas.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            btn_deseleccionar_todas.setCursor(Qt.PointingHandCursor)
            header_seccion.addWidget(btn_deseleccionar_todas)

            seccion_layout.addLayout(header_seccion)

            grid_sub = QGridLayout()
            grid_sub.setSpacing(10)
            grid_sub.setContentsMargins(15, 10, 15, 10)

            self.checkboxes_por_pantalla[id_pant] = []

            for i, sub in enumerate(pantalla['subpantallas']):
                checkbox = QCheckBox(sub['nombre'])
                checkbox.setStyleSheet(checkbox_style)
                checkbox.setProperty("idSubPant", sub['id'])
                if sub['id'] in seleccionadas:
                    checkbox.setChecked(True)
                self.checkboxes.append(checkbox)
                self.checkboxes_por_pantalla[id_pant].append(checkbox)

                fila = i // 2
                columna = i % 2
                grid_sub.addWidget(checkbox, fila, columna)

            btn_seleccionar_todas.clicked.connect(
                lambda checked, lista=self.checkboxes_por_pantalla[id_pant]: self.seleccionar_todos(lista, True)
            )
            btn_deseleccionar_todas.clicked.connect(
                lambda checked, lista=self.checkboxes_por_pantalla[id_pant]: self.seleccionar_todos(lista, False)
            )

            seccion_layout.addLayout(grid_sub)
            scroll_layout.addWidget(seccion_widget)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layoutDatos.addWidget(scroll_area, 1)

        layoutBotones = QHBoxLayout()
        cancelar = QPushButton("CANCELAR")
        modificar = QPushButton("GUARDAR CAMBIOS")

        boton_cancelar_style = """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #dc3545, stop: 1 #c82333);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 14px;
                min-width: 130px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c82333, stop: 1 #bd2130);
            }
            QPushButton:pressed {
                background: #bd2130;
                padding: 11px 24px;
            }
        """

        boton_guardar_style = """
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #28a745, stop: 1 #218838);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 14px;
                min-width: 130px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #218838, stop: 1 #1e7e34);
            }
            QPushButton:pressed {
                background: #1e7e34;
                padding: 11px 24px;
            }
        """

        cancelar.setStyleSheet(boton_cancelar_style)
        modificar.setStyleSheet(boton_guardar_style)
        cancelar.setCursor(Qt.PointingHandCursor)
        modificar.setCursor(Qt.PointingHandCursor)

        cancelar.clicked.connect(self.cerrarVentanaCancelar)
        modificar.clicked.connect(self.guardarCambios)

        layoutBotones.addStretch(1)
        layoutBotones.addWidget(cancelar)
        layoutBotones.addSpacing(20)
        layoutBotones.addWidget(modificar)
        layoutBotones.addStretch(1)
        layoutDatos.addLayout(layoutBotones)

    def seleccionar_todos(self, lista_checkboxes, estado):
        for checkbox in lista_checkboxes:
            checkbox.setChecked(estado)

    def cerrarVentanaCancelar(self):
        self.reject()

    def guardarCambios(self):
        seleccionados = []
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                id_subpantalla = checkbox.property("idSubPant")
                seleccionados.append(id_subpantalla)

        if len(seleccionados) == 0:
            QMessageBox.warning(self, "Advertencia", "Se debe dar acceso por lo menos a una subsección")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        try:
            conn.execute("BEGIN TRANSACTION")

            c.execute("DELETE FROM PermisosCargoSubpantalla WHERE idCarg = ?", (self.id_cargo,))

            for id_sub in seleccionados:
                c.execute(
                    "INSERT INTO PermisosCargoSubpantalla(idCarg, idSubPant) VALUES (?, ?)", (self.id_cargo, id_sub)
                )

            conn.commit()
            QMessageBox.information(self, "Confirmación", "Se ha registrado con éxito la modificación")
            self.accept()

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")
        finally:
            conn.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_start_position'):
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = Pop_up_ModificacionCargos(1, "Administrador")
    pagina.show()
    sys.exit(app.exec_())
