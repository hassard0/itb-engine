"""Tests for the v2.153 Virasoro-Shapiro/Russo R4 K bridge rederivation."""

from experiments.string_r4_normalization_bridge import RUSSO_TREE_R4_CONTACT_SCALAR
from experiments.virasoro_shapiro_k_bridge_rederivation import (
    diagnose_virasoro_shapiro_k_bridge_rederivation,
    evaluate_rederived_k_bridge,
    open_source_formula_inputs,
    rederive_raw_k_bridge,
)


def test_open_source_formula_inputs_are_machine_usable():
    rows = open_source_formula_inputs()
    source_ids = {row["source_id"] for row in rows}

    assert "russo_1997_type_iib_four_graviton" in source_ids
    assert "kallosh_lee_rube_2008_tree_gravity_shape" in source_ids
    assert "bresciani_levati_paradisi_2025_target_basis" in source_ids
    assert all(row["machine_usable"] is True for row in rows)
    assert any(row["url"] == "https://arxiv.org/abs/hep-th/9707241" for row in rows)
    assert any(row["url"] == "https://arxiv.org/abs/0811.3417" for row in rows)
    assert any(row["url"] == "https://arxiv.org/abs/2504.12855" for row in rows)


def test_raw_rederivation_restores_alpha_prime_and_reproduces_control_bridge():
    bridge = rederive_raw_k_bridge()

    assert bridge["massless_barred_variables"]["sbar_tbar_ubar_product"] == (
        "alpha_prime^3*s*t*u/64"
    )
    assert bridge["derived_bridge"]["K_Russo_over_shape"] == (
        "alpha_prime^3/(64*kappa^4)"
    )
    assert bridge["derived_bridge"]["alpha_prime_set_to_one_control"] == (
        "1/(64*kappa^4)"
    )
    assert bridge["derived_bridge"]["reproduces_v2_146_raw_bridge"] is True
    assert bridge["russo_pole_term"]["contact_scalar"] == round(
        RUSSO_TREE_R4_CONTACT_SCALAR,
        12,
    )


def test_evaluation_rejects_absolute_bridge_as_convention_dependent():
    result = evaluate_rederived_k_bridge()

    assert result["criteria"]["source_backed_open_rederivation"] is True
    assert result["criteria"]["reproduces_v2_146_raw_pole_bridge"] is True
    assert result["criteria"]["dimensionless_against_v2_144_shape"] is False
    assert result["criteria"][
        "independent_of_gravitational_coupling_convention"
    ] is False
    assert result["acceptable_absolute_k_bridge"] is False
    assert result["claim_ready_now"] is False
    assert "bridge_depends_on_kappa_convention" in result["blockers"]
    assert "bridge_depends_on_alpha_prime_units" in result["blockers"]
    assert "engine_lambda_r4_unit_conversion_missing" in result["blockers"]


def test_diagnosis_records_next_policy_artifact_instead_of_claim():
    result = diagnose_virasoro_shapiro_k_bridge_rederivation()

    assert result["version"] == "v2.153"
    assert result["ready_to_claim_now"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "open_virasoro_shapiro_rederivation_rejects_absolute_k_bridge"
    )
    assert result["selected_next_build_action"] == (
        "define_or_source_engine_lambda_r4_alpha_prime_policy"
    )
    assert "alpha-prime and kappa convention dependent" in result["interpretation"]
