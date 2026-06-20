"""Tests for the v2.151 R4 claim-blocker attack plan."""

from experiments.r4_claim_blocker_attack_plan import (
    diagnose_r4_claim_blocker_attack_plan,
    evaluate_r4_claim_attack_routes,
    r4_claim_source_rows,
)


def test_source_rows_cover_absolute_and_likelihood_routes():
    rows = r4_claim_source_rows()
    route_set = {row["route"] for row in rows}
    source_ids = {row["source_id"] for row in rows}

    assert "absolute_normalization" in route_set
    assert "measurement_likelihood" in route_set
    assert "gross_witten_1986_tree_graviton_scattering" in source_ids
    assert "russo_1997_type_iib_four_graviton" in source_ids
    assert "public_gravity_r4_likelihood_search_2026_06_20" in source_ids


def test_route_evaluation_selects_absolute_normalization_next():
    result = evaluate_r4_claim_attack_routes()

    assert result["query_surface_ready"] is True
    assert result["query_surface_claim_ready"] is False
    assert result["selected_attack_route"] == "absolute_normalization"
    assert result["selected_next_source_target"] == (
        "gross_witten_1986_tree_graviton_scattering"
    )
    assert result["selected_next_build_action"] == (
        "ingest_or_rederive_gross_witten_k_formula_and_lambda_bridge"
    )
    assert result["route_scores"]["absolute_normalization"]["score"] > (
        result["route_scores"]["measurement_likelihood"]["score"]
    )


def test_measurement_route_remains_likelihood_blocked():
    result = evaluate_r4_claim_attack_routes()
    likelihood = result["route_scores"]["measurement_likelihood"]

    assert likelihood["claim_ready_now"] is False
    assert likelihood["ready_components"] == []
    assert "public_covariance_or_likelihood_over_g_R4_c1_c2_c3" in (
        likelihood["primary_blockers"]
    )


def test_absolute_route_records_k_bridge_and_lambda_blockers():
    result = evaluate_r4_claim_attack_routes()
    absolute = result["route_scores"]["absolute_normalization"]

    assert absolute["claim_ready_now"] is False
    assert absolute["ready_components"] == [
        "russo_1997_type_iib_four_graviton",
        "kallosh_lee_rube_2008_n8_r4_shape",
    ]
    assert "K_Russo_to_Kallosh_shape_bridge" in absolute["primary_blockers"]
    assert "alpha_prime_to_engine_Lambda_R4_conversion" in (
        absolute["primary_blockers"]
    )


def test_diagnosis_records_no_claim_and_next_artifact():
    result = diagnose_r4_claim_blocker_attack_plan()

    assert result["version"] == "v2.151"
    assert result["ready_to_claim_now"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "r4_claim_blockers_ranked_absolute_normalization_next"
    )
    assert result["selected_next_build_action"] == (
        "ingest_or_rederive_gross_witten_k_formula_and_lambda_bridge"
    )
    assert "machine_readable_K_factor_formula" in result["current_blockers"]
