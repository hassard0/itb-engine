"""Tests for the parity<->screening cross-channel correlation (v2.357)."""

from experiments.qnm_parity_screening_correlation import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_mandate_active_at_parity_floor():
    assert _RES["over_cap_at_parity_floor"] > 1.0


def test_over_cap_increases_with_parity():
    facs = [r["over_cap_factor"] for r in _RES["over_cap_ladder"]]
    assert facs == sorted(facs)
    assert facs[0] < facs[-1]


def test_quadratic_scaling():
    assert abs(_RES["ratio_observed_floor_to_edge"] - _RES["ratio_if_quadratic"]) < 1e-3


def test_family_positive_correlation_and_floor():
    assert _RES["family_corr_gR2_gR2parity"] > 0.0
    assert _RES["consistency_checks"]["family_respects_anomaly_floor"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "correlated" in f
    assert "parity" in f and "screening" in f
    assert "quadratic" in f
    sc = _RES["honest_scope"].lower()
    assert "exact algebra" in sc
    assert "v2.329" in sc
    assert "toy basis" in sc
