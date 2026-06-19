"""Regression tests for v2.26 tower literature seed audit."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_literature_seed_audit import diagnose_tower_literature_seed_audit  # noqa: E402


def test_string_sdc_seed_is_recorded_but_not_actionable():
    result = diagnose_tower_literature_seed_audit()
    seed = next(
        row for row in result["seeds"]
        if row["seed_id"] == "ooguri_vafa_distance_conjecture"
    )

    assert seed["framework"] == "string_tree_eft"
    assert seed["url"] == "https://arxiv.org/abs/hep-th/0605264"
    assert seed["actionable_as_tower_spectrum"] is False
    assert "phi_tower_mean" in seed["missing_actionable_fields"]
    assert "phi_tower_sigma" in seed["missing_actionable_fields"]
    assert "normalization" in seed["missing_actionable_fields"]


def test_literature_seed_audit_guardrail_and_threshold_context():
    result = diagnose_tower_literature_seed_audit()

    assert result["candidate_seed_count"] == 2
    assert result["actionable_seed_count"] == 0
    assert result["claimable_framework_exclusions_now"] == []
    assert "qualitative tower relation is not an actionable" in (
        result["literature_guardrail"]["claim"]
    )
    for seed in result["seeds"]:
        context = seed["threshold_context_sigma_0.05"]
        assert context["claimable_exclusion_requires_phi_mean_gt"] > (
            context["claimable_allowance_requires_phi_mean_lte"]
        )
