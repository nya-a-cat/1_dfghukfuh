// cppimport
<%
setup_pybind11(cfg)
cfg['compiler_args'] = ['-O3', '/openmp']
cfg['linker_args'] = ['/openmp']
%>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <complex>
#include <cmath>
#include <omp.h>

namespace py = pybind11;

py::array_t<std::complex<double>> fresnel_hologram_cpp_impl(
    py::array_t<double, py::array::c_style | py::array::forcecast> points,
    py::array_t<std::complex<double>, py::array::c_style | py::array::forcecast> amplitude,
    py::array_t<double, py::array::c_style | py::array::forcecast> grid_x,
    py::array_t<double, py::array::c_style | py::array::forcecast> grid_y,
    double wavelength = 532e-9,
    double z0 = 0.1)
{
    ssize_t n = points.shape(0);
    ssize_t nx = grid_x.shape(0);
    ssize_t ny = grid_y.shape(0);
    double k = 2 * M_PI / wavelength;

    auto result = py::array_t<std::complex<double>>({nx, ny});
    auto pts = points.unchecked<2>();
    auto amp = amplitude.unchecked<1>();
    auto gx = grid_x.unchecked<1>();
    auto gy = grid_y.unchecked<1>();
    auto out = result.mutable_unchecked<2>();

    #pragma omp parallel for
    for (ssize_t i = 0; i < nx; ++i) {
        for (ssize_t j = 0; j < ny; ++j) {
            std::complex<double> U(0.0, 0.0);
            for (ssize_t p = 0; p < n; ++p) {
                double dx = gx(i) - pts(p, 0);
                double dy = gy(j) - pts(p, 1);
                double dz = z0 - pts(p, 2);
                double R = std::sqrt(dx*dx + dy*dy + dz*dz);
                std::complex<double> val = amp(p) * std::exp(std::complex<double>(0.0, k * R)) / R;
                U += val;
            }
            out(i, j) = U / std::complex<double>(0.0, wavelength);
        }
    }
    return result;
}

PYBIND11_MODULE(cpp_integral_impl, m) {
    m.def("fresnel_hologram_cpp_impl", &fresnel_hologram_cpp_impl,
          py::arg("points"), py::arg("amplitude"),
          py::arg("grid_x"), py::arg("grid_y"),
          py::arg("wavelength") = 532e-9,
          py::arg("z0") = 0.1);
}
