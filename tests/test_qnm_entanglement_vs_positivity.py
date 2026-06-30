"""Tests for entanglement-vs-positivity curvature bounds (v2.300)."""

import math

from experiments.qnm_entanglement_vs_positivity import (
    crossover_ratio,
    monogamy_bound,
    positivity_bound,
    run,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_monogamy_harmonic_positivity_geometric():
    # at g4=g6=g: monogamy = (3/2) g (harmonic-mean*3/2), positivity = g (geometric mean)
    assert abs(monogamy_bound(0.4, 0.4) - 1.5 * 0.4) < 1e-9
    assert abs(positivity_bound(0.4, 0.4) - 0.4) < 1e-9
    # harmonic <= geometric always -> at equality only when g4=g6
    for g4, g6 in [(0.5, 0.4), (1.0, 0.2), (0.3, 0.3)]:
        hm = 2 * g4 * g6 / (g4 + g6)
        gm = math.sqrt(g4 * g6)
        assert hm <= gm + 1e-12


def test_crossover_ratio():
    r = crossover_ratio()
    assert abs(r - 6.854) < 0.05
    # at the crossover the two bounds coincide
    assert abs(monogamy_bound(r, 1.0) - positivity_bound(r, 1.0)) < 1e-6


def test_frameworks_positivity_bound():
    res = run()
    for r in res["framework_bounds"]:
        if r.get("has_matter"):
            assert r["binding"] == "positivity"
            assert r["asymmetry_g4_over_g6"] < res["crossover_g4_over_g6"]
            assert r["positivity_bound"] < r["monogamy_bound"]   # positivity tighter


def test_entanglement_bites_for_asymmetric_matter():
    res = run()
    a = res["asymmetric_test_point"]
    assert a["asymmetry"] > res["crossover_g4_over_g6"]
    assert a["entanglement_tighter"] is True
    assert a["monogamy_bound"] < a["positivity_bound"]
    assert a["gap"] > 0


def test_honest_scope_flags_qualitative_robust_quantitative_prefactor():
    res = run()
    sc = res["honest_scope"].lower()
    assert "prefactor-robust" in sc
    assert "harmonic" in sc and "geometric" in sc
    assert "it from qubit" in sc
