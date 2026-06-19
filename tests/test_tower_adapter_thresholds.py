"""Regression tests for v2.25 tower-adapter thresholds."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_adapter_thresholds import diagnose_tower_adapter_thresholds  # noqa: E402


def test_adapter_thresholds_quantify_two_sigma_margins():
    result = diagnose_tower_adapter_thresholds(sigma_values=[0.0, 0.05])
    critical_phi = result["critical_phi_tower"]
    critical_mass = result["critical_tower_mass"]
    row = result["frameworks"]["string_tree_eft"]
    threshold = next(
        item for item in row["sigma_thresholds"]
        if item["phi_tower_sigma"] == 0.05
    )

    assert threshold["claimable_exclusion_requires_phi_mean_gt"] == critical_phi + 0.10
    assert threshold["claimable_allowance_requires_phi_mean_lte"] == critical_phi - 0.10
    assert threshold["claimable_exclusion_requires_mass_gap_mean_lt"] < critical_mass
    assert threshold["claimable_allowance_requires_mass_gap_mean_gte"] > critical_mass


def test_adapter_thresholds_do_not_create_claims_without_native_spectra():
    result = diagnose_tower_adapter_thresholds(sigma_values=[0.0])

    assert result["claimable_framework_exclusions_now"] == []
    assert "string_tree_eft" in result["frameworks_missing_native_tower_adapter"]
    assert result["frameworks"]["string_tree_eft"]["current_claim_status"] == (
        "blocked_missing_tower_spectrum"
    )
    assert "future adapter thresholds" in result["literature_guardrail"]["claim"]
