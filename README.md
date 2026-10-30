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

No hace falta crear la base: `nucleo/init_db.py` la crea en `database/cafebar.db` al iniciar el sistema, con las pantallas, los métodos de pago y el usuario DIRECTORIO. En una base que ya existe solo aplica las migraciones pendientes, sin tocar los datos.

## Ejecución

```bash
python Main.py      # inicia el sistema
inicio.bat          # lo mismo, con doble clic, activando el entorno py310
ruff check .        # revisión de errores y estándares
ruff format .       # formato del código
```

### Primer ingreso

1. En el inicio de sesión, el botón **Directorio** completa el usuario `DIRECTORIO`. La contraseña inicial está en `nucleo/init_db.py`.
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
 ├─ nucleo/init_db.inciarBaseDatos()       crea o migra la base
 └─ paginas/inicio/Login                   valida al empleado o al DIRECTORIO
     └─ paginas/inicio/AdministradorPaginas   menú según permisos y páginas en un QStackedWidget
         ├─ paginas/<modulo>/* (QWidget)       Familia, RegistrarPedidos, Reportes, Configuracion…
         │   └─ Pop_up_* (QDialog)             formularios de modificación del mismo módulo
         └─ paginas/caja/DialogoCobroVenta     cobro y ticket de una mesa
             └─ servicios/Impresion            comanda y ticket en la impresora de barra o cocina
```

| Carpeta | Responsabilidad | Restricción |
|---|---|---|
| `nucleo/` | Rutas, contraseñas y creación o migración de la base | No importa nada de `paginas/` ni de `servicios/` |
| `servicios/` | Impresión de comandas y tickets, sin interfaz propia | Solo depende de `nucleo/` |
| `paginas/<modulo>/` | Pantallas (`QWidget`) y formularios emergentes (`QDialog`) de un módulo del menú | Usa `nucleo/` y `servicios/`; de otro módulo solo importa lo que abre directamente |

| Módulo | Responsabilidad |
|---|---|
| `Main.py` | Prepara la base y abre el inicio de sesión |
| `paginas/inicio/Login.py` | Autentica con bcrypt y abre el administrador de páginas |
| `paginas/inicio/AdministradorPaginas.py` | Arma el menú según los permisos del cargo y crea cada página la primera vez que se abre |
| `nucleo/Rutas.py` | Ruta de la base (junto al ejecutable) y de los recursos empaquetados (`Imagenes`) |
| `nucleo/SeguridadUtils.py` | Hash y verificación de contraseñas |
| `nucleo/init_db.py` | Esquema, datos iniciales, trigger de mesas y migraciones |
| `servicios/Impresion.py` | Comandas y tickets: elige la impresora de cocina o barra y la vía (Windows, puerto o USB) |

Las importaciones son absolutas desde la raíz del proyecto, por eso el sistema se inicia siempre con `python Main.py` desde esa carpeta:

```python
from nucleo.Rutas import get_db_path
from paginas.productos.Pop_up_RegistroProductos import Pop_up_RegistroProductos
```

Los permisos salen de las tablas `Pantalla` y `Subpantalla`: el menú muestra una pantalla si el cargo la tiene en `PermisosCargo` y cada opción si está en `PermisosCargoSubpantalla`. El DIRECTORIO ve todo.

## Estructura

Las pantallas se agrupan en `paginas/` con las mismas secciones del menú:

```
APLICACION-CAFE-BAR/
├── Main.py                          Punto de entrada
├── nucleo/
│   ├── Rutas.py                     Ruta de la base y de las imágenes
│   ├── SeguridadUtils.py            Hash de contraseñas con bcrypt
│   └── init_db.py                   Esquema, datos iniciales y migraciones
├── servicios/
│   └── Impresion.py                 Envío de comandas y tickets
├── paginas/
│   ├── inicio/                      Login, AdministradorPaginas (menú) y PaginaPrincipal
│   ├── familia/                     Familia: catálogo del local
│   ├── caja/                        RegistrarPedidos y DialogoCobroVenta
│   ├── administracion/              Configuracion, Impresoras y EliminacionFisica
│   ├── productos/                   Categorías, subcategorías y productos (registro, modificación y baja)
│   ├── secciones/                   Secciones y mesas
│   ├── stock/                       Ingredientes
│   ├── promociones/                 Promociones
│   ├── empleados/                   Cargos con sus permisos y empleados
│   └── reportes/                    Reportes, gráficos, PDF y envío por correo
├── Imagenes/                        Íconos y logos de la interfaz
├── docs/                            Documentación técnica
├── Main.spec                        Configuración de PyInstaller
├── inicio.bat                       Inicio rápido en Windows
├── requirements.txt
├── pyproject.toml                   Configuración de Ruff
└── reglas.md                        Estándares de ramas, commits y código
```

Dentro de cada módulo los archivos siguen los mismos prefijos: `Registro*` para altas, `Modificacion*` para listados que se modifican, `DarBaja*` para bajas lógicas y `Pop_up_*` para formularios emergentes.

La carpeta `database/` no se versiona: tiene los datos del local y las credenciales de correo.

## Ejecutable

```bash
pyinstaller Main.spec --clean --noconfirm
```

Deja el sistema en `dist/Main/Main.exe`. El detalle, y cómo actualizar el local sin perder datos, está en [`docs/ejecutable.md`](docs/ejecutable.md).

## Ramas

El flujo completo está en [`reglas.md`](reglas.md).

| Rama | Propósito |
|---|---|
| `main` | Versión estable que se entrega al local |
| `develop` | Integración de lo terminado hasta la próxima entrega |
| `feature/<tema>` | Desarrollo de un cambio, creada desde `develop` |

## Estándares

- Commits con Conventional Commits en español (`tipo: Descripción`).
- Nombres en español, igual que las tablas de la base.
- Comentarios de una línea, solo donde explican una decisión.
- Formato y revisión con Ruff (`pyproject.toml`).

El detalle está en [`reglas.md`](reglas.md).

## Autor

Mateo Alejandro Merino Vidal
