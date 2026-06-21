"""Tests for the v2.198 R4 ParSpec continuity ledger."""

import json
from pathlib import Path

from experiments.r4_parspec_continuity_ledger import (
    EXPECTED_VERSIONS,
    PARSPEC_RUNS,
    r4_parspec_continuity_ledger,
)


def test_parspec_runs_cover_every_version_from_v2190_to_v2197():
    versions = tuple(row["version"] for row in PARSPEC_RUNS)

    assert versions == EXPECTED_VERSIONS
    assert len(versions) == 8
    assert versions[0] == "v2.190"
    assert versions[-1] == "v2.197"


def test_every_parspec_run_has_note_artifact_and_retained_details():
    result = r4_parspec_continuity_ledger()

    assert result["evaluation"]["continuity_ledger_ready"] is True
    assert result["evaluation"]["missing_note_versions"] == []
    assert result["evaluation"]["missing_artifact_versions"] == []
    assert result["evaluation"]["missing_detail_versions"] == []
    assert result["evaluation"]["retained_detail_count"] >= 45


def test_ledger_preserves_parspec_source_package_facts():
    result = r4_parspec_continuity_ledger()
    rows = {row["version"]: row for row in result["runs"]}
    digest = rows["v2.191"]["artifact_digest"]

    assert digest["source_package_sha256"] == (
        "11b568f5107b4e31a7efd83b704178e7a9e938467fcd36a4856f53a208b05da2"
    )
    assert digest["qeft_power"] == 6
    assert digest["event_bounds_90_credible_km"] == {
        "GW150914": 51.7,
        "GW200129": 54.8,
        "combined": 51.3,
    }
    assert digest["qnm_deformation_coefficients"]["nmax_1"][
        "delta_tau_qeft_1"
    ] == 171.35
    assert digest["machine_readable_likelihood_ready"] is False


def test_ledger_preserves_source_event_alignment_and_detector_topology():
    result = r4_parspec_continuity_ledger()
    rows = {row["version"]: row for row in result["runs"]}

    v2192 = rows["v2.192"]["artifact_digest"]
    event_versions = {
        row["paper_event"]: row["event_version"] for row in v2192["events"]
    }
    assert event_versions == {
        "GW150914": "GW150914-v3",
        "GW200129": "GW200129_065458-v1",
    }
    assert v2192["detector_topology_by_event"]["GW200129"] == [
        "H1",
        "L1",
        "V1",
    ]

    v2194 = rows["v2.194"]["artifact_digest"]
    networks = {row["paper_event"]: row for row in v2194["event_networks"]}
    assert networks["GW150914"]["detectors"] == ["H1", "L1"]
    assert networks["GW200129"]["detectors"] == ["H1", "L1", "V1"]
    assert "V1" in v2194["detector_channel_responses"]["GW200129"]


def test_ledger_preserves_covariance_and_published_bound_surrogate_values():
    result = r4_parspec_continuity_ledger()
    rows = {row["version"]: row for row in result["runs"]}

    combined = rows["v2.195"]["artifact_digest"][
        "combined_event_set_covariance"
    ]
    assert combined["posterior_mean"] == {
        "g_R4_c1": 0.495622827625,
        "g_R4_c2": 0.495608515333,
        "g_R4_c3": -0.003518833974,
    }
    assert combined["posterior_covariance_eigenvalues"] == [
        0.000792664397,
        0.000801935517,
        0.000802067334,
    ]

    surrogates = {
        row["label"]: row for row in rows["v2.196"]["artifact_digest"]["surrogates"]
    }
    assert surrogates["GW150914"]["upper_bound_km_90"] == 51.7
    assert surrogates["GW200129"]["half_normal_sigma_km"] == 33.316034388765
    assert surrogates["combined"]["variance_km2"] == 972.702913352354
    assert all(row["claim_use_allowed"] is False for row in surrogates.values())


def test_ledger_preserves_qnm_jacobian_and_latest_claim_blockers():
    result = r4_parspec_continuity_ledger()
    rows = {row["version"]: row for row in result["runs"]}
    digest = rows["v2.197"]["artifact_digest"]

    assert digest["qeft_power"] == 6
    assert digest["qnm_coefficient_vector"] == {
        "delta_omega_qeft_0": -0.2114,
        "delta_tau_qeft_0": -0.607,
        "delta_omega_qeft_1": -1.5263,
        "delta_tau_qeft_1": 171.35,
    }
    derivatives = {
        row["label"]: row["dqnm_deformation_d_ell_at_published_bound"]
        for row in digest["event_deformation_rows"]
    }
    assert derivatives["combined"]["delta_tau_qeft_1"] == 20.040935672515
    assert digest["source_space_jacobian_ready"] is True
    assert digest["engine_axis_map_ready"] is False
    assert (
        "qnm_deformation_to_bresciani_engine_r4_operator_basis_map_missing"
        in result["latest_remaining_claim_blockers"]
    )


def test_ledger_is_documentation_only_and_keeps_claim_gate_closed():
    result = r4_parspec_continuity_ledger()

    assert result["version"] == "v2.198"
    assert result["route_status"] == (
        "r4_parspec_continuity_ledger_ready_nonclaiming"
    )
    assert result["claimable_framework_exclusions_now"] == []
    assert result["ready_for_framework_claim"] is False
    assert result["evaluation"]["claim_gate_violations"] == []
    assert result["evaluation"]["claim_boundary_preserved"] is True
    assert result["selected_next_build_action"] == (
        "continue_with_qnm_to_bresciani_operator_map_or_public_likelihood"
    )


def test_committed_artifact_records_complete_parspec_continuity_ledger():
    path = Path("experiments/results/v2.198/r4_parspec_continuity_ledger.json")
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.198"
    assert result["covered_versions"] == list(EXPECTED_VERSIONS)
    assert result["evaluation"]["continuity_ledger_ready"] is True
    assert result["ready_for_framework_claim"] is False
