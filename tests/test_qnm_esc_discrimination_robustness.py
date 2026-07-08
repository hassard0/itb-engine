"""Tests for the ESC-discrimination robustness self-correction (v2.475)."""

from experiments.qnm_esc_discrimination_robustness import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_separation_robust_but_preference_not():
    scan = _RES["p_scan"]
    # Regge > KK for every residue power-law
    assert all(row["regge"] > row["kk"] for row in scan)
    # preference flips across the family
    favs = {row["candidate_favors"] for row in scan}
    assert favs == {"Regge", "KK"}
    # flat/decreasing -> Regge, growing -> KK
    assert all(row["candidate_favors"] == "Regge" for row in scan if row["p"] <= 0.0)
    assert any(row["candidate_favors"] == "KK" for row in scan if row["p"] > 0.0)


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "tempers v2.474" in f
    assert "overstated" in f
    assert "residue-model-dependent" in f or "residue-dependent" in f
    sc = _RES["honest_scope"].lower()
    assert "self-correction" in sc
    assert "growing residues" in sc
