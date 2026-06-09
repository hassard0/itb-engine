"""Tests for the species-scale bound (v1.96)."""
import pytest

from itb.constraints.species_scale import SpeciesScaleBound
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.theory import Theory


def test_species_monotone_in_curvature():
    c = SpeciesScaleBound()
    lo = c._species(Theory(coefficients={"g_R2": 0.1, "g_C": 0.1, "g_R3": 0.0}))
    hi = c._species(Theory(coefficients={"g_R2": 0.3, "g_C": 0.3, "g_R3": 0.2}))
    assert hi > lo
    assert lo == pytest.approx(1.0 + 2.0 * 0.2)        # N = 1 + nu*(sum)


def test_excludes_large_coupling_point():
    """A large curvature sector (sum ~1.5 -> N=4 > 3) is excluded."""
    c = SpeciesScaleBound(nu=2.0, N_max=3.0)
    th = Theory(coefficients={"g_R2": 0.5, "g_C": 0.5, "g_R3": 0.5})
    assert not c.evaluate(th).satisfied


def test_satisfied_by_survivor():
    """String tree-EFT (moderate couplings) satisfies the species bound."""
    assert SpeciesScaleBound().evaluate(StringTreeEFT().encode()).satisfied


def test_wired_into_stack():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
    from stack import build_stack
    s = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    assert "species_scale_bound" in [c.name for c in s]
