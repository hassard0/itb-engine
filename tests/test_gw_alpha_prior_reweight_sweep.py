"""Tests for the v2.123 nuisance-prior reweight sweep."""

import math

import pytest

from experiments.gw_alpha_prior_reweight_sweep import (
    ALPHA_PREFERENCE_LOG_LIKELIHOOD_TOLERANCE,
    DEFAULT_CUBE_EXPORT_PATH,
    declared_prior_catalog,
    diagnose_gw_alpha_prior_reweight_sweep,
    evaluate_alpha_prior_reweight_sweep,
    load_json,
    nuisance_log_weights,
    packet_with_prior_reweight_sweep,
    prior_reweight_sweep_from_cube,
    reweighted_network_surface,
)


def _cube_result():
    return load_json(DEFAULT_CUBE_EXPORT_PATH)


def test_prior_log_weights_are_normalized_for_uniform_and_centered_priors():
    cube = _cube_result()["likelihood_cube"]["detector_cubes"][0]
    catalog = declared_prior_catalog()
    uniform = catalog[0]
    centered = next(row for row in catalog if row["name"] == "central_broad_event_prior")

    uniform_weights = nuisance_log_weights(cube["nuisance_grid"], uniform)
    centered_weights = nuisance_log_weights(cube["nuisance_grid"], centered)

    assert sum(math.exp(value) for value in uniform_weights) == pytest.approx(1.0)
    assert sum(math.exp(value) for value in centered_weights) == pytest.approx(1.0)
    assert len(set(uniform_weights)) == 1
    assert max(centered_weights) > min(centered_weights)


def test_uniform_prior_reconstructs_v2_122_network_best_point():
    cube = _cube_result()
    uniform = declared_prior_catalog()[0]
    surface = reweighted_network_surface(cube["likelihood_cube"], uniform)

    assert surface["best_grid_point"]["alpha_bar_1"] == 0.0
    assert surface["best_grid_point"]["alpha_bar_2"] == 0.0
    assert surface["best_grid_point"]["log_reweighted_likelihood"] == pytest.approx(
        -1.0,
    )
    assert surface["delta_log_likelihood_best_vs_gr"] == pytest.approx(0.0)


def test_declared_prior_catalog_bounds_prior_sensitivity_from_cube():
    sweep = prior_reweight_sweep_from_cube(_cube_result())

    assert sweep["source_cube_version"] == "v2.122"
    assert sweep["catalog_prior_sensitivity_bounded"] is True
    assert sweep["max_abs_axis_grid_steps"] <= 1.0 + 1.0e-12
    assert sweep["max_euclidean_grid_steps"] <= math.sqrt(2.0) + 1.0e-12
    assert (
        sweep["max_delta_log_likelihood_best_vs_gr"]
        < ALPHA_PREFERENCE_LOG_LIKELIHOOD_TOLERANCE
    )

    moved_rows = [
        row
        for row in sweep["prior_summary_rows"]
        if row["shift_from_uniform_best"]["max_abs_axis_grid_steps"] > 0.0
    ]
    assert {row["prior_name"] for row in moved_rows} == {
        "central_tight_event_prior",
        "lower_corner_combined_stress_prior",
        "upper_corner_combined_stress_prior",
    }


def test_prior_reweight_packet_bounds_prior_but_not_global_claim():
    cube = _cube_result()
    sweep = prior_reweight_sweep_from_cube(cube)
    packet = packet_with_prior_reweight_sweep(cube["packet"], sweep)
    result = evaluate_alpha_prior_reweight_sweep(packet, sweep)

    assert packet["systematics_budget"]["components"]["prior_sensitivity"] == (
        "bounded"
    )
    assert result["prior_sensitivity_bounded"] is True
    assert result["bounded_components"] == [
        "detector_calibration",
        "prior_sensitivity",
        "sampler_convergence",
        "public_data_reproducibility",
    ]
    assert result["open_components"] == [
        "waveform_systematics",
        "eft_truncation",
    ]
    assert result["claim_ready"] is False
    assert "waveform_and_eft_systematics_still_open" in (
        result["remaining_nonclaiming_reasons"]
    )


def test_diagnosis_selects_waveform_and_eft_next():
    result = diagnose_gw_alpha_prior_reweight_sweep()

    assert result["version"] == "v2.123"
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "prior_reweight_sweep_bounded_nonclaiming"
    assert result["selected_next_build_action"] == (
        "bound_waveform_and_eft_truncation_systematics"
    )
