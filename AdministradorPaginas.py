import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sqlite3
from datetime import datetime
from PaginaPrincipal import PaginaPrincipal
from Familia import Familia
from RegistrarPedidos import RegistrarPedidos
from RegistroClientes import RegistroClientes
from ModificacionClientes import ModificacionClientes
from Configuracion import Configuracion
from Impresoras import Impresoras
from RegistroCategoriasSubcategorias import RegistroCategoriasSubcategorias
from RegistroProductos import RegistroProductos
from ModificacionProductos import ModificacionProductos
from DarBajaCategorias import DarBajaCategorias
from DarBajaProductos import DarBajaProductos
from Administracion_Secciones_Mesas import Administracion_Secciones_Mesas
from RegistroIngredientes import RegistroIngredientes
from ModificacionIngredientes import ModificacionIngredientes
from Reportes import Reportes
from RegistroEmpleados import RegistroEmpleados
from ModificacionEmpleados import ModificacionEmpleados
from DarBajaEmpleados import DarBajaEmpleados
from RegistroPromociones import RegistroPromociones
from ModificacionPromociones import ModificacionPromociones
from DarBajaPromociones import DarBajaPromociones
from RegistroCargos import RegistroCargos
from ModificacionCargos import ModificacionCargos
from ModificacionCategorias import ModificacionCategorias
from Login import Login
from Rutas import get_db_path

DB_PATH = get_db_path()

PAGINAS = {
    "Home": PaginaPrincipal,
    "Familia": Familia,
    "RegistroClientes": RegistroClientes,
    "ModificacionClientes": ModificacionClientes,
    "Configuracion": Configuracion,
    "Impresoras": Impresoras,
    "RegistroCategorias": RegistroCategoriasSubcategorias,
    "ModificacionCategorias": ModificacionCategorias,
    "RegistroProductos": RegistroProductos,
    "ModificacionProductos": ModificacionProductos,
    "DarBajaProductos": DarBajaProductos,
    "Secciones": Administracion_Secciones_Mesas,
    "RegistroIngredientes": RegistroIngredientes,
    "ModificacionIngredientes": ModificacionIngredientes,
    "Reportes": Reportes,
    "RegistroEmpleados": RegistroEmpleados,
    "ModificacionEmpleados": ModificacionEmpleados,
    "DarBajaEmpleados": DarBajaEmpleados,
    "RegistroPromociones": RegistroPromociones,
    "ModificacionPromociones": ModificacionPromociones,
    "DarBajaPromociones": DarBajaPromociones,
    "RegistroCargos": RegistroCargos,
    "ModificacionCargos": ModificacionCargos,
    "DarBajaCategorias": DarBajaCategorias,
}


