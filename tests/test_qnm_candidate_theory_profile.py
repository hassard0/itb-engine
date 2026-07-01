"""Tests for the candidate-theory-profile capstone (v2.382)."""

from experiments.qnm_candidate_theory_profile import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_unique():
    assert _RES["constructed_feasible"] is True
    assert _RES["no_named_framework_feasible"] is True


def test_four_channels_present():
    assert set(_RES["channels"]) == {"parity", "ringdown", "screening", "bh_extremality"}


def test_both_sectors_string_like_and_bh_decays():
    assert _RES["r_matter"] < 1.0 and _RES["r_curv"] < 1.0     # both multi-state towers
    assert _RES["delta_S_ext"] > 0                              # extremal BHs decay


def test_four_tiers_present():
    tiers = _RES["robustness_tiers"]
    assert len(tiers) == 4
    for name, items in tiers.items():
        assert len(items) >= 1, name


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "candidate for quantum gravity" in f or "candidate" in f
    assert "five-parameter" in f or "5-parameter" in f
    assert "string-like" in f and "wgc" in f
    assert "observationally dark" in f
    sc = _RES["honest_scope"].lower()
    assert "consolidation" in sc
    assert "toy basis" in sc
