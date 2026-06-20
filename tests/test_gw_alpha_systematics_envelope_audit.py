"""Tests for the v2.119 alpha systematics envelope audit."""

from experiments.gw_alpha_systematics_envelope_audit import (
    DEFAULT_GR_REFERENCE_PATH,
    DEFAULT_IMR_REFERENCE_PATH,
    DEFAULT_MARGINAL_RESULT_PATH,
    DEFAULT_PARTIAL_SYSTEMATICS_PATH,
    detector_calibration_proxy,
    diagnose_gw_alpha_systematics_envelope_audit,
    eft_truncation_proxy,
    evaluate_alpha_systematics_envelopes,
    load_json,
    packet_with_quantitative_systematics_envelopes,
    prior_sensitivity_proxy,
    quantitative_open_systematics_evidence,
    waveform_systematics_proxy,
)


def _inputs():
    return (
        load_json(DEFAULT_GR_REFERENCE_PATH),
        load_json(DEFAULT_IMR_REFERENCE_PATH),
        load_json(DEFAULT_MARGINAL_RESULT_PATH),
        load_json(DEFAULT_PARTIAL_SYSTEMATICS_PATH),
    )


def test_waveform_proxy_quantifies_gr_to_imr_projection_shift():
    gr_reference, imr_reference, *_ = _inputs()
    proxy = waveform_systematics_proxy(gr_reference, imr_reference)

    assert proxy["status"] == "open"
    assert proxy["proxy_kind"] == (
        "leading_order_gr_vs_lalsuite_imrphenomd_projection_delta"
    )
    assert proxy["max_network_projection_component_delta"] > 0.0
    assert set(proxy["parameters"]) == {"alpha_bar_1", "alpha_bar_2"}


def test_detector_calibration_proxy_records_h1_l1_spread():
    _gr_reference, imr_reference, *_ = _inputs()
    proxy = detector_calibration_proxy(imr_reference)

    assert proxy["status"] == "open"
    assert proxy["max_abs_detector_spread"] > 0.0
    assert "alpha_bar_1_abs_detector_spread" in proxy["detector_spreads"]


def test_prior_proxy_captures_marginal_profile_disagreement():
    *_references, marginal_result, _partial = _inputs()
    proxy = prior_sensitivity_proxy(marginal_result)

    assert proxy["status"] == "open"
    assert proxy["alpha_best_point_euclidean_shift"] > 0.0
    assert proxy["best_marginal_grid_point"]["alpha_bar_1"] == 0.0
    assert proxy["best_profile_grid_point"]["alpha_bar_1"] == 0.6000000000000001


def test_eft_proxy_uses_source_frequency_window():
    _gr_reference, imr_reference, *_ = _inputs()
    proxy = eft_truncation_proxy(imr_reference)

    assert proxy["status"] == "open"
    assert proxy["v_f_max"] > 0.0
    assert proxy["next_order_power_suppression_proxy"] == proxy["v_f_max"] ** 2


def test_quantitative_evidence_covers_all_open_components():
    gr_reference, imr_reference, marginal_result, _partial = _inputs()
    evidence = quantitative_open_systematics_evidence(
        gr_reference,
        imr_reference,
        marginal_result,
    )

    assert sorted(evidence) == [
        "detector_calibration",
        "eft_truncation",
        "prior_sensitivity",
        "waveform_systematics",
    ]
    assert all(row["status"] == "open" for row in evidence.values())
    assert all("proxy_kind" in row for row in evidence.values())


def test_packet_with_envelopes_keeps_adapter_nonclaiming():
    gr_reference, imr_reference, marginal_result, partial = _inputs()
    packet = packet_with_quantitative_systematics_envelopes(
        partial["packet"],
        gr_reference,
        imr_reference,
        marginal_result,
    )
    result = evaluate_alpha_systematics_envelopes(packet)

    assert result["quantitative_envelopes_ready"] is True
    assert result["claim_ready"] is False
    assert result["bounded_components"] == [
        "sampler_convergence",
        "public_data_reproducibility",
    ]
    assert "systematics_not_closed" in result["remaining_nonclaiming_reasons"]


def test_diagnosis_selects_calibrated_bounds_next():
    result = diagnose_gw_alpha_systematics_envelope_audit()

    assert result["version"] == "v2.119"
    assert result["route_status"] == "alpha_systematics_proxies_quantified_nonclaiming"
    assert result["claimable_discriminator_now"] is False
    assert result["selected_next_build_action"] == (
        "replace_proxy_envelopes_with_calibrated_systematics_bounds"
    )
