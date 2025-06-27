import csv
import datetime
import os
import platform
import subprocess
import sys
import time
import matplotlib
import psutil
matplotlib.use('Agg')  # 确保使用非交互式后端
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------------------------------------
# 1. 设置全局字体和图表风格
# -----------------------------------------------------------
plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 10,
    'grid.linestyle': ':',
    'grid.color': 'lightgray',
    'grid.alpha': 0.7,
    'axes.prop_cycle': plt.cycler(color=plt.cm.Paired.colors)
})

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from main import run_demo
except ImportError:
    print("Warning: main.py not found or run_demo not callable. Benchmarking will fail.", file=sys.stderr)
    def run_demo(method):
        print(f"Placeholder run_demo called for method: {method}")
        return 0.1, (64, 64), (64, 64)

def run_safe(method):
    """Run a demo and catch errors, measuring time and memory."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    try:
        duration, amp_shape, phase_shape = run_demo(method)
        final_memory = process.memory_info().rss
        memory_used = final_memory - initial_memory
        return duration, memory_used, amp_shape, phase_shape, None
    except Exception as exc:
        print(f"{method} failed: {exc}", file=sys.stderr)
        return float("nan"), float("nan"), (0, 0), (0, 0), str(exc)

def get_git_commit():
    """Get the short hash of the current git commit."""
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit = "unknown"
    return commit

def append_to_csv(data_row, filepath="benchmark_results.csv"):
    """Append a new row of data to the CSV file."""
    file_exists = os.path.isfile(filepath)
    with open(filepath, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data_row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data_row)
    print(f"✅ Appended results to {filepath}")

def read_from_csv(filepath="benchmark_results.csv"):
    """Read all benchmark data from the CSV file."""
    if not os.path.exists(filepath):
        print(f"Warning: Benchmark data file not found at {filepath}", file=sys.stderr)
        return []
    
    rows = []
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            processed_row = {}
            for key, value in row.items():
                try:
                    processed_row[key] = float(value)
                except (ValueError, TypeError):
                    processed_row[key] = value
            rows.append(processed_row)
    return rows

def plot(rows):
    """Generate benchmark plot showing time and memory usage for the latest run."""
    print(f"Plotting data for {len(rows)} total runs...")

    if not rows:
        print("No data to plot, creating empty plot...")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'No benchmark data available',
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=16)
        ax.set_title("Benchmark Results")
        plt.tight_layout()
        plt.savefig("benchmark.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        return

    latest_run = rows[-1]
    methods = ['Python', 'SciPy', 'CPP']
    time_values = [latest_run['python_time'], latest_run['scipy_time'], latest_run['cpp_time']]
    memory_values = [latest_run['python_memory'], latest_run['scipy_memory'], latest_run['cpp_memory']]

    x = np.arange(len(methods))
    width = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Plotting Time
    ax1.bar(x, time_values, width, label='Time (s)', color='royalblue')
    ax1.set_ylabel('Time (s)')
    ax1.set_title('Benchmark Runtime by Method')
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods)
    ax1.grid(axis='y', linestyle=':', alpha=0.7)

    # Plotting Memory
    ax2.bar(x, memory_values, width, label='Memory (MB)', color='sandybrown')
    ax2.set_ylabel('Memory (MB)')
    ax2.set_title('Benchmark Memory Usage by Method')
    ax2.set_xticks(x)
    ax2.set_xticklabels(methods)
    ax2.grid(axis='y', linestyle=':', alpha=0.7)

    fig.suptitle(f"Benchmark Performance - {latest_run['date']}")
    plt.tight_layout()
    plt.savefig("benchmark.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("✅ Benchmark plot saved as benchmark.png")

def main():
    print("Starting benchmark update...")
    
    # Run benchmarks
    print("Running benchmarks...")
    duration_py, memory_py, amp_shape, phase_shape, error_py = run_safe("python")
    duration_scipy, memory_scipy, _, _, error_scipy = run_safe("scipy")
    duration_cpp, memory_cpp, _, _, error_cpp = run_safe("cpp")
    
    print(f"Python: {duration_py:.3f}s, {memory_py / (1024*1024):.2f}MB (error: {error_py})")
    print(f"SciPy: {duration_scipy:.3f}s, {memory_scipy / (1024*1024):.2f}MB (error: {error_scipy})")
    print(f"CPP: {duration_cpp:.3f}s, {memory_cpp / (1024*1024):.2f}MB (error: {error_cpp})")
    
    # Create data dictionary
    data_row = {
        "date": datetime.datetime.utcnow().isoformat(timespec='seconds') + "Z",
        "machine": platform.platform(terse=True),
        "python_version": platform.python_version(),
        "git_commit": get_git_commit(),
        "python_time": f"{duration_py:.3f}",
        "python_memory": f"{memory_py / (1024*1024):.2f}",
        "scipy_time": f"{duration_scipy:.3f}",
        "scipy_memory": f"{memory_scipy / (1024*1024):.2f}",
        "cpp_time": f"{duration_cpp:.3f}",
        "cpp_memory": f"{memory_cpp / (1024*1024):.2f}",
        "amp_shape": f"{amp_shape[0]}x{amp_shape[1]}",
        "phase_shape": f"{phase_shape[0]}x{phase_shape[1]}",
        "error_python": error_py,
        "error_scipy": error_scipy,
        "error_cpp": error_cpp,
    }
    
    # Append to CSV
    append_to_csv(data_row)
    
    # Read all data and generate plot
    all_data = read_from_csv()
    plot(all_data)
    
    print("Benchmark update completed!")

if __name__ == "__main__":
    main()