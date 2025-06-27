import numpy as np
from numpy.typing import NDArray
from typing import Tuple
import warnings

# Add a small epsilon for numerical stability to avoid division by zero
EPSILON = 1e-10


def point_source_wavefield(
    points: NDArray[np.float64],
    brightness: NDArray[np.float64],
    wavelength: float = 532e-9
) -> NDArray[np.float64]:
    """Compute per-point amplitude for point source wavefield.

    Parameters
    ----------
    points : NDArray
        Array of shape (N, 3) representing the coordinates (x, y, z) of N points.
    brightness : NDArray
        Array of shape (N,) representing the brightness of each point source.
    wavelength : float, optional
        Wavelength of the wave. Defaults to 532e-9.

    Returns
    -------
    NDArray
        Array of shape (N,) representing the normalized amplitude of each point source.

    Raises
    ------
    ValueError
        If brightness array is empty or contains only zeros.
    """
    if brightness.size == 0:
        raise ValueError("Brightness array cannot be empty.")
    max_brightness = np.max(brightness)
    if max_brightness == 0:
        # Handle case where all brightness values are zero
        # Returning zeros seems reasonable for normalized amplitude
        return np.zeros_like(brightness)
    amplitude = brightness / max_brightness
    return amplitude


def fresnel_hologram(
    points: NDArray[np.float64],
    amplitude: NDArray[np.float64],
    grid_x: NDArray[np.float64],
    grid_y: NDArray[np.float64],
    wavelength: float = 532e-9,
    z0: float = 0.1
) -> NDArray[np.complex128]:
    """Pure NumPy implementation of the Huygens-Fresnel integral for point sources.

    Parameters
    ----------
    points : NDArray
        Array of shape (N, 3) representing the coordinates (x, y, z) of N point sources.
    amplitude : NDArray
        Array of shape (N,) representing the amplitude of each point source.
    grid_x : NDArray
        1-D array of x-coordinates for the observation grid.
    grid_y : NDArray
        1-D array of y-coordinates for the observation grid.
    wavelength : float, optional
        Wavelength of the wave. Defaults to 532e-9.
    z0 : float, optional
        Distance between the source plane (z=0 for point sources) and the observation plane.
        Defaults to 0.1.

    Returns
    -------
    NDArray
        Complex field U(x, y) on the observation plane, shape (len(grid_x), len(grid_y)).

    Raises
    ------
    ValueError
        If wavelength is zero or points/amplitude arrays have incompatible shapes.
    """
    if wavelength == 0:
        raise ValueError("Wavelength cannot be zero.")
    if points.shape[0] != amplitude.shape[0]:
         raise ValueError("Points and amplitude arrays must have the same number of sources.")
    if points.shape[1] != 3:
         raise ValueError("Points array must have shape (N, 3).")

    k = 2 * np.pi / wavelength

    # Observation grid coordinates (x, y, z0)
    x_grid, y_grid = np.meshgrid(grid_x, grid_y, indexing='ij')
    r_obs = np.stack([x_grid, y_grid, np.full_like(x_grid, z0)], axis=-1) # Shape (Nx_obs, Ny_obs, 3)

    # Source points (xs, ys, zs)
    r_src = points # Shape (N_points, 3)
    amplitude_src = amplitude # Shape (N_points,)

    # Reshape for broadcasting:
    # r_obs: (Nx_obs, Ny_obs, 1, 3)
    # r_src: (1, 1, N_points, 3)
    r_obs_reshaped = r_obs[:, :, np.newaxis, :]
    r_src_reshaped = r_src[np.newaxis, np.newaxis, :, :]

    # Calculate difference vectors: (Nx_obs, Ny_obs, N_points, 3)
    # diff = r_obs - r_src
    diff = r_obs_reshaped - r_src_reshaped

    # Calculate distances R: (Nx_obs, Ny_obs, N_points)
    # R = |r_obs - r_src| = sqrt(dx^2 + dy^2 + dz^2)
    R_sq = np.sum(diff**2, axis=-1)
    # Add epsilon inside sqrt for better numerical stability to avoid division by zero if R is exactly zero
    R = np.sqrt(R_sq + EPSILON**2)

    # Reshape amplitude for broadcasting: (1, 1, N_points)
    amplitude_src_reshaped = amplitude_src[np.newaxis, np.newaxis, :]

    # Calculate the term for each source point and observation point
    # This corresponds to A * exp(i * k * R) / R for each source-observation pair
    # term shape: (Nx_obs, Ny_obs, N_points)
    term = amplitude_src_reshaped * np.exp(1j * k * R) / R

    # Sum contributions from all source points: (Nx_obs, Ny_obs)
    # This performs the summation over all point sources
    U = np.sum(term, axis=-1)

    # Final constant multiplication: 1 / (i * lambda)
    U *= 1 / (1j * wavelength)

    return U


