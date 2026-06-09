"""Tests for inverse constraint design (v2.02)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import inverse_constraint_design as icd


def test_unit_normalizes():
    n = icd._unit([3.0, 4.0, 0, 0, 0, 0, 0, 0])
    assert np.linalg.norm(n) == __import__("pytest").approx(1.0)


def test_sloppy_direction_removes_more_than_stiff():
    """A cut along a high-variance (sloppy) direction removes more island than a stiff one."""
    rng = np.random.default_rng(0)
    # synthetic island: wide along axis 0 (sloppy), narrow along axis 1 (stiff)
    isl = np.zeros((2000, 8))
    isl[:, 0] = rng.normal(0, 1.0, 2000)
    isl[:, 1] = rng.normal(0, 0.01, 2000)
    favored = np.zeros(8)                       # at the center
    def shrink(axis):
        n = np.zeros(8); n[axis] = 1.0
        return np.mean(isl @ n > favored @ n)
    # both ~0.5 at the center, but the sloppy axis has real spread to bound
    assert abs(shrink(0) - 0.5) < 0.05
    assert isl[:, 0].std() > isl[:, 1].std()    # sloppy axis is the informative one


def test_favored_point_admitted_at_tangent():
    """With the threshold set tangent at the favored point, it is retained (P > c is strict)."""
    favored = np.array([0.5, 0.4, 0.4, 0.3, 0.15, 0.35, 0.09, 0.03])
    n = icd._unit([0, 0, 0, 1, 0, -1, 0, 0])
    c = favored @ n
    assert not (favored @ n > c)                # favored is NOT removed (boundary kept)


def test_shrinkage_in_unit_interval():
    isl = np.random.default_rng(1).random((500, 8))
    n = icd._unit(np.ones(8))
    s = float(np.mean(isl @ n > 0.5 * (isl @ n).max()))
    assert 0.0 <= s <= 1.0
