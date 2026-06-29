"""Tests for the first-principles WKB QNM solver (v2.210)."""

import numpy as np

from experiments.qnm_wkb_solver import (
    REFERENCE,
    fornberg_weights,
    qnm_potential_sensitivity,
    rw_potential,
    r_of_rstar,
    schwarzschild_qnm,
    validate,
)


def test_tortoise_inversion_roundtrips():
    import math
    for r in (2.5, 3.28, 10.0, 50.0):
        rstar = r + 2.0 * math.log(r / 2.0 - 1.0)
        assert abs(r_of_rstar(rstar) - r) < 1e-9


def test_fornberg_reproduces_known_derivatives():
    # weights for f(x)=x^3 on a symmetric grid: f'(0)=0, f''(0)=0, f'''(0)=6
    x = np.linspace(-2, 2, 7)
    w = fornberg_weights(0.0, x, 3)
    samples = x**3
    assert abs(w[1] @ samples - 0.0) < 1e-9
    assert abs(w[3] @ samples - 6.0) < 1e-9


def test_potential_peak_value_is_textbook():
    # l=2 RW potential peaks near r=3.28 with V0 ~ 0.151 (M=1)
    rs = np.linspace(2.5, 4.5, 4000)
    V = [rw_potential(r) for r in rs]
    assert abs(max(V) - 0.1513) < 2e-3


def test_fundamental_and_overtone_match_canonical_modes():
    for n in (0, 1):
        w = schwarzschild_qnm(n)
        ref = REFERENCE[n]
        assert w.imag < 0                       # decaying (QNM convention)
        assert abs(w - ref) / abs(ref) < 5e-3   # 3rd-order WKB accuracy


def test_validate_reports_validated():
    out = validate()
    assert out["validated"] is True
    assert out["max_rel_error"] < 5e-3


def test_sensitivity_is_finite_and_nonzero():
    # a short-range deformation shifts both the frequency and the damping
    sens = qnm_potential_sensitivity(lambda r: (1 - 2 / r) / r**6, n=0)
    assert np.isfinite(sens["d_omega_R_d_eps"])
    assert np.isfinite(sens["d_omega_I_d_eps"])
    assert abs(sens["d_omega_R_d_eps"]) + abs(sens["d_omega_I_d_eps"]) > 1e-6
