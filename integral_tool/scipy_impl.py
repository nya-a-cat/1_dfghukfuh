import numpy as np

try:
    from scipy import integrate as _integrate
except Exception:  # pragma: no cover - SciPy optional
    _integrate = None


def fresnel_hologram_scipy(points, amplitude, grid_x, grid_y, wavelength=532e-9, z0=0.1):
    """SciPy-based Simpson rule implementation of the integral."""
    if _integrate is None:
        raise RuntimeError("SciPy is required for this function")
    k = 2 * np.pi / wavelength
    x_grid, y_grid = np.meshgrid(grid_x, grid_y, indexing='ij')
    r = np.stack([x_grid, y_grid, np.full_like(x_grid, z0)], axis=-1)
    diff = r[np.newaxis, ...] - points[:, np.newaxis, np.newaxis, :]
    R = np.linalg.norm(diff, axis=-1)
    integrand = amplitude[:, np.newaxis, np.newaxis] * np.exp(1j * k * R) / R
    U = _integrate.simpson(integrand, dx=1.0, axis=0)
    U *= 1/(1j * wavelength)
    return U
