"""Tests for the v1.83 master predictions scorecard."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import master_scorecard as ms


def test_scorecard_assembles_all_rows():
    rows = ms.build_scorecard()
    keys = {r["key"] for r in rows}
    expected = {"submm", "cmb_beta", "tension", "gw_bire", "pta", "eta_s",
                "ac_wedge", "bh_entropy", "island", "data_eft"}
    assert expected <= keys
    assert len(rows) >= 10


def test_statuses_valid():
    rows = ms.build_scorecard()
    for r in rows:
        assert r["status"] in ms.STATUS_ORDER
        assert r["prediction"] and r["version"] and r["next"]


def test_live_numbers_present():
    """Key live-pulled numbers appear (cosmic birefringence + BH entropy)."""
    rows = {r["key"]: r for r in ms.build_scorecard()}
    assert "deg" in rows["cmb_beta"]["prediction"]
    assert "Delta S_ext" in rows["bh_entropy"]["prediction"]
    # the data-driven EFT's BH entropy is positive (WGC), so the row reads "> 0"
    assert "> 0" in rows["bh_entropy"]["prediction"]
