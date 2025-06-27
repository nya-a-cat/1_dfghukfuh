# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

project_root = os.path.abspath('.')

# 查找 cppimport 编译生成的 .pyd 文件 (同 app.spec)
cpp_pyd_dir = os.path.join(project_root, 'integral_tool', '.cppimporter', 'integral_tool')
cpp_pyd_file = None
if os.path.exists(cpp_pyd_dir):
    for f in os.listdir(cpp_pyd_dir):
        if f.startswith('cpp_integral_impl') and f.endswith('.pyd'):
            cpp_pyd_file = os.path.join(cpp_pyd_dir, f)
            break

a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        ('tests/sample.obj', 'tests'), # 包含示例 obj 文件
        ('integral_tool', 'integral_tool'),
    ],
    hiddenimports=[
        'integral_tool.cpp_integral_impl',
        'scipy.special._ufuncs_cxx',
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

if cpp_pyd_file:
    a.datas.append((cpp_pyd_file, os.path.join('integral_tool', '.cppimporter', 'integral_tool')))
    print(f"Adding pre-compiled C++ module: {cpp_pyd_file}")
else:
    print("Warning: Pre-compiled C++ module (.pyd) not found. Dynamic compilation might be attempted at runtime.")
    print("Please ensure 'python precompile_cpp.py' was run successfully before PyInstaller.")

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HuygensFresnelCLI', # 可执行文件名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True, # 命令行工具需要控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)