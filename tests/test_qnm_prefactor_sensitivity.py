"""Tests for the prefactor-sensitivity swing (v2.405)."""

from experiments.qnm_prefactor_sensitivity import run

_RES = run(n_region=1200)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_no_framework_survives_all():
    assert _RES["no_framework_survives_all"] is True


def test_region_never_collapses():
    assert _RES["region_always_nonempty"] is True
    for f in _RES["failures"]:
        assert f["region_nonempty"] is True     # every failure is a point shift


def test_unique_feasibility_mostly_robust():
    assert _RES["unique_feasibility_survival_fraction"] > 0.8


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "empirically robust" in f
    assert "point shifts" in f
    assert "four independent robustness axes" in f or "4th robustness axis" in f or "prefactor variation" in f
    sc = _RES["honest_scope"].lower()
    assert "one-at-a-time" in sc or "single-prefactor" in sc
    assert "hardcode" in sc or "hardcoded prefactors excluded" in sc
