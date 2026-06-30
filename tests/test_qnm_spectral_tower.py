"""Tests for the spectral-tower (multi-state UV) result (v2.343)."""

from experiments.qnm_spectral_tower import run, disp_ratio


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_constructed_ratio_below_one():
    res = run()
    assert res["constructed_ratio"] < 1.0
    # exact arithmetic
    assert abs(disp_ratio({"g_4": 0.529, "g_6": 0.4, "g_8": 0.4}) - 0.4 ** 2 / (0.529 * 0.4)) < 1e-9


def test_all_candidates_multistate():
    res = run()
    for r in res["dispersion_ratios"]:
        assert r["dispersion_ratio"] < 1.0


def test_constructed_among_most_spread():
    res = run()
    rows = res["dispersion_ratios"]
    # constructed is at or near the lowest (most spread) ratio
    con = next(r for r in rows if r["theory"] == "engine_constructed")
    assert con["dispersion_ratio"] <= sorted(r["dispersion_ratio"] for r in rows)[1] + 1e-9


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "multi-state" in f and "tower" in f
    assert "single resonance" in f
    assert "three" in f and "independent" in f
    sc = res["honest_scope"].lower()
    assert "cauchy-schwarz" in sc
    assert "theorem, not a heuristic" in sc
    assert "toy basis" in sc
