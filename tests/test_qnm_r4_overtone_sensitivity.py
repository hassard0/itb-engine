"""Tests for the R4 overtone-sensitivity hierarchy (v2.217)."""

from experiments.qnm_r4_overtone_sensitivity import qeft_shift_per_gamma, run


def test_overtone_far_more_sensitive():
    res = run()
    e = res["overtone_enhancement"]
    # the n=1 first overtone is ~490x more sensitive (complex-shift magnitude) than n=0
    assert e["complex_shift_magnitude_ratio_n1_over_n0"] > 100
    assert e["damping_shift_ratio_n1_over_n0"] > 200


def test_damping_response_signs_opposite():
    # fundamental decays faster (Im < 0); first overtone decays slower (Im > 0)
    s0 = qeft_shift_per_gamma(0)
    s1 = qeft_shift_per_gamma(1)
    assert s0.imag < 0
    assert s1.imag > 0
    res = run()
    assert res["overtone_enhancement"]["damping_signs_opposite"] is True


def test_parspec_reconstruction_convention():
    # d(omega_R)/d(gamma) = omega_R^0 * dwq ; d(omega_I)/d(gamma) = -omega_I^0 * dtq
    s0 = qeft_shift_per_gamma(0)
    assert abs(s0.real - (0.373672 * -0.2114)) < 1e-9
    assert abs(s0.imag - (-(-0.088962) * -0.6070)) < 1e-9
    s1 = qeft_shift_per_gamma(1)
    assert abs(s1.real - (0.346711 * -1.5263)) < 1e-9
    assert abs(s1.imag - (-(-0.273915) * 171.35)) < 1e-9


def test_full_delta_v_negative_preserved():
    res = run()
    assert res["claim_gate"].startswith("closed")
    assert "not sourceable" in res["claim_gate"].lower()
    assert "delicate" in res["perturbative_caveat"].lower()
