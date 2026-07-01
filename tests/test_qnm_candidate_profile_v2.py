"""Tests for the refreshed candidate-profile capstone (v2.402)."""

from experiments.qnm_candidate_profile_v2 import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_live_core():
    lc = _RES["live_checks"]
    assert lc["constructed_feasible"] is True
    assert lc["no_framework"] is True
    assert lc["matter_forces_gravity"] is True
    assert 0.5 < lc["cutoff_over_Mpl"] < 1.0
    assert lc["cmb_s4_tension_sigma"] > 10.0


def test_four_tiers_including_assumptions():
    tiers = _RES["robustness_tiers"]
    assert len(tiers) == 4
    # the new-since-v2.382 ASSUMPTIONS tier must be present and list a=c and g_6=g_8
    assum = [t for t in tiers if "ASSUMPTION" in t][0]
    joined = " ".join(tiers[assum]).lower()
    assert "a = c" in joined
    assert "g_6 = g_8" in joined


def test_profile_has_spine_and_moduli():
    pr = _RES["profile"]
    assert "two keystones" in pr["spine"]
    assert "g_8" in pr["free_moduli"] and "g_C" in pr["free_moduli"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "matter-dominant" in f
    assert "make-or-break" in f
    assert "assumptions" in f or "not predictions" in f
    sc = _RES["honest_scope"].lower()
    assert "consolidation" in sc
    assert "two explicit assumptions" in sc or "assumptions not predictions" in sc or "a=c" in sc
