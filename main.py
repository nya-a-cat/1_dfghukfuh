import numpy as np
import time
from integral_tool.integral import (
    point_source_wavefield,
    fresnel_hologram,
    fresnel_hologram_scipy,
    fresnel_hologram_mkl,
    amplitude_phase,
)


def generate_sample_points(n=50, scale=0.01):
    rng = np.random.default_rng(0)
    points = rng.uniform(-scale, scale, size=(n, 3))
    brightness = rng.uniform(0, 255, size=n)
    return points, brightness


def run_demo(method="python"):
    """Run a demo using the specified implementation."""
    points, brightness = generate_sample_points()
    amplitude = point_source_wavefield(points, brightness)
    grid = np.linspace(-0.05, 0.05, 64)
    start = time.time()
    if method == "python":
        U = fresnel_hologram(points, amplitude, grid, grid)
    elif method == "scipy":
        U = fresnel_hologram_scipy(points, amplitude, grid, grid)
    elif method == "mkl":
        U = fresnel_hologram_mkl(points, amplitude, grid, grid)
    else:
        raise ValueError(f"Unknown method: {method}")
    duration = time.time() - start
    A, phi = amplitude_phase(U)
    print(f"[{method}] Field computed in {duration:.3f} s")
    print(f"Amplitude shape: {A.shape}, phase shape: {phi.shape}")
    return duration, A.shape, phi.shape


if __name__ == "__main__":
    run_demo()
