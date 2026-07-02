"""Tests for the chiral-GW amplitude computation / honest negative (v2.444)."""

from experiments.qnm_chiral_gw_amplitude import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_chirality_suppressed_below_threshold():
    assert _RES["chirality_Pi_estimate"] < 1e-3
    assert _RES["chirality_Pi_estimate"] < _RES["cmb_threshold"]
    assert _RES["orders_below_threshold"] > 3


def test_cs_scale_planckian():
    assert _RES["M_CS_over_Mpl"] > 1.0


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "honest negative" in f
    assert "unobservable" in f
    assert "birefringence" in f  # parity observable via late-time front instead
    sc = _RES["honest_scope"].lower()
    assert "order-of-magnitude" in sc or "parametric" in sc
    assert "normalization" in sc
    assert "f_a" in sc  # the sub-Planckian escape hatch flagged
