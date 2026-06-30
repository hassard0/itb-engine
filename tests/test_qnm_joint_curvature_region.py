"""Tests for the joint carved curvature region (v2.309)."""

import numpy as np

from experiments.qnm_joint_curvature_region import run, feasible_mask, engine_margins


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_joint_region_nonempty_and_bounded():
    res = run()
    bb = res["joint_region_bbox"]
    assert bb is not None
    # bounded within the EFT box, and a strict sliver (not the whole box)
    for pair in bb.values():
        assert all(abs(v) <= 2.0 + 1e-9 for v in pair)
    assert 0.0 < res["joint_region_feasible_fraction_of_box"] < 0.5


def test_moment_tower_excludes_gR4_zero():
    # a point with a nonzero cubic but g_R4 = 0 violates the moment tower -> outside
    assert not bool(feasible_mask(0.5, np.array([0.2]), np.array([0.15]), np.array([0.0]))[0])
    # lifting g_R4 to the floor g_R3^2/g_R2 brings it in
    floor = 0.15 ** 2 / 0.2
    assert bool(feasible_mask(0.5, np.array([0.2]), np.array([0.15]), np.array([floor + 1e-9]))[0])


def test_every_framework_enters_at_moment_floor():
    res = run()
    for r in res["frameworks"]:
        assert r["feasible_with_gR4_zero"] is False        # outside with default g_R4=0
        assert r["feasible_at_gR4_floor"] is True           # inside at the moment floor
        assert abs(r["gR4_moment_floor"] - r["g_R3"] ** 2 / r["g_R2"]) < 1e-12


def test_vectorized_region_matches_engine_classes():
    # at each framework's floor point, the engine constraint classes all agree (margins >= 0)
    res = run()
    for r in res["frameworks"]:
        m = engine_margins(r["g_4"], r["g_R2"], r["g_R3"], r["gR4_moment_floor"] + 1e-9)
        assert all(v >= -1e-9 for v in m.values())
        assert r["engine_classes_all_satisfied_at_floor"] is True


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "joint" in f and "ladder" in f
    assert "moment-tower floor" in f or "moment tower floor" in f
    sc = res["honest_scope"].lower()
    assert "synthesis-as-computation" in sc
    assert "cross-checked against the engine" in sc
    assert "toy basis" in sc
