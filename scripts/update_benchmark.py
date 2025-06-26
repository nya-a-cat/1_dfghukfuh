import csv
import datetime
import os
import platform
import subprocess
import sys
import matplotlib
matplotlib.use('Agg')  # 确保使用非交互式后端
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import run_demo

START_MARK = "<!-- BENCHMARK_START -->"
END_MARK = "<!-- BENCHMARK_END -->"

def run_safe(method):
    """Run a demo and catch errors so they are visible."""
    try:
        duration, amp_shape, phase_shape = run_demo(method)
        return duration, amp_shape, phase_shape, None
    except Exception as exc:  # pragma: no cover - display runtime issues
        print(f"{method} failed: {exc}", file=sys.stderr)
        return float("nan"), (0, 0), (0, 0), str(exc)

def update_table(row):
    path = "README.md"
    text = open(path).read().splitlines()
    try:
        start = text.index(START_MARK)
        end = text.index(END_MARK)
    except ValueError:
        raise SystemExit("Benchmark markers not found in README")
    
    table = text[start + 1 : end]
    if not table or not table[0].startswith("| Date |"):
        header = [
            "| Date | Machine | Python | Git | Python(s) | SciPy(s) | MKL(s) | Amp shape | Phase shape |",
            "|------|---------|--------|-----|----------|---------|-------|-----------|------------|",
        ]
        table = header + [row]
    else:
        table.append(row)
    
    text[start + 1 : end] = table
    with open(path, "w") as fh:
        fh.write("\n".join(text) + "\n")

def parse_rows():
    """Parse the benchmark table from README for plotting."""
    lines = []
    with open("README.md") as fh:
        in_table = False
        for line in fh:
            if line.strip() == START_MARK:
                in_table = True
                continue
            if line.strip() == END_MARK:
                break
            if in_table:
                lines.append(line.strip())
    
    if not lines:
        return []
    
    # 过滤掉表头和分隔符行
    data_lines = []
    for line in lines:
        if line.startswith("|") and not line.startswith("|---"):
            # 跳过表头
            if "Date" not in line:
                data_lines.append(line)
    
    if not data_lines:
        return []
    
    reader = csv.reader([l.strip("|") for l in data_lines])
    rows = []
    for row in reader:
        if len(row) < 9:
            continue
        try:
            rows.append({
                "date": row[0].strip(),
                "python": float(row[4].strip()),
                "scipy": float(row[5].strip()),
                "mkl": float(row[6].strip()),
            })
        except (ValueError, IndexError) as e:
            print(f"Error parsing row {row}: {e}", file=sys.stderr)
            continue
    
    return rows

def plot(rows):
    """Generate benchmark plot."""
    print(f"Plotting {len(rows)} data points...")
    
    if not rows:
        print("No data to plot, creating empty plot...")
        plt.figure(figsize=(8, 4))
        plt.text(0.5, 0.5, 'No benchmark data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=plt.gca().transAxes, fontsize=16)
        plt.title("Benchmark Results")
        plt.tight_layout()
        plt.savefig("benchmark.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("Empty benchmark plot saved as benchmark.png")
        return
    
    dates = [r["date"] for r in rows]
    py = [r["python"] for r in rows]
    sp = [r["scipy"] for r in rows]
    mk = [r["mkl"] for r in rows]
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, py, label="Python", marker='o', linewidth=2)
    plt.plot(dates, sp, label="SciPy", marker='s', linewidth=2)
    plt.plot(dates, mk, label="MKL", marker='^', linewidth=2)
    
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Time (s)")
    plt.title("Benchmark Performance Over Time")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # 保存图片
    plt.savefig("benchmark.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Benchmark plot saved as benchmark.png")

def main():
    print("Starting benchmark update...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    
    # 确保matplotlib可以正常工作
    try:
        import matplotlib.pyplot as plt
        print("✅ Matplotlib imported successfully")
    except ImportError as e:
        print(f"❌ Matplotlib import failed: {e}")
        return
    
    # 运行基准测试
    print("Running benchmarks...")
    duration_py, amp_shape, phase_shape, error_py = run_safe("python")
    duration_scipy, _, _, error_scipy = run_safe("scipy")
    duration_mkl, _, _, error_mkl = run_safe("mkl")
    
    print(f"Python: {duration_py:.3f}s (error: {error_py})")
    print(f"SciPy: {duration_scipy:.3f}s (error: {error_scipy})")
    print(f"MKL: {duration_mkl:.3f}s (error: {error_mkl})")
    
    # 获取系统信息
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except subprocess.CalledProcessError:
        commit = "unknown"
    
    machine = platform.platform()
    pyver = platform.python_version()
    date = datetime.datetime.utcnow().isoformat() + "Z"
    
    # 创建表格行
    row = (
        f"| {date} | {machine} | {pyver} | {commit} | "
        f"{duration_py:.3f} | {duration_scipy:.3f} | {duration_mkl:.3f} | "
        f"{amp_shape[0]}x{amp_shape[1]} | {phase_shape[0]}x{phase_shape[1]} |"
    )
    
    print(f"Adding row: {row}")
    
    # 更新表格
    try:
        update_table(row)
        print("✅ Table updated successfully")
    except Exception as e:
        print(f"❌ Failed to update table: {e}")
        return
    
    # 解析数据并生成图表
    try:
        rows = parse_rows()
        print(f"Parsed {len(rows)} rows from table")
        plot(rows)
        print("✅ Plot generated successfully")
    except Exception as e:
        print(f"❌ Failed to generate plot: {e}")
        # 即使解析失败，也创建一个基本的图表
        try:
            plt.figure(figsize=(8, 4))
            plt.text(0.5, 0.5, f'Error generating plot: {str(e)}', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=plt.gca().transAxes, fontsize=12)
            plt.title("Benchmark Results (Error)")
            plt.tight_layout()
            plt.savefig("benchmark.png", dpi=300, bbox_inches='tight')
            plt.close()
            print("Error plot saved as benchmark.png")
        except Exception as e2:
            print(f"❌ Failed to create error plot: {e2}")
    
    # 验证文件是否创建
    if os.path.exists("benchmark.png"):
        file_size = os.path.getsize("benchmark.png")
        print(f"✅ benchmark.png created successfully ({file_size} bytes)")
    else:
        print("❌ benchmark.png was not created")
    
    print("Benchmark update completed!")

if __name__ == "__main__":
    main()
