"""Tests for the Diosi-Penrose exclusion (v1.90)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

import diosi_penrose as dp


def test_rate_scales_inverse_cube():
    """DP spontaneous emission ~ 1/R_0^3."""
    assert dp.rate_ratio(dp.R0_BOUND_m) == 1.0
    assert dp.rate_ratio(dp.R0_BOUND_m / 2) == 8.0          # half R_0 -> 8x rate


def test_parameter_free_excluded():
    """The nucleon-scale (parameter-free) DP rate is far above the limit."""
    r = dp.rate_ratio(dp.R0_NUCLEON_m)
    assert r > 1e10                                          # excluded by >10 orders


def test_large_R0_allowed():
    """A macroscopic R_0 above the bound is allowed (rate below the limit)."""
    assert dp.rate_ratio(1e-9) < 1.0
