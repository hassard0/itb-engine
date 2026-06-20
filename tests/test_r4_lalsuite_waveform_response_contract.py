"""Tests for the v2.177 LALSuite R4 waveform response contract."""

import numpy as np
import pytest

from experiments.r4_lalsuite_waveform_response_contract import (
    RESPONSE_AXES,
    default_r4_vf_grid,
    diagnose_r4_lalsuite_waveform_response_contract,
    evaluate_lalsuite_r4_response_candidate,
    lalsuite_r4_waveform_response_contract,
    malformed_lalsuite_r4_response_candidate,
    r4_shape_response_kernels,
    synthetic_lalsuite_r4_response_candidate,
)


def test_r4_response_kernels_are_finite_monotonic_and_rank_three():
    response = r4_shape_response_kernels()
    grid = np.asarray(response["v_f_grid"])

    assert np.all(np.diff(grid) > 0.0)
    assert response["axes"] == list(RESPONSE_AXES)
    assert response["kernel_rank"] == 3
    assert response["rank_ready"] is True
    for axis in RESPONSE_AXES:
        values = np.asarray(response["kernels"][axis])
        assert values.shape == grid.shape
        assert np.isfinite(values).all()
        assert response["kernel_summary"][axis]["l2_norm"] > 0.0


def test_default_grid_validation_rejects_bad_bounds():
    with pytest.raises(ValueError, match="count"):
        default_r4_vf_grid(count=2)
    with pytest.raises(ValueError, match="grid"):
        default_r4_vf_grid(minimum=0.4, maximum=0.2)


def test_contract_uses_bresciani_axes_and_lalsuite_hook():
    contract = lalsuite_r4_waveform_response_contract()

    assert contract["contract_id"] == "lalsuite_r4_shape_response_contract_v1"
    assert contract["response_axes"] == list(RESPONSE_AXES)
    assert contract["axis_mapping"]["status"] == "maps_to_bresciani_r4_axes"
    assert contract["lalsuite_hook"]["status"] == "compatible_contract_defined"
    assert contract["packet_export_target"]["target_packet"] == (
        "v2.160_r4_shape_likelihood_packet_manifest"
    )


def test_candidate_is_software_ready_but_not_real_reanalysis_ready():
    result = evaluate_lalsuite_r4_response_candidate(
        synthetic_lalsuite_r4_response_candidate()
    )

    assert result["software_response_contract_ready"] is True
    assert result["ready_to_replace_v2_176_fixture_response_contract"] is True
    assert result["ready_for_real_public_r4_reanalysis"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["contract_blockers"] == []
    assert "source_backed_r4_pn_or_imr_waveform_derivation" in (
        result["real_reanalysis_blockers"]
    )


def test_malformed_candidate_rejects_axis_rank_and_claim_toggles():
    result = evaluate_lalsuite_r4_response_candidate(
        malformed_lalsuite_r4_response_candidate()
    )

    assert result["software_response_contract_ready"] is False
    assert "response_axes_not_bresciani_r4_shape_axes" in result["contract_blockers"]
    assert "r4_response_kernels_not_rank_three" in result["contract_blockers"]
    assert "claim_use_not_disabled" in result["contract_blockers"]


def test_diagnosis_selects_public_strain_projection_next():
    result = diagnose_r4_lalsuite_waveform_response_contract()

    assert result["version"] == "v2.177"
    assert result["software_response_contract_ready"] is True
    assert result["ready_real_public_r4_reanalysis_packets_now"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "lalsuite_r4_waveform_response_contract_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "project_r4_response_contract_onto_public_strain_harness"
    )
