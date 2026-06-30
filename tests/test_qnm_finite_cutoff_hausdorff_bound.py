"""Tests for the finite-cutoff Hausdorff moment bound (v2.306)."""

from experiments.qnm_finite_cutoff_hausdorff_bound import run, two_atom_measure


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_two_atom_measure_reproduces_moments():
    # string_tree_eft couplings
    m = two_atom_measure(0.5, 0.4, 0.4)
    assert m["moment_m1_err"] < 1e-12
    assert m["moment_m2_err"] < 1e-12
    assert m["weights_nonneg"] is True
    # S_min = g_8/g_6
    assert abs(m["S_min"] - 0.4 / 0.4) < 1e-12


def test_weight_positivity_equals_stieltjes():
    # weight at top atom = g_6^2/(g_4 g_8); w_zero >= 0 iff g_6^2 <= g_4 g_8
    # a Stieltjes-violating point must give a negative weight
    m_bad = two_atom_measure(1.0, 1.0, 0.5)  # g_6^2=1.0 > g_4 g_8=0.5
    assert m_bad["weights"][0] < 0.0          # w_zero negative -> no valid measure
    m_ok = two_atom_measure(1.0, 0.5, 1.0)    # g_6^2=0.25 <= 1.0
    assert m_ok["weights"][0] >= 0.0


def test_S_min_is_g8_over_g6_per_framework():
    res = run()
    for r in res["frameworks"]:
        assert abs(r["S_min_g8_over_g6"] - r["g_8"] / r["g_6"]) < 1e-12
        assert r["two_atom_valid"] is True


def test_hausdorff_strictly_stronger_than_stieltjes():
    res = run()
    d = res["hausdorff_demo"]
    assert d["satisfies_stieltjes"] is True
    assert d["excluded_by_finite_cutoff"] is True
    assert d["S_min"] > d["cutoff_S"]


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "hausdorff" in f and "stieltjes" in f
    assert "ceiling" in f
    sc = res["honest_scope"].lower()
    assert "exact mathematics" in sc
    assert "schematic" in sc
    assert "toy basis" in sc
