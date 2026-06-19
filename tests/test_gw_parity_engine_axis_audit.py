"""Tests for current engine-axis audit of the Ng PPV candidate."""

from experiments.gw_parity_engine_axis_audit import (
    diagnose_gw_parity_engine_axis_audit,
    engine_axis_rows,
)


def test_engine_axis_audit_finds_no_promotable_ng_ppv_target():
    result = diagnose_gw_parity_engine_axis_audit()

    assert result["version"] == "v2.75"
    assert result["promotable_axis_count"] == 0
    assert result["promotable_axes"] == []
    assert result["ng_ppv_candidate_packet_can_be_promoted_now"] is False
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "current_engine_axes_cannot_accept_ng_ppv_beta10"
    assert "source-backed operator identity from beta_1_0 to engine axis" in result[
        "required_adapter_contract"
    ]


def test_g_r2_parity_axis_has_internal_sign_but_no_source_normalization():
    row = next(row for row in engine_axis_rows() if row["axis"] == "g_R2_parity")

    assert row["source_backed_ng_ppv_map"] is False
    assert row["can_accept_ng_beta10_packet"] is False
    assert "g_R2 +/- g_R2_parity" in row["internal_sign_status"]
    assert "no_kappa_Gpc_inv_to_g_R2_parity_normalization" in row["blockers"]
    assert "frequency_basis_mismatch_omega0_vs_100Hz" in row["blockers"]


def test_g_r3_parity_axis_rejects_wrong_operator_order():
    row = next(row for row in engine_axis_rows() if row["axis"] == "g_R3_parity")

    assert row["can_accept_ng_beta10_packet"] is False
    assert "wrong_operator_order_for_ng_beta10_candidate" in row["blockers"]


def test_legacy_ligo_bound_is_not_the_reproduced_ng_likelihood():
    row = next(
        row for row in engine_axis_rows()
        if row["axis"] == "legacy_ligo_birefringence_bound"
    )

    assert row["can_accept_ng_beta10_packet"] is False
    assert "not_the_reproduced_ng_restricted_likelihood" in row["blockers"]
    assert "absolute_value_bound_erases_ng_sign" in row["blockers"]