def amplitude_phase(U: NDArray[np.complex128]) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Return amplitude and phase of a complex field.

    Parameters
    ----------
    U : NDArray
        Complex field.

    Returns
    -------
    Tuple[NDArray, NDArray]
        Tuple containing:
        - Amplitude (absolute value) of the complex field.
        - Phase (angle) of the complex field in radians.
    """
    A = np.abs(U)
    phi = np.angle(U)
    return A, phi


def surface_huygens_fresnel(
    U_s: NDArray[np.complex128],
    grid_x_s: NDArray[np.float64],
    grid_y_s: NDArray[np.float64],
    grid_x: NDArray[np.float64],
    grid_y: NDArray[np.float64],
    wavelength: float = 532e-9,
    z0: float = 0.1
) -> NDArray[np.complex128]:
    """Numerically evaluate the Huygens--Fresnel surface integral.

    Parameters
    ----------
    U_s : NDArray (Nx_s, Ny_s)
        Complex field ``U_s(x', y')`` defined on the source plane ``z=0``.
    grid_x_s : NDArray
        1-D array describing the x-coordinates ``x'`` of ``U_s``.
    grid_y_s : NDArray
        1-D array describing the y-coordinates ``y'`` of ``U_s``.
    grid_x : NDArray
        1-D array of the observation x-coordinates ``x`` at ``z=z0``.
    grid_y : NDArray
        1-D array of the observation y-coordinates ``y`` at ``z=z0``.
    wavelength : float, optional
        Wavelength :math:`\lambda` of the wave. Defaults to 532e-9.
    z0 : float, optional
        Distance between the source and observation planes. Defaults to 0.1.

    Returns
    -------
    NDArray
        Complex field ``U(x, y)`` on the observation plane, shape (len(grid_x), len(grid_y)).

    Raises
    ------
    ValueError
        If wavelength is zero, U_s shape is incompatible with source grids,
        or source grids are not 1D.
    RuntimeWarning
        If source grids are not evenly spaced, as dS calculation assumes uniform spacing.

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
    if wavelength == 0:
        raise ValueError("Wavelength cannot be zero.")
    if grid_x_s.ndim != 1 or grid_y_s.ndim != 1:
         raise ValueError("Source grids grid_x_s and grid_y_s must be 1-dimensional.")
    if U_s.shape != (len(grid_x_s), len(grid_y_s)):
         raise ValueError("U_s shape must match the dimensions of grid_x_s and grid_y_s.")
    if grid_x.ndim != 1 or grid_y.ndim != 1:
         raise ValueError("Observation grids grid_x and grid_y must be 1-dimensional.")


    k = 2 * np.pi / wavelength

    # Observation grid coordinates (x, y, z0)
    x_obs, y_obs = np.meshgrid(grid_x, grid_y, indexing="ij") # Shape (Nx_obs, Ny_obs)

    # Source grid coordinates (x', y', 0)
    x_src, y_src = np.meshgrid(grid_x_s, grid_y_s, indexing="ij") # Shape (Nx_s, Ny_s)

    # Assume uniform spacing for the area element dS'
    dx = np.mean(np.diff(grid_x_s))
    dy = np.mean(np.diff(grid_y_s))
    dS = dx * dy

    # Check if spacing is uniform and issue a warning if not
    if not np.allclose(np.diff(grid_x_s), dx) or not np.allclose(np.diff(grid_y_s), dy):
        warnings.warn("Source grids grid_x_s or grid_y_s are not evenly spaced. dS calculation assumes uniform spacing.", RuntimeWarning)


    # Reshape for broadcasting:
    # x_obs: (Nx_obs, Ny_obs, 1, 1)
    # y_obs: (Nx_obs, Ny_obs, 1, 1)
    # x_src: (1, 1, Nx_s, Ny_s)
    # y_src: (1, 1, Nx_s, Ny_s)
    x_obs_reshaped = x_obs[:, :, np.newaxis, np.newaxis]
    y_obs_reshaped = y_obs[:, :, np.newaxis, np.newaxis]
    x_src_reshaped = x_src[np.newaxis, np.newaxis, :, :]
    y_src_reshaped = y_src[np.newaxis, np.newaxis, :, :]

    # Calculate difference vectors components: (Nx_obs, Ny_obs, Nx_s, Ny_s)
    # dx_ = x - x'
    dx_ = x_obs_reshaped - x_src_reshaped
    # dy_ = y - y'
    dy_ = y_obs_reshaped - y_src_reshaped
    # dz_ = z - z' = z0 - 0 = z0
    dz_ = z0 # Scalar

    # Calculate distances R: (Nx_obs, Ny_obs, Nx_s, Ny_s)
    # R = |r - r'| = sqrt((x-x')^2 + (y-y')^2 + (z-z')^2)
    R_sq = dx_ ** 2 + dy_ ** 2 + dz_ ** 2
    # Add epsilon inside sqrt for better numerical stability to avoid division by zero if R is exactly zero
    R = np.sqrt(R_sq + EPSILON**2)

    # cos(theta) between normal (0, 0, 1) and displacement vector (r - r')
    # cos(theta) = (r - r') . (0, 0, 1) / |r - r'| = dz_ / R
    # cos_theta shape: (Nx_obs, Ny_obs, Nx_s, Ny_s)
    cos_theta = dz_ / R
    # Obliquity factor K(theta) = (1 + cos(theta)) / 2
    K = (1.0 + cos_theta) / 2.0 # K shape: (Nx_obs, Ny_obs, Nx_s, Ny_s)

    # Reshape U_s for broadcasting: (1, 1, Nx_s, Ny_s)
    U_s_reshaped = U_s[np.newaxis, np.newaxis, :, :] # Shape (1, 1, Nx_s, Ny_s)

    # Calculate the integrand term: (Nx_obs, Ny_obs, Nx_s, Ny_s)
    # Integrand = U_s(x', y') * K(theta) * exp(i * k * R) / R * dS'
    integrand = U_s_reshaped * K * np.exp(1j * k * R) / R * dS

    # Sum contributions over the source dimensions (-2, -1): (Nx_obs, Ny_obs)
    # This performs the surface integral approximation by summing over the source grid points
    U = np.sum(integrand, axis=(-2, -1))

    # Final constant multiplication: 1 / (i * lambda)
    U *= 1 / (1j * wavelength)

    return U
