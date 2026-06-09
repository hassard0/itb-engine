"""Tests for the thematic taxonomy tool (v2.09)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import taxonomy as tx


def test_assign_returns_valid_theme():
    valid = {t for t, _, _ in tx.THEMES}
    for blob in ["v1.90 diosi-penrose gravitational collapse",
                 "v1.93 constraint jenga irreplaceability",
                 "v1.73 island census dimensionality",
                 "v1.86 starobinsky inflation"]:
        assert tx.assign({"blob": blob}) in valid


def test_data_and_meta_keywords_route_correctly():
    assert tx.assign({"blob": "godel test internal consistency"}) == "Meta-experiments & auditing"
    assert tx.assign({"blob": "sub-mm gravity eot-wash yukawa"}) == "Empirical swampland & data ingestion"
    assert tx.assign({"blob": "bayesian model-comparison data-driven"}) in (
        "Data-driven EFT & the central tension", "Meta-experiments & auditing")


def test_build_assigns_every_note_to_one_theme():
    notes, by_theme = tx.build()
    valid = {t for t, _, _ in tx.THEMES}
    assert len(notes) >= 1
    for n in notes:
        assert n["theme"] in valid             # exactly one valid theme each
    # the partition is exhaustive: counts sum to the note total
    assert sum(len(v) for v in by_theme.values()) == len(notes)
