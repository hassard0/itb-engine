"""Tests for the engine-preferred-framework metric-robustness check (v2.313)."""

from experiments.qnm_preferred_framework_robustness import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_three_objectives_present_and_feasible():
    res = run()
    assert set(res["optima"]) == {"raw", "geom", "analytic"}
    for k in res["optima"]:
        assert res["optima"][k]["strictly_feasible"] is True


def test_all_optima_parity_free():
    res = run()
    for k in res["optima"]:
        c = res["optima"][k]["couplings"]
        assert abs(c["g_R2_parity"]) < 1e-6
        assert abs(c["g_R3_parity"]) < 1e-6


def test_all_optima_string_like_matter_trimmed_curvature():
    res = run()
    for k in res["optima"]:
        c = res["optima"][k]["couplings"]
        assert 0.40 <= c["g_4"] <= 0.75
        assert 0.30 <= c["g_6"] <= 0.50
        assert 0.30 <= c["g_8"] <= 0.50
        # curvature trimmed below the string values (0.2 / 0.15)
        assert c["g_R2"] <= 0.25
        assert c["g_R3"] <= 0.18


def test_optima_converge():
    res = run()
    assert res["max_coordinate_spread_across_objectives"] < 0.25


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "metric-robust" in f
    assert "chebyshev" in f
    sc = res["honest_scope"].lower()
    assert "scale-free" in sc
    assert "not a proven global optimum" in sc or "not a theorem" in sc
    assert "toy basis" in sc
