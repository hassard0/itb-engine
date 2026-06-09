"""Tests for the neutron-star strong-field probe (v1.91)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import neutron_star as ns


def test_scaling_inverse_square_cutoff():
    a = ns.delta_Lambda_over_Lambda(0.4, 1e-3)
    b = ns.delta_Lambda_over_Lambda(0.4, 2e-3)
    assert a / b == __import__("pytest").approx(4.0)      # 1/M^2


def test_blind_at_dark_energy_cutoff():
    """delta Lambda/Lambda at the meV cutoff is far below GW170817 precision (~0.1)."""
    assert ns.delta_Lambda_over_Lambda(0.4, ns.E_LAMBDA_DE_eV) < 1e-10


def test_weaker_than_gw_speed():
    """The strongest-gravity probe reaches a LOWER cutoff than the GW speed test."""
    M_ns = ns.cutoff_reached(0.4, ns.E_CURV_eV, ns.LAMBDA_PRECISION)
    M_gw_speed = ns.cutoff_reached(0.4, 4.1e-13, 5e-16)
    assert M_ns < M_gw_speed                              # NS blinder than GW speed
    assert M_ns < ns.E_LAMBDA_DE_eV                       # both far below the cutoff
