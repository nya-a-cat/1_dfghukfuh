@echo off
setlocal

set "PYTHON_EXE=python"
set "PIP_EXE=pip"

echo 正在检查 Python 环境...
where %PYTHON_EXE% >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误：未找到 Python。请确保 Python 3.9 或更高版本已安装并添加到 PATH。
    pause
    exit /b 1
)

where %PIP_EXE% >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误：未找到 Pip。请确保 Pip 已安装并添加到 PATH。
    pause
    exit /b 1
)

echo 正在安装或更新项目依赖和 PyInstaller...
%PIP_EXE% install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误：安装项目依赖失败。
    pause
    exit /b 1
)

%PIP_EXE% install pyinstaller
if %errorlevel% neq 0 (
    echo 错误：安装 PyInstaller 失败。
    pause
    exit /b 1
)

echo 正在预编译 C++ 模块...
%PYTHON_EXE% precompile_cpp.py
if %errorlevel% neq 0 (
    echo 警告：C++ 模块预编译失败。请确保您已安装 Visual Studio Build Tools 并配置了 C++ 开发环境。
    echo 项目将尝试回退到纯 Python 实现，但性能可能受影响。
    pause
    REM 不退出，继续尝试打包
)

echo 正在打包 Gradio Web 应用...
pyinstaller app.spec --clean
if %errorlevel% neq 0 (
    echo 错误：打包 Web 应用失败。
    pause
    exit /b 1
)

echo 正在打包命令行工具...
pyinstaller main.spec --clean
if %errorlevel% neq 0 (
    echo 错误：打包命令行工具失败。
    pause
    exit /b 1
)

echo 打包完成！可执行文件位于 dist 目录。
echo 请将 dist 目录下的 .exe 文件和 README.md, tests/sample.obj 等相关文件一起分发给用户。
pause
endlocal