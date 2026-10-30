# Ejecutable para Windows

El sistema se entrega al local como una carpeta con `Main.exe`, generada con PyInstaller a partir de `Main.spec`. No necesita Python instalado en la PC del local.

## Generar el ejecutable

En una PC con Windows y el entorno del proyecto (ver Instalación en el README):

```bash
conda activate py310
pip install -r requirements.txt
pyinstaller Main.spec --clean --noconfirm
```

El resultado queda en:

```
dist/
└── Main/
    ├── Main.exe
    └── _internal/          dependencias e imágenes de la interfaz
```

## Qué configura `Main.spec`

| Opción | Valor | Propósito |
|---|---|---|
| Punto de entrada | `Main.py` | Prepara la base y abre el inicio de sesión |
| `datas` | `Imagenes` | Empaqueta los íconos y logos de la interfaz |
| `hiddenimports` | `bcrypt` | PyInstaller no siempre detecta bcrypt por sí solo |
| `console` | `False` | Abre solo la ventana del sistema, sin consola |
| `icon` | `Imagenes\icono.ico` | Ícono del ejecutable |
| Modo | carpeta (`COLLECT`) | Arranca más rápido que un único `.exe` |

Equivale al comando:

```bash
pyinstaller Main.py --onedir --windowed --clean --noconfirm --icon "Imagenes\icono.ico" --add-data "Imagenes;Imagenes" --hidden-import bcrypt
```

## Dónde guarda los datos

`nucleo/Rutas.py` separa dos ubicaciones:

| Ruta | En desarrollo | En el ejecutable |
|---|---|---|
| Base de datos y portada (`database/`) | Carpeta del proyecto | Junto a `Main.exe` |
| Imágenes de la interfaz (`Imagenes/`) | Carpeta del proyecto | Dentro del paquete (`sys._MEIPASS`) |

La base se crea sola la primera vez que se abre el sistema.

## Instalar en el local

1. Copiar la carpeta `dist/Main` a la PC del local, por ejemplo en `C:\CafeBar`.
2. Crear un acceso directo a `Main.exe` en el escritorio.
3. Abrirlo, entrar como DIRECTORIO y cambiar la contraseña inicial.

## Actualizar a una versión nueva

1. Hacer una copia de la carpeta `database` del local.
2. Reemplazar todo el contenido de la carpeta del sistema **menos** `database`.
3. Abrir el sistema: `nucleo/init_db.py` aplica las migraciones pendientes y conserva los datos.

## Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `No module named bcrypt` al abrir | bcrypt no se empaquetó | Generar desde `Main.spec`, que ya lo incluye |
| `No module named 'paginas'` al ejecutar con Python | Se ejecutó desde otra carpeta o un archivo de `paginas/` directamente | Iniciar siempre con `python Main.py` desde la raíz del proyecto |
| Faltan íconos en las pantallas | La carpeta `Imagenes` no se incluyó | Generar desde la raíz del proyecto, donde está `Imagenes` |
| No llegan los correos | Cuenta sin contraseña de aplicación o sin internet | Revisar la cuenta activa en Administrar Correos / Backup |
| No imprime | Impresora no registrada o marcada para otra área | Registrarla en Administración → Impresoras y elegir barra o cocina |
