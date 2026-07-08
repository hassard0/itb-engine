"""Tests for the dark-energy-axion unification (v2.458)."""

from experiments.qnm_dark_energy_axion import run, beta_deg

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_o1_roll_gives_measured_beta():
    # measured 0.34 deg needs c_gamma*Delta_theta ~ O(1-10)
    assert 1.0 <= _RES["c_gamma_times_dtheta_for_measured"] <= 12.0
    assert abs(beta_deg(10, 1) - 0.333) < 0.01


def test_two_field_roles():
    lt = _RES["late_time_fields"]
    assert "inflation" in lt["scalaron_phi_R2"].lower() and "decays" in lt["scalaron_phi_R2"].lower()
    assert "dark energy" in lt["axion_theta"].lower() and "birefringence" in lt["axion_theta"].lower()


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "dark-energy field is the parity axion" in f
    assert "positively correlated" in f
    assert "same-field over-determination" in f
    assert "resolv" in f  # resolves v2.457
    sc = _RES["honest_scope"].lower()
    assert "not explained" in sc or "not solve" in sc  # DE magnitude / coincidence not solved
    assert "directional" in sc  # correlation directional not computed
    assert "revises v2.448" in sc
