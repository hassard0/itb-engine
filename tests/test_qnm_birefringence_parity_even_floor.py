"""Tests for the birefringence -> parity-even cross-sector floor (v2.350)."""

from experiments.qnm_birefringence_parity_even_floor import run

_RES = run()   # default seed/n_walk -> deterministic


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_derived_bound_closed_form():
    # g_4 * g_R2 >= bire_lower^2 / rho
    lo, rho = _RES["birefringence_lower_edge"], _RES["anomaly_rho"]
    assert abs(_RES["derived_lower_bound_g4_gR2"] - lo ** 2 / rho) < 1e-6
    assert _RES["derived_lower_bound_g4_gR2"] > 0


def test_constructed_and_family_respect_bound():
    b = _RES["derived_lower_bound_g4_gR2"]
    assert _RES["constructed_g4_gR2"] >= b
    # the analytic inequality cannot be violated by any feasible point
    assert _RES["family_min_g4_gR2"] >= b - 1e-6


def test_bound_is_data_sourced():
    # without the birefringence detection (lower edge -> 0) the bound vanishes
    assert _RES["bound_without_birefringence_data"] < 1e-4


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "cross-sector" in f
    assert "parity-even" in f
    assert "lower bound" in f
    sc = _RES["honest_scope"].lower()
    assert "exact algebra" in sc or "exact algebra given" in sc
    assert "v2.329" in sc
    assert "toy basis" in sc
