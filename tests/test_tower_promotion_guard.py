"""Tests for tower evidence promotion guardrails."""

from itb.tower import (
    TowerEvidence,
    kk_radius_tower_spectrum,
    classify_tower_source_scope,
    evaluate_tower_promotion_guard,
    tower_positive_control_matches,
)


def _evidence(metadata=None):
    spectrum = kk_radius_tower_spectrum(
        tower_family="kk_fixture",
        radius_ratio_mean=2.6,
        log_radius_sigma=0.04,
        normalization="unit-test radius normalization",
        source="unit-test source",
        metadata=metadata,
    )
    return TowerEvidence(
        framework="string_tree_eft",
        spectrum=spectrum,
        adapter_kind="kk_radius",
        source_url="https://arxiv.org/abs/1812.07548",
        source_type="primary_literature",
        derivation_kind="diagnostic_fixture",
        uncertainty_kind="log_radius_one_sigma",
        normalization_reference="R/R0 diagnostic normalization",
        metadata=metadata or {},
    )


def test_promotion_guard_allows_ready_excluding_non_positive_control():
    result = evaluate_tower_promotion_guard(
        _evidence(),
        tower_claimable_by_math=True,
    )

    assert result["ready_for_promotion"] is True
    assert result["blockers"] == []
    assert result["positive_control_matches"] == []


def test_promotion_guard_blocks_known_positive_control_family():
    evidence = _evidence({
        "source_family": "analytic_kk_decompactification_vector",
        "known_qg_positive_control": True,
    })
    result = evaluate_tower_promotion_guard(
        evidence,
        tower_claimable_by_math=True,
    )

    assert result["ready_for_promotion"] is False
    assert result["blockers"] == ["known_qg_positive_control_family"]
    assert "analytic_kk_decompactification_vector" in (
        result["positive_control_matches"]
    )
    assert result["source_scope"]["range_scope"] == "asymptotic"
    assert "known_qg_positive_control_family" in (
        result["source_scope"]["scope_blockers"]
    )
    assert "known_qg_positive_control" in tower_positive_control_matches(evidence)


def test_promotion_guard_blocks_non_excluding_math():
    result = evaluate_tower_promotion_guard(
        _evidence(),
        tower_claimable_by_math=False,
    )

    assert result["ready_for_promotion"] is False
    assert result["blockers"] == ["tower_math_not_excluding"]


def test_source_scope_classifier_requires_framework_owned_endpoint_and_displacement():
    result = classify_tower_source_scope(_evidence())

    assert result["generic_framework_claim_ready"] is False
    assert result["range_scope"] == "unspecified"
    assert result["compactification_scope"] == "unspecified"
    assert result["scope_blockers"] == [
        "missing_framework_owned_displacement",
        "missing_framework_owned_endpoint",
    ]
