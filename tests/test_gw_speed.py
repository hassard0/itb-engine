"""Tests for the GW170817 graviton-speed bound (v1.84)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from itb.constraints.gw_speed import (
    GWSpeedBound, delta_cGW, CGW_BOUND, E_LAMBDA_DE_eV, E_HIGH_eV)
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.theory import Theory


def test_scaling_frequency_suppressed():
    """delta c_GW grows as the cutoff drops (lower cutoff -> larger deviation)."""
    lo = delta_cGW(0.4, E_LAMBDA_DE_eV)
    hi = delta_cGW(0.4, E_HIGH_eV)
    assert lo > hi
    # even at the dark-energy cutoff, far below the bound
    assert lo < CGW_BOUND


def test_not_constraining_at_dark_energy_cutoff():
    """GW170817 does NOT exclude a normal framework even at the low cutoff."""
    c = GWSpeedBound(low_cutoff=True)
    r = c.evaluate(StringTreeEFT().encode())
    assert r.satisfied
    assert r.details["ratio_to_bound"] < 1e-3      # orders below the bound


def test_would_bite_only_at_ultralow_cutoff():
    """A hypothetical ultra-low cutoff (~ueV) WOULD violate the bound -- confirming
    the constraint is real, just not relevant at the dark-energy scale."""
    th = Theory(coefficients={"g_R2": 0.4, "g_C": 0.4})
    dc = delta_cGW(0.8, 1e-6)        # 1 ueV cutoff
    assert dc > CGW_BOUND


def test_build_stack_gw_speed_optional():
    from stack import build_stack
    theo = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    gw = build_stack(bnossw_mean="geometric", rfc_form="convex_hull",
                     include_gw_speed=True)
    assert len(gw) == len(theo) + 1
    assert gw[-1].name == "gw_speed_bound"
    assert "gw_speed_bound" not in [c.name for c in theo]
