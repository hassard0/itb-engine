"""Tests for the holographic complexity rate observable (v1.98)."""
import pytest

from itb.gravitational_observables import HolographicComplexityRate
from itb.theory import Theory


def test_lloyd_units_and_weyl_driven():
    obs = HolographicComplexityRate(kappa=1.0)
    assert obs.predict(Theory(coefficients={"g_C": 0.0}))[0] == pytest.approx(1.0)
    assert obs.predict(Theory(coefficients={"g_C": 0.4}))[0] == pytest.approx(1.4)


def test_euler_topological_zero_jacobian():
    """g_R2 (Euler) is topological -> no contribution; g_C drives the rate."""
    obs = HolographicComplexityRate(kappa=1.0)
    J = obs.jacobian(Theory(coefficients={"g_C": 0.3, "g_R2": 0.2}), ["g_C", "g_R2"])
    assert J[0, 0] == 1.0          # g_C
    assert J[0, 1] == 0.0          # g_R2 topological


def test_violates_lloyd_for_positive_gC():
    obs = HolographicComplexityRate()
    assert obs.predict(Theory(coefficients={"g_C": 0.3}))[0] > 1.0


def test_in_predict_fingerprint():
    from itb.predict import predict
    p = predict("discovered_data_driven")
    assert "holographic_complexity_rate_lloyd_units" in p["observables"]
    assert p["observables"]["holographic_complexity_rate_lloyd_units"] > 1.0
