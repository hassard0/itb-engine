"""Tests for the v2.96 g8 measurement sensitivity targets."""

import pytest

from experiments.g8_measurement_sensitivity_targets import (
    diagnose_g8_measurement_sensitivity_targets,
)


def test_sensitivity_targets_are_nonclaimable_without_external_packet():
    result = diagnose_g8_measurement_sensitivity_targets()

    assert result["version"] == "v2.96"
    assert result["route_status"] == (
        "g8_sensitivity_targets_defined_no_external_packet"
    )
    assert result["claimable_discriminator_now"] is False
    assert result["external_packet_present"] is False
    assert "real_engine_normalized_g8_packet_missing" in result["claim_blockers"]


def test_eligible_filter_removes_out_of_scope_or_reference_excluded_frameworks():
    result = diagnose_g8_measurement_sensitivity_targets()

    assert result["registered_framework_count"] == 13
    assert result["eligible_framework_count"] == 8
    excluded = {row["framework"] for row in result["ineligible_frameworks"]}

    assert excluded == {
        "causal_set",
        "emergent_gravity",
        "group_field_theory",
        "horava_lifshitz",
        "lqg_induced",
    }


def test_tightest_eligible_pair_sets_global_precision_floor():
    result = diagnose_g8_measurement_sensitivity_targets()

    pair = result["tightest_eligible_pair"]
    assert {pair["framework_a"], pair["framework_b"]} == {
        "discovered_data_driven",
        "string_tree_eft",
    }
    assert pair["separation"] == pytest.approx(0.004)
    assert (
        pair["required_total_sigma_for_2sigma_distinguishability"]
        == pytest.approx(0.002)
    )
    assert (
        result["minimum_total_sigma_to_resolve_all_eligible_g8_targets_at_2sigma"]
        == pytest.approx(0.002)
    )


def test_high_g8_has_widest_eligible_single_axis_target_window():
    result = diagnose_g8_measurement_sensitivity_targets()

    target = result["widest_eligible_single_axis_target"]
    assert target["frameworks"] == ["discovered_high_g8"]
    assert target["nearest_distinct_cluster"]["frameworks"] == [
        "discovered_data_driven"
    ]
    assert target["nearest_distinct_gap"] == pytest.approx(0.148)
    assert (
        target["required_total_sigma_to_exclude_nearest_distinct_at_2sigma"]
        == pytest.approx(0.074)
    )


def test_all_registered_exact_g8_degeneracies_are_reported():
    result = diagnose_g8_measurement_sensitivity_targets()

    clusters = {
        cluster["g8"]: set(cluster["frameworks"])
        for cluster in result["all_registered_exact_degenerate_clusters"]
    }

    assert clusters[0.3] == {"asymptotic_safety", "causal_set"}
    assert clusters[0.4] == {
        "group_field_theory",
        "lqg_induced",
        "string_tree_eft",
    }


def test_eligible_cluster_targets_have_no_exact_degeneracy():
    result = diagnose_g8_measurement_sensitivity_targets()

    assert result["eligible_exact_degenerate_clusters"] == []
    assert all(
        target["target_status"]
        == "single_axis_g8_target_viable_if_external_packet_precision_met"
        for target in result["eligible_cluster_targets"]
    )
