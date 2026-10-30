# Base de datos

Base SQLite en `database/cafebar.db`, junto a `Main.py` o, en el ejecutable, junto a `Main.exe` (ver `nucleo/Rutas.py`). No se versiona: guarda los datos del local y las cuentas de correo.

## Creación y migraciones

`inciarBaseDatos()` de `nucleo/init_db.py` se ejecuta en cada inicio, antes del login. Todas sus operaciones se pueden repetir sin dañar los datos:

| Paso | Función | Qué hace |
|---|---|---|
| 1 | `crear_db` | Crea las tablas que no existen (`CREATE TABLE IF NOT EXISTS`) y carga los datos iniciales que falten |
| 2 | `crearTriggers` | Crea el trigger `asignarMesa`, que numera las mesas dentro de cada sección |
| 3 | `migrarTablaExclusiones` | Tabla de ingredientes excluidos de un producto |
| 4 | `migrarTablaExclusionesPromo` | Tabla de ingredientes excluidos de un producto dentro de una promoción |
| 5 | `migrar_unidades_con_producto` | Columna `idProd` en `DetallesVentaUnidades` y su índice |
| 6 | `migrarIngredientesExtra` | Columna `precioExtra` en `Stock` y tabla `DetallesVentaExtras` |
| 7 | `migrarHoraCierreVenta` | Columna `horaCierre` en `Venta`, que se llena al cobrar |
| 8 | `migrarPasswordsAHash` | Convierte a bcrypt las contraseñas que sigan en texto plano |

Para agregar un cambio de esquema: escribir una función `migrar…` que revise si el cambio ya existe antes de aplicarlo, y llamarla al final de `inciarBaseDatos()`.

### Datos iniciales

| Tabla | Datos |
|---|---|
| `Pantalla` | Las 9 pantallas del menú: Familia, Caja, Administracion, Productos, Secciones, Stock, Promociones, Empleados, Reportes |
| `Subpantalla` | Las 22 acciones de esas pantallas (`REGISTRAR_PEDIDO`, `VER_REPORTES`…) |
| `MetodoPago` | Efectivo y Qr |
| `Enlace` | Enlace al sistema de impuestos (SIAT) |
| `Directorio` | Usuario `DIRECTORIO` con la contraseña inicial, que pasa a bcrypt en el paso 8 |

## Tablas

### Catálogo

| Tabla | Contenido | Relaciones |
|---|---|---|
| `Categoria` | Nombre, imagen y estado activo | |
| `Subcategoria` | Nombre, imagen y estado activo | `idCategoria → Categoria` |
| `Producto` | Nombre, descripción, precio de venta, costo de fabricación, imagen y estado | `idSubcategoria → Subcategoria` |
| `Stock` | Ingredientes: cantidad, unidad de medida, disponibilidad y precio como extra | |
| `ProductosIngredientes` | Receta: cantidad de cada ingrediente por producto | `Producto`, `Stock` |
| `Promocion` | Precio, imagen, fecha específica o rango de fechas y horario | |
| `PromocionDias` | Días de la semana en que aplica (1 = lunes) | `Promocion` |
| `PromocionProd` | Productos y cantidades de la promoción | `Promocion`, `Producto` |

### Local

| Tabla | Contenido | Relaciones |
|---|---|---|
| `Seccion` | Salones del local | |
| `Mesa` | Disponibilidad; la clave es `(idMesa, idSeccion)` | `idSeccion → Seccion` |
| `Impresora` | Dispositivo de Windows o VID/PID USB, y si imprime para barra o cocina | |

### Ventas

| Tabla | Contenido | Relaciones |
|---|---|---|
| `Venta` | La clave es `(numVenta, fechaReg)`: el número se reinicia cada día. Hora de inicio y cierre, total, mesa, mesero (`codEmp`), cajero (`codEmp2`, −1 si fue el DIRECTORIO) y cliente | `Empleado`, `Mesa`, `Seccion`, `Cliente` |
| `DetallesVenta` | Cada línea del pedido: producto o promoción, cantidad, subtotal, tipo de consumo y estado | `Venta`, `Producto`, `Promocion`, `Empleado` |
| `DetallesVentaUnidades` | Cada unidad de una línea, para marcar cuáles ya se entregaron | `DetallesVenta` |
| `DetallesVentaExclusiones` | Ingredientes quitados de un producto | `DetallesVenta`, `Stock` |
| `DetallesVentaExclusionesPromo` | Ingredientes quitados de un producto dentro de una promoción | `DetallesVenta`, `Producto`, `Stock` |
| `DetallesVentaExtras` | Ingredientes agregados con su precio | `DetallesVenta`, `Stock`, `Producto` |
| `Pago` | Monto por método; una venta mixta tiene dos filas | `Venta`, `MetodoPago` |
| `MetodoPago` | Efectivo y Qr | |
| `Cliente` | NIT, nombre y correo para la factura | |

### Personal y permisos

| Tabla | Contenido | Relaciones |
|---|---|---|
| `Cargo` | Nombre del cargo | |
| `Empleado` | Alias de ingreso, contraseña bcrypt, datos personales, foto y disponibilidad | `idCargo → Cargo` |
| `Directorio` | Usuario con acceso total | |
| `Pantalla` / `Subpantalla` | Pantallas del menú y sus acciones | |
| `PermisosCargo` | Pantallas que ve cada cargo | `Cargo`, `Pantalla` |
| `PermisosCargoSubpantalla` | Acciones permitidas a cada cargo | `Cargo`, `Subpantalla` |
| `PermisosPersonal` / `PermisosPersonalSubpantalla` | Permisos por empleado (reservadas, sin uso en la interfaz) | `Empleado` |

### Configuración

| Tabla | Contenido |
|---|---|
| `Cuenta` | Cuentas de Gmail y su contraseña de aplicación; solo una está activa |
| `Enlace` | Enlace del botón de impuestos |

## Bajas y eliminación física

Productos, categorías, subcategorías, promociones y empleados no se borran: se marcan como inactivos (`activo`, `activa` o `disponibleEmp`) para no romper las ventas históricas. **Eliminación física** (en Configuración) los borra de verdad junto con todo lo que depende de ellos.

## Copia de seguridad

**Administrar Correos / Backup** exporta cada tabla a una hoja de Excel, guarda las imágenes aparte y envía todo en un ZIP a la cuenta de Gmail activa. **Importar** reemplaza el contenido de cada tabla con el del archivo.

La copia incluye la tabla `Cuenta`, con las contraseñas de aplicación de Gmail: el ZIP debe guardarse como información sensible.
