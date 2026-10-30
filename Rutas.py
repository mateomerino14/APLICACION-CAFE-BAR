import os
import sys

CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))


# Carpeta del ejecutable o del proyecto, donde vive la base de datos del local
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return CARPETA_PROYECTO


# Ruta de un recurso empaquetado, como las imágenes de la interfaz
def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(CARPETA_PROYECTO, relative_path)


def get_writable_base_path():
    return get_base_dir()


def get_db_path():
    return os.path.join(get_base_dir(), 'database', 'cafebar.db')


def get_images_dir():
    return get_resource_path('Imagenes')
