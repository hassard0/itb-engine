"""Tests for the v2.125 joint-event likelihood calibration."""

import pytest

from experiments.gw_alpha_joint_likelihood_calibration import (
    DEFAULT_CUBE_EXPORT_PATH,
    DEFAULT_WAVEFORM_EFT_PATH,
    diagnose_gw_alpha_joint_likelihood_calibration,
    evaluate_alpha_joint_likelihood_calibration,
    joint_likelihood_surface_from_cube,
    load_json,
    null_likelihood_calibration,
    packet_with_joint_likelihood_calibration,
    posterior_moments_from_joint_surface,
    validate_shared_nuisance_grid,
)


def _inputs():
    return load_json(DEFAULT_CUBE_EXPORT_PATH), load_json(DEFAULT_WAVEFORM_EFT_PATH)


def test_cube_has_shared_nuisance_grid_for_joint_event_surface():
    cube, _waveform_eft = _inputs()
    grid = validate_shared_nuisance_grid(cube["likelihood_cube"])

    assert len(grid) == 81
    assert grid[0]["total_mass_solar"] == 18.0
    assert grid[0]["eta"] == 0.2
    assert grid[0]["tc_shift_seconds"] == -0.002
    assert grid[0]["phic_rad"] == pytest.approx(-0.785398163397)


def test_joint_likelihood_surface_keeps_marginal_best_at_gr():
    cube, _waveform_eft = _inputs()
    surface = joint_likelihood_surface_from_cube(cube["likelihood_cube"])

    assert surface["likelihood_kind"] == (
        "joint_shared_nuisance_lalsuite_imrphenomd_alpha_grid"
    )
    assert surface["nuisance_points"] == 81
    assert surface["grid_points"] == 441
    assert surface["best_marginal_grid_point"]["alpha_bar_1"] == 0.0
    assert surface["best_marginal_grid_point"]["alpha_bar_2"] == 0.0
    assert surface["delta_log_likelihood_best_vs_gr"] == pytest.approx(0.0)
    assert surface["best_profile_grid_point"]["alpha_bar_1"] == pytest.approx(0.4)
    assert surface["delta_profile_log_likelihood_best_vs_gr"] == pytest.approx(
        0.002612755857,
    )


def test_null_likelihood_calibration_recovers_normalized_detector_scale():
    cube, _waveform_eft = _inputs()
    calibration = null_likelihood_calibration(cube["likelihood_cube"])

    assert calibration["calibrated_ready"] is True
    assert calibration["expected_network_null_log_likelihood"] == -1.0
    assert [row["detector"] for row in calibration["per_detector"]] == ["H1", "L1"]
    assert all(
        row["min_zero_alpha_log_likelihood"] == pytest.approx(-0.5)
        for row in calibration["per_detector"]
    )
    assert all(row["within_tolerance"] for row in calibration["per_detector"])


def test_joint_posterior_summary_updates_covariance_and_intervals():
    cube, _waveform_eft = _inputs()
    surface = joint_likelihood_surface_from_cube(cube["likelihood_cube"])
    posterior = posterior_moments_from_joint_surface(surface)

    assert posterior["mean"]["alpha_bar_1"] == pytest.approx(0.001002226468)
    assert posterior["mean"]["alpha_bar_2"] == pytest.approx(0.000788087449)
    assert posterior["covariance"]["matrix"][0][0] == pytest.approx(1.236390183085)
    assert posterior["covariance"]["matrix"][1][1] == pytest.approx(1.236414495125)
    assert posterior["central_90"]["alpha_bar_1"]["lower_90"] == -1.8
    assert posterior["central_90"]["alpha_bar_1"]["upper_90"] == pytest.approx(1.8)


def test_packet_becomes_native_ready_but_g8_keeps_claim_blocked():
    cube, waveform_eft = _inputs()
    surface = joint_likelihood_surface_from_cube(cube["likelihood_cube"])
    posterior = posterior_moments_from_joint_surface(surface)
    calibration = null_likelihood_calibration(cube["likelihood_cube"])
    packet = packet_with_joint_likelihood_calibration(
        waveform_eft["packet"],
        surface,
        posterior,
        calibration,
    )
    result = evaluate_alpha_joint_likelihood_calibration(packet, surface, calibration)

    assert packet["systematics_budget"]["status"] == "bounded"
    assert packet["posterior_or_likelihood_export"]["kind"] == (
        "joint_shared_nuisance_lalsuite_imrphenomd_alpha_grid"
    )
    assert result["adapter_evaluation"]["native_adapter_ready"] is True
    assert result["adapter_evaluation"]["adapter_blockers"] == []
    assert result["adapter_evaluation"]["claim_ready"] is False
    assert result["adapter_evaluation"]["claim_blockers"] == [
        "g8_joint_component_missing",
    ]


def test_diagnosis_selects_g8_joint_component_next():
    result = diagnose_gw_alpha_joint_likelihood_calibration()

    assert result["version"] == "v2.125"
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "joint_likelihood_scale_calibrated_g8_missing_nonclaiming"
    )
    assert result["selected_next_build_action"] == "supply_g8_joint_component"
