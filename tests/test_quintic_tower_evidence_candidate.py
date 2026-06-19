"""Regression tests for v2.34 quintic tower evidence candidate."""

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from quintic_tower_evidence_candidate import (  # noqa: E402
    diagnose_quintic_tower_evidence_candidate,
)


def test_quintic_candidate_is_schema_ready_but_not_claimable():
    result = diagnose_quintic_tower_evidence_candidate()
    candidate = result["candidates"][0]

    assert result["schema_ready_candidates"] == ["ashmore_ruehle_quintic_kk"]
    assert result["framework_claim_ready_candidates"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert candidate["evidence_validation"]["ready_for_framework_claim"] is True
    assert candidate["candidate_scope"]["framework_claim_ready"] is False
    assert "single_compactification_not_full_string_tree_eft_catalogue" in (
        candidate["candidate_scope"]["blockers"]
    )


def test_quintic_candidate_maps_laplacian_fit_to_mass_exponent():
    result = diagnose_quintic_tower_evidence_candidate()
    spectrum = result["candidates"][0]["evidence"]["spectrum"]
    exponent = spectrum["metadata"]["mass_exponent"]

    assert exponent["laplacian_fit_exponent"] == pytest.approx(0.906)
    assert spectrum["phi_tower_mean"] == pytest.approx(0.453)
    assert spectrum["phi_tower_sigma"] == pytest.approx(0.034 / 2.0 / 1.96)
    assert spectrum["tower_mass_gap"] == pytest.approx(0.635718)


def test_quintic_candidate_is_tower_allowed_not_excluding():
    result = diagnose_quintic_tower_evidence_candidate()
    candidate = result["candidates"][0]

    assert candidate["framework_tower_verdict"] == "tower_allowed_by_predictive_spectrum"
    assert candidate["tower_claimable_by_math"] is False
    assert candidate["two_sigma_phi_interval"][1] < candidate["critical_phi_tower"]
    assert "not a framework-level" in result["literature_guardrail"]["claim"]
