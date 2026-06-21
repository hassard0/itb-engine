"""Tests for the v2.191 ParSpec qEFT source-asset audit."""

import json
from pathlib import Path

from experiments.r4_parspec_engine_axis_map_contract import (
    current_v2188_parspec_axis_map_slot,
    evaluate_parspec_engine_axis_map_packet,
)
from experiments.r4_parspec_qeft_source_asset_audit import (
    PARSPEC_SOURCE_PACKAGE_SHA256,
    QEFT_CDF_FIGURE_SHA256,
    QEFT_POSTERIORS_FIGURE_SHA256,
    QEFT_POWER,
    QEFT_TEX_SHA256,
    diagnose_r4_parspec_qeft_source_asset_audit,
    parspec_qeft_source_package_assets,
    qeft_parspec_source_equation_facts,
    qeft_source_axis_power_policy,
    v2191_asset_enriched_parspec_axis_map_slot,
)


def test_source_package_audit_preserves_qeft_assets_without_likelihood():
    assets = parspec_qeft_source_package_assets()
    audited = {item["path"]: item for item in assets["audited_assets"]}

    assert assets["source_package_tarball"]["sha256"] == (
        PARSPEC_SOURCE_PACKAGE_SHA256
    )
    assert audited["paper_alt_theory_bounds.tex"]["sha256"] == QEFT_TEX_SHA256
    assert audited["qeft_posteriors_combined.pdf"]["sha256"] == (
        QEFT_POSTERIORS_FIGURE_SHA256
    )
    assert audited["qeft_cdf_varying_threshold.pdf"]["sha256"] == (
        QEFT_CDF_FIGURE_SHA256
    )
    assert assets["detected_machine_readable_likelihood_assets"] == []
    assert assets["machine_readable_likelihood_ready"] is False


def test_qeft_source_equation_facts_resolve_power_policy():
    facts = qeft_parspec_source_equation_facts()
    policy = qeft_source_axis_power_policy()

    assert facts["parspec_gamma_relation"]["qeft_power"] == QEFT_POWER
    assert facts["qnm_deformation_coefficients"]["nmax_0"] == {
        "delta_omega_qeft_0": -0.2114,
        "delta_tau_qeft_0": -0.6070,
    }
    assert facts["qnm_deformation_coefficients"]["nmax_1"] == {
        "delta_omega_qeft_1": -1.5263,
        "delta_tau_qeft_1": 171.35,
    }
    assert facts["event_bounds_90_credible_km"]["combined"] == 51.3
    assert policy["length_power"] == 6
    assert policy["length_axis"] == "ell_qEFT_km"
    assert policy["status"] == "source_backed"


def test_v2191_asset_packet_removes_power_blocker_but_keeps_axis_blockers():
    baseline = evaluate_parspec_engine_axis_map_packet(
        current_v2188_parspec_axis_map_slot()
    )
    enriched = evaluate_parspec_engine_axis_map_packet(
        v2191_asset_enriched_parspec_axis_map_slot()
    )

    assert "source_axis_power_policy_missing" in baseline["map_blockers"]
    assert "source_axis_power_policy_missing" not in enriched["map_blockers"]
    assert enriched["axis_map_ready"] is False
    assert enriched["map_blockers"] == [
        "axis_normalization_missing",
        "engine_axis_orientation_missing",
        "operator_basis_map_missing",
    ]


def test_v2191_still_blocks_likelihood_event_alignment_and_claims():
    result = diagnose_r4_parspec_qeft_source_asset_audit()
    enriched = result["v2191_asset_enriched_evaluation"]

    assert result["route_status"] == (
        "parspec_qeft_source_asset_audit_ready_nonclaiming"
    )
    assert enriched["likelihood_attachment_ready"] is False
    assert "public_parspec_qeft_likelihood_or_posterior_samples_missing" in (
        enriched["attachment_blockers"]
    )
    assert "event_set_mismatch_gw170608_vs_gw150914_gw200129" in (
        enriched["attachment_blockers"]
    )
    assert result["source_asset_readiness"][
        "machine_readable_likelihood_ready"
    ] is False
    assert result["ready_for_framework_claim"] is False


def test_v2191_diagnosis_splits_v2190_blockers_without_claim():
    result = diagnose_r4_parspec_qeft_source_asset_audit()

    assert result["version"] == "v2.191"
    assert result["source_asset_readiness"][
        "source_axis_power_policy_ready"
    ] is True
    assert result["source_asset_readiness"][
        "engine_bresciani_axis_orientation_ready"
    ] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["selected_next_build_action"] == (
        "derive_qeft_to_bresciani_engine_axis_map_or_acquire_public_likelihood_grid"
    )


def test_committed_artifact_records_source_asset_audit():
    path = Path(
        "experiments/results/v2.191/"
        "r4_parspec_qeft_source_asset_audit.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.191"
    assert result["source_package_assets"]["source_package_tarball"][
        "sha256"
    ] == PARSPEC_SOURCE_PACKAGE_SHA256
    assert result["source_equation_facts"]["parspec_gamma_relation"][
        "qeft_power"
    ] == 6
    assert result["ready_for_framework_claim"] is False
