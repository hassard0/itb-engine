"""Tests for the v2.341-vs-v2.361 margin-robustness audit (v2.362)."""

from experiments.qnm_trilogy_margin_robustness import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_groups_comparably_scaled():
    # the group margins span at most a factor of tens -- nothing like gw_speed's 5e-16 outlier
    assert _RES["margin_max_min_ratio"] < 50.0
    assert _RES["all_group_margin_min"] > 1e-3


def test_v2341_ordering_holds():
    w = _RES["worst_margins"]
    assert w["causality"] > w["wgc"] > w["unitarity"]


def test_ordering_robust_to_rescaling():
    # would take >1.5x rescaling to flip the loosest-vs-tightest -- above O(1) prefactor noise
    assert _RES["causality_to_unitarity_ratio"] > 1.5


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "survives" in f
    assert "v2.361" in f and "v2.341" in f
    assert "artifact" in f
    sc = _RES["honest_scope"].lower()
    assert "constructed point" in sc
    assert "toy basis" in sc
