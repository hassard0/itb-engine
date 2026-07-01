"""Tests for the attack on the tower-unification conjecture (v2.368)."""

from experiments.qnm_tower_unification_attack import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_toy_tower_reproduces_matter_ratio():
    assert abs(_RES["r_matter_at_s0"] - 0.756) < 0.01


def test_strong_form_fragile():
    # the sharp g_R4 drifts with the form factor -> the exact-value claim fails
    assert _RES["consistency_checks"]["sharp_g_R4_value_is_fragile_to_form_factor"] is True
    assert _RES["band_spread_fraction"] > 0.03


def test_weak_form_robust():
    # across the plausible band, curvature stays multi-state and g_R4 stays above the floor
    for row in _RES["form_factor_scan"]:
        if -1.0 <= row["s"] <= 1.0:
            assert row["curvature_multistate"] is True
            assert row["above_floor"] is True
    lo, hi = _RES["g_R4_band"]
    assert lo > _RES["floor"]           # strictly above the moment floor
    assert hi < 0.339                    # well below the causality cap (v2.351)


def test_finding_reports_partial_failure():
    f = _RES["finding"].lower()
    assert "partially breaks" in f or "partial" in f.replace("partially", "partial")
    assert "strong form" in f and "weak form" in f
    assert "refuted" in f or "downgraded" in f
    sc = _RES["honest_scope"].lower()
    assert "toy" in sc
    assert "conjecture" in sc
