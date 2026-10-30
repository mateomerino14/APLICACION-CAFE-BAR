# Sistema de Gestión para Café-Bar

Aplicación de escritorio para Windows que controla las ventas, mesas, cocina, inventario, promociones y empleados de un café-bar. Está hecha en Python con PyQt5 y guarda todo en una base SQLite local, así que funciona sin internet. Solo usa la red para enviar reportes y copias de seguridad por correo.

Es la primera versión del sistema; la versión web se desarrolló después, a partir de esta.

## Documentación

| Documento | Para quién | Contenido |
|---|---|---|
| [`docs/base-de-datos.md`](docs/base-de-datos.md) | Desarrollo | Tablas, relaciones, datos iniciales y migraciones automáticas |
| [`docs/ejecutable.md`](docs/ejecutable.md) | Desarrollo e instalación | Generar el `.exe` con PyInstaller e instalarlo o actualizarlo en el local |
| [`docs/interfaz.md`](docs/interfaz.md) | Desarrollo | Íconos y convenciones visuales de las pantallas |
| [`reglas.md`](reglas.md) | Desarrollo | Commits y estándares de código |

## Funcionalidades

- **Inicio de sesión** por empleado, con selección rápida de su foto, y acceso total para el DIRECTORIO.
- **Familia.** Catálogo del local por categoría y subcategoría, con productos y promociones vigentes del día.
- **Caja.**
  - Mesas libres y ocupadas por sección, y pedidos para llevar.
  - Pedidos por producto o promoción, con ingredientes excluidos y extras con precio adicional.
  - Comanda a cocina y a barra en impresoras térmicas o de Windows.
  - Cobro en efectivo, QR o mixto, y ticket con límite de 2 impresiones; desde la tercera se pide contraseña.
- **Productos.** Categorías y subcategorías con imagen, productos con su receta de ingredientes y bajas lógicas.
- **Stock.** Ingredientes con unidad de medida, cantidad disponible y precio como extra.
- **Secciones y mesas** del local.
- **Promociones** por fecha específica, rango de fechas, días de la semana y horario.
- **Empleados y cargos.** Cada cargo define las pantallas y acciones que puede usar.
- **Reportes** de ventas, ventas por empleado, productos más vendidos y stock, con gráficos. Se abren en PDF o se envían por correo.
- **Administración.**
  - Cuentas de Gmail para enviar reportes y copias de seguridad.
  - Copia de seguridad de la base en Excel con sus imágenes (ZIP), y restauración desde ese archivo.
  - Enlace a impuestos, contraseña del DIRECTORIO, portada de la página principal e impresoras.
  - Eliminación física en cascada de registros dados de baja.

## Requisitos

- Windows 10 u 11
- Python 3.10 (con Anaconda o un entorno virtual)
- Una cuenta de Gmail con contraseña de aplicación, solo para enviar correos

## Instalación

```bash
git clone https://github.com/mateomerino14/APLICACION-CAFE-BAR.git
cd APLICACION-CAFE-BAR
conda create -n py310 python=3.10
conda activate py310
pip install -r requirements.txt
```

No hace falta crear la base: `init_db.py` la crea en `database/cafebar.db` al iniciar el sistema, con las pantallas, los métodos de pago y el usuario DIRECTORIO. En una base que ya existe solo aplica las migraciones pendientes, sin tocar los datos.

## Ejecución

```bash
python Main.py      # inicia el sistema
inicio.bat          # lo mismo, con doble clic, activando el entorno py310
ruff check .        # revisión de errores y estándares
ruff format .       # formato del código
```

### Primer ingreso

