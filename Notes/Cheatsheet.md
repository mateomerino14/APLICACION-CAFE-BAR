# DOCUMENTACIÓN TÉCNICA — ARCHIVO PRINCIPAL `Main.py`

---

# Archivo Principal del Sistema

El archivo **`Main.py`** es el punto de entrada principal de toda la aplicación.

Es el encargado de:

    - Inicializar la base de datos.
    - Iniciar la aplicación gráfica con PyQt5.
    - Activar el sistema de vigilancia de cambios.
    - Mostrar la ventana de Login.
    - Permitir el acceso al Administrador de Páginas.
    - Mantener el ciclo de ejecución del sistema.

---

# Ejecución del Sistema

    El sistema se ejecuta con:

    ```bash
    python Main.py
    ```

O mediante el ejecutable generado con PyInstaller:

    ```bash
    Main.exe
    ```

    ---

# Flujo Completo de Ejecución

    ```text
    Main.py
    ↓
    inciarBaseDatos()
    ↓
    QApplication()
    ↓
    VigilanteCambios()
    ↓
    Login()
    ↓
    AdministradorPaginas()
    ↓
    Sistema en ejecución
    ```

---

#  1. Inicialización de la Base de Datos

    ```python
    from init_db import inciarBaseDatos
    ```

    Dentro del método principal:

    ```python
    def main():
        inciarBaseDatos()
    ```

    ##  ¿Qué hace `inciarBaseDatos()`?

    - Crea la base de datos si no existe.
    - Crea todas las tablas necesarias.
    - Garantiza que la estructura esté lista antes de iniciar el sistema.
    - Previene errores por tablas inexistentes.

    Esto asegura que el sistema siempre arranque con la base de datos preparada.

    ---

#  2. Inicialización de la Aplicación PyQt5

    ```python
    aplicacion = QApplication(sys.argv)
    ```

    ## ¿Qué hace?

    - Inicializa el entorno gráfico.
    - Permite el uso de ventanas, botones y eventos.
    - Controla el ciclo principal de la aplicación con:

    ```python
    resultado = aplicacion.exec_()
    ```

    Este método mantiene el sistema en ejecución hasta que el usuario lo cierre.

---

#  3. Sistema de Vigilancia de Cambios (Hot Reload)

    Clase implementada:

    ```python
    class VigilanteCambios(QObject):
    ```

    ##  Objetivo

    Detectar cambios en archivos del sistema y reiniciar automáticamente la aplicación.

    ---

    ##  Archivos Vigilados

    El sistema monitorea múltiples módulos como:

    - AdministradorPaginas.py
    - Login.py
    - PaginaPrincipal.py
    - RegistroProductos.py
    - CobroPedidos.py
    - Reportes.py
    - Configuracion.py
    - Entre otros módulos del sistema.

    ---

    ##  Método `vigilar()`

    - Se ejecuta cada 1 segundo.
    - Verifica la fecha de modificación de los archivos.
    - Si detecta un cambio → reinicia la aplicación.

    ---

    ##  Método `reiniciar_app()`

    ```python
    os.execv(sys.executable, ['python'] + sys.argv)
    ```

    ### Función:
    - Cierra el proceso actual.
    - Vuelve a ejecutar la aplicación automáticamente.

    Esto facilita el desarrollo sin reinicios manuales.

---

#   4. Ventana de Inicio de Sesión

    ```python
    from Login import Login
    ```

    Dentro del método principal:

    ```python
    inicio = Login()
    inicio.show()
    ```

    ## Función del Login

    - Solicita usuario y contraseña.
    - Valida credenciales.
    - Permite el acceso al sistema si los datos son correctos.
    - Bloquea acceso si son incorrectos.

---

#  5. Administrador de Páginas

    Después de un login exitoso, el sistema carga el módulo:

        ```text
        AdministradorPaginas.py
    ```

    ##  Función del Administrador de Páginas

    Es el núcleo de navegación del sistema:

    - 📊 Panel principal
    - 🍽️ Gestión de mesas
    - 🧾 Registro de pedidos
    - 💰 Cobro de ventas
    - 🏷️ Gestión de productos y categorías
    - 👤 Gestión de empleados
    - 📈 Reportes
    - ⚙️ Configuración

    Controla el cambio entre ventanas y módulos del sistema.

---

#  Método Principal Completo

    ```python
    def main():
        inciarBaseDatos()
        aplicacion = QApplication(sys.argv)

        vigilante = VigilanteCambios()

        inicio = Login()
        inicio.show()
        resultado = aplicacion.exec_()


    if __name__ == "__main__":
        main()
    ```

---

# Conclusiónes

`Main.py` es el núcleo del sistema porque:

- Inicializa la base de datos.
- Inicia el entorno gráfico.
- Activa el monitoreo automático de cambios.
- Lanza la ventana de autenticación.
- Permite el acceso al Administrador de Páginas.
- Mantiene el ciclo de ejecución de la aplicación.

Es el archivo que controla completamente el ciclo de vida del sistema.