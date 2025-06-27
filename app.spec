# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# 获取当前项目的根目录
project_root = os.path.abspath('.')

# 查找 cppimport 编译生成的 .pyd 文件
# 假设 cppimport 会将编译后的文件放在 integral_tool/.cppimporter/integral_tool/ 下
cpp_pyd_dir = os.path.join(project_root, 'integral_tool', '.cppimporter', 'integral_tool')
cpp_pyd_file = None
if os.path.exists(cpp_pyd_dir):
    for f in os.listdir(cpp_pyd_dir):
        if f.startswith('cpp_integral_impl') and f.endswith('.pyd'):
            cpp_pyd_file = os.path.join(cpp_pyd_dir, f)
            break

a = Analysis(
    ['app.py'],
    pathex=[project_root], # 确保 PyInstaller 从项目根目录开始查找模块
    binaries=[],
    datas=[
        ('tests/sample.obj', 'tests'), # 包含示例 obj 文件
        ('integral_tool', 'integral_tool'), # 确保整个 integral_tool 目录被包含
    ],
    hiddenimports=[
        'integral_tool.cpp_integral_impl', # 确保 cppimport 模块被发现
        'matplotlib.backends.backend_agg', # Gradio web app might use agg backend
        'scipy.special._ufuncs_cxx', # Sometimes scipy needs this for C++ extensions
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

# 如果找到了 cpp_integral_impl 的 .pyd 文件，将其添加到 datas
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
    name='HuygensFresnelWebApp', # 可执行文件名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Gradio 是 GUI 应用，不需要控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None, # 可以指定图标文件
)