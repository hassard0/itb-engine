"""Tests for the v2.183 LALSuite detector-channel response."""

import pytest

from experiments.r4_lalsuite_detector_channel_response import (
    CALIBRATED_CHANNEL_RESPONSE,
    EVENT,
    TARGET_HOST,
    diagnose_r4_lalsuite_detector_channel_response,
    evaluate_lalsuite_detector_channel_response,
    lalsuite_detector_channel_response,
    malformed_lalsuite_detector_channel_response,
)


def test_calibrated_response_contains_h1_l1_positive_channels():
    response = lalsuite_detector_channel_response()

    assert response["target_host"] == TARGET_HOST
    assert response["event"] == EVENT
    assert response["grid"]["sample_count"] == 336
    assert sorted(response["detectors"]) == ["H1", "L1"]
    for detector, row in response["detectors"].items():
        assert row["K_plus"] > 0.0, detector
        assert row["Re_K_minus"] > 0.0, detector
        assert row["Im_K_minus"] > 0.0, detector
        assert 0.0 < row["tensor_rms"] <= 1.0


def test_response_values_match_vulcan_lalsuite_probe():
    response = lalsuite_detector_channel_response()["detectors"]

    assert response["H1"]["K_plus"] == pytest.approx(
        CALIBRATED_CHANNEL_RESPONSE["H1"]["K_plus"]
    )
    assert response["L1"]["K_plus"] == pytest.approx(
        CALIBRATED_CHANNEL_RESPONSE["L1"]["K_plus"]
    )
    assert response["H1"]["Re_K_minus"] == pytest.approx(
        CALIBRATED_CHANNEL_RESPONSE["H1"]["Re_K_minus"]
    )
    assert response["L1"]["Im_K_minus"] == pytest.approx(
        CALIBRATED_CHANNEL_RESPONSE["L1"]["Im_K_minus"]
    )


def test_detector_channel_response_ready_but_nonclaiming():
    result = evaluate_lalsuite_detector_channel_response(
        lalsuite_detector_channel_response()
    )

    assert result["detector_channel_response_ready"] is True
    assert result["ready_to_replace_v2_181_detector_channel_proxy"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["response_blockers"] == []
    assert result["removed_v2_182_blocker"] == (
        "detector_antenna_r4_channel_response_not_calibrated"
    )
    assert "nuisance_marginalized_covariance_not_exported" in (
        result["remaining_real_reanalysis_blockers"]
    )


def test_malformed_response_rejects_host_grid_and_channel():
    result = evaluate_lalsuite_detector_channel_response(
        malformed_lalsuite_detector_channel_response()
    )

    assert result["detector_channel_response_ready"] is False
    assert "target_host_not_vulcan" in result["response_blockers"]
    assert "response_grid_sample_count_unexpected" in result["response_blockers"]
    assert "detector_channel_response_not_calibrated" in result["response_blockers"]
    assert "H1_K_plus_not_positive" in result["response_blockers"]


def test_diagnosis_selects_proxy_replacement_next():
    result = diagnose_r4_lalsuite_detector_channel_response()

    assert result["version"] == "v2.183"
    assert result["detector_channel_response_ready"] is True
    assert result["ready_real_public_r4_reanalysis_packets_now"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "r4_lalsuite_detector_channel_response_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "replace_v2_181_detector_proxy_with_lalsuite_channel_response"
    )
