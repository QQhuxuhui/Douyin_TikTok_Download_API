# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('F:\\workspace\\github\\QQhuxuhui\\Douyin_TikTok_Download_API\\config.yaml', '.'), ('F:\\workspace\\github\\QQhuxuhui\\Douyin_TikTok_Download_API\\crawlers\\douyin\\web\\config.yaml', 'crawlers\\douyin\\web')],
    hiddenimports=[],
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
    name='抖音数据',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
