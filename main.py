import argparse
import numpy as np
import time
from integral_tool.integral import (
    point_source_wavefield,
    fresnel_hologram,
    fresnel_hologram_scipy,
    fresnel_hologram_cpp,
    amplitude_phase,
)
from integral_tool.io import load_points_from_obj


def generate_sample_points(n=50, scale=0.01):
    rng = np.random.default_rng(0)
    points = rng.uniform(-scale, scale, size=(n, 3))
    brightness = rng.uniform(0, 255, size=n)
    return points, brightness


def run_demo(method="python", points=None, brightness=None):
    """Run a demo using the specified implementation."""
    if points is None:
        points, brightness = generate_sample_points()
    
    if brightness is None:
        # Assign uniform brightness if not provided (e.g., for obj files)
        brightness = np.full(points.shape[0], 255.0)

    amplitude = point_source_wavefield(points, brightness)
    grid = np.linspace(-0.05, 0.05, 64)
    start = time.time()
    if method == "python":
        U = fresnel_hologram(points, amplitude, grid, grid)
    elif method == "scipy":
        U = fresnel_hologram_scipy(points, amplitude, grid, grid)
    elif method == "cpp":
        U = fresnel_hologram_cpp(points, amplitude, grid, grid)
    else:
        raise ValueError(f"Unknown method: {method}")
    duration = time.time() - start
    A, phi = amplitude_phase(U)
    print(f"[{method}] Field computed in {duration:.3f} s")
    print(f"Amplitude shape: {A.shape}, phase shape: {phi.shape}")
    return duration, A.shape, phi.shape


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Huygens-Fresnel integral demo.")
    parser.add_argument(
        "--method",
        type=str,
        default="python",
        choices=["python", "scipy", "cpp"],
        help="Implementation method to use.",
    )
    parser.add_argument(
        "--input-file",
        type=str,
        help="Path to a .obj file to load points from.",
    )
    args = parser.parse_args()

    points, brightness = None, None
    if args.input_file:
        try:
            points = load_points_from_obj(args.input_file)
            print(f"Loaded {len(points)} points from {args.input_file}")
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            exit(1)
    
    run_demo(method=args.method, points=points, brightness=brightness)
