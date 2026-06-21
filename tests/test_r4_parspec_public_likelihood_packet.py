"""Tests for the v2.206 ParSpec public-likelihood packet gate."""

from __future__ import annotations

import json

from experiments.r4_parspec_public_likelihood_packet import (
    DEFAULT_OUT,
    PUBLIC_LIKELIHOOD_ACCEPTANCE_CRITERIA,
    diagnose_r4_parspec_public_likelihood_packet,
    evaluate_public_likelihood_packet,
    malformed_public_likelihood_packet_candidate,
    parspec_public_likelihood_packet_candidate,
    public_likelihood_acceptance_criteria,
    public_likelihood_surface_recheck,
)
from experiments.r4_parspec_qeft_source_asset_audit import (
    PARSPEC_SOURCE_PACKAGE_SHA256,
    QEFT_CDF_FIGURE_SHA256,
    QEFT_POSTERIORS_FIGURE_SHA256,
    QEFT_TEX_SHA256,
)


def test_acceptance_criteria_are_complete() -> None:
    criteria = public_likelihood_acceptance_criteria()

    assert tuple(row["criterion"] for row in criteria) == (
        PUBLIC_LIKELIHOOD_ACCEPTANCE_CRITERIA
    )
    assert all(row["required"] is True for row in criteria)
    assert {
        "posterior_samples_or_covariance_or_log_likelihood_grid",
        "content_hashes_and_license",
        "calibration_and_systematics_policy",
    }.issubset({row["criterion"] for row in criteria})


def test_packet_preserves_source_hashes_and_bounds_without_likelihood() -> None:
    packet = parspec_public_likelihood_packet_candidate()
    hashes = packet["source_package_hashes"]
    facts = packet["source_facts_preserved"]

    assert hashes["source_package_sha256"] == PARSPEC_SOURCE_PACKAGE_SHA256
    assert hashes["qeft_tex_sha256"] == QEFT_TEX_SHA256
    assert hashes["qeft_posterior_figure_sha256"] == (
        QEFT_POSTERIORS_FIGURE_SHA256
    )
    assert hashes["qeft_cdf_figure_sha256"] == QEFT_CDF_FIGURE_SHA256
    assert facts["source_axis"] == "ell_qEFT_km"
    assert facts["qeft_power"] == 6
    assert facts["event_bounds_90_credible_km"]["combined"] == 51.3
    assert packet["public_likelihood_candidate"]["status"] == "absent"


def test_surface_recheck_records_public_surfaces_and_no_candidates() -> None:
    recheck = public_likelihood_surface_recheck()

    surfaces = {row["surface"]: row for row in recheck["surfaces"]}
    assert recheck["machine_readable_public_likelihood_ready"] is False
    assert recheck["detected_machine_readable_likelihood_assets"] == []
    assert {
        "arxiv_abs",
        "arxiv_eprint_source_package",
        "published_article",
        "lvk_gwtc2_tests_of_gr_zenodo",
        "lvk_gwtc3_tests_of_gr_zenodo",
        "author_and_public_code_surfaces",
        "public_web_search",
    }.issubset(surfaces)
    assert "qeft_posteriors_combined.pdf" in (
        recheck["source_package_top_level_files"]
    )


def test_evaluation_closes_public_likelihood_gate() -> None:
    evaluation = evaluate_public_likelihood_packet()

    assert evaluation["acceptance_gate_documented"] is True
    assert evaluation["public_likelihood_packet_ready"] is False
    assert evaluation["machine_readable_public_likelihood_ready"] is False
    assert evaluation["published_bound_surrogate_retained"] is True
    assert "machine_readable_public_url_missing" in evaluation["blockers"]
    assert (
        "posterior_samples_or_covariance_or_log_likelihood_grid_missing"
        in evaluation["blockers"]
    )
    assert (
        "public_parspec_qeft_likelihood_or_posterior_samples_missing"
        in evaluation["claim_blockers"]
    )
    assert evaluation["ready_for_framework_claim"] is False


def test_malformed_url_shaped_likelihood_still_fails_metadata_gate() -> None:
    evaluation = evaluate_public_likelihood_packet(
        malformed_public_likelihood_packet_candidate()
    )

    assert evaluation["criterion_status"]["machine_readable_public_url"] is True
    assert evaluation["criterion_status"][
        "posterior_samples_or_covariance_or_log_likelihood_grid"
    ] is True
    assert evaluation["public_likelihood_packet_ready"] is False
    assert "source_event_rows_or_combined_policy_missing" in (
        evaluation["blockers"]
    )
    assert "prior_and_threshold_policy_missing" in evaluation["blockers"]
    assert "waveform_sampler_version_metadata_missing" in (
        evaluation["blockers"]
    )
    assert "calibration_and_systematics_policy_missing" in (
        evaluation["blockers"]
    )
    assert "content_hashes_and_license_missing" in evaluation["blockers"]


def test_diagnosis_records_nonclaiming_public_likelihood_packet() -> None:
    result = diagnose_r4_parspec_public_likelihood_packet()

    assert result["version"] == "v2.206"
    assert result["public_likelihood_packet_ready"] is False
    assert result["machine_readable_public_likelihood_ready"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "parspec_public_likelihood_packet_absent_bound_surrogate_retained"
    )
    assert result["selected_next_build_action"] == (
        "build_reproducible_qeft_likelihood_rerun_packet_or_find_new_"
        "source_backed_qnm_to_bresciani_sensitivity"
    )


def test_bound_surrogate_is_retained_but_not_promoted() -> None:
    packet = parspec_public_likelihood_packet_candidate()
    surrogate = packet["published_bound_surrogate_reference"]

    assert surrogate["surrogate_ready_for_nonclaiming_attachment"] is True
    assert surrogate["machine_readable_public_likelihood_ready"] is False
    assert surrogate["claim_use_allowed"] is False
    assert packet["claim_controls"][
        "published_bound_surrogate_not_claim_evidence"
    ] is True


def test_committed_artifact_matches_public_likelihood_contract_if_present() -> None:
    if not DEFAULT_OUT.exists():
        return

    artifact = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    assert artifact["version"] == "v2.206"
    assert artifact["route_status"] == (
        "parspec_public_likelihood_packet_absent_bound_surrogate_retained"
    )
    assert artifact["public_likelihood_packet_ready"] is False
    assert artifact["ready_for_framework_claim"] is False
