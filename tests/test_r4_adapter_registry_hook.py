"""Tests for the v2.149 non-promoting R4 adapter registry hook."""

from copy import deepcopy

from experiments.r4_adapter_registry_hook import (
    diagnose_r4_adapter_registry_hook,
    evaluate_r4_adapter_registry_entry,
    get_r4_adapter_registry_entry,
    r4_adapter_registry_entries,
)


def test_registry_exposes_one_internal_string_r4_adapter():
    entries = r4_adapter_registry_entries()

    assert len(entries) == 1
    entry = entries[0]
    assert entry["adapter_id"] == "string_tree_eft_r4_shape_policy_unit_v1"
    assert entry["framework"] == "string_tree_eft"
    assert entry["axis_family"] == "gravity_R4_Riemann4"
    assert entry["registration_scope"] == "internal_projection_algebra"
    assert entry["claim_path_enabled"] is False
    assert entry["framework_registry_mutation"] is False


def test_registry_entry_is_internal_ready_but_claim_blocked():
    entry = r4_adapter_registry_entries()[0]
    result = evaluate_r4_adapter_registry_entry(entry)

    assert result["adapter_exposed_for_internal_use"] is True
    assert result["policy_scope_ready"] is True
    assert result["base_projection_ready"] is True
    assert result["strict_source_projection_ready"] is True
    assert result["claim_promotion_allowed"] is False
    assert result["claimable_framework_exclusion_now"] is False
    assert result["guard_ready_for_framework_claim"] is False
    assert result["exposure_blockers"] == []
    assert "registry_claim_path_disabled" in result["claim_blockers"]
    assert "measurement_likelihood_missing_or_incomplete" in result["claim_blockers"]


def test_registry_lookup_finds_string_tree_r4_adapter_only():
    entry = get_r4_adapter_registry_entry(
        framework="string_tree_eft",
        axis_family="gravity_R4_Riemann4",
    )
    missing = get_r4_adapter_registry_entry(
        framework="pure_gr",
        axis_family="gravity_R4_Riemann4",
    )

    assert entry is not None
    assert entry["adapter_id"] == "string_tree_eft_r4_shape_policy_unit_v1"
    assert missing is None


def test_registry_blocks_accidental_claim_path_enablement():
    entry = deepcopy(r4_adapter_registry_entries()[0])
    entry["claim_path_enabled"] = True
    entry["measurement_likelihood_attached"] = True

    result = evaluate_r4_adapter_registry_entry(entry)

    assert result["adapter_exposed_for_internal_use"] is False
    assert "claim_path_not_disabled" in result["exposure_blockers"]
    assert "measurement_likelihood_must_not_be_attached" in (
        result["exposure_blockers"]
    )
    assert result["claimable_framework_exclusion_now"] is False


def test_registry_blocks_live_framework_registry_mutation():
    entry = deepcopy(r4_adapter_registry_entries()[0])
    entry["framework_registry_mutation"] = True

    result = evaluate_r4_adapter_registry_entry(entry)

    assert result["adapter_exposed_for_internal_use"] is False
    assert "framework_registry_mutation_not_allowed" in result["exposure_blockers"]


def test_diagnosis_records_nonpromoting_registry_hook():
    result = diagnose_r4_adapter_registry_hook()

    assert result["version"] == "v2.149"
    assert result["registry_entry_count"] == 1
    assert result["internal_projection_ready_adapters"] == [
        "string_tree_eft_r4_shape_policy_unit_v1"
    ]
    assert result["claim_promotion_ready_adapters"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["framework_registry_mutated"] is False
    assert result["lookup_control_found"] is True
    assert result["route_status"] == "r4_adapter_registry_hook_ready_nonpromoting"
    assert result["selected_next_build_action"] == (
        "wire_r4_registry_hook_into_projection_query_surface"
    )
