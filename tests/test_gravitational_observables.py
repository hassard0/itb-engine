"""Tests for the decisive-experiment gravitational observables (v1.42)."""

import numpy as np
import pytest

from itb.frameworks.discovered import DiscoveredParityViolating
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.gravitational_observables import (
    GIEPhaseCorrection,
    GravitationalBirefringence,
    YukawaForceDeviation,
)
from itb.theory import Theory


def test_yukawa_matches_spec_sheet():
    """At 93 um (dark-energy cutoff), string-EFT (g_R2=0.20) deviates ~-11.9%
    from Newton, the parity-violating branch (g_R2=0.395) ~-16.0% (v1.41)."""
    obs = YukawaForceDeviation([93e-6])
    assert obs.predict(StringTreeEFT().encode())[0] == pytest.approx(-0.1185, abs=2e-3)
    assert obs.predict(DiscoveredParityViolating().encode())[0] == pytest.approx(-0.1597, abs=2e-3)


def test_yukawa_larger_gR2_longer_range():
    """Larger g_R2 -> lighter scalar -> deviation persists to longer range
    (bigger |delta| at fixed r)."""
    obs = YukawaForceDeviation([93e-6])
    big = abs(obs.predict(Theory(coefficients={"g_R2": 0.4}))[0])
    small = abs(obs.predict(Theory(coefficients={"g_R2": 0.15}))[0])
    assert big > small


def test_yukawa_jacobian_finite_difference():
    obs = YukawaForceDeviation([50e-6, 93e-6, 150e-6])
    t = Theory(coefficients={"g_R2": 0.25})
    J = obs.jacobian(t, ["g_R2"])[:, 0]
    eps = 1e-6
    fd = (obs.predict(Theory(coefficients={"g_R2": 0.25 + eps}))
          - obs.predict(Theory(coefficients={"g_R2": 0.25 - eps}))) / (2 * eps)
    assert np.allclose(J, fd, rtol=1e-3, atol=1e-6)


def test_birefringence_parity_only():
    """Birefringence vanishes for parity-conserving theories, nonzero otherwise."""
    obs = GravitationalBirefringence(np.linspace(0.5, 2.0, 5))
    assert np.allclose(obs.predict(StringTreeEFT().encode()), 0.0)
    assert np.any(obs.predict(DiscoveredParityViolating().encode()) != 0.0)


def test_birefringence_jacobian():
    obs = GravitationalBirefringence([1.0, 2.0], omega0=1.0)
    J = obs.jacobian(Theory(coefficients={"g_R2_parity": 0.0, "g_R3_parity": 0.0}),
                     ["g_R2_parity", "g_R3_parity"])
    assert np.allclose(J[:, 0], [1.0, 1.0])      # d/d g_R2_parity
    assert np.allclose(J[:, 1], [1.0, 2.0])      # d/d g_R3_parity = omega/omega0


def test_gie_correction_is_negative():
    """The R^2 scalar reduces the entangling phase (Dr. M. sign)."""
    obs = GIEPhaseCorrection(90e-6)
    assert obs.predict(DiscoveredParityViolating().encode())[0] < 0.0
