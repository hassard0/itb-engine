"""Tests for the toy-dependence mapping cycle (v2.413)."""

from experiments.qnm_toy_dependence_map import run
from experiments.stack import HARMLESS_SPECULATIVE, LOAD_BEARING_TOY

_RES = run(n_pts=4000)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_speculative_toys_are_harmless():
    lev = _RES["leverage"]
    assert lev["complexity_cutoff"]["opens_x"] < 1.3
    assert lev["swampland_distance_conjecture"]["opens_x"] < 1.3
    assert HARMLESS_SPECULATIVE == {"complexity_cutoff", "swampland_distance_conjecture"}


def test_anomaly_sector_is_load_bearing():
    lev = _RES["leverage"]
    assert lev["anomaly_cancellation"]["opens_x"] > 1.3
    assert lev["generalized_anomaly_inflow"]["opens_x"] > 1.3
    assert LOAD_BEARING_TOY == {"anomaly_cancellation", "generalized_anomaly_inflow"}


def test_scale_window_robust_to_harmless():
    assert _RES["scale_window_without_harmless"] == _RES["scale_window_full"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "anomaly sector alone" in f
    assert "harmless" in f
    assert "retires two speculative worries" in f or "retires two" in f
    sc = _RES["honest_scope"].lower()
    assert "local" in sc
    assert "real data" in sc
    assert "does not de-toy the anomaly" in sc
