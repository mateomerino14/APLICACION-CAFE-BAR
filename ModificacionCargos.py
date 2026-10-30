import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from Pop_up_ModificacionCargos import Pop_up_ModificacionCargos 
from Rutas import get_db_path, get_images_dir

DB_PATH = get_db_path()

DIRECCION_IMAGEN = get_images_dir()

class ModificacionCargos(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            background-color: #f8fafc;
            font-family: 'Segoe UI', Arial, sans-serif;
            """)
        self.set_up()
        
    def set_up(self):
        self.layoutDatos = QHBoxLayout()
        self.layoutPrincipal = QVBoxLayout()
        self.setLayout(self.layoutPrincipal)
        self.layoutPrincipal.setContentsMargins(20,20,20,20)
        self.crearFiltro()
        self.campoModificar()
        self.showMaximized()
        
    def crearFiltro(self):
        layoutFiltro=QHBoxLayout()
        self.campoBusqueda=QLineEdit()
        self.campoBusqueda.setFixedWidth(300)
        textoBusqueda=QLabel("Nombre: ")
        botonBusqueda=QPushButton()
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
                                background-color: #4a7dbc;
                                border: none;
                                border-radius: 6px;
                                padding: 8px;
                            }
                            QPushButton:hover {
                                background-color: #6a9cec;
                            }
                        """)
        botonBusqueda.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\lupa.png"))
        botonBusqueda.clicked.connect(lambda:self.filtrarDatos(self.campoBusqueda.text().strip()))
        layoutFiltro.addStretch(3)
        layoutFiltro.addWidget(textoBusqueda,alignment=Qt.AlignLeft,stretch=0)
        layoutFiltro.addWidget(self.campoBusqueda,alignment=Qt.AlignLeft,stretch=60)
        layoutFiltro.addWidget(botonBusqueda,alignment=Qt.AlignLeft,stretch=40)
        layoutFiltro.addStretch(100)
        self.layoutPrincipal.addLayout(layoutFiltro)
        
    def obtener_subpantallas_por_cargo_agrupadas(self, id_cargo):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT p.nomPant, s.nomSubPant
            FROM PermisosCargoSubpantalla pcs
            JOIN Subpantalla s ON pcs.idSubPant = s.idSubPant
            JOIN Pantalla p ON s.idPant = p.idPant
            WHERE pcs.idCarg = ?
            ORDER BY p.idPant, s.nomSubPant
        """, (id_cargo,))
        resultados = c.fetchall()
        conn.close()
        
        agrupado = {}
        for pantalla, subpantalla in resultados:
            if pantalla not in agrupado:
                agrupado[pantalla] = []
            agrupado[pantalla].append(subpantalla)
        return agrupado
        
    def filtrarDatos(self,texto):
        tabla=self.tabla
        tabla.setRowCount(0)
        conn = sqlite3.connect(DB_PATH) 
        if(texto==""):
            consulta = """SELECT idCargo, nomCarg FROM Cargo ORDER BY nomCarg"""
            c = conn.cursor()
            resultado = c.execute(consulta)
        else:
            consulta = """SELECT idCargo, nomCarg FROM Cargo WHERE nomCarg LIKE ? ORDER BY nomCarg"""
            c = conn.cursor()
            resultado = c.execute(consulta,(f"{texto}%",))
        registros = resultado.fetchall()
        for f, registro in enumerate(registros):
            id_cargo, nom_cargo = registro
            subpantallas_agrupadas = self.obtener_subpantallas_por_cargo_agrupadas(id_cargo)
            
            container = QWidget()
            container.setStyleSheet("background-color: transparent;")
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)
            
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #f1f3f5;
                    width: 6px;
                    border-radius: 3px;
                }
                QScrollBar::handle:vertical {
                    background: #94a3b8;
                    min-height: 30px;
                    border-radius: 3px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #64748b;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
            
            content = QWidget()
            content.setStyleSheet("background-color: transparent;")
            content_layout = QVBoxLayout(content)
            content_layout.setSpacing(2)
            content_layout.setContentsMargins(8, 8, 8, 8)
            
            for pantalla, subpantallas in subpantallas_agrupadas.items():
                if subpantallas:
                    linea = f"<b>{pantalla}:</b> " + ", ".join(subpantallas)
                    label = QLabel(linea)
                    label.setStyleSheet("""
                        QLabel {
                            color: #2c3e50;
                            font-size: 13px;
                            padding: 1px 0px;
                            background-color: transparent;
                        }
                    """)
                    label.setWordWrap(True)
                    content_layout.addWidget(label)
            
            content_layout.addStretch()
            scroll.setWidget(content)
            container_layout.addWidget(scroll)
            
            self.tabla.insertRow(f)
            item_cargo = QTableWidgetItem(nom_cargo)
            item_cargo.setTextAlignment(Qt.AlignCenter)
            item_cargo.setToolTip(nom_cargo)
            self.tabla.setItem(f, 0, item_cargo)
            container.setFixedHeight(180)
            
            self.tabla.setCellWidget(f, 1, container)
            
            boton=QPushButton()
            boton.setStyleSheet("""background-color: #f8f9fa;""")
            boton.setCursor(Qt.PointingHandCursor)
            boton.setIcon(QIcon(f"{DIRECCION_IMAGEN}\\modificarEmpleado.jpg"))
            boton.setIconSize(QSize(50,50))
            boton.clicked.connect(lambda checked, fila=f, id_cargo=id_cargo, nom_cargo=nom_cargo: self.pantallaModificar(fila, id_cargo, nom_cargo))
            self.tabla.setCellWidget(f, 2, boton)
            self.tabla.setRowHeight(f, 160)
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
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setSelectionMode(QTableWidget.NoSelection) 
        self.tabla.setFocusPolicy(Qt.NoFocus)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers) 
        layoutTabla.addWidget(self.tabla)
        layoutCampoModificar.addWidget(campoTabla)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.verticalHeader().setDefaultSectionSize(150)
        self.layoutPrincipal.addLayout(layoutCampoModificar)   
    
    def cargarDatos(self):
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Cargo", "Accesos por Sección", "Accion"])
        anchos_columnas = {
            'Cargo': 250,
            'Accesos por Sección': 700,
            'Accion': 150
        }
        for i in range(3):
            nombre_col = self.tabla.horizontalHeaderItem(i).text() if self.tabla.horizontalHeaderItem(i) else ""
            self.tabla.setColumnWidth(i, anchos_columnas.get(nombre_col, 100))
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tabla.setWordWrap(True)
        self.filtrarDatos("")
        
    def pantallaModificar(self, fila, id_cargo, nom_cargo):
        scroll_position = self.tabla.verticalScrollBar().value() if hasattr(self, 'tabla') else 0
        try:
            pagina = Pop_up_ModificacionCargos(id_cargo, nom_cargo, self)
            pagina.exec_()
            if hasattr(self, 'tabla'):
                QTimer.singleShot(0, lambda: self.tabla.verticalScrollBar().setValue(scroll_position))
            self.filtrarDatos(self.campoBusqueda.text().strip())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al modificar: {str(e)}")
            if hasattr(self, 'tabla'):
                self.tabla.verticalScrollBar().setValue(scroll_position)
        
if __name__=="__main__":
    app = QApplication(sys.argv)
    pagina = ModificacionCargos()
    pagina.show()
    sys.exit(app.exec_())