# Reglas del proyecto

## ESTÁNDARES DE COMMITS

Se utiliza la convención Conventional Commits para mantener un historial claro y organizado.

### Tipos de commit

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de errores |
| `style` | Cambios visuales o de formato sin afectar la lógica |
| `refactor` | Reestructuración de código sin modificar el comportamiento |
| `docs` | Documentación |
| `test` | Creación o actualización de pruebas |
| `chore` | Configuración, dependencias y empaquetado |

### Formato

```
<tipo>: <Descripción>
```

### Ejemplos válidos

```
feat: Agrega los ingredientes extra con precio adicional en los pedidos
fix: Imprime la ü como u en los tickets en lugar de ue
refactor: Centraliza las rutas de la base de datos y de las imágenes en Rutas.py
style: Aplica un formato uniforme a todo el código con Ruff
docs: Documenta las tablas y migraciones de la base de datos
chore: Agrega las dependencias del proyecto en requirements.txt
```

### Reglas

- Los mensajes deben comenzar con mayúscula después del prefijo.
- Describir la funcionalidad implementada, no los archivos modificados.
- Un commit debe representar una única funcionalidad, corrección o mejora.
- Mantener mensajes cortos, claros y descriptivos.
- Evitar mensajes genéricos: `cambios`, `correcciones`, `ajustes`, `prueba`.

---

## ESTÁNDARES DE CODIFICACIÓN

### Idioma

- Este proyecto mantiene los nombres en español (clases, métodos y variables), igual que las tablas y columnas de la base de datos, para no mezclar idiomas dentro de los archivos.
- Los textos visibles para el usuario van en español y con tildes.

### Archivos

- Una pantalla por archivo, con el mismo nombre que su clase: `RegistroProductos.py` → `class RegistroProductos(QWidget)`.
- Prefijos: `Registro*` para altas, `Modificacion*` para listados que se modifican, `DarBaja*` para bajas lógicas y `Pop_up_*` para formularios emergentes.
- Las rutas a la base y a las imágenes se obtienen siempre de `Rutas.py`; no se calculan dentro de cada archivo.

```python
# Correcto
from Rutas import get_db_path

DB_PATH = get_db_path()

# Incorrecto
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'cafebar.db')
```

### Comentarios

- Comentarios de una línea, solo donde explican una decisión que no se ve en el código.
- Las funciones de módulo (fuera de las pantallas) llevan un comentario de una línea que describe su propósito.
- Los archivos que se ejecutan directamente llevan en la primera línea su forma de uso: `# Uso: python Main.py`.
- Sin docstrings de varias líneas ni separadores decorativos (`# -----`).
- Eliminar el código comentado antes de realizar commits.

```python
# Indica si la contraseña escrita corresponde al hash guardado
def verificar_password(password_plano, password_hash):
```

### Base de datos

- Consultas siempre con parámetros (`?`), nunca armando el SQL con los datos del usuario.
- Cerrar la conexión en `finally` o al terminar el método.
- Todo cambio de esquema se hace con una función `migrar…` en `init_db.py`, que se pueda ejecutar varias veces sin error.
- Las contraseñas se guardan solo con `hashear_password` de `SeguridadUtils.py`.

### Errores

- Capturar `sqlite3.Error` o `Exception`, nunca `except:` sin tipo.
- Mostrar al usuario un `QMessageBox` con un mensaje claro; no dejar fallar la pantalla en silencio.

### Formato y revisión

El formato y la revisión los aplica Ruff con la configuración de `pyproject.toml` (líneas de 120 caracteres, comillas como estén escritas). Antes de cada commit:

```bash
ruff format .
ruff check .
```

### Datos sensibles

- La carpeta `database/` no se sube al repositorio: tiene los datos del local y las contraseñas de aplicación de Gmail.
- No escribir contraseñas, correos ni rutas personales (`C:\Users\...`) en el código.
