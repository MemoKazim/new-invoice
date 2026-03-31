# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for InvoiceScrapper
# Build: pyinstaller invoice.spec --clean --noconfirm
#        (or just run build.bat on Windows)

block_cipher = None

a = Analysis(
    ['projects/invoice/main.py'],
    pathex=['projects', '.'],      # 'projects' → invoice package; '.' → core, config packages
    binaries=[],
    datas=[
        ('data', 'data'),          # include data/ folder (filter.json etc.)
    ],
    hiddenimports=[
        # third-party (not always auto-detected by PyInstaller)
        'loguru',
        'multiprocessing',
        'multiprocessing.queues',
        # config package
        'config',
        'config.logs',
        # core package
        'core.logger',
        'core.endpoints',
        'core.services',
        'core.models',
        'core.validators',
        'core.exceptions',
        'core.colors',
        # dynamic imports inside _build_views() won't be auto-detected
        'invoice.gui.views.login',
        'invoice.gui.views.asan_confirm',
        'invoice.gui.views.certificate',
        'invoice.gui.views.params',
        'invoice.gui.views.progress',
        # platform adapters imported lazily via get_adapter()
        'invoice.adapters.windows',
        'invoice.adapters.macos',
        'invoice.adapters.linux',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='InvoiceScrapper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                      # compress with UPX if available (reduces size)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                 # no terminal window (GUI only)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico',      # uncomment once icon is added to assets/
)
