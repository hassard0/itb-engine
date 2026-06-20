"""Tests for the v2.97 g8 secondary-axis targets."""

import pytest

from experiments.g8_secondary_axis_targets import (
    diagnose_g8_secondary_axis_targets,
)


def _tight_pair(result):
    return result["near_g8_pair_targets"][0]


def _axis(row, axis):
    return next(
        target
        for target in row["secondary_axes_ranked_by_tolerance"]
        if target["axis"] == axis
    )


def test_secondary_axis_targets_are_nonclaimable_without_joint_packet():
    result = diagnose_g8_secondary_axis_targets()

    assert result["version"] == "v2.97"
    assert result["route_status"] == (
        "secondary_axis_targets_defined_no_joint_packet"
    )
    assert result["claimable_discriminator_now"] is False
    assert result["external_joint_packet_present"] is False
    assert "joint_likelihood_and_covariance_missing" in result["claim_blockers"]


def test_tight_g8_pair_is_string_tree_vs_data_driven():
    result = diagnose_g8_secondary_axis_targets()
    row = _tight_pair(result)

    assert result["near_g8_pair_count"] == 1
    assert {row["framework_a"], row["framework_b"]} == {
        "discovered_data_driven",
        "string_tree_eft",
    }
    assert row["g8_separation"] == pytest.approx(0.004)
    assert (
        row["g8_required_total_sigma_for_2sigma_distinguishability"]
        == pytest.approx(0.002)
    )


def test_best_secondary_axis_for_tight_pair_is_g_r2_by_tolerance():
    result = diagnose_g8_secondary_axis_targets()
    row = _tight_pair(result)
    best = row["best_secondary_axis_by_tolerance"]

    assert best["axis"] == "g_R2"
    assert best["separation"] == pytest.approx(0.1258)
    assert (
        best["required_total_sigma_for_2sigma_distinguishability"]
        == pytest.approx(0.0629)
    )


def test_g_c_secondary_axis_is_source_provenance_explicit():
    result = diagnose_g8_secondary_axis_targets()
    row = _tight_pair(result)
    g_c = _axis(row, "g_C")

    assert g_c["is_weyl_g8_frontier_secondary_axis"] is True
    assert g_c["separation"] == pytest.approx(0.1016739130434782)
    assert (
        g_c["required_total_sigma_for_2sigma_distinguishability"]
        == pytest.approx(0.0508369565217391)
    )
    assert {g_c["provenance_a"], g_c["provenance_b"]} == {
        "native",
        "portrait_derived_from_g_R2",
    }


def test_secondary_axis_ranking_excludes_g8_and_keeps_positive_targets():
    result = diagnose_g8_secondary_axis_targets()

    for row in result["all_eligible_pair_targets"]:
        axes = row["secondary_axes_ranked_by_tolerance"]
        assert "g_8" not in {axis_row["axis"] for axis_row in axes}
        assert len(axes) == 7
        assert any(
            axis_row["required_total_sigma_for_2sigma_distinguishability"]
            for axis_row in axes
        )


def test_recommended_joint_target_carries_best_and_weyl_g8_options():
    result = diagnose_g8_secondary_axis_targets()
    target = result["recommended_joint_targets"][0]

    assert set(target["frameworks"]) == {
        "discovered_data_driven",
        "string_tree_eft",
    }
    assert target["best_secondary_axis_by_tolerance"]["axis"] == "g_R2"
    assert target["weyl_g8_frontier_secondary_axis"]["axis"] == "g_C"
