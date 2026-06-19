"""Regression tests for v2.58 birefringence adapter sourceability."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from birefringence_adapter_literature_sourceability import (  # noqa: E402
    diagnose_birefringence_adapter_literature_sourceability,
)


def test_literature_sourceability_finds_no_direct_beta_to_gravity_adapter():
    result = diagnose_birefringence_adapter_literature_sourceability()

    assert result["row_count"] == 5
    assert result["em_birefringence_source_backed"] is True
    assert result["cmb_beta_measurement_source_backed"] is True
    assert result["gravitational_parity_channel_source_backed"] is True
    assert result["universal_em_to_gravity_relation_found"] is False
    assert result["engine_axis_normalization_found"] is False
    assert result["claim_ready_adapter_pieces"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "cmb_beta_not_direct_gravitational_parity_adapter"


def test_cmb_beta_rows_are_measurements_not_operator_adapters():
    result = diagnose_birefringence_adapter_literature_sourceability()
    rows = {row["label"]: row for row in result["rows"]}

    for label in {"wmap_planck_beta_measurement", "act_dr6_beta_measurement"}:
        row = rows[label]
        assert row["supports_beta_measurement"] is True
        assert row["supports_gravitational_parity_map"] is False
        assert row["provides_engine_axis_normalization"] is False
        assert "measurement_not_operator_adapter" in row["blockers"]


def test_em_axion_source_does_not_map_to_engine_gravity_parity():
    result = diagnose_birefringence_adapter_literature_sourceability()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["alp_photon_cmb_rotation_mechanism"]

    assert row["supports_em_axion_photon_map"] is True
    assert row["supports_gravitational_parity_map"] is False
    assert row["provides_universal_em_to_gravity_relation"] is False
    assert "maps_beta_to_alp_photon_not_gravity_parity" in row["blockers"]


def test_gravity_parity_sources_are_separate_gw_channel():
    result = diagnose_birefringence_adapter_literature_sourceability()
    rows = {row["label"]: row for row in result["rows"]}

    for label in {
        "ligo_axion_gravity_coupling_constraint",
        "axion_gravity_wave_birefringence_mechanism",
    }:
        row = rows[label]
        assert row["supports_gravitational_parity_map"] is True
        assert row["supports_beta_measurement"] is False
        assert row["provides_universal_em_to_gravity_relation"] is False
        assert "no_cmb_beta_to_gravity_coupling_relation" in row["blockers"]


def test_best_next_artifact_requires_multimessenger_or_route_split():
    result = diagnose_birefringence_adapter_literature_sourceability()

    assert "multimessenger axion model" in result["best_next_artifact"]
    assert "GW birefringence" in result["best_next_artifact"]
    assert "no_universal_em_gravity_coupling_relation" in result["claim_blockers"]
