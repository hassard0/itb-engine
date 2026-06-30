"""Tests for the string-like-in-two-senses synthesis (v2.342)."""

from experiments.qnm_string_like_two_senses import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_matter_closest_to_string():
    assert _RES["closest_framework"] == "string_tree_eft"
    assert _RES["distance_to_string"] < 0.05


def test_string_clearly_closest():
    ranked = list(_RES["matter_sector_distances"].items())
    # string first, and clearly closer than the runner-up
    assert ranked[0][0] == "string_tree_eft"
    assert ranked[1][1] > 1.5 * ranked[0][1]


def test_pure_gr_is_farthest():
    dists = _RES["matter_sector_distances"]
    assert max(dists, key=dists.get) == "pure_gr"


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "two independent senses" in f
    assert "parity-deformed" in f and "curvature-trimmed" in f
    sc = _RES["honest_scope"].lower()
    assert "toy string_tree_eft encoding" in sc or "engine's string framework" in sc
    assert "not 'matches real string theory" in sc or "not match" in sc or "not 'matches real" in sc
    assert "toy basis" in sc