1. En el inicio de sesión, el botón **Directorio** completa el usuario `DIRECTORIO`. La contraseña inicial está en `init_db.py`.
2. Cambiarla en **Administración → Configuración → Cambiar Contraseña del DIRECTORIO**.
3. Crear las secciones con sus mesas, los cargos con sus permisos y los empleados.
4. Registrar los ingredientes, las categorías y los productos.
5. Para enviar correos, agregar una cuenta de Gmail en **Administrar Correos / Backup** con una [contraseña de aplicación](https://myaccount.google.com/apppasswords), no la contraseña normal.

## Stack

| Tecnología | Propósito |
|---|---|
| Python 3.10 + PyQt5 | Interfaz de escritorio |
| SQLite | Base de datos local |
| bcrypt | Hash de las contraseñas de empleados y del DIRECTORIO |
| fpdf2 + matplotlib | Reportes en PDF y gráficos |
| pandas + openpyxl | Copia de seguridad en Excel |
| pywin32, pyusb, pyserial | Impresión en impresoras de Windows, USB y puerto serie |
| smtplib (Gmail) | Envío de reportes y copias de seguridad |
| PyInstaller | Ejecutable para Windows |
| Ruff | Revisión y formato del código |

## Arquitectura

```
Main.py
 └─ init_db.inciarBaseDatos()     crea o migra la base
 └─ Login                         valida al empleado o al DIRECTORIO
     └─ AdministradorPaginas      menú según permisos y páginas en un QStackedWidget
         ├─ Páginas (QWidget)     Familia, RegistrarPedidos, Reportes, Configuracion…
         │   └─ Pop_up_* (QDialog) formularios de modificación
         └─ DialogoCobroVenta     cobro y ticket de una mesa
```

| Módulo | Responsabilidad |
|---|---|
| `Main.py` | Prepara la base y abre el inicio de sesión |
| `Login.py` | Autentica con bcrypt y abre el administrador de páginas |
| `AdministradorPaginas.py` | Arma el menú según los permisos del cargo y crea cada página la primera vez que se abre |
| `Rutas.py` | Ruta de la base (junto al ejecutable) y de los recursos empaquetados (`Imagenes`) |
| `SeguridadUtils.py` | Hash y verificación de contraseñas |
| `init_db.py` | Esquema, datos iniciales, trigger de mesas y migraciones |
| `Impresion.py` | Comandas y tickets: elige la impresora de cocina o barra y la vía (Windows, puerto o USB) |

Los permisos salen de las tablas `Pantalla` y `Subpantalla`: el menú muestra una pantalla si el cargo la tiene en `PermisosCargo` y cada opción si está en `PermisosCargoSubpantalla`. El DIRECTORIO ve todo.

## Estructura

```
APLICACION-CAFE-BAR/
├── Main.py                         Punto de entrada
├── Login.py
├── AdministradorPaginas.py
├── PaginaPrincipal.py              Inicio con la portada personalizable
├── Familia.py                      Catálogo del local
├── RegistrarPedidos.py             Caja: mesas, pedidos y comandas
├── DialogoCobroVenta.py            Cobro y ticket
├── Registro*.py                    Altas: productos, categorías, ingredientes, promociones, cargos, empleados, clientes
├── Modificacion*.py                Listados con búsqueda para modificar
├── DarBaja*.py                     Bajas lógicas
├── Pop_up_*.py                     Formularios emergentes de modificación
├── Administracion_Secciones_Mesas.py
├── ModificacionSeccion.py
├── Reportes.py                     Reportes, gráficos, PDF y envío por correo
├── Configuracion.py                Correos, copias de seguridad, enlace y contraseña del DIRECTORIO
├── EliminacionFisica.py            Borrado en cascada de registros dados de baja
├── Impresoras.py                   Detección, registro y prueba de impresoras
├── Impresion.py                    Envío de comandas y tickets
├── Rutas.py
├── SeguridadUtils.py
├── init_db.py
├── Imagenes/                       Íconos y logos de la interfaz
├── docs/                           Documentación técnica
├── Main.spec                       Configuración de PyInstaller
├── inicio.bat                      Inicio rápido en Windows
├── requirements.txt
├── pyproject.toml                  Configuración de Ruff
└── reglas.md                       Estándares de commits y de código
```

La carpeta `database/` no se versiona: tiene los datos del local y las credenciales de correo.

## Ejecutable

```bash
pyinstaller Main.spec --clean --noconfirm
```

Deja el sistema en `dist/Main/Main.exe`. El detalle, y cómo actualizar el local sin perder datos, está en [`docs/ejecutable.md`](docs/ejecutable.md).

## Estándares

- Commits con Conventional Commits en español (`tipo: Descripción`).
- Nombres en español, igual que las tablas de la base.
- Comentarios de una línea, solo donde explican una decisión.
- Formato y revisión con Ruff (`pyproject.toml`).

El detalle está en [`reglas.md`](reglas.md).

## Autor

Mateo Alejandro Merino Vidal