class AdministradorPaginas(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.permisos = self.cargar_permisos_usuario()
        self._pages = {}
        self.administradorMenu = None
        self.setWindowTitle("SISTEMA DE ADMINISTRACION DE CAFE-BAR")
        self.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        self._init_ui()
        self.showMaximized()
        self.setFixedSize(QApplication.primaryScreen().size())

    def cargar_permisos_usuario(self):
        if self.usuario == "DIRECTORIO":
            return ["Home", "Familia", "Caja", "Administracion",
                    "Productos", "Secciones", "Stock", "Promociones", "Empleados", "Reportes"]
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT idCargo FROM Empleado WHERE aliasEmp = ?", (self.usuario,))
            resultado = cursor.fetchone()
            if not resultado:
                return ["Home"]
            id_cargo = resultado[0]
            cursor.execute("""
                SELECT DISTINCT p.nomPant
                FROM PermisosCargo pc
                JOIN Pantalla p ON pc.idPant = p.idPant
                WHERE pc.idCarg = ?
            """, (id_cargo,))
            permisos_pantallas = [fila[0] for fila in cursor.fetchall()]
            cursor.execute("""
                SELECT DISTINCT sp.accion
                FROM PermisosCargoSubpantalla pcs
                JOIN Subpantalla sp ON pcs.idSubPant = sp.idSubPant
                WHERE pcs.idCarg = ?
            """, (id_cargo,))
            permisos_subpantallas = [fila[0] for fila in cursor.fetchall()]
            permisos = list(set(permisos_pantallas + permisos_subpantallas))
            if "Home" not in permisos:
                permisos.append("Home")
            return permisos
        except sqlite3.Error as e:
            print(f"Error al cargar permisos: {e}")
            return ["Home"]
        finally:
            if conn:
                conn.close()

    def _init_ui(self):
        self.setUpdatesEnabled(False)
        contenedor = QWidget()
        self.setCentralWidget(contenedor)
        self.layoutPrincipal = QVBoxLayout(contenedor)
        self.crearParteSuperior()
        self.crearMenu()
        self.administradorMenu = QStackedWidget()
        self.layoutPrincipal.addWidget(self.administradorMenu)
        self.titulo.setText("PAGINA PRINCIPAL")
        self.show_page("Home")
        self.setUpdatesEnabled(True)

    def crearParteSuperior(self):
        layoutHorizontalSup = QHBoxLayout()
        layoutHorizontalSup.setContentsMargins(20, 10, 20, 10)
        nombre_usuario = "DIRECTORIO" if self.usuario == "" else self.usuario
        usuario_label = QLabel(f"Usuario: {nombre_usuario}")
        usuario_label.setStyleSheet("""
            font-size: 20px;
            color: #2c3e50;
            font-family: 'Verdana';
            padding: 5px;
            font-weight: bold;
        """)
        layoutHorizontalSup.addWidget(usuario_label)
        self.titulo = QLabel("")
        self.titulo.setStyleSheet("""
            padding-top: 20px;
            font-size: 30px;
            font-weight: bold;
            color: #2c3e50;
            font-family: 'Verdana';
        """)
        layoutHorizontalSup.addStretch(15)
        layoutHorizontalSup.addWidget(self.titulo, alignment=Qt.AlignCenter, stretch=140)
        botonSalir = QPushButton("SALIR")
        botonSalir.setStyleSheet("""
            QPushButton {
                font-family: Verdana;
                background-color: #e74c3c;
                color: white;
                font-size: 18px;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
                margin-top:20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        botonSalir.setCursor(Qt.PointingHandCursor)
        botonSalir.clicked.connect(self.cerrarAplicacion)
        botonCerrarSesion = QPushButton("CERRAR SESION")
        botonCerrarSesion.setStyleSheet("""
            QPushButton {
                font-family: Verdana;
                background-color: orange;
                color: white;
                font-size: 18px;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
                margin-top:20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #b87e14; }
        """)
        botonCerrarSesion.setCursor(Qt.PointingHandCursor)
        botonCerrarSesion.clicked.connect(self.cerrarSesion)
        layoutHorizontalSup.addWidget(botonCerrarSesion, alignment=Qt.AlignRight)
        layoutHorizontalSup.addWidget(botonSalir, alignment=Qt.AlignRight, stretch=30)
        self.layoutPrincipal.addLayout(layoutHorizontalSup)

    def crearMenu(self):
        layoutMenu = QHBoxLayout()
        layoutMenu.setContentsMargins(0, 0, 0, 0)
        layoutMenu.setSpacing(1)
        estilo_menu = """
        QPushButton {
            padding: 15px 5px;
            margin: 0;
            color: #2c3e50;
            font-weight: bold;
            font-size: 16px;
            border: none;
            background: #5d9cec;
            min-width: 120px;
            qproperty-alignment: AlignCenter;
            border-right: 1px solid #4a89dc;
        }
        QPushButton:hover { background-color: #4a89dc; color: white; }
        QMenu {
            background-color: white;
            border: 1px solid #ddd;
            padding: 5px;
            font-size: 14px;
            min-width: 180px;
            border-radius: 4px;
        }
        QMenu::item {
            padding: 8px 25px 8px 15px;
            color: #2c3e50;
            background-color: transparent;
            font-weight: bold;
        }
        QMenu::item:selected { background-color: #e6f2ff; color: #2c3e50; }
        QMenu::separator { height: 1px; background: #eee; margin: 5px 0; }
        """
        mapa_acciones = {
            "REGISTRAR PEDIDO": "REGISTRAR_PEDIDO",
            "CONFIGURACION": "CONFIGURACION",
            "IMPRESORAS": "IMPRESORAS",
            "REGISTRAR CATEGORIA": "REGISTRAR_CATEGORIA",
            "MODIFICAR CATEGORIA": "MODIFICAR_CATEGORIA",
            "DAR DE BAJA CATEGORIA": "BAJA_CATEGORIA",
            "REGISTRAR PRODUCTO": "REGISTRAR_PRODUCTO",
            "MODIFICAR PRODUCTO": "MODIFICAR_PRODUCTO",
            "DAR DE BAJA PRODUCTO": "BAJA_PRODUCTO",
            "REGISTRAR INGREDIENTES": "REGISTRAR_INGREDIENTES",
            "MODIFICAR INGREDIENTES": "MODIFICAR_INGREDIENTES",
            "REGISTRAR PROMOCIONES": "REGISTRAR_PROMOCIONES",
            "MODIFICAR PROMOCIONES": "MODIFICAR_PROMOCIONES",
            "DAR DE BAJA PROMOCIONES": "BAJA_PROMOCIONES",
            "REGISTRAR CARGOS": "REGISTRAR_CARGOS",
            "MODIFICACION CARGOS": "MODIFICAR_CARGOS",
            "REGISTRAR EMPLEADOS": "REGISTRAR_EMPLEADOS",
            "MODIFICAR EMPLEADOS": "MODIFICAR_EMPLEADOS",
            "DAR DE BAJA EMPLEADOS": "BAJA_EMPLEADOS",
            "VER REPORTES": "VER_REPORTES",
            "ADMINISTRAR SECCIONES": "ADMIN_SECCIONES",
            "VER FAMILIA": "VER_FAMILIA"
        }
        opciones_permisos = {
            "HOME": "Home",
            "FAMILIA": "Familia",
            "CAJA": "Caja",
            "ADMINISTRACION": "Administracion",
            "PRODUCTOS": "Productos",
            "SECCIONES": "Secciones",
            "STOCK": "Stock",
            "PROMOCIONES": "Promociones",
            "EMPLEADOS": "Empleados",
            "REPORTES": "Reportes"
        }
        opciones = {
            "HOME": [],
            "FAMILIA": [],
            "CAJA": ["REGISTRAR PEDIDO"],
            "ADMINISTRACION": ["CONFIGURACION", "IMPRESORAS"],
            "PRODUCTOS": ["REGISTRAR CATEGORIA", "MODIFICAR CATEGORIA",  "DAR DE BAJA CATEGORIA", "REGISTRAR PRODUCTO", "MODIFICAR PRODUCTO", "DAR DE BAJA PRODUCTO"],
            "SECCIONES": ["ADMINISTRAR SECCIONES"],
            "STOCK": ["REGISTRAR INGREDIENTES", "MODIFICAR INGREDIENTES"],
            "PROMOCIONES": ["REGISTRAR PROMOCIONES", "MODIFICAR PROMOCIONES", "DAR DE BAJA PROMOCIONES"],
            "EMPLEADOS": ["REGISTRAR CARGOS", "MODIFICACION CARGOS", "REGISTRAR EMPLEADOS", "MODIFICAR EMPLEADOS", "DAR DE BAJA EMPLEADOS"],
            "REPORTES": ["VER REPORTES"]
        }
        def add_action(menu, text, func):
            act = QAction(text, self)
            menu.addAction(act)
            act.triggered.connect(func)
        for opcion, subopciones in opciones.items():
            permiso_requerido = opciones_permisos.get(opcion)
            if permiso_requerido not in self.permisos and permiso_requerido not in [p for p in self.permisos if '_' in p]:
                tiene_permiso = False
                for subopcion in subopciones:
                    accion = mapa_acciones.get(subopcion)
                    if accion and accion in self.permisos:
                        tiene_permiso = True
                        break
                if not tiene_permiso:
                    continue
            btn = QPushButton(opcion)
            btn.setStyleSheet(estilo_menu)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFocusPolicy(Qt.NoFocus)
            if subopciones:
                menuWidget = QMenu()
                menuWidget.setStyleSheet(estilo_menu)
                for subopcion in subopciones:
                    accion = mapa_acciones.get(subopcion)
                    if self.usuario == "DIRECTORIO" or accion in self.permisos or permiso_requerido in self.permisos:
                        if subopcion == "REGISTRAR PEDIDO":
                            add_action(menuWidget, subopcion, self.iniciarPaginaRegistroPedido)
                        elif subopcion == "CONFIGURACION":
                            add_action(menuWidget, subopcion, self.iniciarPaginaConfiguracion)
                        elif subopcion == "IMPRESORAS":
                            add_action(menuWidget, subopcion, self.iniciarPaginaImpresoras)
                        elif subopcion == "MODIFICAR CATEGORIA":
                            add_action(menuWidget, subopcion, self.iniciarPaginaModificacionCategorias)
                        elif subopcion == "REGISTRAR CATEGORIA":
                            add_action(menuWidget, subopcion, self.iniciarPaginaCategorias)
                        elif subopcion == "DAR DE BAJA CATEGORIA":
                            add_action(menuWidget, subopcion, self.iniciarPaginaDarBajaCategorias)
                        elif subopcion == "REGISTRAR PRODUCTO":
                            add_action(menuWidget, subopcion, self.iniciarPaginaRegistoProducto)
                        elif subopcion == "MODIFICAR PRODUCTO":
                            add_action(menuWidget, subopcion, self.iniciarPaginaModificacionProducto)
                        elif subopcion == "DAR DE BAJA PRODUCTO":
                            add_action(menuWidget, subopcion, self.iniciarPaginaDarBajaProducto)
                        elif subopcion == "ADMINISTRAR SECCIONES":
                            add_action(menuWidget, subopcion, self.iniciarPaginaSecciones)
                        elif subopcion == "REGISTRAR INGREDIENTES":
                            add_action(menuWidget, subopcion, self.iniciarPaginaRegistrarIngredientes)
                        elif subopcion == "MODIFICAR INGREDIENTES":
                            add_action(menuWidget, subopcion, self.iniciarPaginaModificarIngredientes)
                        elif subopcion == "VER REPORTES":
                            add_action(menuWidget, subopcion, self.iniciarPaginaReportes)
                        elif subopcion == "REGISTRAR EMPLEADOS":
                            add_action(menuWidget, subopcion, self.iniciarPaginaRegistrarEmpleados)
                        elif subopcion == "MODIFICAR EMPLEADOS":
                            add_action(menuWidget, subopcion, self.iniciarPaginaModificarEmpleados)
                        elif subopcion == "DAR DE BAJA EMPLEADOS":
                            add_action(menuWidget, subopcion, self.iniciarPaginaDarBajaEmpleados)
                        elif subopcion == "REGISTRAR PROMOCIONES":
                            add_action(menuWidget, subopcion, self.iniciarPaginaRegistrarPromociones)
                        elif subopcion == "MODIFICAR PROMOCIONES":
                            add_action(menuWidget, subopcion, self.iniciarPaginaModificacionPromociones)
                        elif subopcion == "DAR DE BAJA PROMOCIONES":
                            add_action(menuWidget, subopcion, self.iniciarPaginaDarBajaPromociones)
                        elif subopcion == "REGISTRAR CARGOS":
                            add_action(menuWidget, subopcion, self.iniciarPaginaRegistrarCargos)
                        elif subopcion == "MODIFICACION CARGOS":
                            add_action(menuWidget, subopcion, self.iniciarPaginaModificacionCargos)
                if not menuWidget.isEmpty():
                    btn.setMenu(menuWidget)
                else:
                    continue
            else:
                if opcion == "HOME":
                    btn.clicked.connect(self.iniciarPaginaPrincipal)
                elif opcion == "FAMILIA":
                    if self.usuario == "DIRECTORIO" or "VER_FAMILIA" in self.permisos:
                        btn.clicked.connect(self.iniciarPaginaFamilia)
                    else:
                        continue
                elif opcion == "SECCIONES":
                    if self.usuario == "DIRECTORIO" or "ADMIN_SECCIONES" in self.permisos:
                        btn.clicked.connect(self.iniciarPaginaSecciones)
                    else:
                        continue
                elif opcion == "REPORTES":
                    if self.usuario == "DIRECTORIO" or "VER_REPORTES" in self.permisos:
                        btn.clicked.connect(self.iniciarPaginaReportes)
                    else:
                        continue
            layoutMenu.addWidget(btn)
        menuContainer = QWidget()
        menuContainer.setStyleSheet("background: #5d9cec;")
        menuContainer.setLayout(layoutMenu)
        self.layoutPrincipal.addWidget(menuContainer)

    def _create_page(self, name: str) -> QWidget:
        if name == "RegistrarPedidos":
            return RegistrarPedidos(self.usuario)
        return PAGINAS[name]()

    def show_page(self, name: str, after=None):
        if name not in self._pages:
            w = self._create_page(name)
            self._pages[name] = w
            self.administradorMenu.addWidget(w)
        self.administradorMenu.setCurrentWidget(self._pages[name])
        if name=="RegistrarPedidos":
            self._pages[name]._clear_grid(self._pages[name].layoutProductos)
            self._pages[name].cargarCategorias()
            self._pages[name].actualizarNumeroVenta(datetime.now().date())
        else:
            if name=="Secciones":
                self._pages[name].actualizarYMostrar()
        if after:
            after(self._pages[name])

    def iniciarPaginaPrincipal(self):
        self.titulo.setText("PAGINA PRINCIPAL")
        self.show_page("Home")

    def iniciarPaginaFamilia(self):
        self.titulo.setText("FAMILIA")
        self.show_page("Familia", after=lambda p: p.cargarCategorias())

    def iniciarPaginaRegistroPedido(self):
        self.titulo.setText("REGISTRAR PEDIDO")
        self.show_page("RegistrarPedidos")

    def iniciarPaginaRegistroCliente(self):
        self.titulo.setText("REGISTRAR CLIENTE")
        self.show_page("RegistroClientes")

    def iniciarPaginaModificacionCliente(self):
        self.titulo.setText("MODIFICACION DE CLIENTES")
        self.show_page("ModificacionClientes", after=lambda p: p.filtrarDatos(""))

    def iniciarPaginaConfiguracion(self):
        self.titulo.setText("CONFIGURACIONES")
        self.show_page("Configuracion")

    def iniciarPaginaDarBajaCategorias(self):
        self.titulo.setText("DAR DE BAJA CATEGORÍAS")
        self.show_page("DarBajaCategorias", after=lambda p: p.filtrarDatos(""))
    
    def iniciarPaginaImpresoras(self):
        self.titulo.setText("ADMINISTRACION DE IMPRESORAS")
        self.show_page("Impresoras")

    def iniciarPaginaCategorias(self):
        self.titulo.setText("REGISTRAR CATEGORIA")
        self.show_page("RegistroCategorias")

    def iniciarPaginaRegistoProducto(self):
        self.titulo.setText("REGISTRAR PRODUCTO")
        def post(p):
            p.cargarSubcategorias(); p.cargarCategorias(); p.cargarIngredientes()
        self.show_page("RegistroProductos", after=post)

    def iniciarPaginaModificacionProducto(self):
        self.titulo.setText("MODIFICAR PRODUCTO")
        self.show_page("ModificacionProductos", after=lambda p: p.filtrarDatos(""))

    def iniciarPaginaDarBajaProducto(self):
        self.titulo.setText("DAR DE BAJA PRODUCTO")
        self.show_page("DarBajaProductos", after=lambda p: p.filtrarDatos(""))

    def iniciarPaginaSecciones(self):
        self.titulo.setText("ADMINISTRACION DE SECCIONES")
        self.show_page("Secciones")

    def iniciarPaginaRegistrarIngredientes(self):
        self.titulo.setText("REGISTRAR INGREDIENTES")
        self.show_page("RegistroIngredientes")

    def iniciarPaginaModificarIngredientes(self):
        self.titulo.setText("MODIFICACION DE INGREDIENTES")
        self.show_page("ModificacionIngredientes", after=lambda p: p.filtrarDatos(""))

    def iniciarPaginaReportes(self):
        self.titulo.setText("RESPORTES ESTADISTICOS")
        self.show_page("Reportes", after=lambda p: QTimer.singleShot(0, p.cargarEmpleados))

    def iniciarPaginaRegistrarEmpleados(self):
        self.titulo.setText("REGISTRAR EMPLEADOS")
        self.show_page("RegistroEmpleados", after=lambda p: p.cargarDatosComboBox())

    def iniciarPaginaModificarEmpleados(self):
        self.titulo.setText("MODIFICAR EMPLEADOS")
        self.show_page("ModificacionEmpleados", after=lambda p: p.filtrarDatos(""))

    def iniciarPaginaDarBajaEmpleados(self):
        self.titulo.setText("DAR DE BAJA A EMPLEADOS")
        self.show_page("DarBajaEmpleados", after=lambda p: p.filtrarDatos(""))

    def iniciarPaginaRegistrarPromociones(self):
        self.titulo.setText("REGISTRAR PROMOCIONES")
        self.show_page("RegistroPromociones", after=lambda p: p.cargar_categorias())
        
    def iniciarPaginaModificacionCategorias(self):
        self.titulo.setText("MODIFICAR CATEGORIAS")
        self.show_page("ModificacionCategorias", after=lambda p: p.filtrarDatos(""))    

    def iniciarPaginaModificacionPromociones(self):
        self.titulo.setText("MODIFICAR PROMOCIONES")
        self.show_page("ModificacionPromociones", after=lambda p: p.filtrarDatos(""))

    def iniciarPaginaDarBajaPromociones(self):
        self.titulo.setText("DAR DE BAJA PROMOCIONES")
        self.show_page("DarBajaPromociones", after=lambda p: p.filtrarDatos(""))

    def iniciarPaginaRegistrarCargos(self):
        self.titulo.setText("REGISTRAR CARGOS")
        self.show_page("RegistroCargos")

    def iniciarPaginaModificacionCargos(self):
        self.titulo.setText("MODIFICAR CARGOS")
        self.show_page("ModificacionCargos", after=lambda p: p.filtrarDatos(""))

    def cerrarSesion(self):
        self.paginaLogin = Login()
        self.paginaLogin.show()
        self.close()

    def cerrarAplicacion(self):
        self.close()
        sys.exit(0)

if __name__ == "__main__":
    aplicacion = QApplication(sys.argv)
    pagina = AdministradorPaginas("")
    pagina.show()
    sys.exit(aplicacion.exec_())