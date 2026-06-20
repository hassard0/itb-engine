"""Tests for the v2.124 waveform and EFT component bounds."""

import pytest

from experiments.gw_alpha_waveform_eft_bound import (
    DEFAULT_GR_REFERENCE_PATH,
    DEFAULT_IMR_REFERENCE_PATH,
    DEFAULT_PRIOR_REWEIGHT_PATH,
    DEFAULT_SOURCE_RESPONSE_PATH,
    NATURALNESS_COEFFICIENT_RATIO_CAP,
    WAVEFORM_ENVELOPE_SAFETY_FACTOR,
    diagnose_gw_alpha_waveform_eft_bound,
    eft_truncation_component_bound,
    evaluate_alpha_waveform_eft_bound,
    load_json,
    packet_with_waveform_eft_bounds,
    prior_alpha_domain,
    waveform_component_bound,
)


def _inputs():
    return (
        load_json(DEFAULT_PRIOR_REWEIGHT_PATH),
        load_json(DEFAULT_GR_REFERENCE_PATH),
        load_json(DEFAULT_IMR_REFERENCE_PATH),
        load_json(DEFAULT_SOURCE_RESPONSE_PATH),
    )


def test_prior_alpha_domain_uses_prior_sweep_best_cells_plus_one_grid_step():
    prior_reweight, *_ = _inputs()
    domain = prior_alpha_domain(prior_reweight)

    assert domain["axis_step"] == 0.2
    assert domain["max_abs_best_alpha"] == 0.2
    assert domain["domain_half_width"] == pytest.approx(0.4)
    assert domain["max_delta_log_likelihood_best_vs_gr"] == pytest.approx(
        0.000542496189,
    )


def test_waveform_component_bound_replaces_proxy_with_finite_envelope():
    prior_reweight, gr_reference, imr_reference, _source_response = _inputs()
    domain = prior_alpha_domain(prior_reweight)
    evidence = waveform_component_bound(gr_reference, imr_reference, domain)

    assert evidence["status"] == "bounded"
    assert evidence["bounded_ready"] is True
    assert evidence["safety_factor"] == WAVEFORM_ENVELOPE_SAFETY_FACTOR
    assert evidence["max_network_projection_component_delta"] > 0.036
    assert evidence["waveform_projection_envelope"] == pytest.approx(
        evidence["max_network_projection_component_delta"]
        * WAVEFORM_ENVELOPE_SAFETY_FACTOR,
    )


def test_eft_truncation_bound_uses_next_pn_power_counting_cap():
    prior_reweight, _gr_reference, imr_reference, source_response = _inputs()
    domain = prior_alpha_domain(prior_reweight)
    evidence = eft_truncation_component_bound(
        source_response,
        imr_reference,
        domain,
    )

    assert evidence["status"] == "bounded"
    assert evidence["bounded_ready"] is True
    assert evidence["coefficient_ratio_cap"] == NATURALNESS_COEFFICIENT_RATIO_CAP
    assert evidence["next_order_power_suppression"] == pytest.approx(
        evidence["v_f_max"] ** 2,
    )
    assert evidence["relative_remainder_bound"] == pytest.approx(
        NATURALNESS_COEFFICIENT_RATIO_CAP
        * evidence["next_order_power_suppression"],
    )
    assert evidence["alpha_equivalent_remainder_bound"] > domain["domain_half_width"]


def test_packet_bounds_components_but_keeps_top_level_budget_open():
    prior_reweight, gr_reference, imr_reference, source_response = _inputs()
    domain = prior_alpha_domain(prior_reweight)
    waveform = waveform_component_bound(gr_reference, imr_reference, domain)
    eft = eft_truncation_component_bound(source_response, imr_reference, domain)
    packet = packet_with_waveform_eft_bounds(
        prior_reweight["packet"],
        waveform,
        eft,
    )
    result = evaluate_alpha_waveform_eft_bound(packet)

    assert packet["systematics_budget"]["components"] == {
        "waveform_systematics": "bounded",
        "detector_calibration": "bounded",
        "prior_sensitivity": "bounded",
        "eft_truncation": "bounded",
        "sampler_convergence": "bounded",
        "public_data_reproducibility": "bounded",
    }
    assert packet["systematics_budget"]["component_status"] == "bounded"
    assert packet["systematics_budget"]["status"] == "open"
    assert result["component_systematics_bounded"] is True
    assert result["open_components"] == []
    assert result["adapter_evaluation"]["claim_ready"] is False
    assert result["adapter_evaluation"]["adapter_blockers"] == [
        "systematics_not_closed",
    ]


def test_diagnosis_selects_joint_likelihood_scale_next():
    result = diagnose_gw_alpha_waveform_eft_bound()

    assert result["version"] == "v2.124"
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "waveform_eft_components_bounded_budget_hold_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "calibrate_likelihood_scale_and_joint_event_posterior"
    )
