"""Tests for the rigorous cross-sector tilted-Hankel bound (v2.294)."""

import math

from experiments.qnm_cross_sector_tilted_hankel import ABC, run, tilted_hankel_ok


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_tilted_hankel_predicate():
    # A t^2 + B t + C >= 0 for all t >= 0
    assert tilted_hankel_ok(1.0, 1.0, 1.0) is True       # B>=0
    assert tilted_hankel_ok(1.0, -1.0, 1.0) is True      # B<0 but B^2=1 <= 4AC=4
    assert tilted_hankel_ok(0.01, -1.0, 0.01) is False   # B^2=1 > 4AC=4e-4 -> dips negative


def test_cross_term_B_nonnegative_for_all_frameworks():
    res = run()
    for r in res["framework_cross_hankel"]:
        if r.get("has_both_sectors"):
            assert r["B_nonnegative"] is True
            assert r["tilted_hankel_ok"] is True


def test_am_gm_chain_holds():
    # g4 gR4 + gR2 g8 >= 2 sqrt(g4 g8 gR2 gR4) >= 2 g6 g3 whenever both towers hold -> B >= 0
    res = run()
    assert res["am_gm_chain_holds"] is True
    # explicit: a tower-saturated point has B >= 0
    A, B, C = ABC(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)   # both towers saturated
    assert A == 0 and C == 0 and B >= -1e-12


def test_v293_decoupled_passes_rigorous_bound():
    # the honest correction: v2.293's ratio-band rejected this point, but it passes the rigorous bound
    res = run()
    d = res["decoupled_v293"]
    assert d["passes_both_towers"] is True
    assert d["B"] > 0
    assert d["tilted_hankel_ok"] is True


def test_honest_scope_demotes_v293_band():
    res = run()
    sc = res["honest_scope"].lower()
    assert "demotes" in sc
    assert "over-stated" in sc or "over-strong" in res["finding"].lower()
    assert "g_10" in sc or "higher" in sc
