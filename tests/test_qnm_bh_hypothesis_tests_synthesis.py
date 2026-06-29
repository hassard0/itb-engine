"""Tests for the 'is it a black hole?' test-suite synthesis (v2.250)."""

from experiments.qnm_bh_hypothesis_tests_synthesis import channel_map, cross_checks, run


def test_cross_test_consistency_holds():
    res = run()
    assert res["all_consistent"] is True
    for c in res["cross_test_consistency"]:
        assert c["ok"] is True


def test_shared_omega_h_checks_present():
    names = " ".join(c["check"] for c in cross_checks())
    assert "Omega_H" in names and "photon sphere" in names and "Love number" in names


def test_channel_map_two_probes():
    cmap = channel_map()
    probes = {g["probe"][:7] for g in cmap}
    assert any("HORIZON" in g["probe"] for g in cmap)
    assert any("SPIN" in g["probe"] for g in cmap)
    # the horizon is tested three distinct ways
    horizon = next(g for g in cmap if "HORIZON" in g["probe"])
    assert len(horizon["channels"]) == 3


def test_honest_scope_synthesis():
    res = run()
    sc = res["honest_scope"].lower()
    assert "synthesis" in sc and "not a new measurement" in sc
    assert "g_R4_c3" in res["honest_scope"]
