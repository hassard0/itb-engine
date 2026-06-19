"""Regression tests for v2.60 GW parity measurement packet search."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from gw_parity_measurement_packet_search import (  # noqa: E402
    diagnose_gw_parity_measurement_packet_search,
)


def test_gw_parity_packet_search_finds_no_claim_ready_route():
    result = diagnose_gw_parity_measurement_packet_search()

    assert result["axis"] == "g_R2_parity/g_R3_parity"
    assert result["candidate_count"] == 5
    assert result["external_bound_or_measurement_candidate_count"] == 3
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "gw_parity_external_bounds_not_engine_claim_ready"


def test_sgwb_bound_is_numeric_but_not_engine_mapped():
    result = diagnose_gw_parity_measurement_packet_search()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["sgwb_nonobservation_parity_bound"]

    assert row["evidence"]["measurement_kind"] == "external_upper_bound"
    assert row["evidence"]["numerical_value"] == 0.1
    assert row["evidence"]["uncertainty"] is None
    assert row["ready_for_engine_gw_parity_claim"] is False
    assert "missing_external_numeric_gw_bound" in row["contract_failures"]
    assert "missing_engine_axis_projection" in row["contract_failures"]
    assert "missing_public_gw_likelihood" in row["contract_failures"]
    assert "frequency_normalization_not_engine_usable" in row["contract_failures"]
    assert "no_framework_excluding_math" in row["contract_failures"]


def test_formalism_and_design_rows_are_not_external_measurement_packets():
    result = diagnose_gw_parity_measurement_packet_search()
    rows = {row["label"]: row for row in result["rows"]}

    for label in {
        "parameterized_parity_violation_formalism",
        "coincident_gw_grb_parity_test",
    }:
        row = rows[label]
        assert row["ready_for_engine_gw_parity_claim"] is False
        assert "missing_external_numeric_gw_bound" in row["contract_failures"]
        assert "measurement_kind_not_external_numeric" in row["guard"]["blockers"]


def test_axis_projection_and_framework_math_are_universal_blockers():
    result = diagnose_gw_parity_measurement_packet_search()
    counts = result["contract_failure_counts"]

    assert counts["missing_engine_axis_projection"] == result["candidate_count"]
    assert counts["missing_public_gw_likelihood"] == result["candidate_count"]
    assert counts["frequency_normalization_not_engine_usable"] == result["candidate_count"]
    assert counts["no_framework_excluding_math"] == result["candidate_count"]


def test_next_artifact_is_likelihood_adapter_not_claim():
    result = diagnose_gw_parity_measurement_packet_search()

    assert "g_R2_parity/g_R3_parity" in result["best_next_artifact"]
    assert "frequency normalization" in result["best_next_artifact"]
    assert result["claimable_discriminator_now"] is False
