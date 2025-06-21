# Integral Tool

This repository contains a simple Python implementation of a Huygens–Fresnel integral
for hologram computation. It includes a GitHub Actions workflow that runs a demo
and can be used for benchmarking.

## Usage

```bash
pip install -r requirements.txt
python main.py
```

The script generates random point sources, computes the field on a plane, and
outputs the amplitude and phase information.

## Benchmark Results

The following table is automatically updated by the GitHub Actions workflow.

<!-- BENCHMARK_START -->
| Date | Machine | Python | Git | Python(s) | SciPy(s) | MKL(s) | Amp shape | Phase shape |
|------|---------|--------|-----|----------|---------|-------|-----------|-------------|
| 2025-06-21T14:03:35.156183Z | Linux-6.12.13-x86_64-with-glibc2.39 | 3.12.10 | 1bb93da | 0.037 | - | - | 64x64 | 64x64 |
| 2025-06-21T14:20:11.087454Z | Linux-6.12.13-x86_64-with-glibc2.39 | 3.12.10 | 1492c36 | 0.014 | 0.020 | 0.008 | 64x64 | 64x64 |
| 2025-06-21T14:28:41.167642Z | Linux-6.12.13-x86_64-with-glibc2.39 | 3.12.10 | 6067630 | 0.014 | 0.019 | 0.008 | 64x64 | 64x64 |
<!-- BENCHMARK_END -->
