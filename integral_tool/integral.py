"""High level interface aggregating different implementations."""

from .python_impl import (
    point_source_wavefield,
    fresnel_hologram,
    surface_huygens_fresnel,
    amplitude_phase,
)

try:
    from .scipy_impl import fresnel_hologram_scipy
except Exception:  # pragma: no cover - SciPy optional
    def fresnel_hologram_scipy(*args, **kwargs):
        raise RuntimeError("SciPy is required for this function")

try:
    from .mkl_integral import fresnel_hologram_mkl as _fresnel_hologram_mkl
except Exception:  # pragma: no cover - fallback if build failed
    _fresnel_hologram_mkl = None

if _fresnel_hologram_mkl is None:
    from .python_impl import fresnel_hologram as fresnel_hologram_mkl
else:
    fresnel_hologram_mkl = _fresnel_hologram_mkl

__all__ = [
    "point_source_wavefield",
    "fresnel_hologram",
    "fresnel_hologram_scipy",
    "fresnel_hologram_mkl",
    "amplitude_phase",
    "surface_huygens_fresnel",
]
