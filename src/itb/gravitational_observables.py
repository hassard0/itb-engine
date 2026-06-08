"""Gravitational observables for the decisive-experiment program (v1.42).

First-class `Observable`s (predict + jacobian) for the three experiments the
engine ties together (docs/results 2026-06-08 v1.39-41), so the Fisher-metric
and first-disagreement machinery can rank them natively against the amplitude
observables:

  - YukawaForceDeviation:   short-range gravity. Fractional deviation from Newton
        delta(r) = -(1/3) exp(-r/lambda_Y),  lambda_Y = hbar c / m0,
        m0 = E_Lambda / sqrt(6 g_R2)  (Stelle R^2 scalar). Depends on g_R2.
  - GravitationalBirefringence: parity sector. Frequency-dependent polarization
        signal ~ g_R2_parity + (omega/omega0) * g_R3_parity. Depends on the parity coeffs.
  - GIEPhaseCorrection: the fractional reduction of the gravitationally-induced
        entangling phase from the same Yukawa (Dr. M.: scalar enters with -sign).

These encode the physics of docs/results v1.39-41; toy normalization, real
structure.
"""

import numpy as np

from itb.observables import Observable
from itb.theory import Theory

HBARC_eV_m = 1.973e-7
E_LAMBDA_DARK_ENERGY = 2.4e-3   # eV; dark-energy / sub-mm scale (v1.40)
SCALAR_AMP = 1.0 / 3.0


class YukawaForceDeviation(Observable):
    """Fractional deviation from Newton vs separation, from the R^2 scalar."""

    name = "yukawa_force_deviation"

    def __init__(self, separations_m, E_Lambda_eV: float = E_LAMBDA_DARK_ENERGY):
        self.r = np.asarray(separations_m, dtype=float)
        self.E_Lambda = float(E_Lambda_eV)

    def _lambda_Y(self, g_R2):
        m0 = self.E_Lambda / np.sqrt(6.0 * max(g_R2, 1e-12))
        return HBARC_eV_m / m0

    def predict(self, theory: Theory) -> np.ndarray:
        g = theory.coefficients.get("g_R2", 0.0)
        lam = self._lambda_Y(g)
        return -SCALAR_AMP * np.exp(-self.r / lam)

    def jacobian(self, theory: Theory, params: list[str]) -> np.ndarray:
        g = theory.coefficients.get("g_R2", 0.0)
        lam = self._lambda_Y(g)
        base = -SCALAR_AMP * np.exp(-self.r / lam)
        # d(delta)/d(g_R2) = base * (r/lam^2) * d(lam)/d(g_R2); d(lam)/dg = lam/(2 g)
        dlam_dg = lam / (2.0 * max(g, 1e-12))
        ddelta_dg = base * (self.r / lam**2) * dlam_dg
        cols = []
        for p in params:
            cols.append(ddelta_dg if p == "g_R2" else np.zeros_like(self.r))
        return np.stack(cols, axis=1)


class GravitationalBirefringence(Observable):
    """Frequency-dependent GW polarization rotation from the parity sector."""

    name = "gravitational_birefringence"

    def __init__(self, omegas, omega0: float = 1.0):
        self.omega = np.asarray(omegas, dtype=float)
        self.omega0 = float(omega0)

    def predict(self, theory: Theory) -> np.ndarray:
        a = theory.coefficients.get("g_R2_parity", 0.0)
        b = theory.coefficients.get("g_R3_parity", 0.0)
        return a + (self.omega / self.omega0) * b

    def jacobian(self, theory: Theory, params: list[str]) -> np.ndarray:
        cols = []
        for p in params:
            if p == "g_R2_parity":
                cols.append(np.ones_like(self.omega))
            elif p == "g_R3_parity":
                cols.append(self.omega / self.omega0)
            else:
                cols.append(np.zeros_like(self.omega))
        return np.stack(cols, axis=1)


class GIEPhaseCorrection(Observable):
    """Fractional change of the GIE entangling phase from the R^2 Yukawa at the
    superposition scale r (single kinematic point). Negative: the scalar reduces
    the phase (Dr. M.)."""

    name = "gie_phase_correction"

    def __init__(self, r_m: float, E_Lambda_eV: float = E_LAMBDA_DARK_ENERGY):
        self.r = float(r_m)
        self._yuk = YukawaForceDeviation([r_m], E_Lambda_eV)

    def predict(self, theory: Theory) -> np.ndarray:
        return self._yuk.predict(theory)

    def jacobian(self, theory: Theory, params: list[str]) -> np.ndarray:
        return self._yuk.jacobian(theory, params)
