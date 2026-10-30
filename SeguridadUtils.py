import bcrypt

PREFIJOS_BCRYPT = ('$2a$', '$2b$', '$2y$')


# Genera el hash bcrypt de una contraseña para guardarlo en la base
def hashear_password(password_plano):
    if not password_plano:
        return password_plano
    password_bytes = password_plano.encode('utf-8')
    hash_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hash_bytes.decode('utf-8')


# Indica si la contraseña escrita corresponde al hash guardado
def verificar_password(password_plano, password_hash):
    if not password_plano or not password_hash:
        return False
    try:
        return bcrypt.checkpw(password_plano.encode('utf-8'), password_hash.encode('utf-8'))
    except (ValueError, TypeError):
        return False


# Distingue un hash bcrypt de una contraseña antigua todavía en texto plano
def es_hash_bcrypt(valor):
    if not valor:
        return False
    return valor.startswith(PREFIJOS_BCRYPT)
