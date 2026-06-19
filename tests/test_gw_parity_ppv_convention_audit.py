"""Regression tests for v2.70 GW parity PPV convention audit."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from gw_parity_ppv_convention_audit import (  # noqa: E402
    diagnose_gw_parity_ppv_convention_audit,
)


def test_ppv_convention_audit_remains_nonpromoting():
    result = diagnose_gw_parity_ppv_convention_audit()

    assert result["version"] == "v2.70"
    assert result["row_count"] == 3
    assert result["ng_beta10_candidate_ready"] is True
    assert result["ppv_beta1_projection_ready"] is False
    assert result["helicity_harmonization_ready"] is False
    assert result["engine_projection_ready"] is False
    assert result["claimable_discriminator_now"] is False
    assert (
        result["route_status"]
        == "ppv_convention_audit_partial_candidates_projection_blocked"
    )


def test_ng_row_is_source_declared_beta10_candidate_but_not_claim_ready():
    result = diagnose_gw_parity_ppv_convention_audit()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["ng_kappa_to_jenks_beta10_candidate"]

    assert row["source_packet"] == "ng_gwtc3_kappa_at_100hz"
    assert row["source_declared_mapping"]["target_ppv_parameter"] == (
        "beta_1_0_amplitude_branch"
    )
    assert row["readiness"]["source_declared_ppv_mapping_ready"] is True
    assert row["readiness"]["posterior_ingestion_ready"] is False
    assert row["readiness"]["engine_projection_ready"] is False
    assert row["readiness"]["claim_ready"] is False
    assert "D_C_Gpc" in row["source_declared_mapping"]["candidate_formula"]
    assert "source_declared_beta10_not_engine_axis" in row["blockers"]


def test_callister_waveform_row_blocks_single_beta1_promotion():
    result = diagnose_gw_parity_ppv_convention_audit()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["callister_waveform_alpha1_beta1_split_candidate"]

    assert row["source_declared_mapping"]["target_ppv_parameters"] == [
        "alpha_1_redshift_branch",
        "beta_1_distance_branch",
    ]
    assert row["readiness"]["posterior_ingestion_ready"] is True
    assert "redshift_term_not_beta1_distance_only" in row["blockers"]
    assert "two_axis_alpha1_beta1_not_single_beta1" in row["blockers"]
    assert "kappa_z*z" in row["source_declared_mapping"]["candidate_formula"]


def test_callister_code_row_keeps_energy_argument_separate():
    result = diagnose_gw_parity_ppv_convention_audit()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["callister_public_code_energy_density_convention"]

    assert row["source_declared_mapping"]["target_quantity"] == (
        "sgwb_energy_density_hyperbolic_argument"
    )
    assert row["source_declared_mapping"]["code_argument_matches_2vp"] is True
    assert row["readiness"]["source_declared_ppv_mapping_ready"] is False
    assert "2*pi" in row["source_declared_mapping"]["candidate_formula"]
    assert "energy_density_argument_not_waveform_beta_parameter" in row["blockers"]
    assert "cosh(A)" in row["source_formulas"][2]


def test_common_blockers_are_counted_across_all_rows():
    result = diagnose_gw_parity_ppv_convention_audit()
    counts = result["blocker_counts"]

    assert counts["helicity_convention_not_harmonized_across_sources"] == 3
    assert counts["ppv_beta1_normalization_not_finalized"] == 3
    assert counts["engine_projection_out_of_scope"] == 3
    assert counts["source_declared_beta10_not_engine_axis"] == 1
    assert counts["two_axis_alpha1_beta1_not_single_beta1"] == 1
    assert "Ng public posterior parser" in result["best_next_artifact"]
