# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[('venv39/Lib/site-packages/onnxruntime/capi/onnxruntime_providers_cuda.dll','./onnxruntime/capi/'),
              ('venv39/Lib/site-packages/onnxruntime/capi/onnxruntime_providers_tensorrt.dll','./onnxruntime/capi/'),
              ('venv39/Lib/site-packages/onnxruntime/capi/onnxruntime_providers_shared.dll','./onnxruntime/capi/')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
for d in a.datas:
	if '_C.cp39-win_amd64.pyd' in d[0]:
		a.datas.remove(d)
		break
for d in a.datas:
	if '_C_flatbuffer.cp39-win_amd64.pyd' in d[0]:
		a.datas.remove(d)
		break
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
