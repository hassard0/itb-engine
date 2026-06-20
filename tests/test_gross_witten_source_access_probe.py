"""Tests for the v2.152 Gross-Witten source access probe."""

from experiments.gross_witten_source_access_probe import (
    diagnose_gross_witten_source_access_probe,
    evaluate_gross_witten_source_access,
    gross_witten_file_access_attempts,
    gross_witten_metadata_sources,
)


def test_metadata_sources_confirm_gross_witten_primary_record():
    rows = gross_witten_metadata_sources()
    source_ids = {row["source_id"] for row in rows}

    assert "cern_cds_166499" in source_ids
    assert "inspire_227371" in source_ids
    assert all(row["metadata_status"] == "confirmed" for row in rows)
    cern = next(row for row in rows if row["source_id"] == "cern_cds_166499")
    assert cern["facts"]["title"] == "Superstring modifications of Einstein's equations"
    assert cern["facts"]["pages"] == 18
    assert cern["file_status"] == "files_tab_disabled"


def test_file_access_attempts_do_not_ingest_machine_formula():
    attempts = gross_witten_file_access_attempts()

    assert attempts[0]["observed_status"] == "200_text_html_directory_view"
    assert any(row["observed_status"] == "404_not_found" for row in attempts)
    assert all(row["machine_formula_ingested"] is False for row in attempts)


def test_access_evaluation_selects_open_rederivation_fallback():
    result = evaluate_gross_witten_source_access()

    assert result["metadata_confirmed"] is True
    assert result["primary_file_machine_ingested"] is False
    assert result["k_formula_machine_ingested"] is False
    assert result["claim_ready_now"] is False
    assert result["fallback_route"] == (
        "rederive_virasoro_shapiro_k_bridge_from_open_sources"
    )
    assert "machine_readable_K_factor_formula_missing" in result["claim_blockers"]


def test_diagnosis_records_nonterminal_file_access_block():
    result = diagnose_gross_witten_source_access_probe()

    assert result["version"] == "v2.152"
    assert result["ready_to_claim_now"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "gross_witten_metadata_confirmed_file_access_blocked"
    )
    assert result["selected_next_build_action"] == (
        "rederive_virasoro_shapiro_k_bridge_from_open_sources"
    )
    assert "instead of treating the missing PDF as a terminal blocker" in (
        result["interpretation"]
    )
