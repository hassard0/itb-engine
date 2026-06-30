"""Tests for the cross-sector weight-structure characterization (v2.295)."""

import numpy as np

from experiments.qnm_cross_sector_weight_structure import hankel, is_psd, moments, run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_tilted_hankel_decomposes_to_sum_of_psd():
    # H(t) = H_matter + t H_curv is PSD for all t>=0 whenever both are PSD (sum of PSD matrices)
    p, x, w = [0.4, 0.3, 0.2, 0.1], [0.2, 0.5, 0.9, 1.4], [0.3, 0.95, 0.9, 0.32]
    m, c = moments(p, x, w, 4)
    for n in (1, 2):
        Hm, Hc = hankel(m, n), hankel(c, n)
        assert is_psd(Hm) and is_psd(Hc)
        for t in (0.0, 0.5, 1.0, 5.0, 20.0):
            assert is_psd(Hm + t * Hc)


def test_w_ge_0_adds_nothing():
    # the peaked weight passes both towers AND the tilted-Hankel, yet is a non-monotone weight
    res = res = run()
    peaked = res["weight_cases"]["peaked"]
    assert peaked["matter_tower_ok"] and peaked["curv_tower_ok"]
    assert peaked["tilted_hankel_decomposes"] is True


def test_monotone_w_gives_monotone_ratios_peaked_breaks_it():
    res = run()
    assert res["weight_cases"]["monotone"]["ratios_monotone"] is True
    assert res["weight_cases"]["peaked"]["ratios_monotone"] is False   # the genuine new constraint bites


def test_frameworks_behave_as_monotone_weight():
    res = run()
    for r in res["framework_ratios"]:
        assert r["ratios_monotone"] is True


def test_constraint_map_by_assumption():
    res = run()
    m = res["constraint_by_assumption_on_w"]
    assert "no new" in m["w_ge_0"].lower()
    assert "monoton" in m["w_monotone"].lower()
    assert "cutoff" in m["w_le_W_cutoff"].lower()


def test_honest_scope_flags_assumption_not_theorem():
    res = run()
    sc = res["honest_scope"].lower()
    assert "not a theorem" in sc
    assert "physical refinement" in sc
    assert "conditional" in sc
