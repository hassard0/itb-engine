"""Tests for the holographic eta/s observable (v1.67)."""

import numpy as np
import pytest

from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.discovered import DiscoveredParityViolating
from itb.gravitational_observables import HolographicEtaOverS
from itb.theory import Theory


def test_kss_units_decrease_with_gR2():
    """Larger g_R2 lowers eta/s (further below the KSS bound)."""
    obs = HolographicEtaOverS(lam_map=0.22)
    hi = obs.predict(Theory(coefficients={"g_R2": 0.15}))[0]
    lo = obs.predict(Theory(coefficients={"g_R2": 0.40}))[0]
    assert hi > lo
    assert hi == pytest.approx(1 - 4*0.22*0.15)
    assert lo > 0.0   # largest g_R2 still gives physical (positive) eta/s


def test_all_in_scope_below_KSS():
    """Every framework with positive g_R2 sits below KSS (eta/s < 1 in KSS units)."""
    obs = HolographicEtaOverS()
    for fw in (AsymptoticSafety(), DiscoveredParityViolating()):
        assert obs.predict(fw.encode())[0] < 1.0


def test_jacobian():
    obs = HolographicEtaOverS(lam_map=0.22)
    J = obs.jacobian(Theory(coefficients={"g_R2": 0.2}), ["g_R2", "g_4"])
    assert J[0, 0] == pytest.approx(-4 * 0.22)
    assert J[0, 1] == 0.0


def test_in_predict_fingerprint():
    from itb.predict import predict
    p = predict("discovered_parity_violating")
    assert "holographic_eta_over_s_KSS_units" in p["observables"]
    assert p["observables"]["holographic_eta_over_s_KSS_units"] < 1.0
