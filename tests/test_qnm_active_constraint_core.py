"""Tests for the active-constraint-core audit (v2.325)."""

from experiments.qnm_active_constraint_core import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_active_core_smaller_than_full_stack():
    assert _RES["n_active"] < _RES["n_constraints"]
    assert _RES["n_always_slack"] == _RES["n_constraints"] - _RES["n_active"]


def test_distance_conjecture_top_binder():
    assert _RES["top_binding"][0]["constraint"] == "swampland_distance_conjecture"


def test_dominant_core_is_small():
    assert len(_RES["dominant_core"]) <= _RES["n_constraints"] // 3
    assert "cosmic_birefringence_data" in _RES["dominant_core"]


def test_scalar_positivities_always_slack():
    for g in ("g4", "g6", "g8"):
        assert f"scalar_positivity_{g}" in _RES["always_slack_constraints"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "active" in f and "core" in f
    assert "forbidden zone" in f          # the v2.318 cross-connection
    sc = _RES["honest_scope"].lower()
    assert "relative to the sample" in sc
    assert "not 'non-redundant in general'" in sc or "not 'non-redundant" in sc
    assert "toy basis" in sc
