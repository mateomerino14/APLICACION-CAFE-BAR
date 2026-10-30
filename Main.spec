# -*- mode: python ; coding: utf-8 -*-
# Uso: pyinstaller Main.spec --clean --noconfirm

import os
import escpos

# python-escpos necesita su capabilities.json dentro del ejecutable
capacidadesEscpos = os.path.join(os.path.dirname(escpos.__file__), 'capabilities.json')

a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
    datas=[('Imagenes', 'Imagenes'), (capacidadesEscpos, 'escpos')],
    hiddenimports=['bcrypt'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Imagenes\\icono.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Main',
)
