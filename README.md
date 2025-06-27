# Integral Tool

This repository contains a simple Python implementation of a Huygens–Fresnel integral
for hologram computation. It includes a GitHub Actions workflow that runs a demo
and can be used for benchmarking.

## 如何运行 (针对已打包的可执行文件)

为了方便用户，我们提供了预编译的 Windows 可执行文件。最终用户无需安装 Python 或其他依赖，即可直接运行。

### 1. 获取可执行文件

从项目的发布页面下载最新版本的可执行文件：
*   `HuygensFresnelWebApp.exe` (Web 应用)
*   `HuygensFresnelCLI.exe` (命令行工具)

### 2. 运行 Web 应用 (Gradio)

双击 `HuygensFresnelWebApp.exe`。程序启动后，会自动在您的默认浏览器中打开一个页面（通常是 `http://127.0.0.1:7860`）。

### 3. 运行命令行工具

打开命令提示符 (cmd) 或 PowerShell，导航到 `HuygensFresnelCLI.exe` 所在的目录，然后运行：

```bash
HuygensFresnelCLI.exe <method> [input_file]
```

*   `<method>`: 必选参数，选择计算方法。可选值有 `python`、`scipy`、`cpp`。
*   `[input_file]`: 可选参数，指定 `.obj` 输入文件的路径。例如：`tests\sample.obj`。

**示例：**

```bash
HuygensFresnelCLI.exe python tests\sample.obj
```

### 关于 C++ 性能

打包后的可执行文件已经包含了预编译的 C++ 模块。因此，无论您的系统是否安装 C++ 编译器，都将能够使用 C++ 实现以获得最佳性能。

## 如何打包 (针对开发者)

如果您是开发者并希望自行打包项目，可以按照以下步骤操作：

### 1. 准备打包环境

*   确保您的 Windows 机器上安装了 Python 3.9 或更高版本，并已将其添加到 PATH。
*   确保您的 Windows 机器上安装了 Visual Studio Build Tools (C++ 编译器)，并选择了“使用 C++ 的桌面开发”工作负载。这是预编译 C++ 模块所必需的。

### 2. 一键打包

在项目根目录下，双击运行 `build_exe.bat` 脚本。

该脚本将自动执行以下操作：
*   检查 Python 环境和 Pip。
*   安装 `requirements.txt` 中列出的所有 Python 依赖，以及 `pyinstaller`。
*   运行 `precompile_cpp.py` 以预编译 C++ 模块。
*   使用 `app.spec` 打包 Gradio Web 应用 (`HuygensFresnelWebApp.exe`)。
*   使用 `main.spec` 打包命令行工具 (`HuygensFresnelCLI.exe`)。

打包成功后，生成的可执行文件将位于项目根目录下的 `dist` 文件夹中。

## Benchmark Results

The following table is automatically updated by the GitHub Actions workflow.

<!-- BENCHMARK_START -->
| Date | Machine | Python | Git | Python(s) | SciPy(s) | MKL(s) | Amp shape | Phase shape |
|------|---------|--------|-----|----------|---------|-------|-----------|-------------|

| 2025-06-21T14:32:53.330929Z | Linux-6.11.0-1015-azure-x86_64-with-glibc2.39 | 3.13.5 | 8cbfb0e | 0.016 | 0.057 | 0.009 | 64x64 | 64x64 |
| 2025-06-26T11:01:26.864345Z | Linux-6.11.0-1015-azure-x86_64-with-glibc2.39 | 3.11.13 | 622f4de | 0.016 | 0.048 | 0.009 | 64x64 | 64x64 |
| 2025-06-26T11:04:59.553400Z | Linux-6.11.0-1015-azure-x86_64-with-glibc2.39 | 3.11.13 | 5249c99 | 0.016 | 0.049 | 0.009 | 64x64 | 64x64 |
| 2025-06-26T11:34:42.860971Z | Windows-11-10.0.26100-SP0 | 3.12.3 | 75ddcf1 | 0.014 | 0.028 | 0.024 | 64x64 | 64x64 |
| 2025-06-26T11:38:12.048040Z | Windows-11-10.0.26100-SP0 | 3.12.3 | 75ddcf1 | 0.016 | 0.021 | 0.019 | 64x64 | 64x64 |
| 2025-06-26T11:40:56.789467Z | Windows-11-10.0.26100-SP0 | 3.12.3 | 75ddcf1 | 0.014 | 0.021 | 0.019 | 64x64 | 64x64 |
| 2025-06-26T11:43Z | Windows-11-10.0.26100-SP0 | 3.12.3 | 75ddcf1 | 0.014 | 0.022 | 0.021 | 64x64 | 64x64 |
| 2025-06-26T11:47Z | Windows-11-10.0.26100-SP0 | 3.12.3 | 75ddcf1 | nan | nan | nan | nan | nan | nan | 0x0 | 0x0 |
<!-- BENCHMARK_END -->

Below is a plot of benchmark runtimes:

![Benchmark plot](benchmark.png)
