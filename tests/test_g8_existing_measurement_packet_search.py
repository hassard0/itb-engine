"""Regression tests for v2.55 g_8 external measurement packet search."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from g8_existing_measurement_packet_search import (  # noqa: E402
    diagnose_g8_existing_measurement_packet_search,
)


def test_existing_measurement_search_finds_no_claim_ready_g8_packet():
    result = diagnose_g8_existing_measurement_packet_search()

    assert result["axis"] == "g_8"
    assert result["candidate_count"] == 5
    assert result["external_numeric_candidate_count"] == 3
    assert result["claim_ready_routes"] == []
    assert result["contract_satisfied_candidates"] == []
    assert result["claimable_discriminator_now"] is False
    assert (
        result["route_status"]
        == "existing_public_measurements_do_not_satisfy_g8_contract"
    )


def test_external_energy_correlator_measurements_are_design_seeds_not_g8_claims():
    result = diagnose_g8_existing_measurement_packet_search()
    rows = {row["label"]: row for row in result["rows"]}

    for label in {
        "cms_e2c_e3c_jet_substructure",
        "cms_open_data_n_point_energy_correlators",
        "cms_heavy_ion_eec_modification",
    }:
        row = rows[label]
        assert row["evidence"]["measurement_kind"] == "external_numeric_measurement"
        assert row["ready_for_g8_claim"] is False
        assert "source_backed_g8_axis_mapping" in row["contract_failures"]
        assert "framework_applicability_domain" in row["contract_failures"]
        assert "excluding_discriminator_math" in row["contract_failures"]


def test_detector_and_partial_wave_theory_bridges_are_not_external_measurements():
    result = diagnose_g8_existing_measurement_packet_search()
    rows = {row["label"]: row for row in result["rows"]}

    for label in {
        "detector_operator_theory_bridge",
        "hadron_eec_celestial_block_partial_wave_decomposition",
    }:
        row = rows[label]
        assert row["evidence"]["measurement_kind"] == "theory_formalism"
        assert "external_numeric_observable" in row["contract_failures"]
        assert "measurement_kind_not_external_numeric" in row["guard"]["blockers"]
        assert row["ready_for_g8_claim"] is False


def test_contract_failure_counts_show_axis_mapping_is_universal_blocker():
    result = diagnose_g8_existing_measurement_packet_search()
    counts = result["contract_failure_counts"]

    assert counts["source_backed_g8_axis_mapping"] == result["candidate_count"]
    assert counts["excluding_discriminator_math"] == result["candidate_count"]
    assert counts["framework_applicability_domain"] == result["candidate_count"]
    assert counts["eft_valid_energy_window"] == result["candidate_count"]


def test_candidate_search_preserves_next_action_as_adapter_or_new_measurement():
    result = diagnose_g8_existing_measurement_packet_search()

    assert "engine-normalized g_8 likelihood" in result["best_next_artifact"]
    assert "new measurement" in result["best_next_artifact"]
