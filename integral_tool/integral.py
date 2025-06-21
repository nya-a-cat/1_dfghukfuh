import numpy as np

try:
    from scipy import integrate as _integrate
except Exception:  # pragma: no cover - SciPy optional
    _integrate = None

try:
    from .mkl_integral import fresnel_hologram_mkl as fresnel_hologram_mkl
except Exception:  # pragma: no cover - fallback if build failed
    fresnel_hologram_mkl = None


def point_source_wavefield(points, brightness, wavelength=532e-9):
    """Compute per-point amplitude for point source wavefield."""
    amplitude = brightness / np.max(brightness)
    return amplitude


def fresnel_hologram(points, amplitude, grid_x, grid_y, wavelength=532e-9, z0=0.1):
    """Compute Huygens-Fresnel integral on a plane z=z0."""
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


def fresnel_hologram_scipy(points, amplitude, grid_x, grid_y, wavelength=532e-9, z0=0.1):
    """Compute integral using SciPy's Simpson rule."""
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


def fresnel_hologram_mkl_fallback(points, amplitude, grid_x, grid_y, wavelength=532e-9, z0=0.1):
    """Vectorized implementation used if MKL extension is unavailable."""
    k = 2 * np.pi / wavelength
    x_grid, y_grid = np.meshgrid(grid_x, grid_y, indexing='ij')
    r = np.stack([x_grid, y_grid, np.full_like(x_grid, z0)], axis=-1)
    diff = r[np.newaxis, ...] - points[:, np.newaxis, np.newaxis, :]
    R = np.linalg.norm(diff, axis=-1)
    U = np.sum(amplitude[:, np.newaxis, np.newaxis] * np.exp(1j * k * R) / R, axis=0)
    U *= 1/(1j * wavelength)
    return U


if fresnel_hologram_mkl is None:
    fresnel_hologram_mkl = fresnel_hologram_mkl_fallback


def amplitude_phase(U):
    """Return amplitude and phase of complex field."""
    A = np.abs(U)
    phi = np.angle(U)
    return A, phi
