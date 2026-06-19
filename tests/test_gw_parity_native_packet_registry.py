"""Regression tests for v2.62 native GW parity packet registry."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from gw_parity_native_packet_registry import (  # noqa: E402
    diagnose_gw_parity_native_packet_registry,
)


def test_native_registry_has_two_source_ready_nonpromoting_packets():
    result = diagnose_gw_parity_native_packet_registry()

    assert result["registry_packet_count"] == 2
    assert result["native_packet_ready_routes"] == [
        "ng_gwtc3_kappa_at_100hz",
        "callister_sgwb_kappaD_kappaz",
    ]
    assert result["native_packet_ready_count"] == 2
    assert result["engine_projection_ready_routes"] == []
    assert result["engine_projection_ready_count"] == 0
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "native_gw_parity_packets_ready_projection_blocked"


def test_ng_packet_preserves_native_kappa_values():
    result = diagnose_gw_parity_native_packet_registry()
    rows = {row["packet"]["label"]: row for row in result["rows"]}
    row = rows["ng_gwtc3_kappa_at_100hz"]
    params = row["packet"]["parameters"]

    assert row["validation"]["native_packet_ready"] is True
    assert row["validation"]["engine_projection_ready"] is False
    assert row["registry_status"] == "native_source_ready_nonpromoting"
    assert row["packet"]["parameter_basis"] == "ng_kappa_at_100hz"
    assert params["kappa_Gpc_inv"] == -0.019
    assert params["kappa_plus_90"] == 0.038
    assert params["kappa_minus_90"] == 0.029
    assert params["f_ref_hz"] == 100.0


def test_callister_packet_preserves_native_sgwb_basis():
    result = diagnose_gw_parity_native_packet_registry()
    rows = {row["packet"]["label"]: row for row in result["rows"]}
    row = rows["callister_sgwb_kappaD_kappaz"]
    params = row["packet"]["parameters"]

    assert row["validation"]["native_packet_ready"] is True
    assert row["validation"]["engine_projection_ready"] is False
    assert row["packet"]["parameter_basis"] == "sgwb_kappaD_kappaz"
    assert params["kappa_D_scale"] == 0.1
    assert params["kappa_z_scale"] == 0.1
    assert params["constraint_kind"] == "order_of_magnitude_joint_bound"


def test_projection_blockers_remain_universal_for_native_packets():
    result = diagnose_gw_parity_native_packet_registry()
    counts = result["projection_blocker_counts"]

    assert counts["missing_source_backed_operator_map"] == 2
    assert counts["missing_frequency_normalization"] == 2
    assert counts["missing_dimensionful_to_engine_normalization"] == 2
    assert counts["missing_framework_exclusion_math"] == 2
    assert counts["engine_projection_not_ready"] == 2


def test_next_artifact_is_shared_ppv_basis_not_engine_claim():
    result = diagnose_gw_parity_native_packet_registry()

    assert "shared source-backed propagation basis" in result["best_next_artifact"]
    assert result["claimable_discriminator_now"] is False
