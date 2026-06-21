"""Tests for the v2.189 R4 research continuity ledger."""

import json
from pathlib import Path

from experiments.r4_research_continuity_ledger import (
    EXPECTED_VERSIONS,
    RECENT_RUNS,
    research_continuity_ledger,
)


def test_recent_runs_cover_every_version_from_v2170_to_v2188():
    versions = tuple(row["version"] for row in RECENT_RUNS)

    assert versions == EXPECTED_VERSIONS
    assert len(versions) == 19
    assert versions[0] == "v2.170"
    assert versions[-1] == "v2.188"


def test_every_run_has_a_note_artifact_status_and_retained_details():
    result = research_continuity_ledger()

    assert result["evaluation"]["continuity_ledger_ready"] is True
    assert result["evaluation"]["missing_note_versions"] == []
    assert result["evaluation"]["missing_artifact_versions"] == []
    assert result["evaluation"]["missing_detail_versions"] == []
    assert result["evaluation"]["retained_detail_count"] >= 60


def test_ledger_preserves_recent_numeric_frontier_details():
    result = research_continuity_ledger()
    rows = {row["version"]: row for row in result["runs"]}

    v2185 = rows["v2.185"]["artifact_digest"]
    assert v2185["central_values"]["g_R4_c1"] == 0.495629103212
    assert v2185["central_values"]["g_R4_c2"] == 0.495614794648
    assert v2185["central_values"]["g_R4_c3"] == -0.003513023764

    v2186 = rows["v2.186"]["artifact_digest"]
    assert v2186["nuisance_points"] == 81
    assert v2186["nuisance_parameters"] == [
        "total_mass_solar",
        "eta",
        "tc_shift_seconds",
        "phic_rad",
    ]
    assert v2186["exported_covariance"][0][0] == 0.250002974172

    v2187 = rows["v2.187"]["artifact_digest"]
    assert v2187["coefficient_grid"]["grid_points"] == 125
    assert v2187["nuisance_points_per_detector"] == [81, 81]
    assert v2187["posterior_mean"]["g_R4_c1"] == 0.495635486753
    assert v2187["posterior_mean"]["g_R4_c2"] == 0.495621203259
    assert v2187["posterior_mean"]["g_R4_c3"] == -0.003508798916


def test_ledger_preserves_parspec_bridge_and_remaining_blockers():
    result = research_continuity_ledger()
    rows = {row["version"]: row for row in result["runs"]}
    v2188 = rows["v2.188"]["artifact_digest"]

    assert v2188["parspec_bound_imported"][
        "quartic_eft_length_scale_90_credible_km"
    ] == 51.3
    assert v2188["source_events"] == ["GW150914", "GW200129"]
    assert v2188["current_engine_event"] == "GW170608"
    assert "engine_r4_axes_to_parspec_qeft_length_map_missing" in (
        v2188["bridge_blockers"]
    )
    assert "public_parspec_qeft_likelihood_or_posterior_samples_missing" in (
        v2188["bridge_blockers"]
    )


def test_ledger_is_documentation_only_and_keeps_claim_gate_closed():
    result = research_continuity_ledger()

    assert result["version"] == "v2.189"
    assert result["route_status"] == (
        "r4_research_continuity_ledger_ready_nonclaiming"
    )
    assert result["claimable_framework_exclusions_now"] == []
    assert result["ready_for_framework_claim"] is False
    assert result["evaluation"]["claim_boundary_preserved"] is True
    assert result["selected_next_build_action"] == (
        "continue_with_parspec_qeft_axis_map_or_public_likelihood_packet"
    )


def test_committed_artifact_records_complete_continuity_ledger():
    path = Path("experiments/results/v2.189/r4_research_continuity_ledger.json")
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.189"
    assert result["covered_versions"] == list(EXPECTED_VERSIONS)
    assert result["evaluation"]["continuity_ledger_ready"] is True
    assert result["ready_for_framework_claim"] is False
