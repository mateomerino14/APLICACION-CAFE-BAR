import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
import pandas as pd
from datetime import datetime
import smtplib
import shutil
import zipfile
import tempfile
from EliminacionFisica import EliminacionFisica
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from nucleo.SeguridadUtils import hashear_password, verificar_password
from nucleo.Rutas import get_db_path

DB_PATH = get_db_path()


class Configuracion(QWidget):
    def __init__(self):
        super().__init__()
        self._ensure_configuracion_sistema()
        self.mapaIDs = {}
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton {
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                border: none;
            }
            
            QPushButton:hover { 
                opacity: 0.9; 
            }
            QPushButton:pressed { 
                    opacity: 0.8; 
            }
           QMessageBox {
               background: #ffffff;
           }
           QMessageBox QLabel {
               color: #2c3e50;
               background:transparent;
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
            
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: 500;
            }
            
            QLineEdit {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                min-height: 40px;
            }
            
            QLineEdit:focus {
                border: 2px solid #4a89dc;
                background-color: #f0f7ff;
            }
        """)

        self.set_up()

    def set_up(self):
        self.layoutPrincipal = QVBoxLayout()
        self.layoutPrincipal.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.layoutPrincipal)
        self.iniciarPagina()
        self.showMaximized()

    def iniciarPagina(self):
        contenedorBotones = QWidget()
        contenedorBotones.setStyleSheet("background-color: #f0f7ff; border-radius: 10px; padding: 20px;")
        layoutBotones = QVBoxLayout(contenedorBotones)
        layoutBotones.setAlignment(Qt.AlignCenter)
        layoutBotones.setSpacing(20)
        btnExportar = QPushButton("Exportar Base de Datos a Excel")
        btnExportar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        btnExportar.setCursor(Qt.PointingHandCursor)
        btnExportar.clicked.connect(self.exportar_backup)

        btnImportar = QPushButton("Importar Base de Datos desde Excel")
        btnImportar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btnImportar.setCursor(Qt.PointingHandCursor)
        btnImportar.clicked.connect(self.importar_backup)

        btnEliminarFisica = QPushButton("Eliminar Ventas")
        btnEliminarFisica.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btnEliminarFisica.setCursor(Qt.PointingHandCursor)
        btnEliminarFisica.clicked.connect(self.abrir_eliminacion_fisica)

        btnAdministrarCorreos = QPushButton("Administrar Correos / Backup")
        btnAdministrarCorreos.setStyleSheet("""
            QPushButton {
                background-color: #502f59;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #331e39;
            }
        """)
        btnAdministrarCorreos.setCursor(Qt.PointingHandCursor)
        btnAdministrarCorreos.clicked.connect(self.abrirPopUpConfiguracionCorreos)
        btnImpuestos = QPushButton("Modificar Enlace de Impuestos")
        btnImpuestos.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #7d3c98;
            }
        """)
        btnImpuestos.setCursor(Qt.PointingHandCursor)
        btnImpuestos.clicked.connect(self.abrirPopUpEnlaceImpuestos)
        btnCambiarClaveDir = QPushButton("Cambiar Contraseña del DIRECTORIO")
        btnCambiarClaveDir.setStyleSheet("""
            QPushButton {
                background-color: #d35400;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #ba4a00;
            }
        """)
        btnCambiarClaveDir.setCursor(Qt.PointingHandCursor)
        btnCambiarClaveDir.clicked.connect(self.abrirPopUpCambiarContrasenaDirectorio)
        btnVentasDiarias = QPushButton("Ventas Diarias")
        btnVentasDiarias.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 8px;
                min-width: 300px;
            }
            QPushButton:hover { 
                background-color: #138d75; 
            }
        """)
        btnVentasDiarias.setCursor(Qt.PointingHandCursor)
        btnVentasDiarias.clicked.connect(self.abrir_ventas_diarias)
        self.layoutPrincipal.addWidget(contenedorBotones, alignment=Qt.AlignCenter, stretch=15)
        self.setStyleSheet(
            self.styleSheet()
            + """
            QMessageBox {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-weight: 500;
                font-size: 15px;
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
        """
        )
        layoutBotones.addWidget(btnExportar)
        layoutBotones.addWidget(btnImportar)
        layoutBotones.addWidget(btnEliminarFisica)
        layoutBotones.addWidget(btnAdministrarCorreos)
        layoutBotones.addWidget(btnImpuestos)
        layoutBotones.addWidget(btnCambiarClaveDir)
        layoutBotones.addWidget(btnVentasDiarias)
        self.labelEstado = QLabel("Estado: Listo")
        self.labelEstado.setStyleSheet("color: #7f8c8d; font-size: 14px; font-style: italic; padding: 10px;")
        self.layoutPrincipal.addWidget(self.labelEstado, alignment=Qt.AlignCenter)

    def abrir_eliminacion_fisica(self):
        dialog = EliminacionFisica(self)
        dialog.exec_()

    def abrir_ventas_diarias(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ventas Diarias")
        dialog.setFixedSize(1100, 700)
        dialog.setStyleSheet("""
            QDialog { 
                background:#f8fafc; 
                border-radius:14px; 
            }
            QLabel { 
                font-size:14px; 
                font-weight:600; 
                color:#2c3e50; 
            }
            QTableWidget { 
                border: 1px solid #e2e8f0; 
                font-size:14px; 
            }
            QTableWidget::item:selected { 
                background-color: #2c3e50; 
                color: white; 
            }
            QHeaderView::section { 
                background:#3498db; 
                color:white; 
                font-weight:bold; 
                height:30px; 
                border: none;
            }
            QHeaderView::section:selected,
            QHeaderView::section:pressed {
                background:#3498db; 
                color:white; 
            }
            QPushButton { 
                background:#3498db; 
                color:white; 
                padding:8px 12px; 
                border-radius:6px; 
                font-weight:bold;
                min-width: 120px;
            }
            QPushButton:hover { 
                background:#2980b9; 
            }
            QPushButton[active="true"] { 
                background:#2ecc71; 
            }
            QPushButton[active="true"]:hover { 
                background:#27ae60; 
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        stats_layout = QHBoxLayout()
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        hoy = datetime.now().strftime("%Y-%m-%d")

        cur.execute(
            """
            SELECT COUNT(DISTINCT v.numVenta), COALESCE(SUM(v.totalVenta), 0)
            FROM Venta v
            WHERE DATE(v.fechaReg) = ?
            AND NOT EXISTS (
                SELECT 1 FROM DetallesVenta d 
                WHERE d.numVenta = v.numVenta 
                AND d.fechaRegVenta = v.fechaReg
                AND d.estadoDetalleVenta != 'Finalizado'
            )
        """,
            (hoy,),
        )
        ventas_finalizadas, monto_finalizado = cur.fetchone()
        ventas_finalizadas = ventas_finalizadas or 0
        monto_finalizado = monto_finalizado or 0

        cur.execute(
            """
            SELECT COUNT(DISTINCT v.numVenta)
            FROM Venta v
            WHERE DATE(v.fechaReg) = ?
            AND EXISTS (
                SELECT 1 FROM DetallesVenta d 
                WHERE d.numVenta = v.numVenta 
                AND d.fechaRegVenta = v.fechaReg
                AND d.estadoDetalleVenta = 'Preparacion'
            )
        """,
            (hoy,),
        )
        en_preparacion = cur.fetchone()[0] or 0

        cur.execute(
            """
            SELECT COUNT(DISTINCT v.numVenta)
            FROM Venta v
            WHERE DATE(v.fechaReg) = ?
            AND NOT EXISTS (
                SELECT 1 FROM DetallesVenta d 
                WHERE d.numVenta = v.numVenta 
                AND d.fechaRegVenta = v.fechaReg
                AND d.estadoDetalleVenta != 'Cobrar'
            )
            AND EXISTS (
                SELECT 1 FROM DetallesVenta d 
                WHERE d.numVenta = v.numVenta 
                AND d.fechaRegVenta = v.fechaReg
                AND d.estadoDetalleVenta = 'Cobrar'
            )
        """,
            (hoy,),
        )
        por_cobrar = cur.fetchone()[0] or 0

        cur.execute(
            """
            SELECT COUNT(DISTINCT v.numVenta)
            FROM Venta v
            WHERE DATE(v.fechaReg) = ?
            AND EXISTS (
                SELECT 1 FROM DetallesVenta d 
                WHERE d.numVenta = v.numVenta 
                AND d.fechaRegVenta = v.fechaReg
                AND d.estadoDetalleVenta = 'Preparacion'
            )
            AND EXISTS (
                SELECT 1 FROM DetallesVenta d 
                WHERE d.numVenta = v.numVenta 
                AND d.fechaRegVenta = v.fechaReg
                AND d.estadoDetalleVenta = 'Cobrar'
            )
        """,
            (hoy,),
        )
        mixtas = cur.fetchone()[0] or 0

        conn.close()

        stats_data = [
            (f"✅ Finalizadas: {ventas_finalizadas}", "#2ecc71", f"Total: {monto_finalizado:.2f} Bs"),
            (f"⏳ En Preparación: {en_preparacion}", "#f39c12", None),
            (f"💰 Por Cobrar: {por_cobrar}", "#3498db", None),
            (f"🔄 Mixtas: {mixtas}", "#9b59b6", None),
        ]

        for text, color, extra in stats_data:
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(5, 5, 5, 5)
            container_layout.setSpacing(2)

            label = QLabel(text)
            label.setStyleSheet(f"""
                QLabel {{
                    background: {color};
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 13px;
                    min-width: 150px;
                    text-align: center;
                }}
            """)
            container_layout.addWidget(label)

            if extra:
                extra_label = QLabel(extra)
                if text.startswith("✅"):
                    extra_label.setStyleSheet("""
                        QLabel {
                            background: #000000;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 12px;
                            text-align: center;
                            margin-top: -4px;
                            border: 1px solid #ffffff;
                        }
                    """)
                else:
                    extra_label.setStyleSheet(f"""
                        QLabel {{
                            background: {color}80;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 12px;
                            text-align: center;
                            margin-top: -4px;
                        }}
                    """)
                container_layout.addWidget(extra_label)

            stats_layout.addWidget(container)

        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        filtros_top_layout = QHBoxLayout()
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Buscar por Cajero")
        search_input.setMinimumWidth(300)
        search_button = QPushButton("🔍")
        search_button.setFixedWidth(40)
        search_button.setStyleSheet("font-size: 16px;")
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_button)
        filtros_top_layout.addLayout(search_layout)
        btn_recargar = QPushButton("🔄 Recargar")
        btn_recargar.setStyleSheet("background: #9b59b6;")
        filtros_top_layout.addWidget(btn_recargar)
        filtros_top_layout.addStretch()
        layout.addLayout(filtros_top_layout)

        filtrosLayout = QHBoxLayout()
        filtrosLayout.setSpacing(10)

        btnTodas = QPushButton("📋 TODAS")
        btnTodas.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
            QPushButton:checked {
                background-color: #2ecc71;
                border: 2px solid #27ae60;
            }
        """)

        btnFinalizadas = QPushButton("✅ FINALIZADAS")
        btnFinalizadas.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:checked {
                background-color: #2ecc71;
                border: 2px solid #27ae60;
            }
        """)

        btnEnPreparacion = QPushButton("⏳ EN PREPARACIÓN")
        btnEnPreparacion.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:checked {
                background-color: #f1c40f;
                border: 2px solid #f39c12;
            }
        """)

        btnPorCobrar = QPushButton("💰 POR COBRAR")
        btnPorCobrar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:checked {
                background-color: #5dade2;
                border: 2px solid #3498db;
            }
        """)

        btnMixtas = QPushButton("🔄 MIXTAS")
        btnMixtas.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:checked {
                background-color: #af7ac5;
                border: 2px solid #9b59b6;
            }
        """)

        for btn in [btnTodas, btnFinalizadas, btnEnPreparacion, btnPorCobrar, btnMixtas]:
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            filtrosLayout.addWidget(btn)

        filtrosLayout.addStretch()
        layout.addLayout(filtrosLayout)

        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels(["N° Venta", "Hora", "Mesero (Apertura)", "Cajero", "Total", "Mesa", "Estado"])
        tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        tabla.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        tabla.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        tabla.setSortingEnabled(True)
        tabla.setSelectionBehavior(QTableWidget.SelectRows)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setAlternatingRowColors(True)
        tabla.verticalHeader().setVisible(False)
        tabla.doubleClicked.connect(lambda index: ver_detalles_venta_desde_tabla(tabla, index.row()))
        layout.addWidget(tabla)

        botones_layout = QHBoxLayout()
        btn_ver_detalles = QPushButton("📋 Ver Detalles")
        btn_ver_detalles.setStyleSheet("""
            QPushButton {
                background: #9b59b6;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 20px;
            }
            QPushButton:hover {
                background: #8e44ad;
            }
        """)
        btn_ver_detalles.clicked.connect(lambda: ver_detalles_venta_desde_boton(tabla))
        botones_layout.addWidget(btn_ver_detalles)
        botones_layout.addStretch()
        layout.addLayout(botones_layout)

        def cargar_ventas(filtro=None, busqueda=""):
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            hoy = datetime.now().strftime("%Y-%m-%d")
            query = """
                SELECT 
                    v.numVenta,
                    v.horaReg,
                    e1.aliasEmp as mesero_apertura,
                    CASE 
                        WHEN v.codEmp2 = -1 THEN 'DIRECTORIO'
                        ELSE e2.aliasEmp 
                    END as cajero,
                    v.totalVenta,
                    v.idMesa,
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
                        ) AND NOT EXISTS (
                            SELECT 1 FROM DetallesVenta d 
                            WHERE d.numVenta = v.numVenta 
                            AND d.fechaRegVenta = v.fechaReg
                            AND d.estadoDetalleVenta = 'Cobrar'
                        ) THEN 'En Preparación'
                        
                        WHEN NOT EXISTS (
                            SELECT 1 FROM DetallesVenta d 
                            WHERE d.numVenta = v.numVenta 
                            AND d.fechaRegVenta = v.fechaReg
                            AND d.estadoDetalleVenta != 'Cobrar'
                        ) AND EXISTS (
                            SELECT 1 FROM DetallesVenta d 
                            WHERE d.numVenta = v.numVenta 
                            AND d.fechaRegVenta = v.fechaReg
                            AND d.estadoDetalleVenta = 'Cobrar'
                        ) THEN 'Por Cobrar'
                        
                        ELSE 'Mixta'
                    END AS estado
                FROM Venta v
                JOIN Empleado e1 ON v.codEmp = e1.codEmp
                LEFT JOIN Empleado e2 ON v.codEmp2 = e2.codEmp
                WHERE DATE(v.fechaReg) = ?
                """
            params = [hoy]

            if filtro == "Finalizadas":
                query += """ AND NOT EXISTS (
                    SELECT 1 FROM DetallesVenta d 
                    WHERE d.numVenta = v.numVenta 
                    AND d.fechaRegVenta = v.fechaReg
                    AND d.estadoDetalleVenta != 'Finalizado'
                )"""
            elif filtro == "En preparación":
                query += """ AND EXISTS (
                    SELECT 1 FROM DetallesVenta d 
                    WHERE d.numVenta = v.numVenta 
                    AND d.fechaRegVenta = v.fechaReg
                    AND d.estadoDetalleVenta = 'Preparacion'
                ) AND NOT EXISTS (
                    SELECT 1 FROM DetallesVenta d 
                    WHERE d.numVenta = v.numVenta 
                    AND d.fechaRegVenta = v.fechaReg
                    AND d.estadoDetalleVenta = 'Cobrar'
                )"""
            elif filtro == "Por cobrar":
                query += """ AND NOT EXISTS (
                    SELECT 1 FROM DetallesVenta d 
                    WHERE d.numVenta = v.numVenta 
                    AND d.fechaRegVenta = v.fechaReg
                    AND d.estadoDetalleVenta != 'Cobrar'
                ) AND EXISTS (
                    SELECT 1 FROM DetallesVenta d 
                    WHERE d.numVenta = v.numVenta 
                    AND d.fechaRegVenta = v.fechaReg
                    AND d.estadoDetalleVenta = 'Cobrar'
                )"""
            elif filtro == "Mixtas":
                query += """ AND EXISTS (
                    SELECT 1 FROM DetallesVenta d 
                    WHERE d.numVenta = v.numVenta 
                    AND d.fechaRegVenta = v.fechaReg
                    AND d.estadoDetalleVenta = 'Preparacion'
                ) AND EXISTS (
                    SELECT 1 FROM DetallesVenta d 
                    WHERE d.numVenta = v.numVenta 
                    AND d.fechaRegVenta = v.fechaReg
                    AND d.estadoDetalleVenta = 'Cobrar'
                )"""

            if busqueda:
                query += """ AND (
                    (CASE WHEN v.codEmp2 = -1 THEN 'DIRECTORIO' ELSE e2.aliasEmp END) LIKE ?
                )"""
                params.append(f"%{busqueda}%")

            query += " ORDER BY v.horaReg DESC"
            cur.execute(query, params)
            rows = cur.fetchall()
            conn.close()

            tabla.setRowCount(0)
            for r in rows:
                fila = tabla.rowCount()
                tabla.insertRow(fila)
                estado = r[6]
                for c, val in enumerate(r):
                    item = QTableWidgetItem(str(val))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

                    if estado == "Finalizada":
                        item.setBackground(QColor(230, 255, 230))
                    elif estado == "En Preparación":
                        item.setBackground(QColor(255, 255, 200))
                    elif estado == "Por Cobrar":
                        item.setBackground(QColor(200, 230, 255))
                    elif estado == "Mixta":
                        item.setBackground(QColor(240, 210, 255))

                    if c == 4:
                        try:
                            total_val = float(val)
                            item.setText(f"{total_val:,.2f} Bs")
                        except Exception:
                            pass
                    tabla.setItem(fila, c, item)
            tabla.setToolTip(f"Mostrando {tabla.rowCount()} ventas")

        def buscar_ventas():
            texto = search_input.text().strip()
            filtro_activo = None
            filtros = {
                btnTodas: None,
                btnFinalizadas: "Finalizadas",
                btnEnPreparacion: "En preparación",
                btnPorCobrar: "Por cobrar",
                btnMixtas: "Mixtas",
            }
            filtro_activo = next((estado for btn, estado in filtros.items() if btn.isChecked()), None)
            cargar_ventas(filtro_activo, texto)

        def recargar_todo():
            search_input.clear()
            btnTodas.setChecked(True)
            cargar_ventas()

        btnTodas.clicked.connect(lambda: cargar_ventas(None, search_input.text()))
        btnFinalizadas.clicked.connect(lambda: cargar_ventas("Finalizadas", search_input.text()))
        btnEnPreparacion.clicked.connect(lambda: cargar_ventas("En preparación", search_input.text()))
        btnPorCobrar.clicked.connect(lambda: cargar_ventas("Por cobrar", search_input.text()))
        btnMixtas.clicked.connect(lambda: cargar_ventas("Mixtas", search_input.text()))
        search_button.clicked.connect(buscar_ventas)
        search_input.returnPressed.connect(buscar_ventas)
        btn_recargar.clicked.connect(recargar_todo)

        def ver_detalles_venta_desde_boton(tabla_widget):
            fila_seleccionada = tabla_widget.currentRow()
            if fila_seleccionada == -1:
                QMessageBox.warning(dialog, "Advertencia", "Seleccione una venta primero")
                return
            ver_detalles_venta_desde_tabla(tabla_widget, fila_seleccionada)

        def ver_detalles_venta_desde_tabla(tabla_widget, fila):
            num_venta = tabla_widget.item(fila, 0).text()
            hora = tabla_widget.item(fila, 1).text()
            mesero_apertura = tabla_widget.item(fila, 2).text()
            mesa = tabla_widget.item(fila, 5).text()
            estado = tabla_widget.item(fila, 6).text()
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            hoy = datetime.now().strftime("%Y-%m-%d")
            query = """
            SELECT 
                COALESCE(p.nomProd, pr.nomProm) as producto,
                dv.cantidadProdDet,
                dv.tipoConsumo,
                dv.subtotal,
                dv.estadoDetalleVenta,
                dv.fechaRegDetalleVenta,
                e.aliasEmp as mesero_detalle
            FROM DetallesVenta dv
            LEFT JOIN Producto p ON dv.idProd = p.idProd
            LEFT JOIN Promocion pr ON dv.idProm = pr.idProm
            JOIN Empleado e ON dv.idMeseroActual = e.codEmp
            WHERE dv.numVenta = ?
            AND DATE(dv.fechaRegVenta) = ?
            ORDER BY dv.fechaRegDetalleVenta
            """
            cur.execute(query, (num_venta, hoy))
            detalles = cur.fetchall()
            cur.execute(
                """
                SELECT s.nombSeccion 
                FROM Venta v
                JOIN Seccion s ON v.idSeccion = s.idSeccion
                WHERE v.numVenta = ? 
                AND DATE(v.fechaReg) = ?
            """,
                (num_venta, hoy),
            )
            seccion_result = cur.fetchone()
            seccion = seccion_result[0] if seccion_result else "No especificada"
            conn.close()
            dialog_detalles = QDialog(dialog)
            dialog_detalles.setWindowTitle(f"Detalles Venta #{num_venta}")
            dialog_detalles.setFixedSize(900, 500)
            dialog_detalles.setStyleSheet("""
                QDialog {
                    background: #f8fafc;
                    font-family: 'Segoe UI', Arial;
                }
                QLabel {
                    font-size: 13px;
                    color: #2c3e50;
                }
                QTableWidget {
                    border: 1px solid #e2e8f0;
                    font-size: 12px;
                }
                QHeaderView::section {
                    background: #3498db;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                }
            """)
            layout_detalles = QVBoxLayout(dialog_detalles)
            layout_detalles.setSpacing(15)
            layout_detalles.setContentsMargins(20, 20, 20, 20)
            info_group = QGroupBox("Información de la Venta")
            info_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    font-size: 14px;
                    border: 2px solid #3498db;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 10px 0 10px;
                }
            """)
            info_layout = QGridLayout(info_group)
            info_layout.addWidget(QLabel(f"<b>N° Venta:</b> {num_venta}"), 0, 0)
            info_layout.addWidget(QLabel(f"<b>Hora:</b> {hora}"), 0, 1)
            info_layout.addWidget(QLabel(f"<b>Mesero (Apertura):</b> {mesero_apertura}"), 1, 0)
            info_layout.addWidget(QLabel(f"<b>Mesa:</b> {mesa}"), 1, 1)
            info_layout.addWidget(QLabel(f"<b>Sección:</b> {seccion}"), 2, 0)
            info_layout.addWidget(QLabel(f"<b>Estado:</b> {estado}"), 2, 1)
            layout_detalles.addWidget(info_group)
            tabla_detalles = QTableWidget()
            tabla_detalles.setColumnCount(7)
            tabla_detalles.setHorizontalHeaderLabels(
                ["Producto", "Cantidad", "Tipo", "Precio Unit.", "Subtotal", "Estado", "Mesero"]
            )
            tabla_detalles.horizontalHeader().setStretchLastSection(True)
            total = 0
            for detalle in detalles:
                producto, cantidad, tipo, subtotal, estado_det, fecha_det, mesero_det = detalle
                precio_unitario = subtotal / cantidad if cantidad > 0 else 0
                fila = tabla_detalles.rowCount()
                tabla_detalles.insertRow(fila)
                items_data = [
                    producto,
                    str(cantidad),
                    tipo,
                    f"{precio_unitario:.2f} Bs",
                    f"{subtotal:.2f} Bs",
                    estado_det,
                    mesero_det,
                ]
                for col, val in enumerate(items_data):
                    item = QTableWidgetItem(str(val))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    if estado_det == "Preparacion":
                        item.setBackground(QColor(255, 255, 200))
                    elif estado_det == "Cobrar":
                        item.setBackground(QColor(200, 230, 255))
                    elif estado_det == "Finalizado":
                        item.setBackground(QColor(230, 255, 230))
                    tabla_detalles.setItem(fila, col, item)
                total += subtotal
            tabla_detalles.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            tabla_detalles.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            tabla_detalles.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            tabla_detalles.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            tabla_detalles.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            tabla_detalles.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
            tabla_detalles.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
            layout_detalles.addWidget(QLabel("<b>Detalles de Productos:</b>"))
            layout_detalles.addWidget(tabla_detalles)
            footer_layout = QHBoxLayout()
            total_label = QLabel(f"<b>TOTAL VENTA:</b> {total:,.2f} Bs")
            total_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2ecc71;
                    padding: 10px;
                    background: #f1f8e9;
                    border-radius: 6px;
                }
            """)
            footer_layout.addWidget(total_label)
            footer_layout.addStretch()
            btn_cerrar = QPushButton("Cerrar")
            btn_cerrar.setStyleSheet("""
                QPushButton {
                    background: #3498db;
                    color: white;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #2980b9;
                }
            """)
            btn_cerrar.clicked.connect(dialog_detalles.accept)
            footer_layout.addWidget(btn_cerrar)
            layout_detalles.addLayout(footer_layout)
            dialog_detalles.exec_()

        btnTodas.setChecked(True)
        cargar_ventas()
        dialog.exec_()

    def _ensure_configuracion_sistema(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Enlace(
                    idEnlace INTEGER PRIMARY KEY AUTOINCREMENT,
                    enlace VARCHAR(100) NOT NULL DEFAULT 'https://siat.impuestos.gob.bo/v2/launcher/'
                )
            """)
            cur.execute("SELECT COUNT(*) FROM Enlace")
            count = cur.fetchone()[0]
            if count == 0:
                cur.execute("INSERT INTO Enlace (enlace) VALUES (?)", ("https://siat.impuestos.gob.bo/v2/launcher/",))
            conn.commit()
        finally:
            conn.close()

    def obtener_url_impuestos(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute("SELECT enlace FROM Enlace LIMIT 1")
            r = cur.fetchone()
            return r[0] if r else "https://siat.impuestos.gob.bo/v2/launcher/"
        finally:
            conn.close()

    def abrirPopUpEnlaceImpuestos(self):
        actual = self.obtener_url_impuestos()
        d, inp = self.dialogo_input("Modificar enlace de Impuestos", "URL del SIAT:", False, actual)
        if d.exec_() != QDialog.Accepted:
            return

        url = inp.text().strip()
        if not url.startswith("http"):
            QMessageBox.warning(self, "Error", "URL inválida.")
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute("UPDATE Enlace SET enlace=?", (url,))
            conn.commit()
            QMessageBox.information(self, "Enlace actualizado", "El enlace fue actualizado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar: {str(e)}")
        finally:
            conn.close()

    def exportar_backup(self):
        temp_dir = tempfile.mkdtemp()

        try:
            backend = ConfiguracionBackend(DB_PATH)

            excel_path = os.path.join(temp_dir, "cafebar_export.xlsx")
            carpeta_imagenes = os.path.join(temp_dir, "imagenes")
            zip_path = os.path.join(temp_dir, "cafebar_backup.zip")

            cuenta = self.obtener_cuenta_gmail_activa()
            if not cuenta:
                QMessageBox.warning(self, "Error", "No hay cuenta Gmail activa.")
                return

            correo, password = cuenta

            self.labelEstado.setText("Estado: Exportando datos...")
            QApplication.processEvents()

            backend.exportar_a_excel(excel_path, carpeta_imagenes)
            self.labelEstado.setText("Estado: Creando archivo ZIP...")
            QApplication.processEvents()

            backend.crear_zip_backup(excel_path, carpeta_imagenes, zip_path)
            self.labelEstado.setText("Estado: Enviando por correo...")
            QApplication.processEvents()

            backend.enviar_backup_por_correo(correo, password, correo, zip_path)

            self.labelEstado.setText("Estado: Backup enviado correctamente")
            QMessageBox.information(
                self, "Backup enviado", "Backup enviado al Gmail activo.\nLos archivos temporales han sido eliminados."
            )

        except Exception as e:
            self.labelEstado.setText("Estado: Error en el proceso")
            QMessageBox.critical(self, "Error", f"No se pudo enviar backup: {e}")

        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    def abrirPopUpCambiarContrasenaDirectorio(self):
        d, inpActual = self.dialogo_input("Cambiar contraseña - DIRECTORIO", "Contraseña actual:", True)
        if d.exec_() != QDialog.Accepted:
            return
        actual = inpActual.text().strip()
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT contrasenaAdmin FROM Directorio WHERE idAmin = 1")
        row = cur.fetchone()
        if not row or not verificar_password(actual, row[0]):
            QMessageBox.warning(self, "Error", "Contraseña actual incorrecta.")
            conn.close()
            return
        d2, inpNueva = self.dialogo_input(
            "Nueva contraseña - DIRECTORIO", "Nueva contraseña (mínimo 4 caracteres):", True
        )
        if d2.exec_() != QDialog.Accepted:
            conn.close()
            return
        nueva = inpNueva.text().strip()
        if len(nueva) < 4:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 4 caracteres.")
            conn.close()
            return
        if nueva == actual:
            QMessageBox.warning(self, "Error", "La nueva contraseña debe ser diferente a la actual.")
            conn.close()
            return
        d3, inpRep = self.dialogo_input("Confirmar contraseña", "Repita la nueva contraseña:", True)
        if d3.exec_() != QDialog.Accepted:
            conn.close()
            return
        rep = inpRep.text().strip()
        if nueva != rep:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            conn.close()
            return
        nueva_hash = hashear_password(nueva)
        cur.execute("UPDATE Directorio SET contrasenaAdmin = ? WHERE idAmin = 1", (nueva_hash,))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Éxito", "Contraseña del DIRECTORIO actualizada.")

    def get_connection(self):
        return sqlite3.connect(DB_PATH)

    def obtener_cuenta_gmail_activa(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT correoCuenta, contCuenta FROM Cuenta WHERE activaCuenta=1 LIMIT 1")
        row = cur.fetchone()
        conn.close()
        return row

    def abrirPopUpConfiguracionCorreos(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Cuentas Gmail Backup")
        dialog.setFixedSize(560, 580)
        dialog.setStyleSheet("""
            QDialog {
                background:#f8fafc;
                border-radius:14px;
            }
            QLabel {
                font-size:15px;
                color:#2c3e50;
                font-weight:600;
            }
            QMessageBox {
                background: #ffffff;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                background:transparent;
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
            QListWidget {
                background:white;
                border:2px solid #e2e8f0;
                border-radius:10px;
                padding:8px;
                font-size:14px;
            }
            QListWidget::item {
                padding:10px;
                border-radius:8px;
            }
            QListWidget::item:selected {
                background:#3498db;
                color:white;
            }
            QPushButton {
                background:#3498db;
                color:white;
                padding:12px;
                border-radius:10px;
                font-weight:bold;
                font-size:14px;
            }
            QPushButton:hover { 
                background:#2980b9; 
            }
            QPushButton#danger { 
                background:#e74c3c;
            }
            QPushButton#danger:hover {
                 background:#c0392b; 
            }
            QPushButton#success { 
                background:#27ae60; 
            }
            QPushButton#success:hover { 
                background:#219653; 
            }
        """)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        titulo = QLabel("Administración de Cuentas Gmail")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size:20px;font-weight:800;")
        layout.addWidget(titulo)
        self.listaCuentas = QListWidget()
        layout.addWidget(self.listaCuentas, stretch=1)
        self.cargar_cuentas()
        grid = QGridLayout()
        grid.setSpacing(10)
        btnActivar = QPushButton("📌 ACTIVAR")
        btnActivar.setObjectName("success")
        btnRegistrar = QPushButton("➕ REGISTRAR")
        btnModificar = QPushButton("✏ MODIFICAR CLAVE")
        btnEliminar = QPushButton("🗑 ELIMINAR")
        btnEliminar.setObjectName("danger")
        btnActivar.clicked.connect(self.activar_cuenta)
        btnRegistrar.clicked.connect(self.registrar_cuenta)
        btnModificar.clicked.connect(self.modificar_clave)
        btnEliminar.clicked.connect(self.eliminar_cuenta)
        grid.addWidget(btnActivar, 0, 0)
        grid.addWidget(btnRegistrar, 0, 1)
        grid.addWidget(btnModificar, 1, 0)
        grid.addWidget(btnEliminar, 1, 1)
        layout.addLayout(grid)
        dialog.exec_()

    def cargar_cuentas(self):
        self.listaCuentas.clear()
        self.mapaIDs = {}
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT idCuenta, correoCuenta, activaCuenta FROM Cuenta ORDER BY correoCuenta")
        for n, (idc, correo, activa) in enumerate(cur.fetchall(), start=1):
            if activa:
                texto = f"🟢  {n}.  {correo}   (ACTIVA)"
            else:
                texto = f"⚪  {n}.  {correo}"
            self.listaCuentas.addItem(texto)
            self.mapaIDs[n] = idc
        conn.close()

    def activar_cuenta(self):
        if not self.listaCuentas.currentItem():
            return
        num = int(self.listaCuentas.currentItem().text().split(".")[0].replace("🟢", "").replace("⚪", "").strip())
        idCuenta = self.mapaIDs[num]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE Cuenta SET activaCuenta=0")
        cur.execute("UPDATE Cuenta SET activaCuenta=1 WHERE idCuenta=?", (idCuenta,))
        conn.commit()
        conn.close()
        self.cargar_cuentas()

    def registrar_cuenta(self):
        d, inputCorreo = self.dialogo_input("Nuevo Gmail", "Correo:")
        if d.exec_() != QDialog.Accepted:
            return
        correo = inputCorreo.text().strip()
        if not correo:
            QMessageBox.warning(self, "Error", "El correo no puede estar vacío.")
            return
        d2, inputClave = self.dialogo_input("App Password", "Contraseña de aplicación:", True)
        if d2.exec_() != QDialog.Accepted:
            return
        clave = inputClave.text().strip()
        if not clave:
            QMessageBox.warning(self, "Error", "La contraseña no puede estar vacía.")
            return
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO Cuenta(correoCuenta, contCuenta, activaCuenta) VALUES (?,?,0)", (correo, clave))
        conn.commit()
        conn.close()
        self.cargar_cuentas()

    def modificar_clave(self):
        if not self.listaCuentas.currentItem():
            return
        num = int(self.listaCuentas.currentItem().text().split(".")[0].replace("🟢", "").replace("⚪", "").strip())
        idCuenta = self.mapaIDs[num]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT correoCuenta, contCuenta FROM Cuenta WHERE idCuenta=?", (idCuenta,))
        correo, clave_actual = cur.fetchone()
        conn.close()
        dialog = QDialog(self)
        dialog.setWindowTitle("Modificar Contraseña")
        dialog.setFixedSize(450, 380)
        dialog.setStyleSheet("""
            QDialog {
                background: #ffffff;
            }
            QLabel#titulo {
                font-size: 18px;
                font-weight: bold;
                color: #1e293b;
                padding: 0;
                margin: 0;
            }
            QLabel#correo {
                font-size: 13px;
                color: #64748b;
                padding: 0;
                margin: 0;
            }
            QLabel.field-label {
                font-size: 12px;
                font-weight: 600;
                color: #475569;
                padding: 0;
                margin: 0 0 4px 0;
            }
            QLineEdit {
                background: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
                color: #1e293b;
                min-height: 18px;
                max-height: 18px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
                background: #ffffff;
            }
            QLineEdit:read-only {
                background: #f1f5f9;
                color: #64748b;
            }
            QPushButton#eye {
                background: transparent;
                border: none;
                color: #94a3b8;
                font-size: 16px;
                padding: 0;
                min-width: 32px;
                max-width: 32px;
                min-height: 34px;
                max-height: 34px;
            }
            QPushButton#eye:hover {
                color: #64748b;
            }
            QPushButton#cancelar {
                background: #f1f5f9;
                color: #475569;
                border: none;
                border-radius: 6px;
                padding: 9px 20px;
                font-weight: 600;
                font-size: 13px;
                min-height: 16px;
            }
            QPushButton#cancelar:hover {
                background: #e2e8f0;
            }
            QPushButton#actualizar {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 9px 20px;
                font-weight: 600;
                font-size: 13px;
                min-height: 16px;
            }
            QPushButton#actualizar:hover {
                background: #2563eb;
            }
            QFrame#separador {
                background: #e2e8f0;
                min-height: 1px;
                max-height: 1px;
                margin: 0;
            }
        """)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(0)
        layout.setContentsMargins(30, 25, 30, 25)
        titulo = QLabel("Modificar Contraseña")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)
        layout.addSpacing(4)
        correo_label = QLabel(f"📧 {correo}")
        correo_label.setObjectName("correo")
        layout.addWidget(correo_label)
        layout.addSpacing(12)
        separador = QFrame()
        separador.setObjectName("separador")
        separador.setFrameShape(QFrame.HLine)
        layout.addWidget(separador)
        layout.addSpacing(16)
        label_actual = QLabel("Contraseña actual")
        label_actual.setProperty("class", "field-label")
        layout.addWidget(label_actual)
        actual_layout = QHBoxLayout()
        actual_layout.setSpacing(6)
        actual_layout.setContentsMargins(0, 0, 0, 0)
        txt_clave_actual = QLineEdit(clave_actual)
        txt_clave_actual.setReadOnly(True)
        txt_clave_actual.setEchoMode(QLineEdit.Password)
        btn_ver_actual = QPushButton("👁")
        btn_ver_actual.setObjectName("eye")
        btn_ver_actual.setCheckable(True)

        def toggle_ver_actual():
            txt_clave_actual.setEchoMode(QLineEdit.Normal if btn_ver_actual.isChecked() else QLineEdit.Password)

        btn_ver_actual.clicked.connect(toggle_ver_actual)
        actual_layout.addWidget(txt_clave_actual)
        actual_layout.addWidget(btn_ver_actual)
        layout.addLayout(actual_layout)
        layout.addSpacing(12)
        label_nueva = QLabel("Nueva contraseña")
        label_nueva.setProperty("class", "field-label")
        layout.addWidget(label_nueva)
        nueva_layout = QHBoxLayout()
        nueva_layout.setSpacing(6)
        nueva_layout.setContentsMargins(0, 0, 0, 0)
        txt_nueva = QLineEdit()
        txt_nueva.setEchoMode(QLineEdit.Password)
        txt_nueva.setPlaceholderText("Mínimo 4 caracteres")
        btn_ver_nueva = QPushButton("👁")
        btn_ver_nueva.setObjectName("eye")
        btn_ver_nueva.setCheckable(True)

        def toggle_ver_nueva():
            txt_nueva.setEchoMode(QLineEdit.Normal if btn_ver_nueva.isChecked() else QLineEdit.Password)

        btn_ver_nueva.clicked.connect(toggle_ver_nueva)
        nueva_layout.addWidget(txt_nueva)
        nueva_layout.addWidget(btn_ver_nueva)
        layout.addLayout(nueva_layout)
        layout.addSpacing(12)
        label_confirmar = QLabel("Confirmar contraseña")
        label_confirmar.setProperty("class", "field-label")
        layout.addWidget(label_confirmar)
        confirmar_layout = QHBoxLayout()
        confirmar_layout.setSpacing(6)
        confirmar_layout.setContentsMargins(0, 0, 0, 0)
        txt_confirmar = QLineEdit()
        txt_confirmar.setEchoMode(QLineEdit.Password)
        txt_confirmar.setPlaceholderText("Repita la nueva contraseña")
        btn_ver_confirmar = QPushButton("👁")
        btn_ver_confirmar.setObjectName("eye")
        btn_ver_confirmar.setCheckable(True)

        def toggle_ver_confirmar():
            txt_confirmar.setEchoMode(QLineEdit.Normal if btn_ver_confirmar.isChecked() else QLineEdit.Password)

        btn_ver_confirmar.clicked.connect(toggle_ver_confirmar)
        confirmar_layout.addWidget(txt_confirmar)
        confirmar_layout.addWidget(btn_ver_confirmar)
        layout.addLayout(confirmar_layout)
        layout.addStretch()
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(0, 16, 0, 0)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("cancelar")
        btn_cancelar.clicked.connect(dialog.reject)
        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.setObjectName("actualizar")

        def validar_y_actualizar():
            nueva = txt_nueva.text().strip()
            confirmar = txt_confirmar.text().strip()
            if not nueva:
                QMessageBox.warning(dialog, "Campo requerido", "La nueva contraseña no puede estar vacía.")
                txt_nueva.setFocus()
                return
            if len(nueva) < 4:
                QMessageBox.warning(dialog, "Contraseña muy corta", "La contraseña debe tener al menos 4 caracteres.")
                txt_nueva.setFocus()
                return
            if nueva == clave_actual:
                QMessageBox.warning(dialog, "Contraseña igual", "La nueva contraseña debe ser diferente a la actual.")
                txt_nueva.setFocus()
                return
            if nueva != confirmar:
                QMessageBox.warning(dialog, "No coinciden", "Las contraseñas no coinciden.")
                txt_confirmar.setFocus()
                return
            confirm = QMessageBox.question(
                dialog,
                "Confirmar cambio",
                f"¿Está seguro de cambiar la contraseña de:\n{correo}?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if confirm != QMessageBox.Yes:
                return
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("UPDATE Cuenta SET contCuenta=? WHERE idCuenta=?", (nueva, idCuenta))
                conn.commit()
                conn.close()
                QMessageBox.information(dialog, "Éxito", "Contraseña actualizada correctamente")
                dialog.accept()
                self.cargar_cuentas()
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"No se pudo actualizar: {str(e)}")

        btn_actualizar.clicked.connect(validar_y_actualizar)
        txt_confirmar.returnPressed.connect(validar_y_actualizar)
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_actualizar)
        layout.addLayout(btn_layout)
        dialog.exec_()

    def importar_backup(self):
        zip_path, _ = QFileDialog.getOpenFileName(
            self, "Selecciona el archivo ZIP de backup", "", "Archivos ZIP (*.zip)"
        )

        if not zip_path:
            return

        temp_dir = tempfile.mkdtemp()

        try:
            self.labelEstado.setText("Estado: Extrayendo archivos...")
            QApplication.processEvents()

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            excel_path = None
            imagenes_dir = None

            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.xlsx') and 'cafebar_export' in file:
                        excel_path = os.path.join(root, file)
                for dir_name in dirs:
                    if dir_name == 'imagenes':
                        imagenes_dir = os.path.join(root, dir_name)

            if not excel_path or not os.path.exists(excel_path):
                QMessageBox.warning(self, "Error", "No se encontró un archivo Excel válido en el ZIP.")
                return

            self.labelEstado.setText("Estado: Importando datos...")
            QApplication.processEvents()

            backend = ConfiguracionBackend(DB_PATH)
            backend.importar_desde_excel(excel_path, imagenes_dir)

            self.labelEstado.setText("Estado: Importación completada")
            QMessageBox.information(
                self, "Éxito", "Importación completada correctamente.\nLos archivos temporales han sido eliminados."
            )

        except Exception as e:
            self.labelEstado.setText("Estado: Error en la importación")
            QMessageBox.critical(self, "Error", f"No se pudo importar: {e}")

        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    def eliminar_cuenta(self):
        if not self.listaCuentas.currentItem():
            return
        num = int(self.listaCuentas.currentItem().text().split(".")[0].replace("🟢", "").replace("⚪", "").strip())
        idCuenta = self.mapaIDs[num]
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM Cuenta WHERE idCuenta=?", (idCuenta,))
        conn.commit()
        conn.close()
        self.cargar_cuentas()

    def dialogo_input(self, titulo, texto, password=False, valor=""):
        d = QDialog(self)
        d.setWindowTitle(titulo)
        d.setFixedSize(420, 190)
        d.setStyleSheet("""
            QDialog { background:#f8fafc; border-radius:14px; }
            QLabel { font-size:14px; font-weight:600; color:#2c3e50; }
              QMessageBox QLabel {
                  color: #2c3e50;
                  background:transparent;
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
            QLineEdit {
                background:white;
                border:2px solid #e2e8f0;
                border-radius:8px;
                padding:10px;
                font-size:14px;
            }
            QPushButton#accept {
                background:#3498db;
                color:white;
                padding:10px 24px;
                border-radius:10px;
                font-weight:bold;
                min-width:120px;
            }
            QPushButton#accept:hover { 
                background:#2980b9; 
            }
            QPushButton#cancel {
                background:#95a5a6;
                color:white;
                padding:10px 24px;
                border-radius:10px;
                font-weight:bold;
                min-width:120px;
            }
            QPushButton#cancel:hover {
                background:#7f8c8d;
            }
            QPushButton#eye {
                background:#ecf0f1;
                border-radius:8px;
                min-width:42px;
                max-width:42px;
                font-size:16px;
            }
            QPushButton#eye:hover { 
                background:#dfe6e9; 
            }
        """)
        layout = QVBoxLayout(d)
        label = QLabel(texto)
        cont = QWidget()
        h = QHBoxLayout(cont)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        inputt = QLineEdit()
        inputt.setText(valor)
        if password:
            inputt.setEchoMode(QLineEdit.Password)
            ojo = QPushButton("👁")
            ojo.setObjectName("eye")
            ojo.setCheckable(True)

            def toggle():
                inputt.setEchoMode(QLineEdit.Normal if ojo.isChecked() else QLineEdit.Password)

            ojo.clicked.connect(toggle)
            h.addWidget(inputt, 1)
            h.addWidget(ojo)
        else:
            h.addWidget(inputt)
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(15)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("cancel")
        btn_cancelar.clicked.connect(d.reject)
        btn = QPushButton("Aceptar")
        btn.setObjectName("accept")
        btn.clicked.connect(d.accept)
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(btn)
        layout.addWidget(label)
        layout.addWidget(cont)
        layout.addStretch()
        layout.addLayout(botones_layout)
        return d, inputt

    def closeEvent(self, event):
        event.accept()


class ConfiguracionBackend:
    def __init__(self, db_path):
        self.db_path = db_path

    def getConnection(self):
        return sqlite3.connect(self.db_path)

    def exportar_a_excel(self, excel_path, carpeta_imagenes=None):
        if carpeta_imagenes and os.path.exists(carpeta_imagenes):
            shutil.rmtree(carpeta_imagenes)
        if carpeta_imagenes:
            os.makedirs(carpeta_imagenes)
        conn = self.getConnection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tablas = [r[0] for r in cur.fetchall()]
        writer = pd.ExcelWriter(excel_path, engine="openpyxl")
        for tabla in tablas:
            df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
            if carpeta_imagenes:
                df = self._exportar_imagenes(df, tabla, carpeta_imagenes)
            df.to_excel(writer, sheet_name=tabla, index=False)
        writer.close()
        conn.close()

    def _exportar_imagenes(self, df, tabla, carpeta_imagenes):
        for col in df.columns:
            if df[col].dtype == object:
                if df[col].apply(lambda x: isinstance(x, (bytes, bytearray)) and len(x) > 0).any():
                    rutas = []
                    for i, val in enumerate(df[col].values):
                        if isinstance(val, (bytes, bytearray)) and len(val) > 0:
                            ext = self._detectar_formato_imagen(val)
                            nombre = f"{tabla}_{col}_{i}{ext}"
                            ruta = os.path.join(carpeta_imagenes, nombre)
                            with open(ruta, "wb") as f:
                                f.write(val)
                            rutas.append(nombre)
                        else:
                            rutas.append(None)
                    df[col] = rutas
        return df

    def _detectar_formato_imagen(self, blob):
        if blob is None:
            return ".png"
        if blob.startswith(b"\xff\xd8"):
            return ".jpg"
        if blob.startswith(b"\x89PNG"):
            return ".png"
        if blob.startswith(b"GIF8"):
            return ".gif"
        return ".bin"

    def importar_desde_excel(self, excel_path, carpeta_imagenes=None):
        xls = pd.ExcelFile(excel_path)
        conn = self.getConnection()
        cur = conn.cursor()
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("BEGIN TRANSACTION")
        for tabla in xls.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=tabla)
            if carpeta_imagenes:
                df = self._importar_imagenes(df, carpeta_imagenes, tabla)
            cur.execute(f"DELETE FROM {tabla}")
            if not df.empty:
                df = df.fillna("")
                cols = ",".join(df.columns)
                placeholders = ",".join(["?"] * len(df.columns))
                for _, fila in df.iterrows():
                    valores = tuple(fila.where(pd.notnull(fila), ""))
                    cur.execute(f"INSERT INTO {tabla} ({cols}) VALUES ({placeholders})", valores)
        conn.commit()
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()

    def _importar_imagenes(self, df, carpeta_imagenes, tabla):
        conn = self.getConnection()
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({tabla})")
        columnas_blob = [col[1] for col in cur.fetchall() if str(col[2]).upper() == "BLOB"]
        conn.close()
        for col in columnas_blob:
            if col in df.columns:
                nuevos = []
                for val in df[col].values:
                    if isinstance(val, str) and val and os.path.exists(os.path.join(carpeta_imagenes, val)):
                        ruta = os.path.join(carpeta_imagenes, val)
                        with open(ruta, "rb") as f:
                            nuevos.append(f.read())
                    else:
                        nuevos.append(val)
                df[col] = nuevos
        return df

    def crear_zip_backup(self, excel_path, carpeta_imagenes, zip_path):
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(excel_path, os.path.basename(excel_path))
            if carpeta_imagenes and os.path.exists(carpeta_imagenes):
                for f in os.listdir(carpeta_imagenes):
                    ruta = os.path.join(carpeta_imagenes, f)
                    zf.write(ruta, os.path.join("imagenes", f))

    def enviar_backup_por_correo(self, correo_emisor, password_emisor, correo_destino, zip_path):
        msg = MIMEMultipart()
        msg["From"] = correo_emisor
        msg["To"] = correo_destino
        msg["Subject"] = "Backup Cafebar"
        msg.attach(MIMEText("Adjunto encontrarás el backup de Cafebar (Excel + imágenes).", "plain"))
        with open(zip_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(zip_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(zip_path)}"'
        msg.attach(part)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(correo_emisor, password_emisor)
            smtp.send_message(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pagina = Configuracion()
    pagina.show()
    sys.exit(app.exec_())
