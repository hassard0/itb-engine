"""Tests for the scale-clean UV-embedding fingerprint (v2.465)."""

from experiments.qnm_scale_clean_fingerprint import run, double_ratio

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_family_all_geq_1():
    fp = _RES["candidate_fingerprint"]
    assert len(fp) >= 3
    for name, f in fp.items():
        assert f["value"] >= 1.0 - 1e-9, name


def test_matter_and_curvature_covered():
    fp = _RES["candidate_fingerprint"]
    assert any("matter" in k for k in fp) and any("curvature" in k for k in fp)


def test_double_ratio_math():
    # (0.529*0.4)/0.4^2 = 1.322
    assert abs(double_ratio(0.529, 0.4, 0.4) - 1.322) < 0.005


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "every moment-tower" in f and "scale-independent" in f
    assert "fingerprint" in f
    sc = _RES["honest_scope"].lower()
    assert "does not compute" in sc or "not execute" in sc or "opened" in sc
    assert "chebyshev" in sc  # constructed-point caveat
    assert "geq 1" in sc or ">= 1" in sc
