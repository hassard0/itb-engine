"""Regression tests for v2.59 parity route split frontier."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from parity_route_split_frontier import diagnose_parity_route_split_frontier  # noqa: E402


def test_parity_route_split_retires_direct_cmb_beta_gravity_map():
    result = diagnose_parity_route_split_frontier()

    assert result["route_count"] == 4
    assert result["direct_cmb_beta_to_gravity_route_retired"] is True
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "parity_routes_split_no_claim_ready_path"


def test_cmb_beta_route_is_not_engine_gravity_parity_route():
    result = diagnose_parity_route_split_frontier()
    rows = {row["route"]: row for row in result["rows"]}
    row = rows["cmb_em_axion_beta"]

    assert row["engine_gravity_parity_route"] is False
    assert row["target_axis"] == "axion_photon_coupling_or_field_history"
    assert row["source_backed_theory"] is True
    assert "not_engine_gravity_parity_axis" in row["blockers"]


def test_gw_birefringence_is_right_axis_but_measurement_blocked():
    result = diagnose_parity_route_split_frontier()
    rows = {row["route"]: row for row in result["rows"]}
    row = rows["gw_gravitational_birefringence"]

    assert row["engine_gravity_parity_route"] is True
    assert row["target_axis"] == "g_R2_parity,g_R3_parity"
    assert row["implemented_observable"].endswith(":GravitationalBirefringence")
    assert row["evidence"]["implemented_axes_touched"] == [
        "g_R2_parity",
        "g_R3_parity",
    ]
    assert row["external_measurement_ready"] is False
    assert "no_external_gw_parity_measurement_packet" in row["blockers"]


def test_multimessenger_common_axion_is_hypothesis_not_adapter():
    result = diagnose_parity_route_split_frontier()
    rows = {row["route"]: row for row in result["rows"]}
    row = rows["multimessenger_common_axion"]

    assert row["engine_gravity_parity_route"] is False
    assert row["current_status"] == "common_origin_hypothesis_not_adapter"
    assert "no_source_backed_photon_gravity_coupling_relation" in row["blockers"]
    assert "ratio_not_clean_normalization_cancellation" in row["blockers"]


def test_priority_moves_engine_parity_to_gw_channel_first():
    result = diagnose_parity_route_split_frontier()

    assert result["priority_order"][0] == "gw_gravitational_birefringence"
    assert "gw_gravitational_birefringence" in result["engine_gravity_parity_routes"]
    assert "pta_chiral_sgwb" in result["engine_gravity_parity_routes"]
