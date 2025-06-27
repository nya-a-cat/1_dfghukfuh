import numpy as np

try:
    import cppimport
    cpp_mod = cppimport.imp('integral_tool.cpp_integral_impl')
    fresnel_hologram_cpp = cpp_mod.fresnel_hologram_cpp_impl
except Exception:  # pragma: no cover - fallback to numpy
    def fresnel_hologram_cpp(points, amplitude, grid_x, grid_y, wavelength=532e-9, z0=0.1):
        k = 2 * np.pi / wavelength
        x_grid, y_grid = np.meshgrid(grid_x, grid_y, indexing='ij')
        r = np.stack([x_grid, y_grid, np.full_like(x_grid, z0)], axis=-1)
        diff = r[np.newaxis, ...] - points[:, np.newaxis, np.newaxis, :]
        R = np.linalg.norm(diff, axis=-1)
        U = np.sum(amplitude[:, np.newaxis, np.newaxis] * np.exp(1j * k * R) / R, axis=0)
        U *= 1/(1j * wavelength)
        return U

__all__ = ['fresnel_hologram_cpp']
