"""Tests for tower evidence promotion guardrails."""

from itb.tower import (
    TowerEvidence,
    classify_tower_source_scope,
    evaluate_generic_framework_claim_guard,
    evaluate_tower_promotion_guard,
    kk_radius_tower_spectrum,
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
        "missing_asymptotic_range_scope",
        "missing_framework_owned_displacement",
        "missing_framework_owned_endpoint",
    ]


def test_generic_framework_claim_guard_blocks_promotion_ready_scope_gap():
    result = evaluate_generic_framework_claim_guard(
        _evidence(),
        tower_claimable_by_math=True,
    )

    assert result["promotion_guard"]["ready_for_promotion"] is True
    assert result["ready_for_generic_framework_claim"] is False
    assert result["ready_for_generic_framework_claim"] == (
        result["evidence_ready"]
        and result["tower_claimable_by_math"]
        and not result["positive_control_matches"]
        and result["source_scope"]["generic_framework_claim_ready"]
    )
    assert result["blockers"] == [
        "missing_asymptotic_range_scope",
        "missing_framework_owned_displacement",
        "missing_framework_owned_endpoint",
    ]


def test_generic_framework_claim_guard_allows_owned_asymptotic_fixture():
    evidence = _evidence({
        "range_scope": "asymptotic",
        "native_framework_endpoint": "unit-test endpoint",
        "native_framework_displacement": "unit-test displacement",
    })
    result = evaluate_generic_framework_claim_guard(
        evidence,
        tower_claimable_by_math=True,
    )

    assert result["ready_for_generic_framework_claim"] is True
    assert result["ready_for_generic_framework_claim"] == (
        result["evidence_ready"]
        and result["tower_claimable_by_math"]
        and not result["positive_control_matches"]
        and result["source_scope"]["generic_framework_claim_ready"]
    )
    assert result["blockers"] == []
    assert result["source_scope"]["range_scope"] == "asymptotic"


def test_generic_framework_claim_guard_rejects_false_ownership_markers():
    evidence = _evidence({
        "range_scope": "asymptotic",
        "native_framework_endpoint": False,
        "native_framework_displacement": "",
    })
    result = evaluate_generic_framework_claim_guard(
        evidence,
        tower_claimable_by_math=True,
    )

    assert result["ready_for_generic_framework_claim"] is False
    assert result["blockers"] == [
        "missing_framework_owned_displacement",
        "missing_framework_owned_endpoint",
    ]
