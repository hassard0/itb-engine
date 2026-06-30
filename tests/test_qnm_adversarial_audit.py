"""Tests for the adversarial self-audit of the parity headline (v2.329)."""

from experiments.qnm_adversarial_audit import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_dichotomy_requires_birefringence():
    # parity-even frameworks: excluded WITH birefringence, feasible WITHOUT it
    for r in _RES["with_vs_without_birefringence"]:
        assert r["feasible_with_birefringence"] is False
        assert r["feasible_without_birefringence"] is True


def test_consistency_only_parity_preference_is_mild():
    c = _RES["consistency_only"]
    assert abs(c["constructed_parity_geom_margin"] - c["parity_free_geom_margin"]) < 0.01


def test_robust_core_is_birefringence_independent():
    rc = _RES["robust_core"]
    assert "constructed_beats_community_prefactor_robust" in rc
    assert "lqg_is_the_boundary_prefactor_robust" in rc
    assert _RES["consistency_checks"]["robust_core_independent_of_birefringence"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "single point of failure" in f
    assert "cosmic birefringence" in f
    assert "structural" in f and "survives" in f
    sc = _RES["honest_scope"].lower()
    assert "dependency structure" in sc
    assert "toy basis" in sc
