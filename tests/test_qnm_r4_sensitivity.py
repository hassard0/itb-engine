"""Tests for the source-backed R4 odd-parity ringdown sensitivity (v2.215)."""

from experiments.qnm_r4_sensitivity import (
    E_J,
    R4_ODD_PREFACTOR,
    RH_E_J,
    R_G,
    r4_delta_V,
    r4_sensitivity,
    run,
)
from experiments.qnm_parametrized_basis import R_H, decompose_delta_V


def test_e10_is_sourced_from_mcmanus_table():
    # r_H * e_10^- = 0.0036853 + 0.0065244 i (McManus Table 1, odd-parity grav. l=2 n=0)
    assert RH_E_J[10] == complex(0.0036853, 0.0065244)
    assert E_J[10] == RH_E_J[10] / R_H


def test_r4_odd_parity_is_single_basis_function_at_j10():
    # delta_V_2^- = -432 eta_2 (r_g/r)^10  ->  decomposes to a single alpha_10
    alphas = decompose_delta_V(r4_delta_V(1.0), jmax=10)
    assert abs(alphas[10] - R4_ODD_PREFACTOR * R_H**2) / abs(R4_ODD_PREFACTOR * R_H**2) < 1e-6
    for j in range(10):
        assert abs(alphas[j]) < 1e-3            # all lower coefficients ~0


def test_prefactor_and_convention():
    assert R4_ODD_PREFACTOR == -432            # -18*(l+2)(l+1)l(l-1) for l=2
    assert R_G == 2.0                          # r_g = 2M (M=1)


def test_sensitivity_value_and_cross_check():
    s = r4_sensitivity()
    assert s["decomposition_cross_check_ok"] is True
    assert abs(s["alpha_10_per_eta2_analytic"] - (-1728.0)) < 1e-9
    # d(omega)/d(eta_2) = -1728 * e_10
    expected = -1728.0 * E_J[10]
    assert abs(complex(s["d_omega_d_eta2_re"], s["d_omega_d_eta2_im"]) - expected) < 1e-9
    assert s["d_omega_d_eta2_re"] < 0          # eta_2 > 0 lowers the frequency


def test_claim_gate_closed_on_the_number():
    res = run()
    assert res["claim_gate"].startswith("closed")
    assert "2205.05132" in res["references"][0]
