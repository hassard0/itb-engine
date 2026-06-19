"""Regression tests for v2.54 g_8 measurement specification."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from g8_high_moment_measurement_specification import (  # noqa: E402
    diagnose_g8_high_moment_measurement_specification,
)


def test_g8_measurement_specification_remains_nonclaimable():
    result = diagnose_g8_high_moment_measurement_specification()

    assert result["axis"] == "g_8"
    assert result["route"] == "matter_high_moment_g_8"
    assert result["route_status"] == "measurement_spec_defined_not_satisfied"
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False


def test_partial_wave_geometry_is_good_but_external_evidence_is_missing():
    result = diagnose_g8_high_moment_measurement_specification()
    designs = result["design_summaries"]

    assert designs["forward_only_narrow"]["geometry_passes_isolation_gate"] is False
    assert designs["forward_only_narrow"]["status"] == "rejected_forward_degeneracy"
    assert designs["forward_only_wide_energy"]["geometry_passes_isolation_gate"] is False
    assert (
        designs["forward_only_wide_energy"]["status"]
        == "rejected_energy_reach_artifact_without_eft_control"
    )
    assert (
        designs["spin_0_2_4_partial_waves"]["geometry_passes_isolation_gate"]
        is True
    )
    assert designs["spin_0_2_4_partial_waves"]["pure_g8_row_count"] > 0
    assert result["current_design_probe_guard"]["ready_for_promotion"] is False


def test_measurement_contract_names_all_required_promotion_fields():
    result = diagnose_g8_high_moment_measurement_specification()
    requirement_ids = {row["id"] for row in result["measurement_contract"]}

    assert {
        "external_numeric_observable",
        "source_backed_g8_axis_mapping",
        "angular_or_partial_wave_isolation",
        "public_likelihood_or_covariance",
        "eft_valid_energy_window",
        "closed_systematics_budget",
        "framework_applicability_domain",
        "excluding_discriminator_math",
    } <= requirement_ids
    assert result["missing_or_open_contract_requirements"] == [
        "external_numeric_observable",
        "source_backed_g8_axis_mapping",
        "angular_or_partial_wave_isolation",
        "public_likelihood_or_covariance",
        "eft_valid_energy_window",
        "closed_systematics_budget",
        "framework_applicability_domain",
        "excluding_discriminator_math",
    ]


def test_current_design_probe_guard_blocks_internal_cut_promotion():
    result = diagnose_g8_high_moment_measurement_specification()
    blockers = set(result["current_design_probe_guard"]["blockers"])

    assert "internal_cut_not_external_measurement" in blockers
    assert "missing_external_numeric_measurement" in blockers
    assert "axis_mapping_not_source_backed" in blockers
    assert "systematics_not_closed" in blockers
    assert "discriminator_math_not_excluding" in blockers
    assert "g8_not_isolated_from_lower_matter_moments" in result["claim_blockers"]
    assert "eft_validity_not_bounded" in result["claim_blockers"]


def test_measurement_packet_template_requires_public_likelihood_and_mapping():
    result = diagnose_g8_high_moment_measurement_specification()
    packet = result["measurement_packet_template"]

    assert packet["axis"] == "g_8"
    assert packet["required_measurement_kind"] == "external_numeric_measurement"
    assert "covariance_or_likelihood" in packet["required_numerical_fields"]
    assert "jacobian_or_projection_to_g_8" in packet["required_mapping_fields"]
    assert "eft_truncation" in packet["required_systematics_fields"]
