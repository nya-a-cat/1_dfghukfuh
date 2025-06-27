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
