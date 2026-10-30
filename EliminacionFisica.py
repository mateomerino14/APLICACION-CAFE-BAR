from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from Rutas import get_db_path

DB_PATH = get_db_path()


class EliminacionFisica(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Eliminación Física de Registros")
        self.setFixedSize(1200, 750)

        self.tablas = {}
        self.filtros_estado = {}
        self.dependencias_info = {}

        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QTabWidget::pane {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #e2e8f0;
                padding: 12px 25px;
                margin-right: 2px;
                font-weight: bold;
                font-size: 14px;
                min-width: 110px;
            }
            QTabBar::tab:selected {
                background: #e74c3c;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #cbd5e1;
            }
            QTabBar::tab:!selected {
                color: #2c3e50;
            }
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-size: 13px;
                gridline-color: #e2e8f0;
            }
            QTableWidget::item {
                padding: 0px;
                min-height: 35px;
            }
            QHeaderView::section {
                background: #34495e;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                font-size: 13px;
                min-height: 35px;
            }
            QCheckBox {
                spacing: 8px;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 4px;
                border: 2px solid #cbd5e1;
            }
            QCheckBox::indicator:checked {
                background-color: #e74c3c;
                border-color: #c0392b;
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTE5IDYuNDFMMTcuNTkgNSAxMiAxMC41OSA2LjQxIDUgNSA2LjQxIDEwLjU5IDEyIDUgMTcuNTkgNi40MSAxOSAxMiAxMy40MSAxNy41OSAxOSAxOSAxNy41OSAxMy40MSAxMiAxOSA2LjQxeiIvPjwvc3ZnPg==);
                background-repeat: no-repeat;
                background-position: center;
            }
            QPushButton {
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 140px;
                border: none;
            }
            QPushButton#eliminar {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton#eliminar:hover {
                background-color: #c0392b;
            }
            QPushButton#cancelar {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton#cancelar:hover {
                background-color: #7f8c8d;
            }
            QPushButton#seleccionar {
                background-color: #3498db;
                color: white;
            }
            QPushButton#seleccionar:hover {
                background-color: #2980b9;
            }
            QPushButton#filtro {
                background-color: #f39c12;
                color: white;
                min-width: 100px;
                padding: 8px 16px;
            }
            QPushButton#filtro:hover {
                background-color: #e67e22;
            }
            QLabel#warning {
                background-color: #fef3c7;
                color: #92400e;
                padding: 15px 20px;
                border-radius: 8px;
                border: 1px solid #fbbf24;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        warning_label = QLabel(
            "⚠️  ATENCIÓN: Esta acción es IRREVERSIBLE. Los registros eliminados NO podrán recuperarse. Asegúrese de tener un backup antes de continuar."
        )
        warning_label.setObjectName("warning")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        self.tabs = QTabWidget()

        self.tab_empleados = self.crear_tab_empleados()
        self.tab_cargos = self.crear_tab_cargos()
        self.tab_secciones = self.crear_tab_secciones()
        self.tab_ventas = self.crear_tab_ventas()

        self.tabs.addTab(self.tab_empleados, "Empleados")
        self.tabs.addTab(self.tab_cargos, "Cargos")
        self.tabs.addTab(self.tab_secciones, "Secciones")
        self.tabs.addTab(self.tab_ventas, "Ventas")

        layout.addWidget(self.tabs)

        botones_layout = QHBoxLayout()
        botones_layout.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("cancelar")
        btn_cancelar.clicked.connect(self.reject)

        btn_eliminar = QPushButton("Eliminar Seleccionados")
        btn_eliminar.setObjectName("eliminar")
        btn_eliminar.clicked.connect(self.eliminar_seleccionados)

        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(btn_eliminar)

        layout.addLayout(botones_layout)

    def ajustar_tabla(self, tabla):
        tabla.setSelectionMode(QTableWidget.NoSelection)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.verticalHeader().setVisible(False)
        tabla.horizontalHeader().setStretchLastSection(True)

        total_ancho = tabla.viewport().width()
        num_columnas = tabla.columnCount()

        if num_columnas > 1:
            ancho_checkbox = 50
            ancho_restante = total_ancho - ancho_checkbox
            ancho_por_columna = ancho_restante // (num_columnas - 1)

            tabla.setColumnWidth(0, ancho_checkbox)
            for i in range(1, num_columnas):
                tabla.setColumnWidth(i, ancho_por_columna)

    def crear_filtros_estado(self, tab, tipo, callback):
        filtros_layout = QHBoxLayout()

        btn_todas = QPushButton("Todas")
        btn_todas.setObjectName("filtro")
        btn_todas.clicked.connect(lambda: callback("todas"))

        btn_activas = QPushButton("Activas")
        btn_activas.setObjectName("filtro")
        btn_activas.clicked.connect(lambda: callback("activas"))

        btn_inactivas = QPushButton("Inactivas")
        btn_inactivas.setObjectName("filtro")
        btn_inactivas.clicked.connect(lambda: callback("inactivas"))

        filtros_layout.addWidget(QLabel("Filtrar por estado:"))
        filtros_layout.addWidget(btn_todas)
        filtros_layout.addWidget(btn_activas)
        filtros_layout.addWidget(btn_inactivas)
        filtros_layout.addStretch()

        return filtros_layout

    def crear_tab_empleados(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.filtros_estado["empleados"] = "todas"

        filtros_estado = self.crear_filtros_estado(
            tab, "empleados", lambda estado: self.aplicar_filtro_empleados(estado)
        )
        layout.addLayout(filtros_estado)

        filtros_seleccion = QHBoxLayout()

        btn_todos = QPushButton("Seleccionar Todos")
        btn_todos.setObjectName("seleccionar")

        btn_ninguno = QPushButton("Deseleccionar Todos")
        btn_ninguno.setObjectName("seleccionar")

        btn_invertir = QPushButton("Invertir Selección")
        btn_invertir.setObjectName("seleccionar")

        filtros_seleccion.addWidget(btn_todos)
        filtros_seleccion.addWidget(btn_ninguno)
        filtros_seleccion.addWidget(btn_invertir)
        filtros_seleccion.addStretch()
        layout.addLayout(filtros_seleccion)

        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels(["", "Código", "Nombre Completo", "Alias", "CI", "Cargo", "Disponible"])

        btn_todos.clicked.connect(lambda: self.seleccionar_todos_en_tabla(tabla, True))
        btn_ninguno.clicked.connect(lambda: self.seleccionar_todos_en_tabla(tabla, False))
        btn_invertir.clicked.connect(lambda: self.invertir_seleccion_en_tabla(tabla))

        self.tablas["empleados"] = tabla
        self.cargar_empleados(tabla)

        layout.addWidget(tabla)

        QTimer.singleShot(100, lambda: self.ajustar_tabla(tabla))
        return tab

    def cargar_empleados(self, tabla):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        query = """
            SELECT e.codEmp, e.nomEmp, e.apellPatEmp, e.apellMatEmp, e.aliasEmp, 
                   e.ciEmp, c.nomCarg, e.disponibleEmp
            FROM Empleado e
            LEFT JOIN Cargo c ON e.idCargo = c.idCargo
        """

        filtro = self.filtros_estado.get("empleados", "todas")
        if filtro == "activas":
            query += " WHERE e.disponibleEmp = 1"
        elif filtro == "inactivas":
            query += " WHERE e.disponibleEmp = 0"

        query += " ORDER BY e.nomEmp COLLATE NOCASE"

        cur.execute(query)
        empleados = cur.fetchall()
        conn.close()

        tabla.setRowCount(0)
        tabla.setRowCount(len(empleados))

        for i, (cod, nom, pat, mat, alias, ci, cargo, disponible) in enumerate(empleados):
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            tabla.setCellWidget(i, 0, checkbox_widget)

            nombre_completo = f"{nom} {pat} {mat}".strip()
            estado = "Sí" if disponible else "No"

            items = [cod, nombre_completo, alias, ci, cargo or "Sin cargo", estado]
            for j, valor in enumerate(items):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                if not disponible:
                    item.setForeground(QColor(150, 150, 150))
                tabla.setItem(i, j + 1, item)

    def aplicar_filtro_empleados(self, estado):
        self.filtros_estado["empleados"] = estado
        self.cargar_empleados(self.tablas["empleados"])
        self.ajustar_tabla(self.tablas["empleados"])

    def crear_tab_cargos(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        filtros_seleccion = QHBoxLayout()

        btn_todos = QPushButton("Seleccionar Todos")
        btn_todos.setObjectName("seleccionar")

        btn_ninguno = QPushButton("Deseleccionar Todos")
        btn_ninguno.setObjectName("seleccionar")

        btn_invertir = QPushButton("Invertir Selección")
        btn_invertir.setObjectName("seleccionar")

        filtros_seleccion.addWidget(btn_todos)
        filtros_seleccion.addWidget(btn_ninguno)
        filtros_seleccion.addWidget(btn_invertir)
        filtros_seleccion.addStretch()
        layout.addLayout(filtros_seleccion)

        tabla = QTableWidget()
        tabla.setColumnCount(4)
        tabla.setHorizontalHeaderLabels(["", "ID", "Nombre del Cargo", "Empleados"])

        btn_todos.clicked.connect(lambda: self.seleccionar_todos_en_tabla(tabla, True))
        btn_ninguno.clicked.connect(lambda: self.seleccionar_todos_en_tabla(tabla, False))
        btn_invertir.clicked.connect(lambda: self.invertir_seleccion_en_tabla(tabla))

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT c.idCargo, c.nomCarg, COUNT(e.codEmp) as num_empleados
            FROM Cargo c
            LEFT JOIN Empleado e ON c.idCargo = e.idCargo
            GROUP BY c.idCargo, c.nomCarg
            ORDER BY c.nomCarg COLLATE NOCASE
        """)
        cargos = cur.fetchall()
        conn.close()

        tabla.setRowCount(len(cargos))
        for i, (id_carg, nombre, num_empleados) in enumerate(cargos):
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            tabla.setCellWidget(i, 0, checkbox_widget)

            items = [id_carg, nombre, str(num_empleados)]
            for j, valor in enumerate(items):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                if num_empleados > 0:
                    item.setBackground(QColor(254, 226, 226))
                    item.setForeground(QColor(220, 38, 38))
                    item.setToolTip(f"⚠️ Este cargo tiene {num_empleados} empleado(s) asignado(s)")
                tabla.setItem(i, j + 1, item)

        layout.addWidget(tabla)
        self.tablas["cargos"] = tabla

        QTimer.singleShot(100, lambda: self.ajustar_tabla(tabla))
        return tab

    def crear_tab_secciones(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        filtros_seleccion = QHBoxLayout()

        btn_todos = QPushButton("Seleccionar Todas")
        btn_todos.setObjectName("seleccionar")

        btn_ninguno = QPushButton("Deseleccionar Todas")
        btn_ninguno.setObjectName("seleccionar")

        btn_invertir = QPushButton("Invertir Selección")
        btn_invertir.setObjectName("seleccionar")

        filtros_seleccion.addWidget(btn_todos)
        filtros_seleccion.addWidget(btn_ninguno)
        filtros_seleccion.addWidget(btn_invertir)
        filtros_seleccion.addStretch()
        layout.addLayout(filtros_seleccion)

        tabla = QTableWidget()
        tabla.setColumnCount(5)
        tabla.setHorizontalHeaderLabels(["", "ID", "Nombre", "Mesas", "Ventas Asociadas"])

        btn_todos.clicked.connect(lambda: self.seleccionar_todos_en_tabla(tabla, True))
        btn_ninguno.clicked.connect(lambda: self.seleccionar_todos_en_tabla(tabla, False))
        btn_invertir.clicked.connect(lambda: self.invertir_seleccion_en_tabla(tabla))

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT s.idSeccion, s.nombSeccion, 
                   COUNT(DISTINCT m.idMesa) as num_mesas,
                   COUNT(DISTINCT v.numVenta) as num_ventas
            FROM Seccion s
            LEFT JOIN Mesa m ON s.idSeccion = m.idSeccion AND m.existe = 1
            LEFT JOIN Venta v ON s.idSeccion = v.idSeccion
            GROUP BY s.idSeccion, s.nombSeccion
            ORDER BY s.nombSeccion COLLATE NOCASE
        """)
        secciones = cur.fetchall()
        conn.close()

        tabla.setRowCount(len(secciones))
        for i, (id_sec, nombre, num_mesas, num_ventas) in enumerate(secciones):
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            tabla.setCellWidget(i, 0, checkbox_widget)

            items = [id_sec, nombre, str(num_mesas), str(num_ventas)]
            for j, valor in enumerate(items):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                if num_mesas > 0 or num_ventas > 0:
                    item.setBackground(QColor(254, 226, 226))
                    item.setForeground(QColor(220, 38, 38))
                    tooltip = ""
                    if num_mesas > 0:
                        tooltip += f"⚠️ {num_mesas} mesa(s) asociada(s). "
                    if num_ventas > 0:
                        tooltip += f"⚠️ {num_ventas} venta(s) asociada(s)."
                    item.setToolTip(tooltip)
                tabla.setItem(i, j + 1, item)

        layout.addWidget(tabla)
        self.tablas["secciones"] = tabla

        QTimer.singleShot(100, lambda: self.ajustar_tabla(tabla))
        return tab

    def crear_tab_ventas(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        filtros_seleccion = QHBoxLayout()

        btn_todos = QPushButton("Seleccionar Todas")
        btn_todos.setObjectName("seleccionar")

        btn_ninguno = QPushButton("Deseleccionar Todas")
        btn_ninguno.setObjectName("seleccionar")

        btn_invertir = QPushButton("Invertir Selección")
        btn_invertir.setObjectName("seleccionar")

        filtros_seleccion.addWidget(btn_todos)
        filtros_seleccion.addWidget(btn_ninguno)
        filtros_seleccion.addWidget(btn_invertir)
        filtros_seleccion.addStretch()
        layout.addLayout(filtros_seleccion)

        tabla = QTableWidget()
        tabla.setColumnCount(8)
        tabla.setHorizontalHeaderLabels(["", "N° Venta", "Fecha", "Hora", "Total", "Mesa", "Sección", "Estado"])

        btn_todos.clicked.connect(lambda: self.seleccionar_todos_en_tabla(tabla, True))
        btn_ninguno.clicked.connect(lambda: self.seleccionar_todos_en_tabla(tabla, False))
        btn_invertir.clicked.connect(lambda: self.invertir_seleccion_en_tabla(tabla))

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            SELECT v.numVenta, v.fechaReg, v.horaReg, v.totalVenta, 
                   v.idMesa, s.nombSeccion,
                   CASE 
                       WHEN NOT EXISTS (
                           SELECT 1 FROM DetallesVenta d 
                           WHERE d.numVenta = v.numVenta 
                           AND d.fechaRegVenta = v.fechaReg
                           AND d.estadoDetalleVenta != 'Finalizado'
                       ) THEN 'Finalizada'
                       WHEN EXISTS (
                           SELECT 1 FROM DetallesVenta d 
                           WHERE d.numVenta = v.numVenta 
                           AND d.fechaRegVenta = v.fechaReg
                           AND d.estadoDetalleVenta = 'Preparacion'
                       ) AND EXISTS (
                           SELECT 1 FROM DetallesVenta d 
                           WHERE d.numVenta = v.numVenta 
                           AND d.fechaRegVenta = v.fechaReg
                           AND d.estadoDetalleVenta = 'Cobrar'
                       ) THEN 'Mixta'
                       WHEN EXISTS (
                           SELECT 1 FROM DetallesVenta d 
                           WHERE d.numVenta = v.numVenta 
                           AND d.fechaRegVenta = v.fechaReg
                           AND d.estadoDetalleVenta = 'Preparacion'
                       ) THEN 'En Preparación'
                       WHEN EXISTS (
                           SELECT 1 FROM DetallesVenta d 
                           WHERE d.numVenta = v.numVenta 
                           AND d.fechaRegVenta = v.fechaReg
                           AND d.estadoDetalleVenta = 'Cobrar'
                       ) THEN 'Por Cobrar'
                       ELSE 'Pendiente'
                   END as estado
            FROM Venta v
            LEFT JOIN Seccion s ON v.idSeccion = s.idSeccion
            ORDER BY v.fechaReg DESC, v.horaReg DESC
            LIMIT 500
        """)
        ventas = cur.fetchall()
        conn.close()

        tabla.setRowCount(len(ventas))
        for i, (num, fecha, hora, total, mesa, seccion, estado) in enumerate(ventas):
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            tabla.setCellWidget(i, 0, checkbox_widget)

            fecha_formateada = fecha[:10] if fecha else ""
            mesa_str = str(mesa) if mesa else "N/A"
            seccion_str = seccion if seccion else "N/A"

            items = [num, fecha_formateada, hora, f"{total:.2f} Bs", mesa_str, seccion_str, estado]
            for j, valor in enumerate(items):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                if estado == "Finalizada":
                    item.setBackground(QColor(230, 255, 230))
                elif estado == "En Preparación":
                    item.setBackground(QColor(255, 255, 200))
                elif estado == "Por Cobrar":
                    item.setBackground(QColor(200, 230, 255))
                elif estado == "Mixta":
                    item.setBackground(QColor(240, 210, 255))
                tabla.setItem(i, j + 1, item)

        layout.addWidget(tabla)
        self.tablas["ventas"] = tabla

        QTimer.singleShot(100, lambda: self.ajustar_tabla(tabla))
        return tab

    def resizeEvent(self, event):
        super().resizeEvent(event)
        for tabla in self.tablas.values():
            self.ajustar_tabla(tabla)

    def seleccionar_todos_en_tabla(self, tabla, estado):
        for i in range(tabla.rowCount()):
            checkbox_widget = tabla.cellWidget(i, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.layout().itemAt(0).widget()
                checkbox.setChecked(estado)

    def invertir_seleccion_en_tabla(self, tabla):
        for i in range(tabla.rowCount()):
            checkbox_widget = tabla.cellWidget(i, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.layout().itemAt(0).widget()
                checkbox.setChecked(not checkbox.isChecked())

    def obtener_registros_seleccionados(self):
        seleccionados = {
            "empleados": [],
            "cargos": [],
            "secciones": [],
            "ventas": [],
        }

        for tipo, tabla in self.tablas.items():
            for i in range(tabla.rowCount()):
                checkbox_widget = tabla.cellWidget(i, 0)
                if checkbox_widget and checkbox_widget.layout().itemAt(0).widget().isChecked():
                    id_registro = tabla.item(i, 1).text()
                    nombre = tabla.item(i, 2).text() if tabla.item(i, 2) else ""
                    seleccionados[tipo].append((id_registro, nombre))

        return seleccionados

    def obtener_arbol_dependencias(self, seleccionados):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        arbol = {
            "directos": seleccionados.copy(),
            "dependientes": {
                "empleados": [],
                "cargos": [],
                "secciones": [],
                "ventas": [],
                "mesas": [],
                "pagos": [],
                "detalles_venta": [],
                "permisos": [],
            },
            "resumen": {},
        }

        for id_reg, nombre in seleccionados["cargos"]:
            cur.execute("SELECT codEmp, aliasEmp FROM Empleado WHERE idCargo = ?", (id_reg,))
            empleados = cur.fetchall()
            for emp in empleados:
                arbol["dependientes"]["empleados"].append((str(emp[0]), emp[1]))

        for id_reg, nombre in seleccionados["secciones"]:
            cur.execute("SELECT idMesa FROM Mesa WHERE idSeccion = ?", (id_reg,))
            mesas = cur.fetchall()
            for mesa in mesas:
                arbol["dependientes"]["mesas"].append((str(mesa[0]), f"Mesa {mesa[0]}"))

            cur.execute("SELECT numVenta FROM Venta WHERE idSeccion = ?", (id_reg,))
            ventas = cur.fetchall()
            for venta in ventas:
                arbol["dependientes"]["ventas"].append((str(venta[0]), f"Venta {venta[0]}"))

        for id_reg, nombre in seleccionados["ventas"]:
            cur.execute("SELECT idMetodo, monto FROM Pago WHERE numVenta = ?", (id_reg,))
            pagos = cur.fetchall()
            for pago in pagos:
                arbol["dependientes"]["pagos"].append((str(pago[0]), f"Pago {pago[0]}"))

            cur.execute("SELECT idDetalleVenta FROM DetallesVenta WHERE numVenta = ?", (id_reg,))
            detalles = cur.fetchall()
            for det in detalles:
                arbol["dependientes"]["detalles_venta"].append((str(det[0]), f"Detalle {det[0]}"))

        for id_reg, nombre in seleccionados["empleados"]:
            cur.execute("SELECT numVenta FROM Venta WHERE codEmp = ? OR codEmp2 = ?", (id_reg, id_reg))
            ventas = cur.fetchall()
            for venta in ventas:
                arbol["dependientes"]["ventas"].append((str(venta[0]), f"Venta {venta[0]}"))

            cur.execute("SELECT idDetalleVenta FROM DetallesVenta WHERE idMeseroActual = ?", (id_reg,))
            detalles = cur.fetchall()
            for det in detalles:
                arbol["dependientes"]["detalles_venta"].append((str(det[0]), f"Detalle {det[0]}"))

            cur.execute("SELECT idPant FROM PermisosPersonal WHERE codEmp = ?", (id_reg,))
            permisos = cur.fetchall()
            for perm in permisos:
                arbol["dependientes"]["permisos"].append((str(perm[0]), f"Permiso Pantalla {perm[0]}"))

            cur.execute("SELECT idSubPant FROM PermisosPersonalSubpantalla WHERE codEmp = ?", (id_reg,))
            permisos_sub = cur.fetchall()
            for perm in permisos_sub:
                arbol["dependientes"]["permisos"].append((str(perm[0]), f"Permiso Subpantalla {perm[0]}"))

        conn.close()

        arbol["resumen"] = {
            "empleados_directos": len(seleccionados["empleados"]),
            "empleados_dependientes": len(arbol["dependientes"]["empleados"]),
            "cargos_directos": len(seleccionados["cargos"]),
            "secciones_directas": len(seleccionados["secciones"]),
            "ventas_directas": len(seleccionados["ventas"]),
            "ventas_dependientes": len(arbol["dependientes"]["ventas"]),
            "mesas_dependientes": len(arbol["dependientes"]["mesas"]),
            "pagos_dependientes": len(arbol["dependientes"]["pagos"]),
            "detalles_dependientes": len(arbol["dependientes"]["detalles_venta"]),
            "permisos_dependientes": len(arbol["dependientes"]["permisos"]),
        }

        return arbol

    def generar_mensaje_confirmacion(self, arbol):
        mensaje = "⚠️ ¿Está SEGURO que desea ELIMINAR PERMANENTEMENTE los siguientes registros?\n\n"

        if arbol["directos"]["empleados"]:
            mensaje += f"📌 EMPLEADOS: {len(arbol['directos']['empleados'])} registro(s)\n"
            for i, (id_reg, nombre) in enumerate(arbol["directos"]["empleados"][:5]):
                mensaje += f"   • {nombre} (ID: {id_reg})\n"
            if len(arbol["directos"]["empleados"]) > 5:
                mensaje += f"   ... y {len(arbol['directos']['empleados']) - 5} más\n"
            mensaje += "\n"

        if arbol["directos"]["cargos"]:
            mensaje += f"📌 CARGOS: {len(arbol['directos']['cargos'])} registro(s)\n"
            for i, (id_reg, nombre) in enumerate(arbol["directos"]["cargos"][:5]):
                mensaje += f"   • {nombre} (ID: {id_reg})\n"
            if len(arbol["directos"]["cargos"]) > 5:
                mensaje += f"   ... y {len(arbol['directos']['cargos']) - 5} más\n"
            mensaje += "\n"

        if arbol["directos"]["secciones"]:
            mensaje += f"📌 SECCIONES: {len(arbol['directos']['secciones'])} registro(s)\n"
            for i, (id_reg, nombre) in enumerate(arbol["directos"]["secciones"][:5]):
                mensaje += f"   • {nombre} (ID: {id_reg})\n"
            if len(arbol["directos"]["secciones"]) > 5:
                mensaje += f"   ... y {len(arbol['directos']['secciones']) - 5} más\n"
            mensaje += "\n"

        if arbol["directos"]["ventas"]:
            mensaje += f"📌 VENTAS: {len(arbol['directos']['ventas'])} registro(s)\n"
            for i, (id_reg, nombre) in enumerate(arbol["directos"]["ventas"][:5]):
                mensaje += f"   • Venta N° {id_reg}\n"
            if len(arbol["directos"]["ventas"]) > 5:
                mensaje += f"   ... y {len(arbol['directos']['ventas']) - 5} más\n"
            mensaje += "\n"

        total_dependientes = sum(
            [
                arbol["resumen"]["empleados_dependientes"],
                arbol["resumen"]["ventas_dependientes"],
                arbol["resumen"]["mesas_dependientes"],
                arbol["resumen"]["pagos_dependientes"],
                arbol["resumen"]["detalles_dependientes"],
                arbol["resumen"]["permisos_dependientes"],
            ]
        )

        if total_dependientes > 0:
            mensaje += "📋 REGISTROS DEPENDIENTES QUE SE ELIMINARÁN EN CASCADA:\n"
            if arbol["resumen"]["empleados_dependientes"] > 0:
                mensaje += f"   • {arbol['resumen']['empleados_dependientes']} empleado(s) por cargos eliminados\n"
            if arbol["resumen"]["ventas_dependientes"] > 0:
                mensaje += f"   • {arbol['resumen']['ventas_dependientes']} venta(s) relacionadas\n"
            if arbol["resumen"]["mesas_dependientes"] > 0:
                mensaje += f"   • {arbol['resumen']['mesas_dependientes']} mesa(s) por secciones eliminadas\n"
            if arbol["resumen"]["pagos_dependientes"] > 0:
                mensaje += f"   • {arbol['resumen']['pagos_dependientes']} pago(s) asociados\n"
            if arbol["resumen"]["detalles_dependientes"] > 0:
                mensaje += f"   • {arbol['resumen']['detalles_dependientes']} detalle(s) de venta\n"
            if arbol["resumen"]["permisos_dependientes"] > 0:
                mensaje += f"   • {arbol['resumen']['permisos_dependientes']} permiso(s)\n"
            mensaje += "\n"

        mensaje += "⚠️ ESTA ACCIÓN NO SE PUEDE DESHACER ⚠️"
        return mensaje

    def eliminar_seleccionados(self):
        seleccionados = self.obtener_registros_seleccionados()

        total_seleccionados = sum(len(v) for v in seleccionados.values())
        if total_seleccionados == 0:
            QMessageBox.warning(self, "Advertencia", "No hay registros seleccionados para eliminar.")
            return

        arbol_dependencias = self.obtener_arbol_dependencias(seleccionados)
        mensaje_confirmacion = self.generar_mensaje_confirmacion(arbol_dependencias)

        confirm = QMessageBox.question(
            self, "Confirmar Eliminación Definitiva", mensaje_confirmacion, QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        errores = []
        eliminados = 0

        def condicion_ventas_por_par(pares):
            """
            pares: lista de (numVenta, fecha 'YYYY-MM-DD').
            numVenta se reinicia cada dia (no es un identificador global unico),
            asi que SIEMPRE hay que filtrar por numVenta + fecha juntos. Filtrar
            solo por numVenta borraria tambien ventas de otros dias que por
            coincidencia comparten el mismo numero.
            """
            condiciones = []
            params = []
            for numVenta, fecha in pares:
                condiciones.append("(V.numVenta=? AND DATE(V.fechaReg)=?)")
                params.extend([numVenta, fecha])
            return (" OR ".join(condiciones) if condiciones else "0=1"), params

        def borrar_cascada_por_pares(pares):
            if not pares:
                return
            condicion, params = condicion_ventas_por_par(pares)

            mesas_a_liberar = cur.execute(
                f"""
                SELECT DISTINCT idMesa, idSeccion FROM Venta AS V
                WHERE ({condicion}) AND idMesa IS NOT NULL AND idMesa > 0
            """,
                params,
            ).fetchall()

            cur.execute(
                f"""
                DELETE FROM DetallesVentaUnidades
                WHERE idDetalleVenta IN (
                    SELECT DV.idDetalleVenta FROM DetallesVenta DV
                    JOIN Venta V ON DV.numVenta = V.numVenta AND DV.fechaRegVenta = V.fechaReg
                    WHERE {condicion}
                )
            """,
                params,
            )
            cur.execute(
                f"""
                DELETE FROM DetallesVentaExclusionesPromo
                WHERE idDetalleVenta IN (
                    SELECT DV.idDetalleVenta FROM DetallesVenta DV
                    JOIN Venta V ON DV.numVenta = V.numVenta AND DV.fechaRegVenta = V.fechaReg
                    WHERE {condicion}
                )
            """,
                params,
            )
            cur.execute(
                f"""
                DELETE FROM DetallesVentaExclusiones
                WHERE idDetalleVenta IN (
                    SELECT DV.idDetalleVenta FROM DetallesVenta DV
                    JOIN Venta V ON DV.numVenta = V.numVenta AND DV.fechaRegVenta = V.fechaReg
                    WHERE {condicion}
                )
            """,
                params,
            )
            cur.execute(
                f"""
                DELETE FROM DetallesVentaExtras
                WHERE idDetalleVenta IN (
                    SELECT DV.idDetalleVenta FROM DetallesVenta DV
                    JOIN Venta V ON DV.numVenta = V.numVenta AND DV.fechaRegVenta = V.fechaReg
                    WHERE {condicion}
                )
            """,
                params,
            )
            cur.execute(
                f"""
                DELETE FROM Pago
                WHERE numVenta || '|' || fechaRegVenta IN (
                    SELECT V.numVenta || '|' || V.fechaReg FROM Venta V WHERE {condicion}
                )
            """,
                params,
            )
            cur.execute(
                f"""
                DELETE FROM DetallesVenta
                WHERE idDetalleVenta IN (
                    SELECT DV.idDetalleVenta FROM DetallesVenta DV
                    JOIN Venta V ON DV.numVenta = V.numVenta AND DV.fechaRegVenta = V.fechaReg
                    WHERE {condicion}
                )
            """,
                params,
            )
            cur.execute(
                f"""
                DELETE FROM Venta AS V WHERE {condicion}
            """,
                params,
            )

            for id_mesa, id_seccion in mesas_a_liberar:
                cur.execute(
                    """
                    SELECT COUNT(*) FROM Venta 
                    WHERE idMesa = ? AND idSeccion = ?
                """,
                    (id_mesa, id_seccion),
                )
                count = cur.fetchone()[0]
                if count == 0:
                    cur.execute(
                        """
                        UPDATE Mesa SET disponible = 1
                        WHERE idMesa = ? AND idSeccion = ?
                    """,
                        (id_mesa, id_seccion),
                    )

        def obtener_pares_ventas_de_empleados(lista_ids_empleados):
            placeholders = ','.join('?' * len(lista_ids_empleados))
            filas = cur.execute(
                f"""
                SELECT DISTINCT V.numVenta, DATE(V.fechaReg)
                FROM Venta V
                WHERE V.codEmp IN ({placeholders}) OR V.codEmp2 IN ({placeholders})
            """,
                lista_ids_empleados + lista_ids_empleados,
            ).fetchall()
            filas += cur.execute(
                f"""
                SELECT DISTINCT V.numVenta, DATE(V.fechaReg)
                FROM DetallesVenta DV
                JOIN Venta V ON DV.numVenta = V.numVenta AND DV.fechaRegVenta = V.fechaReg
                WHERE DV.idMeseroActual IN ({placeholders})
            """,
                lista_ids_empleados,
            ).fetchall()
            return list(set(filas))

        try:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("BEGIN TRANSACTION")

            ids_secciones = [id_reg for id_reg, _ in seleccionados["secciones"]]
            ids_cargos = [id_reg for id_reg, _ in seleccionados["cargos"]]
            ids_empleados = [id_reg for id_reg, _ in seleccionados["empleados"]]
            # En ventas la fecha también identifica el registro, no solo numVenta
            pares_ventas_seleccionadas = [(id_reg, fecha) for id_reg, fecha in seleccionados["ventas"]]

            if ids_empleados:
                placeholders = ','.join('?' * len(ids_empleados))
                pares_ventas = obtener_pares_ventas_de_empleados(ids_empleados)
                borrar_cascada_por_pares(pares_ventas)
                cur.execute(f"DELETE FROM PermisosPersonal WHERE codEmp IN ({placeholders})", ids_empleados)
                cur.execute(f"DELETE FROM PermisosPersonalSubpantalla WHERE codEmp IN ({placeholders})", ids_empleados)
                cur.execute(f"DELETE FROM Empleado WHERE codEmp IN ({placeholders})", ids_empleados)
                eliminados += len(ids_empleados)

            if ids_cargos:
                placeholders = ','.join('?' * len(ids_cargos))
                empleados_cargo = cur.execute(
                    f"SELECT codEmp FROM Empleado WHERE idCargo IN ({placeholders})", ids_cargos
                ).fetchall()
                if empleados_cargo:
                    ids_empleados_cargo = [e[0] for e in empleados_cargo]
                    emp_placeholders = ','.join('?' * len(ids_empleados_cargo))
                    pares_ventas = obtener_pares_ventas_de_empleados(ids_empleados_cargo)
                    borrar_cascada_por_pares(pares_ventas)
                    cur.execute(
                        f"DELETE FROM PermisosPersonal WHERE codEmp IN ({emp_placeholders})", ids_empleados_cargo
                    )
                    cur.execute(
                        f"DELETE FROM PermisosPersonalSubpantalla WHERE codEmp IN ({emp_placeholders})",
                        ids_empleados_cargo,
                    )
                    cur.execute(f"DELETE FROM Empleado WHERE idCargo IN ({placeholders})", ids_cargos)
                cur.execute(f"DELETE FROM PermisosCargo WHERE idCarg IN ({placeholders})", ids_cargos)
                cur.execute(f"DELETE FROM PermisosCargoSubpantalla WHERE idCarg IN ({placeholders})", ids_cargos)
                cur.execute(f"DELETE FROM Cargo WHERE idCargo IN ({placeholders})", ids_cargos)
                eliminados += len(ids_cargos)

            if ids_secciones:
                placeholders = ','.join('?' * len(ids_secciones))
                pares_ventas = cur.execute(
                    f"""
                    SELECT DISTINCT numVenta, DATE(fechaReg) FROM Venta
                    WHERE idSeccion IN ({placeholders})
                """,
                    ids_secciones,
                ).fetchall()
                borrar_cascada_por_pares(pares_ventas)
                cur.execute(f"DELETE FROM Mesa WHERE idSeccion IN ({placeholders})", ids_secciones)
                cur.execute(f"DELETE FROM Seccion WHERE idSeccion IN ({placeholders})", ids_secciones)
                eliminados += len(ids_secciones)

            if pares_ventas_seleccionadas:
                borrar_cascada_por_pares(pares_ventas_seleccionadas)
                eliminados += len(pares_ventas_seleccionadas)

            conn.commit()

            if errores:
                QMessageBox.warning(
                    self,
                    "Eliminación con Advertencias",
                    f"Se eliminaron {eliminados} registros principales.\n\nProblemas encontrados:\n"
                    + "\n".join(errores[:10]),
                )
            else:
                QMessageBox.information(
                    self,
                    "Eliminación Completada",
                    f"Se eliminaron {eliminados} registros principales y todos sus dependientes correctamente.",
                )

            self.accept()

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo completar la eliminación:\n{str(e)}")
        finally:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.close()
