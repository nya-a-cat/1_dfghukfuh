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


def surface_huygens_fresnel(U_s, grid_x_s, grid_y_s, grid_x, grid_y, wavelength=532e-9, z0=0.1):
    """Numerically evaluate the Huygens--Fresnel surface integral.

    Parameters
    ----------
    U_s : ndarray (Nx, Ny)
        Complex field ``U_s(x', y')`` defined on the source plane ``z=0``.
    grid_x_s, grid_y_s : ndarray
        1-D arrays describing the coordinates ``x'`` and ``y'`` of ``U_s``.
    grid_x, grid_y : ndarray
        1-D arrays of the observation coordinates ``(x, y)`` at ``z=z0``.
    wavelength : float, optional
        Wavelength :math:`\lambda` of the wave.
    z0 : float, optional
        Distance between the source and observation planes.

    Returns
    -------
    ndarray
        Complex field ``U(x, y)`` on the observation plane.

    Notes
    -----
    The integral implemented is

    .. math::

        U(x, y) = \frac{1}{i\lambda} \iint_S
        U_s(x', y') \, K(\theta) \frac{\exp(i k R)}{R} \, dS',

    where ``k = 2\pi/\lambda``, ``R = |\vec{r} - \vec{r}'|`` and
    ``K(\theta) = (1 + \cos\theta)/2``.  The surface element ``dS'`` is
    approximated assuming an evenly spaced source grid.
    """

    k = 2 * np.pi / wavelength

    # Observation grid coordinates (x, y, z0)
    x_obs, y_obs = np.meshgrid(grid_x, grid_y, indexing="ij")

    # Source grid coordinates (x', y', 0)
    x_src, y_src = np.meshgrid(grid_x_s, grid_y_s, indexing="ij")

    # Assume uniform spacing for the area element dS'
    dx = np.mean(np.diff(grid_x_s))
    dy = np.mean(np.diff(grid_y_s))
    dS = dx * dy

    U = np.zeros_like(x_obs, dtype=np.complex128)

    for i in range(x_src.shape[0]):
        for j in range(x_src.shape[1]):
            # Vector from source point (x', y', 0) to each observation point
            dx_ = x_obs - x_src[i, j]
            dy_ = y_obs - y_src[i, j]
            dz_ = z0
            R = np.sqrt(dx_ ** 2 + dy_ ** 2 + dz_ ** 2)

            # cos(theta) between normal (0, 0, 1) and displacement vector
            cos_theta = dz_ / R
            K = (1.0 + cos_theta) / 2.0

            U += U_s[i, j] * K * np.exp(1j * k * R) / R * dS

    U *= 1 / (1j * wavelength)
    return U
