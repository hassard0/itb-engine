"""Tests for the strong-CP confrontation / axion-universality refinement (v2.468)."""

from experiments.qnm_strong_cp import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_qcd_axion_too_heavy():
    assert _RES["m_qcd_axion_eV"] > 1e6 * _RES["m_de_axion_eV"]
    assert _RES["orders_too_heavy_if_qcd_coupled"] > 10


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "photophilic alp" in f
    assert "does not solve strong-cp" in f
    assert "refines v2.435" in f
    assert "axiverse" in f
    sc = _RES["honest_scope"].lower()
    assert "physics-reasoning" in sc or "not an engine computation" in sc
    assert "consistency requirement" in sc          # photophilic ALP not guaranteed
    assert "survives" in sc and "alpha_em" in sc     # beta ~ alpha_EM survives
