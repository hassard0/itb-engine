"""Tests for the birefringence-anisotropy f_a discriminator (v2.455)."""

from experiments.qnm_birefringence_anisotropy import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_anisotropy_negligible():
    assert _RES["anisotropic_over_isotropic"] < 1e-4
    assert _RES["delta_beta_deg"] < _RES["current_aniso_bound_deg"] / 100


def test_observable_needs_subplanckian_fa():
    assert _RES["f_a_for_observable_anisotropy_over_Mpl"] < 1e-3


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "isotropic" in f
    assert "discriminator" in f and "f_a" in f
    assert "sub-planckian" in f
    sc = _RES["honest_scope"].lower()
    assert "order-of-magnitude" in sc
    assert "compactification-dependent" in sc
    assert "discriminator" in sc
