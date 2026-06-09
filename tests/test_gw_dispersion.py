"""Tests for the LIGO GW dispersion test (v1.85)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from itb.constraints.gw_dispersion import (
    GWDispersionBound, delta_psi, E_LAMBDA_DE_eV)
from itb.constraints.gw_speed import delta_cGW
from itb.frameworks.horava_lifshitz import HoravaLifshitz
from itb.theory import Theory


def test_cumulative_enhancement_over_speed():
    """delta_Psi is enormously larger than delta v_g (lever arm ~ E_GW*D ~ 1e20)."""
    g, M = 0.6, E_LAMBDA_DE_eV
    dpsi = delta_psi(g, M)
    dcgw = delta_cGW(g, M)
    assert dpsi / dcgw > 1e15        # huge cumulative-phase enhancement


def test_reaches_mev_scale():
    """The dispersion frontier M_min is at the meV scale (not ueV like the speed test)."""
    b = GWDispersionBound(low_cutoff=True)
    m_min = b.m_min_excluded(0.6)
    assert 1e-4 < m_min < 1e-1       # ~meV, far above the speed test's ~ueV


def test_high_coupling_excluded_at_DE_cutoff():
    """A high-curvature theory (g_curv~1.2) at a dark-energy cutoff exceeds ~1 rad
    -> excluded by the current dispersion sensitivity."""
    b = GWDispersionBound(low_cutoff=True, psi_sens=1.0)
    r = b.evaluate(Theory(coefficients={"g_R2": 0.6, "g_C": 0.6}))
    assert r.details["delta_Psi_rad"] > 1.0
    assert not r.satisfied


def test_framework_at_frontier():
    """Horava (a high-curvature framework) sits at the dispersion frontier
    (delta_Psi within reach of ~0.1-1 rad) at a dark-energy cutoff."""
    b = GWDispersionBound(low_cutoff=True, psi_sens=1.0)
    r = b.evaluate(HoravaLifshitz().encode())
    assert r.details["delta_Psi_rad"] > 0.1     # at/near the frontier


def test_build_stack_dispersion_optional():
    from stack import build_stack
    theo = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    disp = build_stack(bnossw_mean="geometric", rfc_form="convex_hull",
                       include_gw_dispersion=True)
    assert len(disp) == len(theo) + 1
    assert disp[-1].name == "gw_dispersion_bound"
    assert "gw_dispersion_bound" not in [c.name for c in theo]
