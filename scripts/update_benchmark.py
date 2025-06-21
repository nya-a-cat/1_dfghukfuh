import datetime
import platform
import subprocess
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import run_demo

START_MARK = "<!-- BENCHMARK_START -->"
END_MARK = "<!-- BENCHMARK_END -->"


def main():
    duration, amp_shape, phase_shape = run_demo()
    commit = (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])\
        .decode().strip()
    )
    machine = platform.platform()
    pyver = platform.python_version()
    date = datetime.datetime.utcnow().isoformat() + "Z"

    row = f"| {date} | {machine} | {pyver} | {commit} | {duration:.3f} | {amp_shape[0]}x{amp_shape[1]} | {phase_shape[0]}x{phase_shape[1]} |"

    path = "README.md"
    text = open(path).read().splitlines()
    try:
        start = text.index(START_MARK)
        end = text.index(END_MARK)
    except ValueError:
        raise SystemExit("Benchmark markers not found in README")

    table = text[start + 1:end]
    if not table or not table[0].startswith("| Date |"):
        header = [
            "| Date | Machine | Python | Git | Runtime(s) | Amp shape | Phase shape |",
            "|------|---------|--------|-----|-----------|-----------|-------------|",
        ]
        table = header + [row]
    else:
        table.append(row)
    text[start + 1:end] = table
    with open(path, "w") as fh:
        fh.write("\n".join(text) + "\n")


if __name__ == "__main__":
    main()
