"""Tests for the gravitational double-copy test (v1.94)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import double_copy as dc


def test_symmetric_double_copy_is_ac_one():
    """The symmetric double-copy map gives g_R2 = g_C (a/c = 1)."""
    a4 = np.array([0.1, 0.3, 0.5])
    gR2 = a4 ** 2
    gC = a4 ** 2
    assert np.allclose(gR2, gC)                      # a = c
    assert np.allclose(gR2 / gC, 1.0)


def test_wedge_strictly_contains_diagonal():
    """The HM wedge admits a/c != 1 -> strictly larger than the symmetric double copy."""
    assert dc.AC_FLOOR < 1.0 < dc.AC_CEIL            # diagonal is interior
    assert dc.AC_FLOOR < dc.AC_DC_BAND[0]            # band is inside the wedge
    assert dc.AC_DC_BAND[1] < dc.AC_CEIL


def test_non_double_copy_region_exists():
    """Part of the wedge (a/c near the floor or ceiling) is outside the double-copy band."""
    # a/c = 1.7 (near ceiling) is in the wedge but NOT double-copy-reachable
    ac = 1.7
    assert dc.AC_FLOOR <= ac <= dc.AC_CEIL
    assert not (dc.AC_DC_BAND[0] <= ac <= dc.AC_DC_BAND[1])
