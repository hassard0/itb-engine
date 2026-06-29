"""Tests for the QNM solver validation suite (v2.211)."""

from experiments.qnm_validation_suite import (
    REFERENCE_TABLE,
    run_validation,
    schwarzschild_mode,
    sensitivity_robustness,
)


def test_all_reference_modes_within_wkb_tolerance():
    rows = run_validation()
    assert len(rows) == len(REFERENCE_TABLE) == 8
    assert all(r["within_wkb_tol"] for r in rows)


def test_gravitational_anchor_is_precise():
    # s=2, l=2, n=0 is the exact anchor: 3rd-order WKB to ~0.15%
    w = schwarzschild_mode(2, 2, 0)
    ref = complex(0.373672, -0.088962)
    assert abs(w - ref) / abs(ref) < 3e-3


def test_high_l_mode_is_very_accurate():
    # WKB improves with l; s=2, l=3, n=0 to ~0.03%
    w = schwarzschild_mode(2, 3, 0)
    ref = complex(0.599443, -0.092703)
    assert abs(w - ref) / abs(ref) < 1e-3


def test_solver_general_across_spin_weight():
    # distinct potentials (scalar s=0, EM s=1, gravitational s=2) give distinct modes
    w0 = schwarzschild_mode(0, 2, 0)
    w1 = schwarzschild_mode(1, 2, 0)
    w2 = schwarzschild_mode(2, 2, 0)
    assert w0.real > w1.real > w2.real          # scalar > EM > gravitational (l=2)
    assert all(w.imag < 0 for w in (w0, w1, w2))


def test_sensitivity_machinery_is_stable():
    s = sensitivity_robustness()
    assert s["relative_scatter"] < 0.05         # analytic-through-WKB: noise-free
    assert abs(s["d_omegaR_d_eps_mean"]) > 1e-3
