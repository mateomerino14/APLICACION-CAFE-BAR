"""
SeguridadUtils.py

Utilidades compartidas para el manejo seguro de contraseñas.
Se usa bcrypt: genera un hash distinto cada vez (por el "salt" aleatorio
que incluye), y para verificar una contraseña no se compara texto plano,
se le pide a bcrypt que confirme si el texto ingresado corresponde al
hash guardado.

Requiere el paquete "bcrypt". Instalar con:
    pip install bcrypt --break-system-packages
(o sin --break-system-packages según tu entorno).

Si compilas el proyecto con PyInstaller, asegúrate de que bcrypt viaje
incluido (normalmente se detecta solo, pero si el .exe da error de
módulo no encontrado, agrega --hidden-import=bcrypt al build o
inclúyelo en el archivo Main.spec).
"""

import bcrypt


def hashear_password(password_plano):
    """
    Convierte una contraseña en texto plano a su hash seguro.
    Devuelve un string listo para guardar en la base de datos.
    """
    if not password_plano:
        return password_plano
    password_bytes = password_plano.encode('utf-8')
    hash_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hash_bytes.decode('utf-8')


def verificar_password(password_plano, password_hash):
    """
    Compara una contraseña en texto plano (lo que el usuario escribió)
    contra un hash guardado en la base de datos.
    Devuelve True si coinciden, False en cualquier otro caso
    (incluyendo si password_hash está vacío, es None, o no es un hash
    válido de bcrypt).
    """
    if not password_plano or not password_hash:
        return False
    try:
        return bcrypt.checkpw(password_plano.encode('utf-8'), password_hash.encode('utf-8'))
    except (ValueError, TypeError):
        return False


def es_hash_bcrypt(valor):
    """
    Determina si un texto ya es un hash de bcrypt (empieza con $2a$, $2b$
    o $2y$) o si todavía es una contraseña en texto plano sin migrar.
    Sirve para la migración automática de contraseñas antiguas.
    """
    if not valor:
        return False
    return valor.startswith('$2a$') or valor.startswith('$2b$') or valor.startswith('$2y$')