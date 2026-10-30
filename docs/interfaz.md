# Interfaz

Convenciones visuales que siguen las pantallas, para que las nuevas se vean igual que las existentes.

## Paleta

| Color | Uso |
|---|---|
| `#2c3e50` | Títulos y texto principal |
| `#7f8c8d` | Texto secundario y pie de página |
| `#3498db` / `#2980b9` | Botones principales y su estado al pasar el mouse |
| `#27ae60` / `#2ecc71` | Confirmar, registrar y cobrar |
| `#e74c3c` / `#c0392b` | Cancelar, eliminar y dar de baja |
| `#f39c12` | Avisos y pedidos en preparación |
| `#e2e8f0` | Bordes de tarjetas, tablas y campos |
| `#f8f9fa` / `#ffffff` | Fondos de página y de tarjetas |

Tipografía: **Segoe UI** en toda la interfaz; **Verdana** en el inicio de sesión y en la barra superior.

## Íconos de texto

Los botones y etiquetas usan emojis para que la acción se reconozca de un vistazo:

| Grupo | Íconos |
|---|---|
| Descripción | 📝 Descripción · 📛 Nombre · 🥗 Ingredientes · ⭐ Destacado · 📌 Importante · ℹ️ Información |
| Ventas | 💰 Precio, ventas · 📊 Costo, fabricación · 📈 Ventas · 📉 Gastos |
| Clasificación | 🏷️ Categoría · 🔖 Subcategoría |
| Acciones | ➕ Añadir · ✏️ Modificar · 🗑️ Eliminar · 💾 Guardar · 🔍 Buscar · 🔄 Actualizar · 📋 Lista · 📁 Archivo · 🖼️ Imagen |
| Personas | 👤 Empleado · 👥 Empleados · 🔐 Contraseña · 📱 Teléfono · 📧 Correo · 📍 Dirección |
| Tiempo | 📅 Fecha · 🎂 Fecha especial · ⏰ Hora |
| Local | 🏪 Tienda · 🍽️ Mesa · 🥤 Bebida · 🥡 Para llevar · 🍔 Comida |
| Estados | ✅ Éxito, confirmar · ❌ Error, cancelar · ⚠️ Advertencia · 🔔 Notificación |

## Imágenes

Los íconos de los menús y botones están en `Imagenes/` y se cargan siempre con `get_resource_path` o `get_images_dir` de `nucleo/Rutas.py`, para que funcionen igual en el ejecutable.

Las imágenes que carga el usuario (productos, categorías, promociones y fotos de empleados) se guardan como BLOB en la base. La portada de la página principal se guarda en `database/banner_custom.png`.

## Pantallas

- Cada página es un `QWidget` en `paginas/<modulo>/` que `paginas/inicio/AdministradorPaginas.py` registra en el diccionario `PAGINAS` y crea la primera vez que se abre.
- Los formularios de modificación son `QDialog` en archivos `Pop_up_*.py`, en la misma carpeta que la pantalla que los abre.
- Para agregar una pantalla: crear el archivo en su módulo, importarlo en `AdministradorPaginas.py`, sumarlo a `PAGINAS` y agregar la opción al menú.
- Los mensajes al usuario se muestran con `QMessageBox`, con títulos en español y con tildes.
