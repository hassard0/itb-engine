"""Tests for the v2.80 g_8 public data-product acquisition audit."""

from experiments.g8_public_data_product_acquisition_audit import (
    acquisition_candidates,
    diagnose_g8_public_data_product_acquisition_audit,
)


def test_public_data_product_acquisition_finds_no_g8_claim_ready_packet():
    result = diagnose_g8_public_data_product_acquisition_audit()

    assert result["version"] == "v2.80"
    assert result["candidate_count"] == 6
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "public_data_products_exist_but_no_g8_adapter_packet"
    )


def test_cms_hepdata_collection_is_public_data_but_not_engine_g8():
    rows = {row["label"]: row for row in acquisition_candidates()}
    row = rows["cms_smp_22_015_hepdata_energy_correlators"]

    assert row["data_product_kind"] == "hepdata_collection_and_table_dois"
    assert row["external_numerical_data"] is True
    assert row["adapter_assessment"]["ready_for_g8_claim"] is False
    assert "wilson_coefficient_normalization_not_engine_g8" in (
        row["acquisition_blockers"]
    )
    assert "data_product_measures_alpha_s_and_qcd_jet_structure_not_qg_g8" in (
        row["acquisition_blockers"]
    )


def test_heavy_ion_eec_is_public_measurement_not_low_energy_qg_eft():
    rows = {row["label"]: row for row in acquisition_candidates()}
    row = rows["cms_hin_23_004_heavy_ion_eec"]

    assert row["external_numerical_data"] is True
    assert row["adapter_role"] == "heavy_ion_qcd_design_seed_not_qg_g8"
    assert "heavy_ion_medium_observable_not_low_energy_qg_eft_g8" in (
        row["acquisition_blockers"]
    )
    assert "framework_domain_not_validated" in row["acquisition_blockers"]


def test_theory_bridges_are_not_external_measurement_packets():
    result = diagnose_g8_public_data_product_acquisition_audit()

    assert len(result["theory_bridge_candidates"]) == 3
    assert result["blocker_counts"]["measurement_kind_not_external_numeric"] == 3
    assert result["blocker_counts"]["theory_calculation_not_external_measurement"] == 1


def test_every_current_candidate_fails_the_v279_adapter_gate():
    rows = acquisition_candidates()

    assert rows
    assert all(
        row["adapter_assessment"]["adapter_acceptance_ready"] is False
        for row in rows
    )
