import numpy as np
from integral_tool.integral import (
    point_source_wavefield,
    fresnel_hologram,
    fresnel_hologram_scipy,
    fresnel_hologram_cpp,
    surface_huygens_fresnel,
    amplitude_phase,
)
from integral_tool.io import load_points_from_obj


def test_load_obj():
    """Test loading points from a .obj file."""
    points = load_points_from_obj("tests/sample.obj")
    assert points.shape == (3, 3)
    
    expected_points = np.array([
        [0.01, 0.01, 0.0],
        [-0.01, 0.01, 0.0],
        [0.0, -0.01, 0.0]
    ])
    assert np.allclose(points, expected_points)


def test_hologram_shape():
    points = np.array([[0.0, 0.0, 0.0]])
    brightness = np.array([255.0])
    amp = point_source_wavefield(points, brightness)
    grid = np.linspace(-0.01, 0.01, 8)
    U = fresnel_hologram(points, amp, grid, grid)
    A, phi = amplitude_phase(U)
    assert A.shape == (8, 8)
    assert phi.shape == (8, 8)


def test_scipy_and_cpp_shapes():
    points = np.array([[0.0, 0.0, 0.0]])
    brightness = np.array([255.0])
    amp = point_source_wavefield(points, brightness)
    grid = np.linspace(-0.01, 0.01, 8)
    U1 = fresnel_hologram_scipy(points, amp, grid, grid)
    U2 = fresnel_hologram_cpp(points, amp, grid, grid)
    assert U1.shape == (8, 8)
    assert U2.shape == (8, 8)


def test_surface_integral_shape():
    xs = np.linspace(-0.01, 0.01, 8)
    ys = np.linspace(-0.01, 0.01, 8)
    xg, yg = np.meshgrid(xs, ys, indexing="ij")
    Us = np.ones_like(xg, dtype=np.complex128)
    U = surface_huygens_fresnel(Us, xs, ys, xs, ys)
    assert U.shape == (8, 8)


def test_numerical_consistency():
    """Test that python, scipy, and cpp implementations are numerically consistent."""
    points = np.array([[0.001, 0.002, 0.0], [-0.001, -0.002, 0.003]])
    brightness = np.array([200.0, 150.0])
    amp = point_source_wavefield(points, brightness)
    grid = np.linspace(-0.01, 0.01, 4)

    U_py = fresnel_hologram(points, amp, grid, grid)
    U_scipy = fresnel_hologram_scipy(points, amp, grid, grid)
    U_cpp = fresnel_hologram_cpp(points, amp, grid, grid)

    # Check that pure python and C++ implementations are very close
    assert np.allclose(U_py, U_cpp, rtol=1e-5, atol=1e-8)

    # The SciPy implementation uses a different integration rule, so the tolerance is looser
    assert np.allclose(U_py, U_scipy, rtol=1e-3, atol=1e-5)
