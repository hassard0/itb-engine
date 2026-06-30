"""Tests for the theory-vs-data capstone scorecard (v2.322)."""

from experiments.qnm_theory_vs_data_scorecard import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_parity_even_frameworks_data_excluded():
    for r in _RES["scorecard"]:
        if r["theory"] in ("pure_gr", "string_tree_eft", "asymptotic_safety", "cdt"):
            assert r["theory_ok"] is True
            assert r["data_ok"] is False
            assert "cosmic_birefringence_data" in r["data_excluded_by"]


def test_lqg_data_favored_theory_excluded():
    lqg = next(r for r in _RES["scorecard"] if r["theory"] == "lqg_induced")
    assert lqg["data_ok"] is True
    assert lqg["theory_ok"] is False


def test_no_named_framework_satisfies_both():
    named = [r for r in _RES["scorecard"] if r["theory"] != "engine_constructed"]
    assert all(not r["satisfies_both"] for r in named)


def test_constructed_satisfies_both():
    c = next(r for r in _RES["scorecard"] if r["theory"] == "engine_constructed")
    assert c["theory_ok"] is True
    assert c["data_ok"] is True
    assert c["satisfies_both"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "no named framework satisfies both" in f
    assert "constructed" in f
    assert "symmetry statement" in f
    sc = _RES["honest_scope"].lower()
    assert "dichotomy" in sc
    assert "3.6 sigma" in sc or "~3.6 sigma" in sc
    assert "toy basis" in sc
