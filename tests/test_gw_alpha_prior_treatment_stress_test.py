"""Tests for the v2.121 prior/nuisance treatment stress test."""

from experiments.gw_alpha_prior_treatment_stress_test import (
    DEFAULT_CALIBRATION_BOUND_PATH,
    DEFAULT_MARGINAL_RESULT_PATH,
    alpha_axis_step,
    best_grid_point_at_profile_temperature,
    diagnose_gw_alpha_prior_treatment_stress_test,
    evaluate_alpha_prior_treatment_stress_test,
    load_json,
    packet_with_prior_treatment_stress_test,
    profile_temperature_sweep,
)


def _inputs():
    return (
        load_json(DEFAULT_CALIBRATION_BOUND_PATH),
        load_json(DEFAULT_MARGINAL_RESULT_PATH),
    )


def test_alpha_axis_step_recovers_v2_115_grid_spacing():
    _calibration, marginal = _inputs()
    step = alpha_axis_step(marginal["network_likelihood"]["grid"])

    assert step == 0.19999999999999996


def test_profile_temperature_best_point_walks_from_marginal_to_profile():
    _calibration, marginal = _inputs()
    grid = marginal["network_likelihood"]["grid"]

    marginal_best = best_grid_point_at_profile_temperature(grid, 0.0)
    profile_best = best_grid_point_at_profile_temperature(grid, 1.0)

    assert marginal_best["alpha_bar_1"] == 0.0
    assert marginal_best["alpha_bar_2"] == 0.0
    assert profile_best["alpha_bar_1"] == 0.6000000000000001
    assert profile_best["alpha_bar_2"] == 0.6000000000000001


def test_profile_temperature_sweep_keeps_prior_sensitivity_open():
    _calibration, marginal = _inputs()
    sweep = profile_temperature_sweep(marginal)

    assert sweep["status"] == "open"
    assert sweep["stable_under_profile_stress"] is False
    assert sweep["first_temperature_exceeding_one_axis_grid_step"] == 0.25
    assert sweep["max_best_point_shift"] > 0.84


def test_packet_with_prior_stress_preserves_previous_bounded_components():
    calibration, marginal = _inputs()
    packet = packet_with_prior_treatment_stress_test(
        calibration["packet"],
        marginal,
    )
    result = evaluate_alpha_prior_treatment_stress_test(packet)

    assert result["prior_sensitivity_bounded"] is False
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
    assert "prior_nuisance_cube_missing" in result["remaining_nonclaiming_reasons"]


def test_diagnosis_selects_per_nuisance_likelihood_cube_next():
    result = diagnose_gw_alpha_prior_treatment_stress_test()

    assert result["version"] == "v2.121"
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "prior_treatment_stress_test_nonclaiming"
    assert result["selected_next_build_action"] == (
        "export_per_nuisance_likelihood_cube"
    )
