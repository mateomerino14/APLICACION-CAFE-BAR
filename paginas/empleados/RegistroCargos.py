import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from nucleo.Rutas import get_db_path

DB_PATH = get_db_path()


class RegistroCargos(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #e6f2ff;
                font-family: 'Segoe UI', Arial, sans-serif;
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
            QScrollArea {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 14px;
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #a0a0a0;
                min-height: 30px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical:hover {
                background: #808080;
            }
            QScrollBar::handle:vertical:pressed {
                background: #606060;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 14px;
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal {
                background: #a0a0a0;
                min-width: 30px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #808080;
            }
            QScrollBar::handle:horizontal:pressed {
                background: #606060;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        self.checkboxes = {}
        self.cargar_cargos_existentes()
        self.set_up()

    def cargar_cargos_existentes(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT nomCarg FROM Cargo ORDER BY nomCarg")
            self.cargos_existentes = [row[0] for row in c.fetchall()]
            conn.close()
        except Exception:
            self.cargos_existentes = []

    def set_up(self):
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.layoutPrincipal.setSpacing(0)
        self.anadirAreaRegistro()
        self.showMaximized()

    def obtener_pantallas_con_subpantallas(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT p.idPant, p.nomPant, s.idSubPant, s.nomSubPant, s.accion
            FROM Pantalla p
            LEFT JOIN Subpantalla s ON p.idPant = s.idPant
            ORDER BY p.idPant, s.idSubPant
        """)
        resultados = c.fetchall()
        conn.close()

        pantallas = {}
        for id_pant, nom_pant, id_sub, nom_sub, accion in resultados:
            if id_pant not in pantallas:
                pantallas[id_pant] = {'nombre': nom_pant, 'subpantallas': []}
            if id_sub:
                if not (nom_pant == "Caja" and nom_sub in ["Ver Pedidos Pendientes", "Cobrar Pedidos"]):
                    pantallas[id_pant]['subpantallas'].append({'id': id_sub, 'nombre': nom_sub, 'accion': accion})
        return pantallas

    def seleccionar_todas_seccion(self, id_pant, estado):
        for checkbox in self.checkboxes[id_pant]:
            checkbox.setChecked(estado)

    def anadirAreaRegistro(self):
        area = QWidget()
        area.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
            padding: 25px;
            border: 1px solid #d1d5db;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        """)
        area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layoutPrincipal.addWidget(area)

        layoutVertical = QVBoxLayout(area)
        layoutVertical.setContentsMargins(40, 40, 40, 40)
        layoutVertical.setSpacing(20)

        layoutCampos = QHBoxLayout()
        layoutCampos.setSpacing(20)

        nombre = QLabel("Nombre del Cargo: ")
        nombre.setStyleSheet("""
            font-size: 18px;
            font-weight: 500;
            color: #374151;
            padding: 5px 0;
        """)
        layoutCampos.addWidget(nombre)

        self.campoNombre = QComboBox()
        self.campoNombre.setEditable(True)

        cargos_base = ["Cocinero", "Mesero", "Cajero"]
        todos_cargos = list(set(cargos_base + self.cargos_existentes))
        todos_cargos.sort()
        self.campoNombre.addItems(todos_cargos)

        self.campoNombre.setStyleSheet("""
            QComboBox {
                border: 2px solid #d1d5db;
                border-radius: 6px;
                padding: 12px 15px;
                font-size: 16px;
                background-color: white;
            }
            QComboBox:hover {
                border: 2px solid #4f46e5;
            }
            QComboBox:focus {
                border: 2px solid #4f46e5;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #d1d5db;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #4f46e5;
                width: 0;
                height: 0;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                selection-background-color: #4f46e5;
                selection-color: white;
                outline: 0;
            }
        """)
        self.campoNombre.setMinimumHeight(45)
        self.campoNombre.setCurrentIndex(-1)
        layoutCampos.addWidget(self.campoNombre, 1)
        layoutVertical.addLayout(layoutCampos)

        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        separador.setStyleSheet("background-color: #e5e7eb; max-height: 2px;")
        layoutVertical.addWidget(separador)

        tituloPermisos = QLabel("Permisos de Acción por Subsección")
        tituloPermisos.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #374151;
            padding: 5px 0;
            background-color: #f8fafc;
            border-radius: 8px;
            padding: 15px;
        """)
        tituloPermisos.setAlignment(Qt.AlignCenter)
        layoutVertical.addWidget(tituloPermisos)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                background-color: #f8fafc;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #f8fafc;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(25, 25, 25, 25)

        checkbox_style = """
            QCheckBox {
                font-size: 14px;
                color: #374151;
                spacing: 10px;
                padding: 8px;
                background-color: white;
                border-radius: 6px;
            }
            QCheckBox:hover {
                background-color: #f1f5f9;
                border: 1px solid #4f46e5;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border: 2px solid #94a3b8;
                border-radius: 6px;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #4f46e5;
            }
            QCheckBox::indicator:checked {
                background-color: #4f46e5;
                border: 2px solid #4f46e5;
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTkgMTYuMTdMNC44MyAxMmwtMS40MiAxLjQxTDkgMTkgMjEgN2wtMS40MS0xLjQxTDkgMTYuMTd6Ii8+PC9zdmc+);
                background-repeat: no-repeat;
                background-position: center;
            }
        """

        self.pantallas = self.obtener_pantallas_con_subpantallas()

        for id_pant, pantalla in self.pantallas.items():
            seccion_widget = QWidget()
            seccion_widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 12px;
                    border: 1px solid #e2e8f0;
                }
            """)
            seccion_layout = QVBoxLayout(seccion_widget)
            seccion_layout.setSpacing(12)

            header_seccion = QHBoxLayout()

            titulo_seccion = QLabel(f"📌 {pantalla['nombre']}")
            titulo_seccion.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #1e293b;
                background-color: #e2e8f0;
                padding: 12px 15px;
                border-radius: 8px;
                margin: 5px;
            """)
            header_seccion.addWidget(titulo_seccion, 1)

            btn_seleccionar_todas = QPushButton("✓ Seleccionar Todas")
            btn_seleccionar_todas.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            btn_seleccionar_todas.setCursor(Qt.PointingHandCursor)
            btn_seleccionar_todas.clicked.connect(
                lambda checked, pid=id_pant: self.seleccionar_todas_seccion(pid, True)
            )
            header_seccion.addWidget(btn_seleccionar_todas)

            btn_deseleccionar_todas = QPushButton("✗ Deseleccionar Todas")
            btn_deseleccionar_todas.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            btn_deseleccionar_todas.setCursor(Qt.PointingHandCursor)
            btn_deseleccionar_todas.clicked.connect(
                lambda checked, pid=id_pant: self.seleccionar_todas_seccion(pid, False)
            )
            header_seccion.addWidget(btn_deseleccionar_todas)

            seccion_layout.addLayout(header_seccion)

            grid_sub = QGridLayout()
            grid_sub.setSpacing(15)
            grid_sub.setContentsMargins(20, 15, 20, 15)

            self.checkboxes[id_pant] = []

            for i, sub in enumerate(pantalla['subpantallas']):
                checkbox = QCheckBox(sub['nombre'])
                checkbox.setStyleSheet(checkbox_style)
                checkbox.setProperty("idSubPant", sub['id'])
                self.checkboxes[id_pant].append(checkbox)

                fila = i // 2
                columna = i % 2
                grid_sub.addWidget(checkbox, fila, columna)

            seccion_layout.addLayout(grid_sub)
            scroll_layout.addWidget(seccion_widget)

        scroll_area.setWidget(scroll_content)
        layoutVertical.addWidget(scroll_area, 1)

        layoutBotones = QHBoxLayout()
        layoutBotones.setSpacing(30)
        layoutBotones.setContentsMargins(100, 20, 100, 20)

        botonSubir = QPushButton("Registrar Cargo")
        botonSubir.clicked.connect(self.subirDatos)

        botonCancelar = QPushButton("Cancelar")
        botonCancelar.clicked.connect(self.limpiarTodo)

        button_style = """
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 14px 28px;
                font-size: 16px;
                font-weight: 500;
            }
        """

        botonSubir.setStyleSheet(
            button_style
            + """
            QPushButton {
                background-color: #4f46e5;
                color: white;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
        """
        )

        botonCancelar.setStyleSheet(
            button_style
            + """
            QPushButton {
                background-color: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
            QPushButton:pressed {
                background-color: #d1d5db;
            }
        """
        )

        for btn in [botonSubir, botonCancelar]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumSize(180, 50)
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            layoutBotones.addWidget(btn)

        layoutVertical.addLayout(layoutBotones)

    def subirDatos(self):
        if not os.path.exists(DB_PATH):
            QMessageBox.critical(
                self, "Error de base de datos", f"No se encontró la base de datos en la ruta:\n{DB_PATH}"
            )
            return

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            c = conn.cursor()

            nuevoCargo = self.campoNombre.currentText().strip()
            if not nuevoCargo:
                QMessageBox.warning(self, "Advertencia", "El nombre del cargo no puede estar vacío")
                return

            subpantallas_seleccionadas = []
            for id_pant, checkboxes in self.checkboxes.items():
                for cb in checkboxes:
                    if cb.isChecked():
                        id_sub = cb.property("idSubPant")
                        subpantallas_seleccionadas.append(id_sub)

            if len(subpantallas_seleccionadas) == 0:
                QMessageBox.information(self, "Advertencia", "Se debe dar acceso por lo menos a una subsección")
                return

            conn.execute("BEGIN TRANSACTION")

            c.execute("INSERT INTO Cargo(nomCarg) VALUES(?)", (nuevoCargo,))
            id_cargo = c.lastrowid

            for id_sub in subpantallas_seleccionadas:
                c.execute("INSERT INTO PermisosCargoSubpantalla(idCarg, idSubPant) VALUES(?, ?)", (id_cargo, id_sub))

            conn.commit()

            QMessageBox.information(
                self,
                "Operación exitosa",
                f"El cargo '{nuevoCargo}' se registró correctamente con {len(subpantallas_seleccionadas)} permisos",
            )
            self.limpiarTodo()

        except sqlite3.IntegrityError:
            if conn:
                conn.rollback()
            QMessageBox.critical(self, "Error", "Este cargo ya existe en la base de datos")
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            QMessageBox.critical(self, "Error de base de datos", f"No se pudo completar la operación:\n{str(e)}")
        except Exception as e:
            if conn:
                conn.rollback()
            QMessageBox.critical(self, "Error inesperado", f"Ocurrió un error no previsto:\n{str(e)}")
        finally:
            if conn:
                conn.close()

    def limpiarTodo(self):
        self.campoNombre.setCurrentIndex(-1)
        for id_pant, checkboxes in self.checkboxes.items():
            for checkbox in checkboxes:
                checkbox.setChecked(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = RegistroCargos()
    pagina.show()
    sys.exit(app.exec_())
