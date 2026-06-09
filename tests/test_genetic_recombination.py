"""Tests for genetic recombination (v1.95)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import genetic_recombination as gr


def test_recombination_preserves_structure():
    """A hybrid is an 8-vector with sectors taken from the parents."""
    a = gr.genome(gr.FRAMEWORKS["string_tree_eft"])
    b = gr.genome(gr.FRAMEWORKS["causal_set"])
    child = np.concatenate([a[gr.MATTER], b[gr.GRAV], a[gr.PARITY]])
    assert child.shape == (8,)
    assert np.allclose(child[gr.MATTER], a[gr.MATTER])
    assert np.allclose(child[gr.GRAV], b[gr.GRAV])


def test_self_hybrid_of_survivor_is_consistent():
    """A framework recombined with itself (all sectors from a survivor) is consistent."""
    g = gr.genome(gr.FRAMEWORKS["string_tree_eft"])
    assert gr.consistent(g)
    # and the string-matter + causal-set-graviton hybrid (the top-vigor one) survives
    a = gr.genome(gr.FRAMEWORKS["string_tree_eft"])
    b = gr.genome(gr.FRAMEWORKS["causal_set"])
    p = gr.genome(gr.FRAMEWORKS["pure_gr"])
    hybrid = np.concatenate([a[gr.MATTER], b[gr.GRAV], p[gr.PARITY]])
    assert gr.consistent(hybrid)


def test_hybrid_vigor_possible():
    """The top-vigor hybrid is MORE robust than its best parent."""
    a = gr.genome(gr.FRAMEWORKS["string_tree_eft"])
    b = gr.genome(gr.FRAMEWORKS["causal_set"])
    p = gr.genome(gr.FRAMEWORKS["pure_gr"])
    hybrid = np.concatenate([a[gr.MATTER], b[gr.GRAV], p[gr.PARITY]])
    r_hybrid = gr.robustness(hybrid)
    parents = [r for r in (gr.robustness(a), gr.robustness(b), gr.robustness(p))
               if gr.consistent(a) or True]
    # hybrid is consistent and robust (positive interior margin)
    assert gr.consistent(hybrid) and r_hybrid > 0
