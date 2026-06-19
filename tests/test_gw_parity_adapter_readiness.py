"""Regression tests for v2.61 GW parity adapter readiness."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from gw_parity_adapter_readiness import (  # noqa: E402
    diagnose_gw_parity_adapter_readiness,
)


def test_public_source_material_exists_but_no_engine_adapter_is_ready():
    result = diagnose_gw_parity_adapter_readiness()

    assert result["target_axis"] == "g_R2_parity/g_R3_parity"
    assert result["candidate_count"] == 5
    assert result["source_side_likelihood_ready_count"] == 2
    assert result["source_side_likelihood_ready_routes"] == [
        "ng_gwtc3_kappa_at_100hz",
        "callister_sgwb_kappaD_kappaz",
    ]
    assert result["engine_adapter_ready_routes"] == []
    assert result["engine_adapter_ready_count"] == 0
    assert result["claimable_discriminator_now"] is False
    assert (
        result["route_status"]
        == "public_gw_likelihood_material_exists_engine_adapter_missing"
    )


def test_ng_release_is_source_ready_but_dimensionally_unmapped():
    result = diagnose_gw_parity_adapter_readiness()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["ng_gwtc3_kappa_at_100hz"]

    assert row["public_material"]["code"] is True
    assert row["public_material"]["data"] is True
    assert row["source_side_likelihood_ready"] is True
    assert row["engine_adapter_ready"] is False
    assert "kappa_Gpc^-1_at_100_Hz" in row["measured_parameters"]
    assert "missing_engine_axis_map" in row["adapter_blockers"]
    assert "missing_dimensionful_to_engine_normalization" in row["adapter_blockers"]
    assert "missing_frequency_normalization" in row["adapter_blockers"]


def test_callister_release_is_public_but_not_engine_axis_likelihood():
    result = diagnose_gw_parity_adapter_readiness()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["callister_sgwb_kappaD_kappaz"]

    assert row["public_material"]["source_likelihood_material_public"] is True
    assert row["source_side_likelihood_ready"] is True
    assert row["engine_adapter_ready"] is False
    assert row["measured_parameters"] == ["kappa_D", "kappa_z"]
    assert "missing_engine_axis_map" in row["adapter_blockers"]
    assert "missing_source_backed_operator_map" in row["adapter_blockers"]


def test_jenks_formalism_is_operator_language_not_measurement():
    result = diagnose_gw_parity_adapter_readiness()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["jenks_parameterized_parity_formalism"]

    assert row["source_backed_operator_map"] is True
    assert row["source_side_likelihood_ready"] is False
    assert row["engine_adapter_ready"] is False
    assert "missing_public_source_likelihood_material" in row["adapter_blockers"]
    assert "missing_published_numeric_constraint" in row["adapter_blockers"]


def test_engine_observable_is_target_basis_but_toy_normalized():
    result = diagnose_gw_parity_adapter_readiness()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["engine_gravitational_birefringence_observable"]

    assert row["maps_to_engine_axes"] is True
    assert row["adapter_role"] == "engine_target_basis_toy_normalization"
    assert row["engine_adapter_ready"] is False
    assert "missing_source_backed_operator_map" in row["adapter_blockers"]
    assert "missing_frequency_normalization" in row["adapter_blockers"]


def test_legacy_ligo_bound_is_not_promotable_by_this_audit():
    result = diagnose_gw_parity_adapter_readiness()

    assert "legacy toy constraint" in result["legacy_stack_warning"]
    assert result["can_build_nonpromoting_source_loader_now"] is True
    assert result["can_promote_engine_packet_now"] is False
    assert result["recommended_intermediate_basis"]["name"] == (
        "gw_parity_native_or_ppv_basis"
    )
    assert result["recommended_intermediate_basis"]["engine_projection_status"] == (
        "blocked_pending_source_backed_operator_normalization"
    )
    assert "native-parameter or PPV-basis source packet" in result["best_next_artifact"]
