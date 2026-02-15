import sys
import os
import sqlite3
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
import usb.core
import usb.util
import serial
import win32print 
import serial.tools.list_ports

def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'database', 'cafebar.db')

DB_PATH = get_db_path()

class ManejadorImpresion(QObject):
    impresion_completada = pyqtSignal(str, bool) 

    def __init__(self):
        super().__init__()
        self.conn_impresion = sqlite3.connect(DB_PATH)
        self.cursor_impresion = self.conn_impresion.cursor()
    
    def obtener_impresora(self, tipo):
        try:
            if tipo == "Barra":
                self.cursor_impresion.execute(
                    "SELECT idImpresora, idVendor, idProducto, dispositivo, descripcion, es_barra, es_cocina FROM Impresora WHERE es_barra = 1"
                )
            else:
                self.cursor_impresion.execute(
                    "SELECT idImpresora, idVendor, idProducto, dispositivo, descripcion, es_barra, es_cocina FROM Impresora WHERE es_cocina = 1"
                )
            impresoras = self.cursor_impresion.fetchall()
            print(f"DEBUG obtener_impresora({tipo}): {len(impresoras)} encontradas")
            if impresoras:
                impresora = impresoras[0]
                print(f"  ✓ Impresora: {impresora[3]}")
                print(f"    Descripcion: {impresora[4]}, VID: {impresora[1]}, PID: {impresora[2]}")
                print(f"    Barra: {impresora[5]}, Cocina: {impresora[6]}")
                return {
                    'id': impresora[0],
                    'vid': impresora[1] if impresora[1] else 0,
                    'pid': impresora[2] if impresora[2] else 0,
                    'dispositivo': impresora[3] if impresora[3] else '',
                    'descripcion': impresora[4] if impresora[4] else '',
                    'es_barra': impresora[5],
                    'es_cocina': impresora[6]
                }
            else:
                print(f"  ✗ No hay impresora configurada para {tipo}")
                return None
        except Exception as e:
            print(f"Error en obtener_impresora({tipo}): {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def imprimir_ticket(self, datos_venta, items):
        try:
            print("\n=== INICIANDO IMPRESIÓN TICKET ===")
            impresora = self.obtener_impresora("Barra")
            if not impresora:
                return False, "No hay impresora configurada para Barra"
            contenido = self._construir_ticket(datos_venta, items)
            print(f"Imprimiendo en: {impresora.get('dispositivo', 'Sin nombre')}")
            print(f"VID/PID: {impresora.get('vid', 0)}/{impresora.get('pid', 0)}")
            es_termica = self._es_impresora_termica(impresora)
            print(f"¿Es impresora térmica?: {es_termica}")
            exito, mensaje = self._intentar_imprimir(impresora, contenido, es_termica)
            if not exito:
                print(f"Fallo impresión directa: {mensaje}")
                return self._guardar_en_archivo(contenido, "Barra")
            return exito, mensaje  
        except Exception as e:
            error_msg = f"Error al imprimir ticket: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def imprimir_cocina(self, datos_venta, items):
        try:
            print("\n=== INICIANDO IMPRESIÓN COCINA ===")
            impresora = self.obtener_impresora("Cocina")
            if not impresora:
                return False, "No hay impresora configurada para Cocina"
            contenido = self._construir_pedido_cocina(datos_venta, items)
            print(f"Imprimiendo en: {impresora.get('dispositivo', 'Sin nombre')}")
            print(f"VID/PID: {impresora.get('vid', 0)}/{impresora.get('pid', 0)}")
            es_termica = self._es_impresora_termica(impresora)
            print(f"¿Es impresora térmica?: {es_termica}")
            exito, mensaje = self._intentar_imprimir(impresora, contenido, es_termica)
            if not exito:
                print(f"Fallo impresión directa: {mensaje}")
                return self._guardar_en_archivo(contenido, "Cocina")
            return exito, mensaje
        except Exception as e:
            error_msg = f"Error al imprimir pedido cocina: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    

    def _es_impresora_termica(self, impresora_info):
        dispositivo = impresora_info.get('dispositivo', '').lower()
        descripcion = impresora_info.get('descripcion', '').lower()
        keywords_termicas = [
            'thermal', 'termica', 'ticket', 'receipt', 'pos', 
            'tm-t20', 'tm-t70', 'tm-t88', 'tm-', 'tsp', 
            'bixolon', 'star', 'citizen', 'zjiang', 'serial printer'
        ]
        texto_completo = f"{dispositivo} {descripcion}".lower()
        for keyword in keywords_termicas:
            if keyword in texto_completo:
                return True
        vids_termicas = [0x04B8, 0x03F0, 0x04F9, 0x0924, 0x0525]
        vid = impresora_info.get('vid', 0)
        if vid in vids_termicas:
            return True
        if 'com' in dispositivo:
            return True
        return False
    
    def _intentar_imprimir(self, impresora, contenido, es_termica=True):
        print(f"\n🔍 _intentar_imprimir:")
        print(f"  Dispositivo: {impresora.get('dispositivo')}")
        print(f"  VID: {impresora.get('vid')}, PID: {impresora.get('pid')}")
        print(f"  Descripcion: {impresora.get('descripcion')}")
        print(f"  Es térmica: {es_termica}")
        contenido = self._limpiar_caracteres_especiales(contenido)
        dispositivo_nombre = impresora.get('dispositivo', '').strip()
        if dispositivo_nombre and impresora.get('vid', 0) == 0 and impresora.get('pid', 0) == 0:
            print(f"  📄 Impresora Windows con nombre: {dispositivo_nombre}")
            return self._imprimir_por_windows_nombre(dispositivo_nombre, contenido, es_termica)
        if dispositivo_nombre and ('COM' in dispositivo_nombre.upper() or '/dev/' in dispositivo_nombre):
            print(f"  Intentando puerto serie: {dispositivo_nombre}")
            return self._imprimir_por_puerto(dispositivo_nombre, contenido, es_termica)
        elif impresora.get('vid', 0) > 0 and impresora.get('pid', 0) > 0:
            print(f"  Intentando USB: VID={impresora['vid']}, PID={impresora['pid']}")
            return self._imprimir_por_usb(impresora['vid'], impresora['pid'], contenido, es_termica)
        else:
            print("  Intentando impresora predeterminada de Windows")
            return self._imprimir_por_windows(contenido, es_termica)
    

    def _limpiar_caracteres_especiales(self, texto):
        reemplazos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N',
            'ü': 'u', 'Ü': 'U',
            '¿': '?', '¡': '!',
            '´': "'", '`': "'",
            '«': '"', '»': '"',
            '€': 'EUR', '£': 'GBP', '$': 'USD',
            '°': ' grados',
            '×': 'x', '÷': '/',
            '©': '(c)', '®': '(r)', '™': '(tm)',
            '…': '...', '—': '-', '–': '-',
            'ç': 'c', 'Ç': 'C',
            'ß': 'ss', 'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
            'Ä': 'AE', 'Ö': 'OE', 'Ü': 'UE'
        }
        resultado = []
        for char in texto:
            if char in reemplazos:
                resultado.append(reemplazos[char])
            else:
                if 32 <= ord(char) <= 126:
                    resultado.append(char)
                elif char == '\n' or char == '\r' or char == '\t':
                    resultado.append(char)
                else:
                    resultado.append(' ')
        return ''.join(resultado)
    

    def _imprimir_por_windows_nombre(self, nombre_impresora, contenido, es_termica=True):
        try:
            contenido = self._limpiar_caracteres_especiales(contenido)
            if es_termica:
                contenido_bytes = b'\x1b\x40'
                contenido_bytes += contenido.encode('latin-1', errors='ignore')
                contenido_bytes += b'\n' * 5
                contenido_bytes += b'\x1d\x56\x00'
            else:
                contenido_bytes = contenido.encode('latin-1', errors='ignore')
                contenido_bytes += b'\x0c'
            hprinter = win32print.OpenPrinter(nombre_impresora)
            try:
                doc_info = ("Ticket Cafebar", None, "RAW")
                job_id = win32print.StartDocPrinter(hprinter, 1, doc_info)
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(hprinter, contenido_bytes)
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
                tipo = "térmica" if es_termica else "normal"
                return True, f"Impresión exitosa en {nombre_impresora} ({tipo})"
            finally:
                win32print.ClosePrinter(hprinter)
        except Exception as e:
            print(f"Error impresión Windows por nombre: {e}")
            return self._imprimir_por_windows(contenido, es_termica)
    

    def _construir_ticket(self, datos_venta, items):
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        contenido = []
        contenido.append("=" * 40)
        contenido.append(f"{'CAFEBAR RESTAURANTE':^40}")
        contenido.append("=" * 40)
        contenido.append(f"Fecha: {fecha}  Hora: {hora}")
        contenido.append(f"Nro. Venta: {datos_venta.get('num_venta', '')}")
        mesa = str(datos_venta.get('mesa', ''))
        seccion = self._limpiar_caracteres_especiales(str(datos_venta.get('seccion', '')))
        empleado = self._limpiar_caracteres_especiales(str(datos_venta.get('empleado', '')))
        cajero = self._limpiar_caracteres_especiales(str(datos_venta.get('cajero', '')))
        contenido.append(f"Mesa: {mesa} - {seccion}")
        contenido.append(f"Mesero: {empleado}")
        contenido.append(f"Cajero: {cajero}")
        tipo_set = {item.get('tipo', 'Local') for item in items}
        if tipo_set == {'Local'}:
            tipo_linea = "CONSUMO EN LOCAL"
        elif tipo_set == {'Para llevar'}:
            tipo_linea = "PARA LLEVAR"
        else:
            tipo_linea = "CONSUMO MIXTO"
        contenido.append(f"{tipo_linea:^40}")
        contenido.append("-" * 40)
        contenido.append(f"{'CANT':<5}{'DESCRIPCION':<20}{'TIPO':<7}{'P.U.':>6}{'TOTAL':>7}")
        contenido.append("-" * 40)
        total_general = 0
        for item in items:
            cantidad = item.get('cantidad', 1)
            producto = self._limpiar_caracteres_especiales(str(item.get('producto', '')))
            tipo = "L" if item.get('tipo') == 'Local' else "P.L"
            precio = item.get('precio', 0)
            subtotal = cantidad * precio
            total_general += subtotal
            if len(producto) > 18:
                producto = producto[:15] + "..."
            contenido.append(f"{cantidad:<5}{producto:<20}{tipo:<7}{precio:>6.2f}{subtotal:>7.2f}")
        contenido.append("-" * 40)
        contenido.append(f"{'TOTAL:':>33}{total_general:>7.2f} Bs")
        contenido.append("=" * 40)
        return "\n".join(contenido)
    

    def _construir_pedido_cocina(self, datos_venta, items):
        fecha = datetime.now().strftime("%d/%m/%Y")
        hora = datetime.now().strftime("%H:%M:%S")
        contenido = []
        contenido.append("=" * 40)
        contenido.append(f"{'PEDIDO COCINA':^40}")
        contenido.append("=" * 40)
        contenido.append(f"Fecha: {fecha}  Hora: {hora}")
        contenido.append(f"Nro. Venta: {datos_venta.get('num_venta', '')}")
        empleado = self._limpiar_caracteres_especiales(str(datos_venta.get('empleado', '')))
        seccion = self._limpiar_caracteres_especiales(str(datos_venta.get('seccion', '')))
        mesa = str(datos_venta.get('mesa', ''))
        contenido.append(f"Mesero: {empleado}")
        contenido.append(f"Salon: {seccion}  Mesa: {mesa}")
        contenido.append(f"Hora Pedido: {datos_venta.get('hora', '')}")
        tipo_set = {item.get('tipo', 'Local') for item in items}
        if tipo_set == {'Local'}:
            tipo_linea = "CONSUMO EN LOCAL"
        elif tipo_set == {'Para llevar'}:
            tipo_linea = "PARA LLEVAR"
        else:
            tipo_linea = "PEDIDO MIXTO"
        contenido.append(f"{tipo_linea:^40}")
        contenido.append("-" * 40)
        contenido.append(f"{'CANT':<5}{'PRODUCTO':<25}{'TIPO':<10}")
        contenido.append("-" * 40)
        items_cocina = [i for i in items if i.get('tipo') != 'Bebida']
        for item in items_cocina:
            cantidad = item.get('cantidad', 1)
            producto = self._limpiar_caracteres_especiales(str(item.get('producto', '')))
            tipo = "Local" if item.get('tipo') == 'Local' else "Llevar"
            if len(producto) > 22:
                producto = producto[:19] + "..."
            contenido.append(f"{cantidad:<5}{producto:<25}{tipo:<10}")
        contenido.append("=" * 40)
        return "\n".join(contenido)
    

    def _imprimir_por_puerto(self, puerto, contenido, es_termica=True):
        try:
            contenido = self._limpiar_caracteres_especiales(contenido)
            ser = serial.Serial(
                port=puerto,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=2
            )
            if es_termica:
                ser.write(b'\x1B\x40')
                ser.write(contenido.encode('cp850', errors='ignore'))
                ser.write(b'\n' * 5)
                ser.write(b'\x1D\x56\x00')
            else:
                contenido_con_saltos = contenido + '\n' * 8
                ser.write(contenido_con_saltos.encode('cp850', errors='ignore'))
            ser.close()
            tipo = "térmica" if es_termica else "normal"
            return True, f"Impresión exitosa por puerto {puerto} ({tipo})"
        except Exception as e:
            print(f"Error impresión puerto {puerto}: {e}")
            return False, f"Error en puerto {puerto}: {str(e)}"
    

    def _imprimir_por_usb(self, vid, pid, contenido, es_termica=True):
        try:
            contenido = self._limpiar_caracteres_especiales(contenido)
            dispositivo = usb.core.find(idVendor=vid, idProduct=pid)
            if dispositivo is None:
                return False, f"Dispositivo USB no encontrado: VID={vid:04x}, PID={pid:04x}"
            try:
                if dispositivo.is_kernel_driver_active(0):
                    dispositivo.detach_kernel_driver(0)
            except:
                pass
            dispositivo.set_configuration()
            cfg = dispositivo.get_active_configuration()
            intf = cfg[(0,0)]
            ep_out = None
            for ep in intf:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                    ep_out = ep
                    break
            if ep_out:
                if es_termica:
                    contenido_completo = b'\x1b\x40'
                    contenido_completo += contenido.encode('utf-8', errors='ignore')
                    contenido_completo += b'\n' * 5
                    contenido_completo += b'\x1d\x56\x00'
                else:
                    contenido_completo = contenido.encode('utf-8', errors='ignore')
                    contenido_completo += b'\n' * 8
                
                ep_out.write(contenido_completo)
                usb.util.dispose_resources(dispositivo)
                
                tipo = "térmica" if es_termica else "normal"
                return True, f"Impresión USB exitosa ({tipo})"
            else:
                usb.util.dispose_resources(dispositivo)
                return False, "No se encontró endpoint de salida"
                
        except Exception as e:
            print(f"Error impresión USB: {e}")
            return False, f"Error USB: {str(e)}"
    

    def _imprimir_por_windows(self, contenido, es_termica=True):
        try:
            contenido = self._limpiar_caracteres_especiales(contenido)
            impresora_default = win32print.GetDefaultPrinter()
            if not impresora_default:
                return False, "No hay impresora configurada en Windows"
            if es_termica:
                contenido_bytes = b'\x1b\x40'
                contenido_bytes += contenido.encode('latin-1', errors='ignore')
                contenido_bytes += b'\n' * 5
                contenido_bytes += b'\x1d\x56\x00'
            else:
                contenido_bytes = contenido.encode('latin-1', errors='ignore')
                contenido_bytes += b'\n' * 8
            hprinter = win32print.OpenPrinter(impresora_default)
            try:
                doc_info = ("Ticket Cafebar", None, "RAW")
                job_id = win32print.StartDocPrinter(hprinter, 1, doc_info)
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(hprinter, contenido_bytes)
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
                tipo = "térmica" if es_termica else "normal"
                return True, f"Impresión exitosa en {impresora_default} ({tipo})"
            finally:
                win32print.ClosePrinter(hprinter)   
        except Exception as e:
            print(f"Error impresión Windows: {e}")
            return False, f"Error Windows: {str(e)}"
    
    def _guardar_en_archivo(self, contenido, tipo="Ticket"):
        try:
            directorio = os.path.join(os.path.expanduser("~"), "Desktop", "Tickets_Cafebar")
            os.makedirs(directorio, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta = os.path.join(directorio, f"{tipo}_{timestamp}.txt")
            with open(ruta, 'a', encoding='utf-8') as f:
                f.write("\n" + "="*50 + "\n")
                f.write(f"Ticket tipo: {tipo}\n")
                f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("="*50 + "\n")
                f.write(contenido)
                f.write("\n" + "="*50 + "\n")
            return True, f"Ticket guardado en: {ruta}"
        except Exception as e:
            return False, f"Error al guardar archivo: {str(e)}"
    
    
    def __del__(self):
        if hasattr(self, 'conn_impresion'):
            self.conn_impresion.close()