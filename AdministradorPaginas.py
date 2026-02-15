import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import sqlite3
from datetime import datetime
from PaginaPrincipal import PaginaPrincipal
from Familia import Familia
from RegistrarPedidos import RegistrarPedidos
from PedidosPendientes import PedidosPendientes
from CobroPedidos import CobroPedidos
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

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'database', 'cafebar.db')

DB_PATH = get_db_path()

class AdministradorPaginas(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.permisos = self.cargar_permisos_usuario()
        self._pages = {}
        self.administradorMenu = None
        self.setWindowTitle("SISTEMA DE ADMINISTRACION DE CAFE-BAR")
        self.setStyleSheet("""self{
                              font-family: 'Segoe UI', Arial, sans-serif
                              }
                              QMessageBox {
                                  background-color: #ffffff;
                                  border: 1px solid #e2e8f0;
                                  border-radius: 8px;
                                  
                              }""")
        self._init_ui()
        self.showMaximized()
        self.setFixedSize(QApplication.primaryScreen().size())

    def cargar_permisos_usuario(self):
        if self.usuario == "DIRECTORIO":
            #Clientes Quitados
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
                SELECT p.nomPant
                FROM PermisosCargo pc
                JOIN Pantalla p ON pc.idPant = p.idPant
                WHERE pc.idCarg = ?
            """, (id_cargo,))
            permisos = [fila[0] for fila in cursor.fetchall()]
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
        opciones_permisos = {
            "HOME": "Home",
            "FAMILIA": "Familia",
            "CAJA": "Caja",
            #"CLIENTES": "Clientes",
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
            "CAJA": ["REGISTRAR PEDIDO", "PEDIDOS PENDIENTES", "PEDIDOS POR COBRAR"],
            #"CLIENTES": ["REGISTRAR CLIENTE", "MODIFICAR CLIENTE"],
            "ADMINISTRACION": ["CONFIGURACION", "IMPRESORAS"],
            "PRODUCTOS": ["REGISTRAR CATEGORIA", "MODIFICAR CATEGORIA",  "DAR DE BAJA CATEGORIA", "REGISTRAR PRODUCTO", "MODIFICAR PRODUCTO", "DAR DE BAJA PRODUCTO"],
            "SECCIONES": [],
            "STOCK": ["REGISTRAR INGREDIENTES", "MODIFICAR INGREDIENTES"],
            "PROMOCIONES": ["REGISTRAR PROMOCIONES", "MODIFICAR PROMOCIONES", "DAR DE BAJA PROMOCIONES"],
            "EMPLEADOS": ["REGISTRAR CARGOS", "MODIFICACION CARGOS", "REGISTRAR EMPLEADOS", "MODIFICAR EMPLEADOS", "DAR DE BAJA EMPLEADOS"],
            "REPORTES": []
        }
        def add_action(menu, text, func):
            act = QAction(text, self)
            menu.addAction(act)
            act.triggered.connect(func)
        for opcion, subopciones in opciones.items():
            permiso_requerido = opciones_permisos.get(opcion)
            if permiso_requerido not in self.permisos:
                continue
            btn = QPushButton(opcion)
            btn.setStyleSheet(estilo_menu)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFocusPolicy(Qt.NoFocus)
            if subopciones:
                menuWidget = QMenu()
                menuWidget.setStyleSheet(estilo_menu)
                for subopcion in subopciones:
                    if subopcion == "REGISTRAR PEDIDO":
                        add_action(menuWidget, subopcion, self.iniciarPaginaRegistroPedido)
                    elif subopcion == "PEDIDOS PENDIENTES":
                        add_action(menuWidget, subopcion, self.iniciarPaginaListaPedidosPendientes)
                    elif subopcion == "PEDIDOS POR COBRAR":
                        add_action(menuWidget, subopcion, self.iniciarPaginaCobroPedido)
                    elif subopcion == "REGISTRAR CLIENTE":
                        add_action(menuWidget, subopcion, self.iniciarPaginaRegistroCliente)
                    elif subopcion == "MODIFICAR CLIENTE":
                        add_action(menuWidget, subopcion, self.iniciarPaginaModificacionCliente)
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
                    elif subopcion == "REGISTRAR INGREDIENTES":
                        add_action(menuWidget, subopcion, self.iniciarPaginaRegistrarIngredientes)
                    elif subopcion == "MODIFICAR INGREDIENTES":
                        add_action(menuWidget, subopcion, self.iniciarPaginaModificarIngredientes)
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
                btn.setMenu(menuWidget)
            else:
                if opcion == "HOME":
                    btn.clicked.connect(self.iniciarPaginaPrincipal)
                elif opcion == "FAMILIA":
                    btn.clicked.connect(self.iniciarPaginaFamilia)
                elif opcion == "SECCIONES":
                    btn.clicked.connect(self.iniciarPaginaSecciones)
                elif opcion == "REPORTES":
                    btn.clicked.connect(self.iniciarPaginaReportes)
            layoutMenu.addWidget(btn)
        menuContainer = QWidget()
        menuContainer.setStyleSheet("background: #5d9cec;")
        menuContainer.setLayout(layoutMenu)
        self.layoutPrincipal.addWidget(menuContainer)

    def _create_page(self, name: str) -> QWidget:
        if name == "Home":                      return PaginaPrincipal()
        if name == "Familia":                   return Familia()
        if name == "RegistrarPedidos":          return RegistrarPedidos(self.usuario)
        if name == "PedidosPendientes":         return PedidosPendientes()
        if name == "CobroPedidos":              return CobroPedidos()
        if name == "RegistroClientes":          return RegistroClientes()
        if name == "ModificacionClientes":      return ModificacionClientes()
        if name == "Configuracion":             return Configuracion()
        if name == "Impresoras":                return Impresoras()
        if name == "RegistroCategorias":        return RegistroCategoriasSubcategorias()
        if name == "ModificacionCategorias":  return ModificacionCategorias()
        if name == "RegistroProductos":         return RegistroProductos()
        if name == "ModificacionProductos":     return ModificacionProductos()
        if name == "DarBajaProductos":          return DarBajaProductos()
        if name == "Secciones":                 return Administracion_Secciones_Mesas()
        if name == "RegistroIngredientes":      return RegistroIngredientes()
        if name == "ModificacionIngredientes":  return ModificacionIngredientes()
        if name == "Reportes":                  return Reportes()
        if name == "RegistroEmpleados":         return RegistroEmpleados()
        if name == "ModificacionEmpleados":     return ModificacionEmpleados()
        if name == "DarBajaEmpleados":          return DarBajaEmpleados()
        if name == "RegistroPromociones":       return RegistroPromociones()
        if name == "ModificacionPromociones":   return ModificacionPromociones()
        if name == "DarBajaPromociones":        return DarBajaPromociones()
        if name == "RegistroCargos":            return RegistroCargos()
        if name == "ModificacionCargos":        return ModificacionCargos()
        if name == "DarBajaCategorias":         return DarBajaCategorias()
        raise KeyError(name)

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

    def iniciarPaginaListaPedidosPendientes(self):
        self.titulo.setText("PEDIDOS PENDIENTES")
        self.show_page("PedidosPendientes", after=lambda p: p.cargarVentasPreparacion())

    def iniciarPaginaCobroPedido(self):
        self.titulo.setText("COBRO DE PEDIDOS")
        self.show_page("CobroPedidos", after=lambda p: p.cargarDatosTabla())

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
