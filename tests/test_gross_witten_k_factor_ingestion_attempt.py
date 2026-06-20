"""Tests for the v2.141 Gross-Witten K-factor ingestion attempt."""

from experiments.gross_witten_k_factor_ingestion_attempt import (
    diagnose_gross_witten_k_factor_ingestion_attempt,
    k_factor_ingestion_requirements,
    next_ingestion_routes,
    source_record_attempts,
)


def test_wrong_cern_pdf_is_not_gross_witten():
    rows = {row["attempt_id"]: row for row in source_record_attempts()}
    wrong_pdf = rows["cern_record_170189_pdf"]

    assert wrong_pdf["is_gross_witten_target"] is False
    assert wrong_pdf["rendered_title"] == (
        "Higher Curvature Supergravity and Superstrings"
    )
    assert wrong_pdf["blocker"] == "wrong_cern_pdf_record_for_gross_witten"


def test_actual_cern_record_identifies_gross_witten_but_exposes_no_file():
    rows = {row["attempt_id"]: row for row in source_record_attempts()}
    record = rows["cern_record_166499_actual_gross_witten"]

    assert record["is_gross_witten_target"] is True
    assert record["metadata_title"] == "Superstring modifications of Einstein's equations"
    assert record["file_list_entries_found"] == 0
    assert record["provides_machine_checkable_k_formula"] is False


def test_requirements_keep_k_formula_missing():
    requirements = {
        row["requirement"]: row for row in k_factor_ingestion_requirements()
    }

    assert requirements["target_source_identity_verified"]["status"] == "satisfied"
    assert requirements["wrong_source_removed_from_route"]["status"] == "satisfied"
    assert requirements["machine_checkable_k_formula"]["status"] == "missing"
    assert requirements["k_plus_k_minus_projection"]["status"] == "missing"


def test_next_routes_include_ocr_library_and_rederivation():
    routes = {row["route"]: row for row in next_ingestion_routes()}

    assert "obtain_gross_witten_article_pdf_from_library_or_elsevier" in routes
    assert "ocr_physical_scan_of_gross_witten_article" in routes
    assert "rederive_k_from_string_polarization_tensors" in routes


def test_diagnosis_records_corrected_record_but_no_k_formula():
    result = diagnose_gross_witten_k_factor_ingestion_attempt()

    assert result["version"] == "v2.141"
    assert result["verified_gross_witten_records"] == [
        "cern_record_166499_actual_gross_witten",
        "doi_record",
    ]
    assert result["machine_checkable_k_formula_sources"] == []
    assert result["can_ingest_k_formula_now"] is False
    assert result["missing_requirements"] == [
        "machine_checkable_k_formula",
        "k_plus_k_minus_projection",
    ]
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "gross_witten_record_corrected_k_formula_not_ingested"
    )
