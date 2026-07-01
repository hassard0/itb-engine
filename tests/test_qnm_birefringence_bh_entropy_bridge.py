"""Tests for the birefringence -> BH-entropy cross-sector bridge (v2.379)."""

import math

from experiments.qnm_birefringence_bh_entropy_bridge import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_bound_from_amgm_and_birefringence_floor():
    floor = _RES["g4_gR2_floor_v2350"]
    # Delta S_ext >= 2 sqrt(0.5 * floor)
    assert abs(_RES["bh_entropy_lower_bound"] - 2.0 * math.sqrt(0.5 * floor)) < 1e-3
    assert _RES["bh_entropy_lower_bound"] > 0


def test_constructed_respects_bound():
    assert _RES["constructed_delta_S_ext"] >= _RES["bh_entropy_lower_bound"]


def test_bound_is_data_sourced():
    assert _RES["bound_without_birefringence"] < 1e-4


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "bridge" in f
    assert "channel 1" in f and "channel 4" in f
    assert "black-hole" in f and "birefringence" in f
    sc = _RES["honest_scope"].lower()
    assert "am-gm step is exact" in sc or "exact algebra" in sc
    assert "toy" in sc
    assert "v2.329" in sc
