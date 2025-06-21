import numpy as np
from integral_tool.integral import (
    point_source_wavefield,
    fresnel_hologram,
    fresnel_hologram_scipy,
    fresnel_hologram_mkl,
    amplitude_phase,
)


def test_hologram_shape():
    points = np.array([[0.0, 0.0, 0.0]])
    brightness = np.array([255.0])
    amp = point_source_wavefield(points, brightness)
    grid = np.linspace(-0.01, 0.01, 8)
    U = fresnel_hologram(points, amp, grid, grid)
    A, phi = amplitude_phase(U)
    assert A.shape == (8, 8)
    assert phi.shape == (8, 8)


def test_scipy_and_mkl_shapes():
    points = np.array([[0.0, 0.0, 0.0]])
    brightness = np.array([255.0])
    amp = point_source_wavefield(points, brightness)
    grid = np.linspace(-0.01, 0.01, 8)
    U1 = fresnel_hologram_scipy(points, amp, grid, grid)
    U2 = fresnel_hologram_mkl(points, amp, grid, grid)
    assert U1.shape == (8, 8)
    assert U2.shape == (8, 8)
