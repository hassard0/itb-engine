"""Regression tests for v2.35 quintic SDC-bound scope audit."""

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from quintic_sdc_bound_audit import diagnose_quintic_sdc_bound_audit  # noqa: E402


def test_quintic_sdc_bound_audit_keeps_no_decisive_claims():
    result = diagnose_quintic_sdc_bound_audit()

    assert result["decisive_sdc_tests_now"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert "not an adjudication" in result["literature_guardrail"]["claim"]


def test_quintic_sdc_bound_audit_recovers_source_slope_interval():
    result = diagnose_quintic_sdc_bound_audit()
    slope = result["candidate"]["mass_exponent_alpha"]

    assert slope["mean"] == pytest.approx(0.453)
    assert slope["one_sigma"] == pytest.approx(0.034 / 2.0 / 1.96)
    assert slope["ci95_lower"] == pytest.approx(0.436)
    assert slope["ci95_upper"] == pytest.approx(0.470)


def test_quintic_sdc_bound_audit_separates_legitimate_and_scope_mismatch_bounds():
    result = diagnose_quintic_sdc_bound_audit()
    rows = {row["label"]: row for row in result["bounds"]}

    assert rows["ashmore_ruehle_finite_range_sqrt6_reference"][
        "comparison_status"
    ] == "candidate_95ci_above_bound"
    assert rows["ashmore_ruehle_finite_range_sqrt6_reference"][
        "adjudication"
    ] == "legitimate_finite_range_context"
    assert rows["etheredge_d4_asymptotic_lightest_tower_bound"][
        "comparison_status"
    ] == "candidate_95ci_below_bound"
    assert rows["etheredge_d4_asymptotic_lightest_tower_bound"][
        "adjudication"
    ] == "not_adjudicable_scope_mismatch"
    assert result["bound_status_counts"]["not_adjudicable_scope_mismatch"] == 1
