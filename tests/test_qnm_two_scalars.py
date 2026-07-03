"""Tests for the two-scalar cosmological field-content clarification (v2.448)."""

from experiments.qnm_two_scalars import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_two_fields_opposite_parity():
    f = _RES["fields"]
    assert f["scalaron_phi"]["parity"] == "even"
    assert f["axion_theta"]["parity"] == "odd"


def test_roles_assigned():
    f = _RES["fields"]
    assert any("dark energy" in r for r in f["scalaron_phi"]["roles"])
    assert any("inflation" in r for r in f["scalaron_phi"]["roles"])
    assert any("birefringence" in r for r in f["axion_theta"]["roles"])


def test_finding_and_scope_flags():
    fnd = _RES["finding"].lower()
    assert "two distinct scalars" in fnd
    assert "opposite parity" in fnd
    assert "cannot be the same field" in fnd
    sc = _RES["honest_scope"].lower()
    assert "standard" in sc
    assert "order-of-magnitude" in sc
    assert "not computed" in sc  # axion potential not computed
