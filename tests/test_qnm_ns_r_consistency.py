"""Tests for the n_s-r inflation consistency relation (v2.452)."""

from experiments.qnm_ns_r_consistency import run, r_of_ns

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_relation_formula():
    assert abs(r_of_ns(0.9649) - 3 * (1 - 0.9649) ** 2) < 1e-12
    assert abs(r_of_ns(1.0)) < 1e-12   # n_s=1 => r=0


def test_r_pinned_near_expected():
    assert 0.002 < _RES["r_predicted_central"] < 0.006
    assert _RES["equivalent_N_efolds"] > 40


def test_litebird_testable():
    assert _RES["r_predicted_central"] > 2 * _RES["litebird_sigma_r"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "scale-independent" in f
    assert "r = 3(1-n_s)^2" in f
    assert "second" in f  # second dimensionless prediction
    sc = _RES["honest_scope"].lower()
    assert "plateau-class" in sc
    assert "leading order" in sc
    assert "not uniquely" in sc
