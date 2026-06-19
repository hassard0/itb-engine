"""Regression tests for v2.46 native tower-ownership frontier audit."""

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from native_tower_ownership_frontier import (  # noqa: E402
    diagnose_native_tower_ownership_frontier,
)


def test_native_tower_ownership_frontier_counts_live_blockers():
    result = diagnose_native_tower_ownership_frontier()

    assert result["registered_framework_count"] == 13
    assert result["n_reference_feasible_in_scope_frameworks"] == 8
    assert result["native_tower_evidence_frameworks"] == []
    assert result["native_ownership_ready_frameworks"] == []
    assert result["generic_framework_claim_ready_candidates"] == []
    assert result["tower_discriminator_claim_ready"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["target_blocker_counts"]["missing_native_tower_spectrum"] == 8
    assert result["target_blocker_counts"]["missing_native_tower_evidence"] == 8


def test_native_tower_ownership_frontier_pins_pass_condition():
    result = diagnose_native_tower_ownership_frontier()

    assert result["critical_phi_tower"] == pytest.approx(0.7433019116911739)
    assert result["pass_condition"] == {
        "target_reference_feasible_in_scope": True,
        "native_tower_evidence_present": True,
        "native_ownership_ready": True,
        "generic_claim_guard_ready": True,
        "two_sigma_lower_bound_required": (
            "phi_tower_mean - 2 * phi_tower_sigma > critical_phi_tower"
        ),
    }


def test_native_tower_ownership_frontier_marks_string_tree_gap():
    result = diagnose_native_tower_ownership_frontier()
    row = result["frameworks"]["string_tree_eft"]

    assert row["target_reference_feasible_in_scope"] is True
    assert row["native_tower_spectrum_present"] is False
    assert row["native_tower_evidence_present"] is False
    assert row["native_ownership_ready"] is False
    assert row["generic_claim_guard_ready"] is False
    assert row["blockers"] == [
        "missing_native_tower_evidence",
        "missing_native_tower_spectrum",
    ]
    assert "native TowerSpectrum and TowerEvidence adapters" in (
        result["interpretation"]
    )
