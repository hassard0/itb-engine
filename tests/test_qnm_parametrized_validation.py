"""Tests for the parametrized-ringdown validation (v2.212).

Documents the honest finding: the WKB-at-peak operator->QNM sensitivity is numerically
stable (v2.211) but does NOT reproduce the published McManus et al. e_j to claim grade --
because the true sensitivity is a global mode-overlap integral, not a peak quantity.
"""

from experiments.qnm_parametrized_validation import RH_E, R_H, basis_delta_V, run
from experiments.qnm_wkb_solver import qnm_potential_sensitivity


def test_reference_coefficients_in_M1_units():
    # tabulated r_H * e_0 = 0.24725 + 0.092643 i  ->  e_0 (M=1) = that / 2
    e0 = RH_E[0] / R_H
    assert abs(e0.real - 0.123625) < 1e-6
    assert abs(e0.imag - 0.0463215) < 1e-6


def test_wkb_peak_sensitivity_is_structured_but_not_claim_grade():
    res = run()
    rows = res["comparison"]
    assert len(rows) == 3
    # finite, real-part-positive, and DECREASING in magnitude with j (correct structure)
    mags = [abs(complex(r["e_wkb_re"], r["e_wkb_im"])) for r in rows]
    assert all(r["e_wkb_re"] > 0 for r in rows)
    assert mags[0] > mags[1] > mags[2]
    # but NOT accurate: misses the published e_j by a large factor (the honest negative)
    assert res["wkb_peak_sensitivity_reproduces_e_j"] is False
    assert res["max_rel_error"] > 0.5


def test_sensitivity_still_numerically_stable():
    # stability (v2.211) holds even though accuracy (v2.212) does not
    a = qnm_potential_sensitivity(basis_delta_V(1), n=0, t=3e-4)["d_omega_d_eps"]
    b = qnm_potential_sensitivity(basis_delta_V(1), n=0, t=3e-3)["d_omega_d_eps"]
    assert abs(a - b) / abs(b) < 1e-2
