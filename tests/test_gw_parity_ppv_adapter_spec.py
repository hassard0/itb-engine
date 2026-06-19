"""Regression tests for v2.63 GW parity PPV adapter spec."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from gw_parity_ppv_adapter_spec import diagnose_gw_parity_ppv_adapter_spec  # noqa: E402


def test_ppv_adapter_spec_defines_no_ready_adapter_yet():
    result = diagnose_gw_parity_ppv_adapter_spec()

    assert result["target_intermediate_basis"] == "ppv_amplitude_birefringence_branch"
    assert result["spec_count"] == 2
    assert result["implementation_ready_specs"] == []
    assert result["implementation_ready_count"] == 0
    assert result["engine_projection_allowed_now"] is False
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "ppv_adapter_spec_defined_formula_missing"


def test_ng_spec_targets_amplitude_branch_with_formula_blockers():
    result = diagnose_gw_parity_ppv_adapter_spec()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["ng_kappa_to_ppv_amplitude_branch"]

    assert row["native_packet"] == "ng_gwtc3_kappa_at_100hz"
    assert row["target_basis"] == "ppv_amplitude_birefringence_branch"
    assert "kappa_Gpc_inv" in row["native_axes"]
    assert "ppv_amplitude_distance_slope" in row["target_axes"]
    assert "missing_explicit_native_to_ppv_formula" in row["blockers"]
    assert "missing_helicity_sign_convention" in row["blockers"]
    assert "posterior_mass_normalizes_to_one" in row["required_validation_tests"]


def test_callister_spec_keeps_distance_and_redshift_terms_separate():
    result = diagnose_gw_parity_ppv_adapter_spec()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["callister_kappaD_kappaz_to_ppv_amplitude_branch"]

    assert row["native_packet"] == "callister_sgwb_kappaD_kappaz"
    assert "kappa_D" in row["native_axes"]
    assert "kappa_z" in row["native_axes"]
    assert "ppv_amplitude_distance_slope" in row["target_axes"]
    assert "ppv_amplitude_redshift_slope" in row["target_axes"]
    assert "missing_distance_redshift_normalization" in row["blockers"]
    assert "distance_and_redshift_terms_remain_separable" in row["required_validation_tests"]


def test_formula_and_engine_projection_blockers_are_explicit():
    result = diagnose_gw_parity_ppv_adapter_spec()
    counts = result["blocker_counts"]

    assert counts["missing_explicit_native_to_ppv_formula"] == 2
    assert counts["engine_projection_out_of_scope"] == 2
    assert "posterior parser tests" in result["best_next_artifact"]
