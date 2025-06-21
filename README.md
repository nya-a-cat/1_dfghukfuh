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

<!-- BENCHMARK_END -->
