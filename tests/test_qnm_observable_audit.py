"""Tests for the observable-consistency audit (v2.463)."""

from experiments.qnm_observable_audit import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_etas_fixed_and_core_ok():
    assert _RES["fixed"] == ["holographic_eta_over_s"]
    assert {"gravitational_birefringence", "bh_entropy_shift", "starobinsky_inflation"} <= set(_RES["ok"])


def test_submm_stale_but_inert():
    assert _RES["stale_inert"] == ["yukawa_force_deviation_submm"]
    assert "non-binding" in _RES["audit"]["yukawa_force_deviation_submm"]["note"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "internally consistent" in f
    assert "topological in 4d" in f          # BH entropy g_R2 drop
    assert "non-binding" in f and "margin = 1.0" in f
    sc = _RES["honest_scope"].lower()
    assert "audit, not a new physics result" in sc or "audit, not a new" in sc
    assert "not exhaustive" in sc
    assert "candidate-specific" in sc or "candidate + stack" in sc
