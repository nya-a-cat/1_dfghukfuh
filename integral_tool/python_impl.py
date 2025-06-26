import numpy as np


def point_source_wavefield(points, brightness, wavelength=532e-9):
    """Compute per-point amplitude for point source wavefield."""
    amplitude = brightness / np.max(brightness)
    return amplitude


def fresnel_hologram(points, amplitude, grid_x, grid_y, wavelength=532e-9, z0=0.1):
    """Pure NumPy implementation of the Huygens-Fresnel integral."""
    k = 2 * np.pi / wavelength
    x_grid, y_grid = np.meshgrid(grid_x, grid_y, indexing='ij')
    r = np.stack([x_grid, y_grid, np.full_like(x_grid, z0)], axis=-1)
    U = np.zeros(x_grid.shape, dtype=np.complex128)
    for (xs, ys, zs), A in zip(points, amplitude):
        r_s = np.array([xs, ys, zs])
        diff = r - r_s
        R = np.linalg.norm(diff, axis=-1)
        U += A * np.exp(1j * k * R) / R
    U *= 1/(1j * wavelength)
    return U


def amplitude_phase(U):
    """Return amplitude and phase of a complex field."""
    A = np.abs(U)
    phi = np.angle(U)
    return A, phi
