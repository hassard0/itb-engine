"""Tests for the SDC+tower light-couplings swing (v2.388)."""

import math

from experiments.qnm_sdc_tower_light_couplings import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_window_formula():
    # n_max = log(R_max)/log(1/r)
    expected = math.log(20.0) / math.log(1.0 / (0.09 / 0.193))
    assert abs(_RES["curvature_window_levels"] - expected) < 0.05


def test_curvature_window_about_four_and_smaller():
    assert 3.0 < _RES["curvature_window_levels"] < 5.0
    assert _RES["curvature_window_levels"] < _RES["matter_window_levels"]


def test_basis_fits_and_curvature_near_saturation():
    assert _RES["curvature_basis_used"] <= _RES["curvature_window_levels"] + 1e-9
    assert _RES["matter_basis_used"] <= _RES["matter_window_levels"]
    assert _RES["curvature_window_saturation"] > 0.7
    assert _RES["matter_window_saturation"] < 0.5


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "two faces of one physics" in f or "two faces" in f
    assert "heavier states" in f
    assert "saturat" in f
    sc = _RES["honest_scope"].lower()
    assert "heuristic" in sc
    assert "toy" in sc
    assert "ordering" in sc
