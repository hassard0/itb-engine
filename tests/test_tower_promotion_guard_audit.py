"""Regression tests for v2.41 tower promotion guard audit."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_promotion_guard_audit import diagnose_tower_promotion_guard_audit  # noqa: E402


def test_tower_promotion_guard_blocks_all_positive_controls():
    result = diagnose_tower_promotion_guard_audit()

    assert result["registered_framework_count"] == 13
    assert result["candidate_count"] == 8
    assert len(result["positive_control_promotion_blocked"]) == 7
    assert result["status_counts"]["promotion_blocked_known_positive_control"] == 7
    assert result["tower_discriminator_candidates_now"] == []
    assert result["claimable_framework_exclusions_now"] == []


def test_tower_promotion_guard_allows_non_positive_control_fixture():
    result = diagnose_tower_promotion_guard_audit()

    assert result["promotion_guard_ready_non_positive_control_fixtures"] == [
        "non_positive_control_excluding_fixture"
    ]
    fixture = next(
        row for row in result["candidates"]
        if row["label"] == "non_positive_control_excluding_fixture"
    )
    assert fixture["promotion_guard"]["ready_for_promotion"] is True
    assert fixture["promotion_guard"]["blockers"] == []
    assert fixture["claimable_now"] is False


def test_tower_promotion_guard_audit_guardrail_text():
    result = diagnose_tower_promotion_guard_audit()

    assert "synthetic non-positive fixture" in result["literature_guardrail"]["claim"]
    assert "keep tower math as a diagnostic" in result["interpretation"]
