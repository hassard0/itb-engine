"""Tests for the parity one-channel closure (v2.456)."""

from experiments.qnm_parity_one_channel import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_exactly_one_observable_channel():
    assert _RES["observable_channels"] == ["isotropic_CMB_birefringence"]
    assert len(_RES["suppressed_channels"]) == 3


def test_gw_propagation_present_and_suppressed():
    assert "GW_propagation_birefringence" in _RES["channels"]
    assert _RES["channels"]["GW_propagation_birefringence"]["observable"] is False


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "one-channel object" in f
    assert "planck-suppressed" in f
    assert "v2.447" in f  # parity analog of the primordial closure
    sc = _RES["honest_scope"].lower()
    assert "order-of-magnitude" in sc
    assert "gw-propagation" in sc and "least certain" in sc
    assert "f_a ~ m_pl" in sc or "planckian" in sc
