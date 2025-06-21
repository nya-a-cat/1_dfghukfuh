import numpy as np
from integral_tool.integral import point_source_wavefield, fresnel_hologram, amplitude_phase


def test_hologram_shape():
    points = np.array([[0.0, 0.0, 0.0]])
    brightness = np.array([255.0])
    amp = point_source_wavefield(points, brightness)
    grid = np.linspace(-0.01, 0.01, 8)
    U = fresnel_hologram(points, amp, grid, grid)
    A, phi = amplitude_phase(U)
    assert A.shape == (8, 8)
    assert phi.shape == (8, 8)
