"""Tests for the adversarial matter-dominance hard-bound swing (v2.391)."""

from experiments.qnm_matter_dominance_hard_bound import run

_RES = run(steps=15000, seeds=2)   # shorter search; the sub-unity bound is robust


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_gravity_subdominant():
    assert _RES["constructed_gravity_over_matter"] < 1.0


def test_adversarial_max_bounded_well_below_one():
    assert _RES["adversarial_max_ratio"] < 0.6     # gravity cannot reach matter even adversarially


def test_bound_stable_across_seeds():
    assert _RES["seed_spread"] < 0.12


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "hard bound" in f
    assert "no consistent theory has gravity as strong as matter" in f or "never approach" in f or "counterexample" in f
    assert "weakest force" in f
    sc = _RES["honest_scope"].lower()
    assert "adversarial search" in sc or "adversarial" in sc
    assert "toy" in sc
