"""Tests for the cosmological-collider / primordial-closure cycle (v2.447)."""

from experiments.qnm_cosmological_collider import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_states_out_of_collider_window():
    lo, hi = _RES["collider_window_m_over_H"]
    assert _RES["tower_end_over_H"] > hi        # tower too heavy even at its lightest
    assert _RES["axion_over_H"] < lo            # axion too light


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "no cosmological-collider signal" in f
    assert "generic single-field starobinsky" in f
    assert "late-time" in f
    sc = _RES["honest_scope"].lower()
    assert "order-of-magnitude" in sc
    assert "negative" in sc
    assert "model-dependent" in sc  # axion mass caveat
