# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
# from PyQt5.QtCore import *
# import sys
# import os
# from Backend.Utils.Dev.hot_reload import MonitorChanges
# from Backend.Database.init__ import DatabaseInitializer
# from Frontend.Pages.Login.login import Login



# def main():
#     init_db = DatabaseInitializer()
#     init_db.initialize_database()
#     aplication = QApplication(sys.argv)
#     vigilant = MonitorChanges()
#     begin = Login()
#     begin.show()
#     result = aplication.exec_()

# if __name__ == "__main__":
#     main()


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import os
from Login import Login
from init_db import inciarBaseDatos

# ARCHIVOS_A_VIGILAR = [
#     'Administracion_Secciones_Mesas.py',
#     'AdministradorPaginas.py',
#     'CobroPedidos.py',
#     'Configuracion.py',
#     'DarBajaCategorias.py',
#     'DarBajaEmpleados.py',
#     'DarBajaProductos.py',
#     'DarBajaPromociones.py',
#     'Familia.py',
#     'Impresion.py',
#     'Impresoras.py',
#     'init_db.py',
#     'Login.py',
#     'Main.py',
#     'ModificacionCargos.py',
#     'ModificacionCategorias.py',
#     'ModificacionClientes.py',
#     'ModificacionEmpleados.py',
#     'ModificacionIngredientes.py',
#     'ModificacionProductos.py',
#     'ModificacionPromociones.py',
#     'ModificacionSeccion.py',
#     'PaginaPrincipal.py',
#     'PedidosPendientes.py',
#     'Pop_upRegistroCliente.py',
#     'Pop_up_ModificacionCargos.py',
#     'Pop_up_ModificacionClientes.py',
#     'Pop_up_ModificacionEmpleado.py',
#     'Pop_up_ModificacionIngredientes.py',
#     'Pop_up_ModificacionProductos.py',
#     'Pop_up_ModificacionSubcategoria.py',
#     'Pop_up_ModificarPromocion.py',
#     'Pop_up_RegistrarEmpleados.py',
#     'Pop_up_RegistroProductoModificacionIngrediente.py',
#     'Pop_up_RegistroProductos.py',
#     'Pop_up_Registro_Seccion.py',
#     'RegistrarPedidos.py',
#     'RegistroCargos.py',
#     'RegistroCategoriasSubcategorias.py',
#     'RegistroClientes.py',
#     'RegistroEmpleados.py',
#     'RegistroIngredientes.py',
#     'RegistroProductos.py',
#     'RegistroPromociones.py',
#     'Reportes.py'
# ]

# class VigilanteCambios(QObject):
#     def __init__(self):
#         super().__init__()
#         self.ultimos_tiempos = {}
#         for archivo in ARCHIVOS_A_VIGILAR:
#             ruta_completa = os.path.join(os.path.dirname(__file__), archivo)
#             if os.path.exists(ruta_completa):
#                 self.ultimos_tiempos[archivo] = os.path.getmtime(ruta_completa)
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.vigilar)
#         self.timer.start(1000)
    
#     def vigilar(self):
#         for archivo in ARCHIVOS_A_VIGILAR:
#             ruta_completa = os.path.join(os.path.dirname(__file__), archivo)
#             if os.path.exists(ruta_completa):
#                 mod_time = os.path.getmtime(ruta_completa)
#                 if archivo in self.ultimos_tiempos:
#                     if mod_time > self.ultimos_tiempos[archivo]:
#                         QTimer.singleShot(500, self.reiniciar_app)
#                         return
#                 self.ultimos_tiempos[archivo] = mod_time
    
#     def reiniciar_app(self):
#         os.execv(sys.executable, ['python'] + sys.argv)

def main():
    inciarBaseDatos()
    aplicacion = QApplication(sys.argv)
    
    #vigilante = VigilanteCambios()
    
    inicio = Login()
    inicio.show()
    resultado = aplicacion.exec_()

if __name__ == "__main__":
    main()