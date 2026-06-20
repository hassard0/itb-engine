"""Tests for the v2.120 detector-calibration bound."""

from experiments.gw_alpha_detector_calibration_bound import (
    DEFAULT_ENVELOPE_AUDIT_PATH,
    DEFAULT_IMR_REFERENCE_PATH,
    calibration_bound_for_parameter,
    calibration_corner_factors,
    detector_calibration_bound,
    detector_projection_complexes,
    diagnose_gw_alpha_detector_calibration_bound,
    evaluate_alpha_detector_calibration_bound,
    load_json,
    packet_with_detector_calibration_bound,
)


def _inputs():
    return (
        load_json(DEFAULT_ENVELOPE_AUDIT_PATH),
        load_json(DEFAULT_IMR_REFERENCE_PATH),
    )


def test_calibration_corner_factors_cover_amplitude_and_phase_extremes():
    factors = calibration_corner_factors(
        amplitude_fraction=0.1,
        phase_degrees=6.0,
    )

    assert len(factors) == 4
    assert sorted(round(abs(factor), 12) for factor in factors) == [
        0.9,
        0.9,
        1.1,
        1.1,
    ]


def test_parameter_bound_propagates_all_h1_l1_corners():
    _audit, imr_reference = _inputs()
    detector_projections = detector_projection_complexes(
        imr_reference,
        "alpha_bar_1",
    )
    bound = calibration_bound_for_parameter(
        detector_projections,
        amplitude_fraction=0.1,
        phase_degrees=6.0,
    )

    assert bound["calibration_corner_count"] == 16
    assert bound["max_complex_mean_shift"] > 0.0
    assert bound["max_abs_detector_mean_shift"] > 0.0


def test_detector_calibration_bound_replaces_proxy_with_bounded_evidence():
    _audit, imr_reference = _inputs()
    evidence = detector_calibration_bound(imr_reference)

    assert evidence["status"] == "bounded"
    assert evidence["bounded_ready"] is True
    assert evidence["applied_envelope"]["amplitude_fraction"] == 0.1
    assert evidence["applied_envelope"]["phase_degrees"] == 6.0
    assert evidence["max_network_projection_shift"] > 0.004


def test_packet_with_calibration_bound_keeps_other_components_open():
    audit, imr_reference = _inputs()
    packet = packet_with_detector_calibration_bound(
        audit["packet"],
        imr_reference,
    )
    result = evaluate_alpha_detector_calibration_bound(packet)

    assert result["detector_calibration_bounded"] is True
    assert result["claim_ready"] is False
    assert result["bounded_components"] == [
        "detector_calibration",
        "sampler_convergence",
        "public_data_reproducibility",
    ]
    assert result["open_components"] == [
        "waveform_systematics",
        "prior_sensitivity",
        "eft_truncation",
    ]


def test_diagnosis_selects_remaining_systematics_next():
    result = diagnose_gw_alpha_detector_calibration_bound()

    assert result["version"] == "v2.120"
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "detector_calibration_bounded_alpha_packet_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "bound_waveform_prior_and_eft_systematics"
    )
