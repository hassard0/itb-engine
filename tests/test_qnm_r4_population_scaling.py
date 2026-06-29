"""Tests for the R4 population scaling of ringdown bounds (v2.223)."""

from experiments.qnm_r4_population_scaling import (
    inverse_variance_combination,
    n_events_to_improve,
    run,
    snr_event_equivalence,
)


def test_population_scaling_is_weak():
    # ell ~ N^{-1/12}: halving the bound needs 2^12 = 4096 events
    assert abs(n_events_to_improve(2.0) - 4096) < 1e-6
    assert abs(n_events_to_improve(10.0) - 1e12) < 1.0


def test_snr_is_quadratically_stronger_than_count():
    # one event k-times louder is worth k^2 events (independent of p)
    assert abs(snr_event_equivalence(2.0) - 4.0) < 1e-9
    assert abs(snr_event_equivalence(10.0) - 100.0) < 1e-9


def test_two_event_combination_barely_tightens():
    L = inverse_variance_combination([51.7, 54.8])
    # combining two comparable events improves the bound only a few percent
    assert 49.0 < L < 51.7
    assert (1.0 - L / 51.7) < 0.06


def test_published_combined_comparison_honest():
    res = run()
    c = res["two_event_combination_check"]
    # naive inverse-variance lands a few percent tighter than the published combined bound
    assert c["published_combined_km"] == 51.3
    assert c["iv_vs_published_relative_diff"] < 0.05
    assert c["inverse_variance_estimate_km"] < c["published_combined_km"]


def test_claim_gate_scaling_law_vs_number():
    res = run()
    cg = res["claim_gate"].lower()
    assert "scaling law" in cg and "claim-grade" in cg
    assert "approximation" in cg or "approximation" in cg
    assert "g_R4_c3" in res["claim_gate"]
