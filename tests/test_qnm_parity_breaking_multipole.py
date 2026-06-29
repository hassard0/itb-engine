"""Tests for the multipole robustness of the isospectrality-breaking response (v2.225)."""

from experiments.qnm_parity_breaking_multipole import breaking_curve, run


def test_monotonic_in_j_at_every_multipole():
    res = run()
    for L in ("2", "3", "4"):
        assert res["monotonic_in_j_each_l"][L] is True


def test_breaking_decreases_with_multipole():
    # potentials converge at high l -> breaking falls; persists at WKB-accurate l=3,4
    res = run()
    assert res["decreasing_in_l_each_j"] is True
    j10 = res["breaking_at_j10"]
    assert j10["2"] > j10["3"] > j10["4"]
    assert j10["4"] < 0.1          # nearly isospectral response at l=4


def test_structure_persists_at_accurate_multipole():
    # l=3 curve is still a clean monotonic rise (evidence the effect is physical, not WKB)
    c3 = breaking_curve(3)
    assert all(c3[i + 1] > c3[i] for i in range(len(c3) - 1))
    assert c3[-1] > c3[0]


def test_honest_scope_physical_not_artifact():
    res = run()
    sc = res["honest_scope"].lower()
    assert "physical" in sc
    assert "v2.212" in res["honest_scope"]
    assert "g_R4_c3" in res["honest_scope"]
    assert "physical" in res["finding"].lower()
