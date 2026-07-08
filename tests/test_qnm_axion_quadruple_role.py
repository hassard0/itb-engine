"""Tests for the axion quadruple-role synthesis (v2.470)."""

from experiments.qnm_axion_quadruple_role import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_four_roles_one_field():
    roles = _RES["roles"]
    assert set(roles) == {"dark_energy", "cosmic_birefringence", "baryon_asymmetry", "chiral_primordial_GW"}
    # baryon asymmetry and chiral GW share the gravitational Chern-Simons coupling
    assert roles["baryon_asymmetry"]["coupling"] == roles["chiral_primordial_GW"]["coupling"] == "theta R^R-tilde"


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "quadruple" in f
    assert "one field" in f or "one parity axion" in f
    assert "v2.324" in f and "v2.458" in f
    sc = _RES["honest_scope"].lower()
    assert "structural" in sc
    assert "not computed" in sc          # eta_B not computed
    assert "not four solved" in sc or "not four solutions" in sc
