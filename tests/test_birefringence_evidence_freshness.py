"""Regression tests for v2.49 birefringence evidence freshness audit."""

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from birefringence_evidence_freshness import (  # noqa: E402
    diagnose_birefringence_evidence_freshness,
)


def test_birefringence_freshness_keeps_route_alive_but_not_claimable():
    result = diagnose_birefringence_evidence_freshness()

    assert result["dataset_count"] == 5
    assert result["positive_sign_dataset_count"] == 5
    assert result["route_status"] == "alive_but_not_claimable"
    assert result["claimable_discriminator_now"] is False
    assert result["claim_blockers"] == [
        "no_5sigma_single_dataset_detection",
        "instrument_angle_miscalibration_degeneracy",
        "foreground_systematics_not_closed",
        "data_driven_eft_still_one_observable_dominated",
    ]


def test_birefringence_freshness_tracks_engine_baseline_and_act_shift():
    result = diagnose_birefringence_evidence_freshness()
    baseline = result["engine_baseline"]
    act = next(row for row in result["datasets"] if row["label"] == "act_dr6")

    assert baseline["beta_deg"] == pytest.approx(0.34)
    assert baseline["sigma_deg"] == pytest.approx(0.09)
    assert baseline["zero_exclusion_sigma"] == pytest.approx(3.7777777778)
    assert act["beta_deg"] == pytest.approx(0.215)
    assert act["zero_exclusion_sigma"] == pytest.approx(2.9054054054)
    assert act["consistent_with_zero_at_2sigma"] is False


def test_birefringence_freshness_flags_systematic_dominated_planck_rows():
    result = diagnose_birefringence_evidence_freshness()

    assert result["systematic_dominated_datasets"] == [
        "planck_pr4_map_space_sevem",
        "planck_pr4_map_space_commander",
    ]
    sevem = next(
        row for row in result["datasets"]
        if row["label"] == "planck_pr4_map_space_sevem"
    )
    assert sevem["total_sigma_deg"] == pytest.approx((0.04**2 + 0.28**2) ** 0.5)
    assert sevem["consistent_with_zero_at_2sigma"] is True


def test_birefringence_freshness_pair_combination_is_sub_discovery():
    result = diagnose_birefringence_evidence_freshness()
    pair = result["independent_instrument_pair_fixed_effect"]

    assert pair["labels"] == ["engine_baseline_wmap_planck", "act_dr6"]
    assert pair["beta_deg"] == pytest.approx(0.2635922303)
    assert pair["zero_exclusion_sigma"] == pytest.approx(4.5333911785)
    assert pair["zero_exclusion_sigma"] < 5.0
    assert "one-observable" in result["interpretation"]
