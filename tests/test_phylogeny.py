"""Tests for the RG phylogeny (v1.89)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import phylogeny as ph


def test_gstar_is_a_fixed_point():
    """beta vanishes at the NGFP g*."""
    assert np.allclose(ph.beta(ph.GSTAR), 0.0, atol=1e-12)


def test_weyl_coupling_asymptotically_free():
    """g_C (index 5) has beta < 0 for g_C > 0 -> driven to 0 in the UV."""
    g = ph.GSTAR.copy(); g[5] = 0.4
    assert ph.beta(g)[5] < 0
    # and the UV flow drives g_C down
    t, Y = ph.flow(g, t_span=(0.0, 6.0))
    assert Y[-1, 5] < Y[0, 5]


def test_flow_starts_at_initial_point():
    """At t in the integration the trajectory passes through the start (t=0 anchor)."""
    g0 = np.array([0.5, 0.4, 0.4, 0.33, 0.14, 0.35, 0.09, 0.03])
    t, Y = ph.flow(g0, t_span=(0.0, 5.0))
    assert np.allclose(Y[0], g0, atol=1e-6)


def test_flow_converges_toward_fixed_point():
    """UV flow reduces the distance to g* (frameworks are in its basin)."""
    g0 = np.array([0.5, 0.4, 0.4, 0.33, 0.14, 0.35, 0.09, 0.03])
    t, Y = ph.flow(g0, t_span=(0.0, 8.0))
    d0 = np.linalg.norm(Y[0] - ph.GSTAR)
    d1 = np.linalg.norm(Y[-1] - ph.GSTAR)
    assert d1 < d0
