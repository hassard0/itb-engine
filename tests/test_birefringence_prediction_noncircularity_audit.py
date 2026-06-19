"""Regression tests for v2.57 non-circular beta prediction audit."""

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from birefringence_prediction_noncircularity_audit import (  # noqa: E402
    diagnose_birefringence_prediction_noncircularity_audit,
)


def _rows_by_framework():
    result = diagnose_birefringence_prediction_noncircularity_audit()
    return result, {row["framework"]: row for row in result["rows"]}


def test_noncircularity_audit_finds_no_claim_ready_framework():
    result, _ = _rows_by_framework()

    assert result["framework_count"] == 13
    assert result["claim_ready_frameworks"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "no_non_circular_source_backed_beta_prediction"


def test_data_driven_framework_matches_by_reusing_beta_input():
    result, rows = _rows_by_framework()
    row = rows["discovered_data_driven"]

    assert row["uses_beta_input"] is True
    assert row["independent_of_beta_input"] is False
    assert row["matches_beta_hint_2sigma_under_toy_map"] is True
    assert row["beta_pred_deg_toy_map"] == pytest.approx(0.3186, abs=1e-4)
    assert "prediction_reuses_beta_input" in row["blockers"]
    assert "discovered_data_driven" in result["data_driven_toy_map_matches_2sigma"]


def test_independent_beta_matches_are_not_claim_ready_without_source_adapter():
    result, rows = _rows_by_framework()

    assert {
        "group_field_theory",
        "horava_lifshitz",
        "lqg_induced",
    } <= set(result["independent_toy_map_matches_2sigma"])
    for framework in result["independent_toy_map_matches_2sigma"]:
        row = rows[framework]
        assert row["independent_of_beta_input"] is True
        assert row["source_backed_beta_adapter"] is False
        assert row["claim_ready"] is False
        assert "missing_source_backed_beta_adapter" in row["blockers"]


def test_parity_even_catalogued_frameworks_do_not_match_beta_hint():
    _, rows = _rows_by_framework()

    for framework in {
        "pure_gr",
        "string_tree_eft",
        "asymptotic_safety",
        "cdt",
        "causal_set",
        "emergent_gravity",
    }:
        row = rows[framework]
        assert row["beta_pred_deg_toy_map"] == pytest.approx(0.0)
        assert row["matches_beta_hint_2sigma_under_toy_map"] is False
        assert "beta_prediction_not_within_hint_band" in row["blockers"]


def test_all_frameworks_are_blocked_by_missing_source_backed_beta_adapter():
    result, rows = _rows_by_framework()

    assert result["blocker_counts"]["missing_source_backed_beta_adapter"] == 13
    assert all(row["source_backed_beta_adapter"] is False for row in rows.values())
    assert all(row["claim_ready"] is False for row in rows.values())
