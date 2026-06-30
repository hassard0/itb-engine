"""Tests for the WGC / deep-consistency-trilogy result (v2.340)."""

from experiments.qnm_wgc_extremal_decay import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_wgc_family_satisfied_with_margin():
    for name, d in _RES["wgc_family_margins"].items():
        assert d["margin"] >= 0, name
    assert min(d["signed_distance"] for d in _RES["wgc_family_margins"].values()) > 0.05


def test_weak_gravity_and_repulsive_force_present():
    m = _RES["wgc_family_margins"]
    assert "weak_gravity_conjecture" in m
    assert "repulsive_force_conjecture" in m
    assert m["weak_gravity_conjecture"]["margin"] > 0
    assert m["repulsive_force_conjecture"]["margin"] > 0


def test_trilogy_has_three_pillars():
    t = _RES["deep_consistency_trilogy"]
    assert "unitarity_no_ghost_v2338" in t
    assert "causality_no_time_advance_v2339" in t
    assert "weak_gravity_extremal_decay_v2340" in t


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "weak gravity conjecture" in f
    assert "extremal black hole" in f and ("decay" in f or "shed" in f)
    assert "trilogy" in f or "three" in f
    sc = _RES["honest_scope"].lower()
    assert "convention-dependent" in sc
    assert "toy basis" in sc
