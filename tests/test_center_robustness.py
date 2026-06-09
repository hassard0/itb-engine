"""Sanity tests for the central-prediction robustness sweep (v1.75)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import center_robustness as cr
from stack import CANONICAL


def test_pct_structure():
    p = cr.pct([1.0, 2.0, 3.0, 4.0, 5.0])
    assert p["median"] == 3.0
    assert p["min"] == 1.0 and p["max"] == 5.0
    assert p["p16"] <= p["median"] <= p["p84"]


def test_one_draw_canonical_reproduces_center():
    """A draw at the CANONICAL prefactors gives a valid interior center whose
    sub-mm Yukawa lands in the dark-energy sub-mm band (reproduces v1.74)."""
    r = cr._one_draw((0, dict(CANONICAL)))
    assert r["all_satisfied"]
    assert 60.0 <= r["submm_yukawa_range_um"] <= 110.0
    # a/c interior to the Hofman-Maldacena wedge
    assert 1.0 / 3.0 <= r["a_over_c_direct"] <= 31.0 / 18.0
    assert r["inradius"] > 0.0
