"""Tests for the v2.199 ParSpec absolute gamma metadata artifact."""

import json
import math
from pathlib import Path

import pytest

from experiments.r4_parspec_absolute_gamma_metadata import (
    GWOSC_PARAMETER_SNAPSHOT,
    QEFT_POWER,
    SOLAR_MASS_GEOMETRIC_RADIUS_KM,
    absolute_gamma,
    absolute_gamma_metadata_range,
    absolute_gamma_ratio,
    diagnose_r4_parspec_absolute_gamma_metadata,
)


def test_gwosc_snapshot_preserves_preferred_final_mass_and_redshift_metadata():
    gw150914 = GWOSC_PARAMETER_SNAPSHOT["GW150914"]
    gw200129 = GWOSC_PARAMETER_SNAPSHOT["GW200129"]

    assert gw150914["selected_pe_record"] == "gwtc1_pe_GW150914"
    assert gw150914["is_preferred"] is True
    assert gw150914["parameters"]["final_mass_source"]["best"] == 63.1
    assert gw150914["parameters"]["redshift"]["best"] == 0.09

    assert gw200129["selected_pe_record"] == (
        "GWTC-3-confident_GW200129_065458_R2_pe_combined"
    )
    assert gw200129["is_preferred"] is True
    assert gw200129["parameters"]["final_mass_source"]["best"] == 60.2
    assert gw200129["parameters"]["redshift"]["best"] == 0.18


def test_absolute_gamma_formula_uses_source_mass_redshift_and_power_six():
    ratio = absolute_gamma_ratio(
        51.7,
        final_mass_source_solar=63.1,
        redshift=0.09,
    )
    expected_ratio = 51.7 * 1.09 / (63.1 * SOLAR_MASS_GEOMETRIC_RADIUS_KM)

    assert ratio == pytest.approx(expected_ratio)
    assert absolute_gamma(
        51.7,
        final_mass_source_solar=63.1,
        redshift=0.09,
    ) == pytest.approx(expected_ratio**QEFT_POWER)


def test_absolute_gamma_rejects_nonphysical_inputs():
    with pytest.raises(ValueError, match="ell_qeft_km"):
        absolute_gamma_ratio(0.0, final_mass_source_solar=63.1, redshift=0.09)
    with pytest.raises(ValueError, match="final_mass_source_solar"):
        absolute_gamma_ratio(51.7, final_mass_source_solar=0.0, redshift=0.09)
    with pytest.raises(ValueError, match="redshift"):
        absolute_gamma_ratio(51.7, final_mass_source_solar=63.1, redshift=-0.01)


def test_metadata_range_uses_conservative_mass_redshift_extremes():
    gamma_range = absolute_gamma_metadata_range(
        51.7,
        final_mass_source={"best": 63.1, "lower": 60.1, "upper": 66.5},
        redshift={"best": 0.09, "lower": 0.06, "upper": 0.12},
    )
    central = absolute_gamma(
        51.7,
        final_mass_source_solar=63.1,
        redshift=0.09,
    )

    assert gamma_range["lower"] < central < gamma_range["upper"]


def test_diagnosis_exports_event_and_combined_bound_absolute_gamma_rows():
    result = diagnose_r4_parspec_absolute_gamma_metadata()
    packet = result["absolute_gamma_metadata_packet"]

    assert result["version"] == "v2.199"
    assert packet["absolute_gamma_metadata_ready"] is True
    assert packet["combined_bound_single_remnant_metadata_ready"] is False
    assert packet["combined_bound_km_90"] == 51.3

    rows = {row["label"]: row for row in packet["event_bound_absolute_gamma_rows"]}
    assert set(rows) == {"GW150914", "GW200129"}
    assert rows["GW150914"]["ell_qEFT_km"] == 51.7
    assert rows["GW200129"]["ell_qEFT_km"] == 54.8
    assert rows["GW200129"]["absolute_gamma_central"] > (
        rows["GW150914"]["absolute_gamma_central"]
    )
    assert all(
        row["metadata_only_not_public_likelihood"] is True
        for row in rows.values()
    )

    combined_rows = {
        row["label"]: row for row in packet["combined_bound_projected_per_event"]
    }
    assert combined_rows["GW150914"]["ell_qEFT_km"] == 51.3
    assert combined_rows["GW200129"]["ell_qEFT_km"] == 51.3


def test_qnm_deformation_uses_absolute_gamma_not_normalized_bound_gamma():
    result = diagnose_r4_parspec_absolute_gamma_metadata()
    rows = {
        row["label"]: row
        for row in result["absolute_gamma_metadata_packet"][
            "event_bound_absolute_gamma_rows"
        ]
    }
    gw150914 = rows["GW150914"]

    gamma = gw150914["absolute_gamma_central"]
    assert gamma != 1.0
    assert gw150914["qnm_deformation_at_absolute_gamma"][
        "delta_tau_qeft_1"
    ] == pytest.approx(171.35 * gamma)
    assert gw150914["d_absolute_gamma_d_ell_km"] == pytest.approx(
        QEFT_POWER * gamma / 51.7
    )


def test_absolute_gamma_metadata_keeps_claim_gate_closed():
    result = diagnose_r4_parspec_absolute_gamma_metadata()
    evaluation = result["evaluation"]
    malformed = result["malformed_control_evaluation"]

    assert evaluation["absolute_gamma_metadata_ready"] is True
    assert evaluation["ready_for_framework_claim"] is False
    assert evaluation["metadata_blockers"] == []
    assert evaluation["resolved_v2197_subpiece"] == (
        "source_event_absolute_gamma_metadata"
    )
    assert (
        "public_parspec_qeft_likelihood_or_posterior_samples_missing"
        in evaluation["remaining_claim_blockers"]
    )
    assert (
        "qnm_deformation_to_bresciani_engine_r4_operator_basis_map_missing"
        in evaluation["remaining_claim_blockers"]
    )
    assert malformed["absolute_gamma_metadata_ready"] is False
    assert "claim_use_not_disabled" in malformed["metadata_blockers"]
    assert "GW150914_absolute_gamma_not_positive" in malformed["metadata_blockers"]


def test_committed_artifact_records_absolute_gamma_metadata():
    path = Path("experiments/results/v2.199/r4_parspec_absolute_gamma_metadata.json")
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.199"
    assert result["absolute_gamma_metadata_ready"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["route_status"] == (
        "parspec_absolute_gamma_metadata_ready_engine_axis_map_missing"
    )
    assert math.isclose(
        result["absolute_gamma_metadata_packet"]["event_bound_absolute_gamma_rows"][
            0
        ]["final_mass_source_solar"]["best"],
        63.1,
    )
