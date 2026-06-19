"""Regression tests for v2.38 analytic KK tower benchmark scan."""

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from analytic_kk_tower_benchmark import (  # noqa: E402
    diagnose_analytic_kk_tower_benchmark,
    kk_tower_vector_norm,
)


def test_analytic_kk_formula_matches_known_d4_values():
    assert kk_tower_vector_norm(4, 1) == pytest.approx((3.0 / 2.0) ** 0.5)
    assert kk_tower_vector_norm(4, 2) == pytest.approx(1.0)
    assert kk_tower_vector_norm(4, 6) == pytest.approx((8.0 / 12.0) ** 0.5)


def test_analytic_kk_benchmark_all_d4_candidates_cross_threshold():
    result = diagnose_analytic_kk_tower_benchmark()

    assert result["candidate_count"] == 6
    assert len(result["benchmark_excluding_candidates"]) == 6
    assert len(result["registration_ready_if_scoped_candidates"]) == 6
    assert result["claimable_framework_exclusions_now"] == []
    assert result["critical_phi_tower"] == pytest.approx(0.7433019116911739)


def test_analytic_kk_benchmark_keeps_scope_guardrail():
    result = diagnose_analytic_kk_tower_benchmark()
    p6 = result["candidates"][-1]

    assert p6["label"] == "d4_p6_kk_vector"
    assert p6["lambda_kk"] > result["critical_phi_tower"]
    assert p6["delta_moduli_required_for_exclusion"] < 1.0
    assert p6["claimable_now"] is False
    assert "analytic_tower_vector_not_registered_framework_evidence" in p6[
        "scope_blockers"
    ]
    assert "not current framework exclusions" in result["literature_guardrail"]["claim"]
