import csv
import datetime
import os
import platform
import subprocess
import sys

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
    rows = []
    with open("README.md") as fh:
        in_table = False
        for line in fh:
            if line.strip() == START_MARK:
                in_table = True
                continue
            if line.strip() == END_MARK:
                break
            if not in_table:
                continue
            line = line.strip()
            if not line or line.startswith("| Date ") or line.startswith("|------"):
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) < 9:
                continue
            rows.append(
                {
                    "date": parts[0],
                    "python": float(parts[4]),
                    "scipy": float(parts[5]),
                    "mkl": float(parts[6]),
                }
            )
    return rows


def plot(rows):
    if not rows:
        return
    dates = [r["date"] for r in rows]
    py = [r["python"] for r in rows]
    sp = [r["scipy"] for r in rows]
    mk = [r["mkl"] for r in rows]
    plt.figure(figsize=(8, 4))
    plt.plot(dates, py, label="Python")
    plt.plot(dates, sp, label="SciPy")
    plt.plot(dates, mk, label="MKL")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Time (s)")
    plt.tight_layout()
    plt.legend()
    plt.savefig("benchmark.png")


def main():
    duration_py, amp_shape, phase_shape, _ = run_safe("python")
    duration_scipy, _, _, _ = run_safe("scipy")
    duration_mkl, _, _, _ = run_safe("mkl")
    commit = (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    )
    machine = platform.platform()
    pyver = platform.python_version()
    date = datetime.datetime.now(datetime.timezone.utc).isoformat()

    row = (
        f"| {date} | {machine} | {pyver} | {commit} | "
        f"{duration_py:.3f} | {duration_scipy:.3f} | {duration_mkl:.3f} | "
        f"{amp_shape[0]}x{amp_shape[1]} | {phase_shape[0]}x{phase_shape[1]} |"
    )

    update_table(row)
    rows = parse_rows()
    plot(rows)


if __name__ == "__main__":
    main()
