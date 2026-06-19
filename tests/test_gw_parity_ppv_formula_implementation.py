"""Regression tests for v2.64 GW parity formula implementation."""

import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from gw_parity_ppv_formula_implementation import (  # noqa: E402
    diagnose_gw_parity_ppv_formula_implementation,
)


def test_formula_layer_is_ready_but_nonpromoting():
    result = diagnose_gw_parity_ppv_formula_implementation()

    assert result["implemented_layer"] == "source_native_amplitude_log_gain"
    assert result["formula_ready_routes"] == [
        "ng_kappa_amplitude_log_gain",
        "callister_sgwb_amplitude_log_gain",
        "callister_sgwb_energy_hyperbolic_argument",
        "normalize_discrete_posterior",
    ]
    assert result["ppv_beta1_projection_ready"] is False
    assert result["engine_projection_ready"] is False
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "native_amplitude_formula_ready_projection_blocked"


def test_ng_example_preserves_source_native_scaling():
    result = diagnose_gw_parity_ppv_formula_implementation()
    rows = {row["label"]: row for row in result["rows"]}
    zero = rows["ng_zero_control"]["log_gain"]
    example = rows["ng_source_native_example"]["log_gain"]

    assert zero["value"] == 0.0
    assert example["value"] == pytest.approx(-0.019 * 2.0 * 2.0)
    assert example["native_parameters"]["kappa_Gpc_inv"] == -0.019
    assert example["helicity_convention"] == "positive_kappa_enhances_left_in_ng_convention"
    assert example["engine_projection_allowed"] is False


def test_callister_distance_and_redshift_examples_are_separable():
    result = diagnose_gw_parity_ppv_formula_implementation()
    rows = {row["label"]: row for row in result["rows"]}
    distance = rows["callister_distance_term_example"]["log_gain"]
    redshift = rows["callister_redshift_term_example"]["log_gain"]
    energy_argument = rows["callister_energy_density_argument_example"]["log_gain"]

    assert distance["value"] == pytest.approx(math.pi * 0.1 * 2.0)
    assert redshift["value"] == pytest.approx(math.pi * 0.1 * 0.3)
    assert energy_argument["value"] == pytest.approx(2.0 * distance["value"])
    assert energy_argument["target_basis"] == "sgwb_energy_density_hyperbolic_argument"
    assert distance["native_parameters"] == {"kappa_D": 0.1, "kappa_z": 0.0}
    assert redshift["native_parameters"] == {"kappa_D": 0.0, "kappa_z": 0.1}
    assert distance["engine_projection_allowed"] is False


def test_projection_blockers_remain_explicit():
    result = diagnose_gw_parity_ppv_formula_implementation()
    counts = result["blocker_counts"]

    assert counts["helicity_convention_not_harmonized_across_sources"] == 5
    assert counts["posterior_release_parser_not_implemented"] == 5
    assert counts["ppv_beta1_normalization_not_finalized"] == 5
    assert counts["engine_projection_out_of_scope"] == 5
    assert result["posterior_normalizer_ready"] is True
    assert result["posterior_normalizer_norm"] == pytest.approx(1.0)
