"""Tests for the effective-dimension PCA result (v2.333)."""

from experiments.qnm_effective_dimension import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_effective_dimension_about_three():
    pr = _RES["participation_ratio_effective_dim"]
    assert 2.0 < pr < 4.0
    assert pr < 5.0   # below the ambient 6


def test_top_soft_direction_is_matter():
    pc1 = _RES["top_soft_direction_PC1"]
    dom = max(pc1, key=lambda k: abs(pc1[k]))
    assert dom in ("g_4", "g_6", "g_8")


def test_stiffest_direction_is_parity():
    stiff = _RES["stiffest_direction"]
    dom = max(stiff, key=lambda k: abs(stiff[k]))
    assert dom == "g_R2_parity"
    # parity has the smallest per-coupling spread
    stds = _RES["per_coupling_std"]
    assert stds["g_R2_parity"] == min(stds.values())


def test_top3_capture_majority():
    assert sum(_RES["explained_variance_ratios"][:3]) > 0.8


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "effectively" in f and "3" in f
    assert "matter sector" in f
    assert "parity" in f and ("pinned" in f or "fixed" in f)
    sc = _RES["honest_scope"].lower()
    assert "convention-dependent" in sc
    assert "toy basis" in sc
