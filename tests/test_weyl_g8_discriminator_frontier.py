"""Regression tests for v2.50 Weyl/g8 discriminator frontier audit."""

import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from weyl_g8_discriminator_frontier import (  # noqa: E402
    CLAIM_BLOCKERS,
    COEFFS,
    _cut_row,
    diagnose_weyl_g8_discriminator_frontier,
)


@pytest.fixture(scope="module")
def frontier_result():
    return diagnose_weyl_g8_discriminator_frontier(
        30_000,
        seed=25050,
        bootstrap_count=8,
        robustness_sample_count=20_000,
    )


def test_weyl_g8_frontier_confirms_top_single_axes(frontier_result):
    result = frontier_result

    assert result["island_survivors"] >= 100
    assert result["geometry_status"] == "weyl_g8_frontier_confirmed"
    assert result["top_single_directions"] == ["single:g_C", "single:g_8"]
    assert result["directions_ranked_by_extent"][0]["direction"] == "PCA:PC1"
    assert result["directions_ranked_by_extent"][0]["dominant_coefficient"] == "g_C"
    pc2 = next(
        row for row in result["directions_ranked_by_extent"]
        if row["direction"] == "PCA:PC2"
    )
    assert pc2["dominant_coefficient"] == "g_8"


def test_weyl_g8_frontier_is_alive_but_not_claimable(frontier_result):
    result = frontier_result
    assert result["route_status"] == "frontier_alive_but_not_claimable"
    assert result["claimable_discriminator_now"] is False
    assert result["claim_blockers"] == list(CLAIM_BLOCKERS)
    assert "not a discovery or exclusion claim" in result["honest"]


def test_favored_safe_cut_preserves_data_driven_boundary(frontier_result):
    for row in frontier_result["directions_ranked_by_extent"]:
        cut = row["favored_safe_cut"]
        assert cut["cut"] == "tangent_discovered_data_driven"
        assert "discovered_data_driven" not in cut["frameworks_excluded"]


def test_audit_configuration_and_framework_provenance_are_explicit(frontier_result):
    config = frontier_result["audit_configuration"]
    assert config["coefficient_order"] == list(COEFFS)
    assert config["stack_config"] == {
        "bnossw_mean": "geometric",
        "rfc_form": "convex_hull",
    }
    assert config["framework_feasibility_basis"] == "full_stack"

    frameworks = {row["framework"]: row for row in frontier_result["frameworks"]}
    assert frameworks["discovered_data_driven"]["g_C_source"] == "native"
    assert frameworks["string_tree_eft"]["g_C_source"] == "portrait_derived_from_g_R2"
    assert frameworks["emergent_gravity"]["engine_scope"]["in_scope"] is False
    assert frameworks["horava_lifshitz"]["preexisting_full_stack_excluded"] is True


def test_seed_robustness_matrix_stays_above_acceptance_bar(frontier_result):
    robustness = frontier_result["robustness"]
    assert robustness["passes_minimum_robustness"] is True
    assert robustness["pass_fraction"] >= 0.8
    assert len(robustness["rows"]) == 5
    for row in robustness["rows"]:
        assert row["top_single_directions"] == ["single:g_C", "single:g_8"]


def test_cut_row_reports_framework_exclusion_and_retained_fraction():
    island_projection = np.array([0.1, 0.2, 0.3, 0.4])
    direction = np.eye(len(COEFFS))[COEFFS.index("g_C")]
    frameworks = [
        {
            "framework": "low",
            "feasible_under_current_stack": True,
            "coefficients": {key: 0.0 for key in COEFFS},
        },
        {
            "framework": "high",
            "feasible_under_current_stack": True,
            "coefficients": {key: 0.0 for key in COEFFS},
        },
    ]
    frameworks[1]["coefficients"]["g_C"] = 0.5

    row = _cut_row(
        label="q50",
        threshold=0.25,
        projections=island_projection,
        direction=direction,
        frameworks=frameworks,
    )

    assert row["island_removed_fraction"] == pytest.approx(0.5)
    assert row["island_retained_fraction"] == pytest.approx(0.5)
    assert row["frameworks_excluded"] == ["high"]
    assert row["feasible_frameworks_excluded"] == ["high"]
    assert row["preexisting_excluded_frameworks"] == []
