"""Tests for the v2.182 Vulcan LALSuite runtime target."""

from experiments.r4_vulcan_lalsuite_runtime_target import (
    LAL_VERSION,
    TARGET_HOST,
    diagnose_r4_vulcan_lalsuite_runtime_target,
    evaluate_vulcan_lalsuite_runtime_evidence,
    malformed_vulcan_lalsuite_runtime_evidence,
    vulcan_lalsuite_runtime_evidence,
)


def test_vulcan_runtime_evidence_records_imrphenomd_probe():
    evidence = vulcan_lalsuite_runtime_evidence()
    import_probe = evidence["import_probe"]
    waveform = evidence["imrphenomd_reference_probe"]

    assert evidence["target_host"] == TARGET_HOST
    assert import_probe["available"] is True
    assert import_probe["lal_version"] == LAL_VERSION
    assert import_probe["has_imrphenomd"] is True
    assert waveform["approximant"] == "IMRPhenomD"
    assert waveform["nonzero_bins"] == 366
    assert float(waveform["max_abs_h_plus"]) > 0.0
    assert waveform["max_abs_h_plus_x1e23"] > 0.0


def test_runtime_target_ready_but_nonclaiming():
    result = evaluate_vulcan_lalsuite_runtime_evidence(
        vulcan_lalsuite_runtime_evidence()
    )

    assert result["lalsuite_runtime_target_ready"] is True
    assert result["ready_to_clear_runtime_availability_gate_on_vulcan"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["runtime_blockers"] == []
    assert result["removed_v2_181_blocker"] == (
        "lalsuite_r4_runtime_projection_not_run"
    )
    assert "detector_antenna_r4_channel_response_not_calibrated" in (
        result["remaining_real_reanalysis_blockers"]
    )


def test_malformed_runtime_evidence_rejects_missing_imrphenomd_and_waveform():
    result = evaluate_vulcan_lalsuite_runtime_evidence(
        malformed_vulcan_lalsuite_runtime_evidence()
    )

    assert result["lalsuite_runtime_target_ready"] is False
    assert "target_host_not_vulcan" in result["runtime_blockers"]
    assert "imrphenomd_not_available" in result["runtime_blockers"]
    assert "reference_nonzero_bin_count_unexpected" in result["runtime_blockers"]
    assert "reference_waveform_zero_or_invalid" in result["runtime_blockers"]


def test_diagnosis_selects_calibrated_detector_channel_response_next():
    result = diagnose_r4_vulcan_lalsuite_runtime_target()

    assert result["version"] == "v2.182"
    assert result["lalsuite_runtime_target_ready"] is True
    assert result["ready_real_public_r4_reanalysis_packets_now"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "r4_vulcan_lalsuite_runtime_target_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "derive_calibrated_r4_detector_channel_response"
    )
