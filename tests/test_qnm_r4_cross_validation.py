"""Tests for the R4 odd-parity cross-validation (v2.216)."""

from experiments.qnm_r4_cross_validation import (
    mcmanus_shift_per_eta2,
    qeft_shift_per_gamma,
    run,
)


def test_both_routes_agree_on_signs():
    # qualitative validation: R4 lowers omega_R and increases damping (both Delta < 0)
    mc = mcmanus_shift_per_eta2()
    qe = qeft_shift_per_gamma()
    assert mc.real < 0 and mc.imag < 0
    assert qe.real < 0 and qe.imag < 0
    res = run()
    assert res["signs_agree"] is True


def test_convention_independent_ratio_disagrees():
    # the damping/frequency ratio (Im/Re) is convention-independent and does NOT match
    res = run()
    c = res["convention_independent_comparison"]
    assert abs(c["damping_over_frequency_ratio_mcmanus"] - 1.77) < 0.05
    assert abs(c["damping_over_frequency_ratio_qeft"] - 0.68) < 0.05
    assert c["ratio_relative_difference"] > 0.5      # ~159% mismatch
    assert res["directions_agree_5pct"] is False


def test_claim_gate_closed_negative_preserved():
    res = run()
    assert res["claim_gate"].startswith("closed")
    assert "INCOMPLETE" in res["diagnosis"] or "incomplete" in res["diagnosis"].lower()


def test_qeft_reconstruction_uses_parspec_convention():
    # d(omega_R)/d(gamma) = omega_R^0 * dwq ; d(omega_I)/d(gamma) = -omega_I^0 * dtq
    qe = qeft_shift_per_gamma()
    assert abs(qe.real - (0.373672 * -0.2114)) < 1e-9
    assert abs(qe.imag - (-(-0.088962) * -0.6070)) < 1e-9
